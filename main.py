import argparse
from dotenv import load_dotenv

# Importação dos módulos de processamento e modelagem
from scripts.processamento.carga_informacoes_usinas_eolicas import ProcessadorDadosUsinasEolicas
from scripts.processamento.carga_informacoes_usinas_solares import ProcessadorDadosUsinasSolares
from scripts.modelos.processador_regressao_eolica import ProcessadorRegressaoUsinaEolica
from scripts.modelos.processador_regressao_solar import ProcessadorRegressaoUsinaSolar


def main():
    """
    Função principal responsável por configurar o menu de opções
    via linha de comando (argparse) e executar o processamento
    conforme o comando informado pelo usuário.
    """
    
    # --- Configuração inicial do menu principal ---
    parser = argparse.ArgumentParser(
        description="Menu de opções - Processamento e Modelagem de Usinas"
    )

    # Criação dos subcomandos (agrupamentos de opções)
    subparsers = parser.add_subparsers(dest="command", required=True)


    # ==========================================================
    # SUBCOMANDO: Preparar dados de usinas eólicas
    # ==========================================================
    parser_eolicas = subparsers.add_parser(
        "prep-eolicas",
        help="Preparar dados para treinamento de usinas eólicas"
    )
    parser_eolicas.set_defaults(
        func=lambda args: ProcessadorDadosUsinasEolicas.prepare_os_dados_para_treino_usina_eolica()
    )


    # ==========================================================
    # SUBCOMANDO: Preparar dados de usinas solares
    # ==========================================================
    parser_solares = subparsers.add_parser(
        "prep-solares",
        help="Preparar dados para treinamento de usinas solares"
    )
    parser_solares.set_defaults(
        func=lambda args: ProcessadorDadosUsinasSolares.prepare_os_dados_para_treino_usina_solar()
    )


    # ==========================================================
    # SUBCOMANDO: Executar regressão em usinas eólicas
    # ==========================================================
    parser_reg_eolica = subparsers.add_parser(
        "reg-eolica",
        help="Executar modelo de regressão para usinas eólicas"
    )
    parser_reg_eolica.set_defaults(
        func=lambda args: ProcessadorRegressaoUsinaEolica().processe_regressao()
    )


    # ==========================================================
    # SUBCOMANDO: Executar regressão em usinas solares
    # ==========================================================
    parser_reg_solar = subparsers.add_parser(
        "reg-solar",
        help="Executar modelo de regressão para usinas solares"
    )
    parser_reg_solar.set_defaults(
        func=lambda args: ProcessadorRegressaoUsinaSolar().processe_regressao()
    )


    # --- Processa os argumentos e executa a função associada ---
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    # Carrega as variáveis de ambiente do arquivo 'variaveis.env'
    load_dotenv(dotenv_path="variaveis.env")

    # Executa o programa principal
    main()
