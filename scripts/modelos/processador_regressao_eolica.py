import pandas as pd
from scripts.modelos.processador_regressao import ProcessadorDeRegressao
from scripts.modelos.modelos_regressao import ModelosEnum
from utils.gerenciador_arquivos import GerenciadorDeArquivos
from scripts.modelos.tipos_de_usinas import TipoDeUsinasEnum

class ProcessadorRegressaoUsinaEolica(ProcessadorDeRegressao):
    """
    Classe responsável por preparar os dados das usinas eólicas. 
    """
     
    def __init__(self):
       # --- Dados para treino ---
        GerenciadorDeArquivos.descompacte("dados_treino_usinas_eolicas")
        df_usinas = pd.read_csv("data/processados/dados_treino_usinas_eolicas.csv")

        # --- Dados de Goiás para predição---
        GerenciadorDeArquivos.descompacte("potencial_energia_eolica_goias")
        df_goias = pd.read_csv("data/processados/potencial_energia_eolica_goias.csv")
        
        # cria instância do objeto
        super().__init__(modelo_enum=ModelosEnum.XGBOOST,
                        df_dados_treino=df_usinas,
                        df_dados_predicao=df_goias,
                        previsao="fator_capacidade",
                        nome_arquivo="resultado_eolica_xgboost.csv",
                        tipoDeUsina= TipoDeUsinasEnum.EOLICA)
        
        # Lista de colunas utilizadas como variáveis preditoras
        self.feature_cols = ['vento_medio_m_s', 'rajada_vento_10m', 'direcao_vento_10m',
                             'altitude_m', 'rugosidade', 'indice_potencial',
                             'ano', 'mes', 'dia', 'hora', 'dia_da_semana']

    def processe():
        super().processe_regressao()