import pandas as pd
import os

class GeradorDeArquivos:

    def gere_arquivo(self, dados, nome_arquivo):
        #Salva CSV
        df_result = pd.DataFrame(dados)
        caminho_csv = os.path.join("data/processados", nome_arquivo)
        # Salva o CSV na pasta
        df_result.to_csv(caminho_csv, index=False)
        print(f"CSV gerado em: {nome_arquivo}")

