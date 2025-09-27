from dotenv import load_dotenv
from scripts.processamento.carga_informacoes_usinas_eolicas import ProcessadorDadosUsinasEolicas
from scripts.processamento.carga_informacoes_usinas_solares import ProcessadorDadosUsinasSolares
from scripts.modelos.processador_regressao_eolica import ProcessadorRegressaoUsinaEolica
from scripts.modelos.processador_regressao_solar import ProcessadorRegressaoUsinaSolar

import pandas as pd
#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
def main():
    #ProcessadorDadosUsinasEolicas.prepare_os_dados_para_treino_usina_eolica()
    #ProcessadorDadosUsinasEolicas.prepare_os_dados_usinas_eolicas_de_goias()

    #ProcessadorDadosUsinasSolares.prepare_os_dados_para_treino_usina_solar()
    #ProcessadorDadosUsinasSolares.prepare_os_dados_usinas_solar_de_goias()

    #geracao_programada
    #geracao_verificada
    #fator_capacidade

    #Regressão usina eólica
    #proc = ProcessadorRegressaoUsinaEolica()
    #proc.processe_regressao()

    #Regressão usina solar
    proc = ProcessadorRegressaoUsinaSolar()
    proc.processe_regressao()


    # df_usinas = pd.read_csv("dados_tratados/dados_treino_usinas_eolicas.csv")
    # df_usinas["din_instante"] = pd.to_datetime(df_usinas["din_instante"])

    # # Extração de variáveis temporais
    # df_usinas["ano"] = df_usinas["din_instante"].dt.year
    # df_usinas["mes"] = df_usinas["din_instante"].dt.month
    # df_usinas["dia"] = df_usinas["din_instante"].dt.day
    # df_usinas["hora"] = df_usinas["din_instante"].dt.hour
    # df_usinas["dia_da_semana"] = df_usinas["din_instante"].dt.weekday

    # # Agrupar por ano, mês e usina
    # usina_total_mes_dados_treino = (
    #     df_usinas.groupby(["ano", "mes", "nomeUsina"])["geracao_programada"]
    #     .sum()
    #     .reset_index()
    # )

    # # Ordenar de forma decrescente pela geração
    # ordenado_dados = usina_total_mes_dados_treino.sort_values(
    #     by=["ano", "mes", "geracao_programada"], ascending=[True, True, False]
    # )

    # print(ordenado_dados[["ano", "mes", "nomeUsina", "geracao_programada"]])

    # # Carregar CSV
    # df_usinas_xboost = pd.read_csv("resultados/resultado_elocia_xgboost.csv")

    # # Agrupar por ano, mês e usina
    # usina_total_mes = (
    #     df_usinas_xboost.groupby(["ano", "mes", "nomeUsina"])["geracao_programada"]
    #     .sum()
    #     .reset_index()
    # )

    # # Ordenar de forma decrescente pela geração
    # ordenado = usina_total_mes.sort_values(
    #     by=["ano", "mes", "geracao_programada"], ascending=[True, True, False]
    # )
    # print("Geração por usina/ano/mês em MW:")
    # print(ordenado[["ano", "mes", "nomeUsina", "geracao_programada"]])

    # # Calcular o total geral (ano/mês)
    # totais = (
    #     df_usinas.groupby(["ano", "mes"])["geracao_programada"]
    #     .sum()
    #     .reset_index()
    # )
    # totais["nomeUsina"] = "TOTAL"
    # totais["geracao_MW"] = totais["geracao_programada"] / 1_000_000

    # # Concatenar o total com os dados originais
    # resultado_final = pd.concat([usina_total_mes, totais], ignore_index=True)

    # # Ordenar de forma decrescente pela geração
    # resultado_final = resultado_final.sort_values(
    #     by=["ano", "mes", "geracao_MW"], ascending=[True, True, False]
    # )

    # print("\nResultado final com TOTAL incluído (em MW):")
    # print(resultado_final[["ano", "mes", "nomeUsina", "geracao_MW"]])



if __name__ == "__main__":
    load_dotenv(dotenv_path="variaveis.env")  # carrega variáveis do .env
    main()


