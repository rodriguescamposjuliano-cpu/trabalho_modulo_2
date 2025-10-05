import requests
import math
import geopandas as gpd
from shapely.geometry import shape, MultiPolygon, Polygon
import pandas as pd
from datetime import datetime
from datetime import timezone
from scripts.integracao.conexao_snow_flake import Conexao
from utils.gerenciador_arquivos import GerenciadorDeArquivos

class ProcessadorDadosUsinasEolicas:
    """ 
    Classe responsável por obter, processar e preparar os dados de usinas eólicas
    para fins analíticos e de modelagem preditiva.

    Esta classe integra dados do banco Snowflake (fatores de capacidade e informações operacionais)
    com dados meteorológicos obtidos via API (Open-Meteo), enriquecendo o dataset
    com atributos ambientais como velocidade do vento, rajadas e direção.
    """

    # ========================================================
    # CONSULTA À API METEOROLÓGICA
    # ========================================================
    @staticmethod
    def obtenha_informacoes_vento_altitude(lat, lon):
        """
        Consulta a API Open-Meteo para obter informações de vento e altitude
        com base na latitude e longitude informadas.

        Retorna um dicionário contendo:
        - velocidade média do vento (m/s)
        - rajada de vento (m/s)
        - direção do vento (graus)
        - altitude (metros)
        indexado por data/hora.

        Caso haja erro na API, retorna None.
        """
        url = f"https://archive-api.open-meteo.com/v1/era5?latitude={lat}&longitude={lon}&start_date=2024-01-01&end_date=2025-09-26&hourly=windspeed_10m,windgusts_10m,winddirection_10m"

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            # Extrai dados horários
            wind_speeds = data.get("hourly", {}).get("windspeed_10m", [])
            windgusts_10m = data.get("hourly", {}).get("windgusts_10m", [])
            winddirection_10m = data.get("hourly", {}).get("winddirection_10m", [])
            times = data.get("hourly", {}).get("time", [])
            altitude_m = data["elevation"]

            result = {}
            for i in range(len(times)):
                # Ignora valores nulos ou inválidos
                if (
                    wind_speeds[i] is None 
                    or windgusts_10m[i] is None 
                    or winddirection_10m[i] is None
                ):
                    continue
                    
                # Converte a data/hora ISO para datetime UTC
                time_dt = datetime.fromisoformat(times[i]).replace(tzinfo=timezone.utc)
                result[time_dt] = {
                    "velocidade_vendo_10m": wind_speeds[i],
                    "rajada_vento_10m": windgusts_10m[i],
                    "direcao_vento_10m": winddirection_10m[i],
                    "altitude_m": altitude_m
                }
            
            return result
        except Exception as e:
            print(f"Erro ao consultar vento: {e}")
            return None
        
    # ========================================================
    # CÁLCULOS DE RUGOSIDADE E POTENCIAL EÓLICO
    # ========================================================
    @staticmethod
    def get_rugosidade(lat, lon):
        """
        Retorna um valor aproximado de rugosidade do terreno com base na latitude.
        A rugosidade é um fator que influencia diretamente a velocidade do vento
        e, portanto, o potencial eólico.

        Valores típicos:
        - 0.2: terrenos planos (menor atrito)
        - 0.3 a 0.5: terrenos com relevo mais irregular
        """
        if abs(lat) < 5:
            return 0.2
        elif lat > 10:
            return 0.5
        else:
            return 0.3
    
    @staticmethod
    def classificar_potencial(ipe):
        """
        Classifica o Índice de Potencial Eólico (IPE) em três níveis:
        - Alto Potencial (≥ 5000)
        - Médio Potencial (≥ 2500)
        - Baixo Potencial (< 2500)
        """
        if ipe >= 5000:
            return "Alto Potencial"
        elif ipe >= 2500:
            return "Médio Potencial"
        else:
            return "Baixo Potencial"
    
    @staticmethod
    def calcular_potencial_eolico(lat, lon, vento, altitude):
        """
        Calcula o Índice de Potencial Eólico (IPE) a partir da velocidade do vento,
        altitude e rugosidade do terreno.

        Fórmula:
            IPE = (vento³ / rugosidade) * ajuste_altitude

        Onde:
        - rugosidade: coeficiente de atrito do terreno
        - ajuste_altitude: fator logarítmico que aumenta o potencial conforme a altitude
        """
        rugosidade = ProcessadorDadosUsinasEolicas.get_rugosidade(lat, lon)

        if vento is None or altitude is None:
            return None

        ajuste_altitude = math.log(max(1 + altitude / 10, 1.01))
        ipe = (vento**3 / max(rugosidade, 0.1)) * ajuste_altitude
        classificacao = ProcessadorDadosUsinasEolicas.classificar_potencial(ipe)

        return ipe, classificacao, rugosidade

    # ========================================================
    # PREPARAÇÃO DOS DADOS DE TREINO (USINAS EÓLICAS)
    # ========================================================
    def prepare_os_dados_para_treino_usina_eolica():
        """
        Extrai os dados das usinas eólicas do Snowflake, consulta as informações
        meteorológicas via API e gera um arquivo CSV consolidado com atributos
        físicos, geográficos e de geração elétrica.

        Saída: 'dados_treino_usinas_eolicas.csv'
        """
        sql = """
            SELECT DIN_INSTANTE, ID_ESTADO, NOM_USINA_CONJUNTO, 
            VAL_FATORCAPACIDADE, VAL_GERACAOPROGRAMADA, 
            VAL_GERACAOVERIFICADA, VAL_CAPACIDADEINSTALADA,
            val_latitudesecoletora, val_longitudesecoletora
            FROM fator_capacidade
            WHERE nom_tipousina = 'Eólica'
            ORDER BY NOM_USINA_CONJUNTO, val_latitudesecoletora, val_longitudesecoletora, DIN_INSTANTE
        """

        conexao = Conexao.obtenha()
        cur = conexao.cursor()
        batch_size = 10000  
        dados_treino = []

        try:
            cur.execute(sql)
            colunas = [col[0] for col in cur.description]
            res_cache = {}  # cache para evitar consultas repetidas na API

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

                    # Consulta os dados de vento (usando cache se disponível)
                    if coord_key not in res_cache:
                        res_cache[coord_key] = ProcessadorDadosUsinasEolicas.obtenha_informacoes_vento_altitude(lat, lon)
                        
                    dados_lat_lon = res_cache[coord_key]
                    dados_dia_hora = dados_lat_lon[data_hora]

                    velocidade_vendo_10m = dados_dia_hora["velocidade_vendo_10m"]
                    rajada_vento_10m = dados_dia_hora["rajada_vento_10m"]
                    direcao_vento_10m = dados_dia_hora["direcao_vento_10m"]
                    altitude = dados_dia_hora["altitude_m"]
                        
                    # Cálculo do potencial eólico
                    indice_potencial_eolico, classificacao, rugosidade = ProcessadorDadosUsinasEolicas.calcular_potencial_eolico(lat, lon, velocidade_vendo_10m, altitude)
                
                    # Montagem do registro final
                    informacao_do_dia = {
                        "estado": linha_dict["ID_ESTADO"],
                        "nomeUsina": linha_dict["NOM_USINA_CONJUNTO"],
                        "din_instante": data_hora.strftime('%Y-%m-%d %H:%M:%S'),
                        "latitude": lat,
                        "longitude": lon,
                        "vento_medio_m_s": round(velocidade_vendo_10m, 2),
                        "rajada_vento_10m": round(rajada_vento_10m, 2),
                        "direcao_vento_10m": round(direcao_vento_10m, 2),
                        "altitude_m": altitude,
                        "rugosidade": rugosidade,
                        "indice_potencial": round(indice_potencial_eolico, 2),
                        "classificacao": classificacao,
                        "fator_capacidade": linha_dict["VAL_FATORCAPACIDADE"],
                        "geracao_programada": linha_dict["VAL_GERACAOPROGRAMADA"],
                        "geracao_verificada": linha_dict["VAL_GERACAOVERIFICADA"],
                        "capacidade_instalada": linha_dict["VAL_CAPACIDADEINSTALADA"],
                    }

                    dados_treino.append(informacao_do_dia)

            # Gera o arquivo final consolidado
            GerenciadorDeArquivos().gere_arquivo(dados_treino, "dados_treino_usinas_eolicas.csv")

        finally:
            cur.close()

    # ========================================================
    # GERA POTENCIAL EÓLICO PARA O ESTADO DE GOIÁS
    # ========================================================
    def prepare_os_dados_usinas_eolicas_de_goias():
        """
        Obtém o mapa dos municípios de Goiás via GeoJSON, extrai o centróide
        de cada cidade e consulta a API Open-Meteo para calcular o potencial
        eólico de cada localidade.

        Saída: 'potencial_energia_eolica_goias.csv'
        """
        # Carrega o GeoJSON dos municípios goianos
        PATH_MUNICIPIOS_GO = "https://raw.githubusercontent.com/tbrugz/geodata-br/master/geojson/geojs-52-mun.json"
        mun_raw = gpd.read_file(PATH_MUNICIPIOS_GO)
        mun_raw['geometry'] = mun_raw['geometry'].apply(shape)

        resultados = []

        for idx, row in mun_raw.iterrows():
            geom = row['geometry']
            nome_municipio = row['name']
            
            # Extrai o centróide da cidade
            centroid = geom.centroid
            lat = centroid.y
            lon = centroid.x

            # Consulta dados de vento
            resultado = ProcessadorDadosUsinasEolicas.obtenha_informacoes_vento_altitude(lat, lon)

            for time_dt, dados_dia_hora in resultado.items():
                velocidade_vendo_10m = dados_dia_hora["velocidade_vendo_10m"]
                rajada_vento_10m = dados_dia_hora["rajada_vento_10m"]
                direcao_vento_10m = dados_dia_hora["direcao_vento_10m"]
                altitude = dados_dia_hora["altitude_m"]
                    
                indice_potencial_eolico, classificacao, rugosidade = ProcessadorDadosUsinasEolicas.calcular_potencial_eolico(lat, lon, velocidade_vendo_10m, altitude)
                
                informacao_do_dia = {
                    "estado": "GO",
                    "nomeUsina": nome_municipio,
                    "din_instante": time_dt.strftime('%Y-%m-%d %H:%M:%S'),
                    "latitude": lat,
                    "longitude": lon,
                    "vento_medio_m_s": round(velocidade_vendo_10m, 2),
                    "rajada_vento_10m": round(rajada_vento_10m, 2),
                    "direcao_vento_10m": round(direcao_vento_10m, 2),
                    "altitude_m": altitude,
                    "rugosidade": rugosidade,
                    "indice_potencial": round(indice_potencial_eolico, 2),
                    "classificacao": classificacao
                }

                resultados.append(informacao_do_dia)
                
        GerenciadorDeArquivos().gere_arquivo(resultados, "potencial_energia_eolica_goias.csv")
