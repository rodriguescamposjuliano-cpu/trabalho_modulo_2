import os
import snowflake.connector

class Conexao:
    """
    Classe responsável por gerenciar a conexão com o banco de dados Snowflake.

    Esta classe encapsula o processo de criação de uma conexão com o Snowflake, 
    utilizando variáveis de ambiente para garantir a segurança das credenciais 
    e facilitar a configuração em diferentes ambientes (desenvolvimento, teste, produção).

    Métodos:
        obtenha(): Estabelece e retorna uma conexão ativa com o banco de dados Snowflake.
    """
    
    def obtenha():
        conexao = snowflake.connector.connect(
            user=os.getenv("SNOWFLAKE_USER"),
            password=os.getenv("SNOWFLAKE_PASSWORD"),
            account=os.getenv("SNOWFLAKE_ACCOUNT"),
            warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
            database=os.getenv("SNOWFLAKE_DATABASE"),
            schema=os.getenv("SNOWFLAKE_SCHEMA"),
        )

        return conexao