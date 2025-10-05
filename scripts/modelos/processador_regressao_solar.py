import pandas as pd
from scripts.modelos.processador_regressao import ProcessadorDeRegressao
from scripts.modelos.modelos_regressao import ModelosEnum
from utils.gerenciador_arquivos import GerenciadorDeArquivos
from scripts.modelos.tipos_de_usinas import TipoDeUsinasEnum

class ProcessadorRegressaoUsinaSolar(ProcessadorDeRegressao):
    """
    Classe responsável por preparar os dados das usinas solares. 
    """

    def __init__(self):
        # --- Dados para treino ---
        GerenciadorDeArquivos.descompacte("dados_treino_usinas_solares")
        df_dados_treino = pd.read_csv("data/processados/dados_treino_usinas_solares.csv")

        # --- Dados de Goiás ---
        GerenciadorDeArquivos.descompacte("potencial_energia_solar_goias")
        df_dados_predicao_goias = pd.read_csv("data/processados/potencial_energia_solar_goias.csv")
        
        # cria instância do objeto
        super().__init__(modelo_enum=ModelosEnum.XGBOOST,
                        df_dados_treino=df_dados_treino,
                        df_dados_predicao=df_dados_predicao_goias,
                        previsao="fator_capacidade",
                        nome_arquivo="resultado_solar_xgboost.csv",
                        tipoDeUsina= TipoDeUsinasEnum.SOLAR)
       
        # Lista de colunas utilizadas como variáveis preditoras
        self.feature_cols = ['temperatura_C', 'nebulosidade_percentual', 'irradiancia_Wm2',
                             'altitude_m','ano', 'mes', 'dia', 'hora', 'dia_da_semana']

    def processe():
        super().processe_regressao()