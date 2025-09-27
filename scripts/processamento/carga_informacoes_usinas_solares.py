import requests
import geopandas as gpd
from shapely.geometry import shape, MultiPolygon, Polygon
from datetime import datetime
from datetime import timezone
from scripts.integracao.conexao_snow_flake import Conexao
from utils.gerador_arquivos import GeradorDeArquivos

class ProcessadorDadosUsinasSolares:

    # Funções utilizada para consultar o clima
    @staticmethod
    def obtenha_clima(latitude, longitude):
        try:
            start_date = "2025-01-01"
            end_date = "2025-09-23"

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

            #Temperaturas
            temperatures = data.get("hourly", {}).get("temperature_2m", [])
            #Nubulosidade
            cloudcover = data.get("hourly", {}).get("cloudcover", [])
            #Irradianca
            irradiance = data.get("hourly", {}).get("shortwave_radiation", [])
            #Data e hora
            times = data.get("hourly", {}).get("time", [])
            #Altitude
            altitude_m = data.get("elevation")

            total = len(times)
            result = {}
            for i in range(total):
                # Ignorar valores nulos
                if (
                    temperatures[i] is None
                    or cloudcover[i] is None
                    or irradiance[i] is None
                ):
                    continue

                # Converter string ISO para datetime
                time_dt = datetime.fromisoformat(times[i]).replace(tzinfo=timezone.utc)
                result[time_dt] = {
                    "temperatura_C": temperatures[i],
                    "nebulosidade_%": cloudcover[i],
                    "irradiancia_Wm2": irradiance[i],
                    "altitude_m": altitude_m
                }

            return result

        except Exception as e:
            print(f"Erro ao consultar clima: {e}")
            return None

    def prepare_os_dados_para_treino_usina_solar():

            sql = """
                SELECT DIN_INSTANTE, ID_ESTADO, NOM_USINA_CONJUNTO, 
                VAL_FATORCAPACIDADE, VAL_GERACAOPROGRAMADA, 
                VAL_GERACAOVERIFICADA, VAL_CAPACIDADEINSTALADA,
                val_latitudesecoletora, val_longitudesecoletora
                FROM fator_capacidade
                WHERE nom_tipousina = 'Solar'
                ORDER BY NOM_USINA_CONJUNTO, val_latitudesecoletora, val_longitudesecoletora, DIN_INSTANTE
            """

            conexao = Conexao.obtenha()
            cur = conexao.cursor()
            batch_size = 10000  # número de linhas por batch
            dados_treino = []

            try:
                cur.execute(sql)
                colunas = [col[0] for col in cur.description]

                res_cache = {}  # cache por coordenada para evitar recalcular potencial

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
                        data_hora = linha_dict["DIN_INSTANTE"]

                        # se vier como datetime sem tz, adiciona UTC
                        data_hora = data_hora.replace(tzinfo=timezone.utc)
                           
                        # Recalcula apenas se coordenada não está no cache
                        if coord_key not in res_cache:
                            res_cache[coord_key] = ProcessadorDadosUsinasSolares.obtenha_clima(lat, lon)
                            
                        dados_lat_lon = res_cache[coord_key]
                        dados_dia_hora = dados_lat_lon[data_hora]

                        temperatura_C = dados_dia_hora["temperatura_C"]
                        nebulosidade = dados_dia_hora["nebulosidade_%"]
                        irradiancia_Wm2 = dados_dia_hora["irradiancia_Wm2"]
                        altitude = dados_dia_hora["altitude_m"]
                      
                        informacao_do_dia = {
                            "estado": linha_dict["ID_ESTADO"],
                            "nomeUsina": linha_dict["NOM_USINA_CONJUNTO"],
                            "din_instante": data_hora.strftime('%Y-%m-%d %H:%M:%S'),
                            "latitude": lat,
                            "longitude": lon,
                            "temperatura_C": temperatura_C,
                            "nebulosidade_percentual": nebulosidade,
                            "irradiancia_Wm2": irradiancia_Wm2,
                            "altitude_m": altitude,
                            "fator_capacidade": linha_dict["VAL_FATORCAPACIDADE"],
                            "geracao_programada": linha_dict["VAL_GERACAOPROGRAMADA"],
                            "geracao_verificada": linha_dict["VAL_GERACAOVERIFICADA"],
                            "capacidade_instalada": linha_dict["VAL_CAPACIDADEINSTALADA"],
                        }

                        dados_treino.append(informacao_do_dia)
                
                GeradorDeArquivos().gere_arquivo(dados_treino, "dados_treino_usinas_solares.csv")

            finally:
                cur.close()

    def prepare_os_dados_usinas_solar_de_goias():
        # Carregar municípios de Goiás
        PATH_MUNICIPIOS_GO = "https://raw.githubusercontent.com/tbrugz/geodata-br/master/geojson/geojs-52-mun.json"
        mun_raw = gpd.read_file(PATH_MUNICIPIOS_GO)

        # Transformar geometria em Shapely
        mun_raw['geometry'] = mun_raw['geometry'].apply(shape)

        # Lista para armazenar resultados
        resultados = []

        for idx, row in mun_raw.iterrows():
            geom = row['geometry']
            nome_municipio = row['name']
            
            centroid = geom.centroid
            lat = centroid.y
            lon = centroid.x

            resultado = ProcessadorDadosUsinasSolares.obtenha_clima(lat, lon)
    
            for time_dt, dados_dia_hora in resultado.items():
                temperatura_C = dados_dia_hora["temperatura_C"]
                nebulosidade = dados_dia_hora["nebulosidade_%"]
                irradiancia_Wm2 = dados_dia_hora["irradiancia_Wm2"]
                altitude = dados_dia_hora["altitude_m"]
                
                
                informacao_do_dia = {
                    "estado": "GO",
                    "nomeUsina": nome_municipio,
                    "din_instante": time_dt.strftime('%Y-%m-%d %H:%M:%S'),
                    "latitude": lat,
                    "longitude": lon,
                    "temperatura_C": temperatura_C,
                    "nebulosidade_percentual": nebulosidade,
                    "irradiancia_Wm2": irradiancia_Wm2,
                    "altitude_m": altitude
                }

                resultados.append(informacao_do_dia)
                

        GeradorDeArquivos().gere_arquivo(resultados, "potencial_energia_solar_goias.csv")
