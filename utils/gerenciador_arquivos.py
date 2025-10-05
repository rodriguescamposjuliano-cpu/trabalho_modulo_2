import pandas as pd
import os
import zipfile

class GerenciadorDeArquivos:
    """
    Classe responsável por gerenciar operações básicas de arquivos, como:
    - Geração de arquivos CSV a partir de listas ou dicionários de dados.
    - Descompactação de arquivos ZIP na pasta de destino padrão.

    Diretório padrão de trabalho:
        data/processados/

    Exemplo de uso:
        GerenciadorDeArquivos.gere_arquivo(dados, "resultado.csv")
        GerenciadorDeArquivos.descompacte("resultado")
    """

    @staticmethod
    def gere_arquivo(dados, nome_arquivo):
        """
        Gera um arquivo CSV a partir dos dados informados e salva no diretório padrão.

        Parâmetros:
            dados (list[dict] | pandas.DataFrame): 
                Lista de dicionários ou DataFrame contendo os dados a serem salvos.
            nome_arquivo (str):
                Nome do arquivo de saída (ex: 'dados.csv').

        Efeitos:
            - Cria (ou sobrescreve) o arquivo CSV no caminho 'data/processados/{nome_arquivo}'.
            - Exibe no console o caminho relativo do arquivo gerado.
        """
        # Converte a lista de dicionários em DataFrame
        df_result = pd.DataFrame(dados)

        # Caminho completo do CSV
        caminho_csv = os.path.join("data/processados", nome_arquivo)

        # Cria diretório se não existir
        os.makedirs(os.path.dirname(caminho_csv), exist_ok=True)

        # Salva o CSV
        df_result.to_csv(caminho_csv, index=False)
        print(f"CSV gerado em: {caminho_csv}")

    @staticmethod
    def descompacte(nome_arquivo):
        """
        Descompacta um arquivo ZIP localizado no diretório 'data/processados'.

        Parâmetros:
            nome_arquivo (str):
                Nome do arquivo (sem a extensão .zip) que será descompactado.

        Efeitos:
            - Extrai todos os arquivos do ZIP para o mesmo diretório.
            - Exibe no console o nome do arquivo extraído.
        """
        # Caminho completo do arquivo ZIP
        zip_path = os.path.join("data/processados", nome_arquivo + '.zip')

        # Diretório onde o ZIP será extraído
        extract_dir = os.path.dirname(os.path.abspath(zip_path))

        # Verifica se o arquivo ZIP existe antes de extrair
        if not os.path.exists(zip_path):
            print(f"Arquivo ZIP não encontrado: {zip_path}")
            return

        # Extrai o conteúdo do ZIP
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)

        print(f"Arquivo extraído com sucesso: {nome_arquivo}")
