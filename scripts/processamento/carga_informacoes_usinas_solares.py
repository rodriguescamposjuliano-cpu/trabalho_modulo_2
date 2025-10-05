import requests
import geopandas as gpd
from shapely.geometry import shape, MultiPolygon, Polygon
from datetime import datetime, timezone
from scripts.integracao.conexao_snow_flake import Conexao
from utils.gerenciador_arquivos import GerenciadorDeArquivos


class ProcessadorDadosUsinasSolares:
    """
    Classe responsável por preparar e enriquecer os dados relacionados às usinas solares.

    Essa classe realiza:
      - Consulta dos dados históricos de clima (temperatura, nebulosidade e irradiância);
      - Extração de dados das usinas solares do banco de dados Snowflake;
      - Geração de datasets para treinamento de modelos de regressão;
      - Criação de arquivos CSV com os resultados organizados.

    Métodos principais:
      - obtenha_clima(latitude, longitude): consulta clima histórico via API Open-Meteo.
      - prepare_os_dados_para_treino_usina_solar(): extrai dados de usinas do banco + clima.
      - prepare_os_dados_usinas_solar_de_goias(): gera dataset de potencial solar para GO.
    """

    # ==========================================================
    # MÉTODO ESTÁTICO: Consulta dados climáticos históricos
    # ==========================================================
    @staticmethod
    def obtenha_clima(latitude, longitude):
        """
        Consulta os dados históricos de clima (temperatura, nebulosidade, irradiância)
        para uma coordenada geográfica específica (latitude e longitude).

        Utiliza a API pública Open-Meteo para obter dados horários desde
        01/01/2024 até 26/09/2025.

        Retorna:
            dict: Mapeamento datetime → medições climáticas (temperatura, nebulosidade, etc.)
        """
        try:
            start_date = "2024-01-01"
            end_date = "2025-09-26"

            url = (
                f"https://archive-api.open-meteo.com/v1/archive?"
                f"latitude={latitude}&longitude={longitude}&"
                f"start_date={start_date}&end_date={end_date}&"
                f"hourly=temperature_2m,cloudcover,shortwave_radiation&"
                f"timezone=America/Sao_Paulo"
            )

            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            # Extração dos dados relevantes
            temperatures = data.get("hourly", {}).get("temperature_2m", [])
            cloudcover = data.get("hourly", {}).get("cloudcover", [])
            irradiance = data.get("hourly", {}).get("shortwave_radiation", [])
            times = data.get("hourly", {}).get("time", [])
            altitude_m = data.get("elevation")

            result = {}
            for i in range(len(times)):
                # Ignora medições com valores nulos
                if (
                    temperatures[i] is None
                    or cloudcover[i] is None
                    or irradiance[i] is None
                ):
                    continue

                # Converte string ISO em datetime UTC
                time_dt = datetime.fromisoformat(times[i]).replace(tzinfo=timezone.utc)
                result[time_dt] = {
                    "temperatura_C": temperatures[i],
                    "nebulosidade_%": cloudcover[i],
                    "irradiancia_Wm2": irradiance[i],
                    "altitude_m": altitude_m,
                }

            return result

        except Exception as e:
            print(f"Erro ao consultar clima: {e}")
            return None

    # ==========================================================
    # MÉTODO PRINCIPAL: Prepara dados de usinas solares do banco
    # ==========================================================
    def prepare_os_dados_para_treino_usina_solar():
        """
        Extrai dados de geração das usinas solares do banco Snowflake,
        enriquece com dados climáticos e gera um CSV com as informações
        consolidadas para treinamento de modelos preditivos.
        """
        sql = """
            SELECT DIN_INSTANTE, ID_ESTADO, NOM_USINA_CONJUNTO, 
                   VAL_FATORCAPACIDADE, VAL_GERACAOPROGRAMADA, 
                   VAL_GERACAOVERIFICADA, VAL_CAPACIDADEINSTALADA,
                   VAL_LATITUDESECOLETORA, VAL_LONGITUDESECOLETORA
            FROM fator_capacidade
            WHERE nom_tipousina = 'Solar'
            ORDER BY NOM_USINA_CONJUNTO, VAL_LATITUDESECOLETORA, VAL_LONGITUDESECOLETORA, DIN_INSTANTE
        """

        conexao = Conexao.obtenha()
        cur = conexao.cursor()
        batch_size = 10000  # Quantidade de linhas por leitura (otimiza memória)
        dados_treino = []

        try:
            cur.execute(sql)
            colunas = [col[0] for col in cur.description]

            # Cache de coordenadas (evita consultas repetidas à API)
            res_cache = {}

            while True:
                rows = cur.fetchmany(batch_size)
                if not rows:
                    break

                for row in rows:
                    linha_dict = dict(zip(colunas, row))
                    lat = linha_dict["VAL_LATITUDESECOLETORA"]
                    lon = linha_dict["VAL_LONGITUDESECOLETORA"]

                    if lat is None or lon is None:
                        continue

                    coord_key = (lat, lon)
                    data_hora = linha_dict["DIN_INSTANTE"].replace(tzinfo=timezone.utc)

                    # Consulta clima apenas uma vez por coordenada
                    if coord_key not in res_cache:
                        res_cache[coord_key] = ProcessadorDadosUsinasSolares.obtenha_clima(lat, lon)

                    dados_lat_lon = res_cache[coord_key]
                    dados_dia_hora = dados_lat_lon.get(data_hora)
                    if not dados_dia_hora:
                        continue

                    # Enriquecimento com clima
                    informacao_do_dia = {
                        "estado": linha_dict["ID_ESTADO"],
                        "nomeUsina": linha_dict["NOM_USINA_CONJUNTO"],
                        "din_instante": data_hora.strftime('%Y-%m-%d %H:%M:%S'),
                        "latitude": lat,
                        "longitude": lon,
                        "temperatura_C": dados_dia_hora["temperatura_C"],
                        "nebulosidade_percentual": dados_dia_hora["nebulosidade_%"],
                        "irradiancia_Wm2": dados_dia_hora["irradiancia_Wm2"],
                        "altitude_m": dados_dia_hora["altitude_m"],
                        "fator_capacidade": linha_dict["VAL_FATORCAPACIDADE"],
                        "geracao_programada": linha_dict["VAL_GERACAOPROGRAMADA"],
                        "geracao_verificada": linha_dict["VAL_GERACAOVERIFICADA"],
                        "capacidade_instalada": linha_dict["VAL_CAPACIDADEINSTALADA"],
                    }

                    dados_treino.append(informacao_do_dia)

            # Gera arquivo CSV consolidado
            GerenciadorDeArquivos().gere_arquivo(dados_treino, "dados_treino_usinas_solares.csv")

        finally:
            cur.close()

    # ==========================================================
    # MÉTODO AUXILIAR: Potencial solar dos municípios de Goiás
    # ==========================================================
    def prepare_os_dados_usinas_solar_de_goias():
        """
        Gera dataset de potencial de energia solar para os municípios do estado de Goiás.

        O método:
          - Lê o arquivo GeoJSON com os municípios de GO;
          - Calcula o centróide (latitude/longitude) de cada município;
          - Consulta dados climáticos históricos via API;
          - Gera um CSV consolidando o potencial solar horário.
        """
        PATH_MUNICIPIOS_GO = "https://raw.githubusercontent.com/tbrugz/geodata-br/master/geojson/geojs-52-mun.json"
        mun_raw = gpd.read_file(PATH_MUNICIPIOS_GO)
        mun_raw['geometry'] = mun_raw['geometry'].apply(shape)

        resultados = []

        for _, row in mun_raw.iterrows():
            geom = row['geometry']
            nome_municipio = row['name']

            # Coordenadas do centróide do município
            centroid = geom.centroid
            lat, lon = centroid.y, centroid.x

            resultado = ProcessadorDadosUsinasSolares.obtenha_clima(lat, lon)
            if not resultado:
                continue

            # Monta registros diários por município
            for time_dt, dados_dia_hora in resultado.items():
                informacao_do_dia = {
                    "estado": "GO",
                    "nomeUsina": nome_municipio,
                    "din_instante": time_dt.strftime('%Y-%m-%d %H:%M:%S'),
                    "latitude": lat,
                    "longitude": lon,
                    "temperatura_C": dados_dia_hora["temperatura_C"],
                    "nebulosidade_percentual": dados_dia_hora["nebulosidade_%"],
                    "irradiancia_Wm2": dados_dia_hora["irradiancia_Wm2"],
                    "altitude_m": dados_dia_hora["altitude_m"],
                }
                resultados.append(informacao_do_dia)

        # Gera CSV final com o potencial solar
        GerenciadorDeArquivos().gere_arquivo(resultados, "potencial_energia_solar_goias.csv")
