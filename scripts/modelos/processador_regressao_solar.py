import pandas as pd
from scripts.modelos.processador_regressao import ProcessadorDeRegressao
from scripts.modelos.modelos_regressao import ModelosEnum

class ProcessadorRegressaoUsinaSolar(ProcessadorDeRegressao):

    def __init__(self):
        # --- Dados para treino ---
        df_usinas = pd.read_csv("data/processados/dados_treino_usinas_solares.csv")
        # --- Dados de Goiás ---
        df_goias = pd.read_csv("data/processados/potencial_energia_solar_goias.csv")
        
        # cria instância do objeto
        super().__init__(modelo_enum=ModelosEnum.XGBOOST,
                        df_dados_treino=df_usinas,
                        df_dados_predicao=df_goias,
                        previsao="fator_capacidade",
                        nome_arquivo="resultado_solar_xgboost.csv")
       

        self.feature_cols = ['temperatura_C', 'nebulosidade_percentual', 'irradiancia_Wm2',
                             'altitude_m','ano', 'mes', 'dia', 'hora', 'dia_da_semana']

    def processe():
        super().processe_regressao()