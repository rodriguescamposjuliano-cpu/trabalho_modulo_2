import pandas as pd
from scripts.modelos.processador_regressao import ProcessadorDeRegressao
from scripts.modelos.modelos_regressao import ModelosEnum

class ProcessadorRegressaoUsinaEolica(ProcessadorDeRegressao):

    def __init__(self):
       # --- Dados para treino ---
        df_usinas = pd.read_csv("data/processados/dados_treino_usinas_eolicas.csv")
        # --- Dados de Goiás ---
        df_goias = pd.read_csv("data/processados/potencial_energia_eolica_goias.csv")
        
        # cria instância do objeto
        super().__init__(modelo_enum=ModelosEnum.XGBOOST,
                        df_dados_treino=df_usinas,
                        df_dados_predicao=df_goias,
                        previsao="fator_capacidade",
                        nome_arquivo="resultado_elocia_xgboost.csv")
        
        self.feature_cols = ['vento_medio_m_s', 'rajada_vento_10m', 'direcao_vento_10m',
                             'altitude_m', 'rugosidade', 'indice_potencial',
                             'ano', 'mes', 'dia', 'hora', 'dia_da_semana']

    def processe():
        super().processe_regressao()