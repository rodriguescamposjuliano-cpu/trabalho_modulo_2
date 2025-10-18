import os
import numpy as np
import pandas as pd
import xgboost as xgb
import matplotlib.pyplot as plt
import seaborn as sns

from xgboost import XGBRegressor, plot_importance
from sklearn.model_selection import train_test_split, KFold, cross_val_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

from scripts.modelos.modelos_regressao import ModelosEnum
from scripts.visualizacao.gerenciador_graficos import GerenciadorDeGraficos


class ProcessadorDeRegressao:
    """
    Classe responsável por preparar dados, treinar e avaliar modelos de regressão
    (Linear, Random Forest, XGBoost, MLP) para previsão de geração de energia
    de usinas solares ou eólicas.
    """

    # Lista de colunas utilizadas como variáveis preditoras
    feature_cols = []

    # ==========================================================
    # CONSTRUTOR
    # ==========================================================
    def __init__(self, modelo_enum: ModelosEnum, df_dados_treino, df_dados_predicao,
                 nome_arquivo, previsao, tipoDeUsina):
        """
        Inicializa o processador de regressão.

        Parâmetros:
            modelo_enum: tipo de modelo (Enum de ModelosEnum)
            df_dados_treino: DataFrame com dados históricos para treino
            df_dados_predicao: DataFrame com dados para predição
            nome_arquivo: nome do arquivo CSV a ser gerado
            previsao: nome da coluna-alvo (variável dependente)
            tipoDeUsina: string identificando o tipo de usina (eólica ou solar)
        """
        self.df_dados_treino = df_dados_treino
        self.df_dados_predicao = df_dados_predicao
        self.nomeArquivo = nome_arquivo
        self.enumModelo = modelo_enum
        self.previsao = previsao
        self.tipoDeUsina = tipoDeUsina
        self.gerenciadorDeGraficos = GerenciadorDeGraficos(modelo_enum)

    # ==========================================================
    # OBTENÇÃO DE MODELOS
    # ==========================================================
    @staticmethod
    def obter_modelo(modelo_enum: ModelosEnum):
        """
        Retorna uma instância do modelo correspondente ao tipo informado.
        """
        modelos = {
            ModelosEnum.REGRESSAO_LINEAR: LinearRegression(),

            ModelosEnum.RANDOM_FOREST: RandomForestRegressor(
                n_estimators=100,
                random_state=42
            ),

            ModelosEnum.XGBOOST: XGBRegressor(
                n_estimators=10000,
                learning_rate=0.02,
                max_depth=16,
                subsample=0.75,
                colsample_bytree=0.75,
                reg_alpha=1,
                reg_lambda=1,
                min_child_weight=1,
                gamma=0.05,
                random_state=42,
                n_jobs=-1,
                eval_metric="rmse",
                early_stopping_rounds=50
            ),

            ModelosEnum.MLP: MLPRegressor(
                hidden_layer_sizes=(512, 256),
                learning_rate_init=0.01,
                alpha=0.01,
                max_iter=500,
                early_stopping=False,
                random_state=42
            )
        }

        return modelos[modelo_enum]

    # ==========================================================
    # PREPARAÇÃO DE DADOS
    # ==========================================================
    def prepare_data_sets(self):
        """
        Prepara os dados de treino e predição, extraindo variáveis
        temporais (ano, mês, dia, hora, dia da semana).
        """
        # --- Dados de treino ---
        self.df_dados_treino["din_instante"] = pd.to_datetime(self.df_dados_treino["din_instante"])

        self.df_dados_treino["ano"] = self.df_dados_treino["din_instante"].dt.year
        self.df_dados_treino["mes"] = self.df_dados_treino["din_instante"].dt.month
        self.df_dados_treino["dia"] = self.df_dados_treino["din_instante"].dt.day
        self.df_dados_treino["hora"] = self.df_dados_treino["din_instante"].dt.hour
        self.df_dados_treino["dia_da_semana"] = self.df_dados_treino["din_instante"].dt.weekday

        self.df_dados_treino.fillna(0, inplace=True)

        # --- Dados de predição ---
        self.df_dados_predicao["din_instante"] = pd.to_datetime(self.df_dados_predicao["din_instante"])

        self.df_dados_predicao["ano"] = self.df_dados_predicao["din_instante"].dt.year
        self.df_dados_predicao["mes"] = self.df_dados_predicao["din_instante"].dt.month
        self.df_dados_predicao["dia"] = self.df_dados_predicao["din_instante"].dt.day
        self.df_dados_predicao["hora"] = self.df_dados_predicao["din_instante"].dt.hour
        self.df_dados_predicao["dia_da_semana"] = self.df_dados_predicao["din_instante"].dt.weekday

    # ==========================================================
    # TREINAMENTO E AVALIAÇÃO
    # ==========================================================
    def processe_regressao(self, k_fold=5):
        """
        Executa o processo completo de treinamento, avaliação e geração
        de predições, exibindo métricas e gráficos.
        """
        # --- Etapa 1: preparar os dados ---
        self.prepare_data_sets()

        # --- Etapa 2: selecionar o modelo ---
        self.modelo = ProcessadorDeRegressao.obter_modelo(self.enumModelo)

        X = self.df_dados_treino[self.feature_cols]
        y = self.df_dados_treino[self.previsao]

        # --- Etapa 3: divisão em treino e teste (80/20) ---
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        self.realize_validacao_cruzada_kfold(X=X, y=y, k_fold=5)

        # --- Etapa 4: treinamento ---
        if self.enumModelo == ModelosEnum.XGBOOST:
            # Treino com monitoramento (validação cruzada interna)
            self.modelo.fit(
                X_train, y_train,
                eval_set=[(X_train, y_train), (X_test, y_test)],
                verbose=False
            )

            # Curva de erro (XGBoost)
            results = self.modelo.evals_result()
            self.gerenciadorDeGraficos.gere_grafico_curva_de_erro(results, self.tipoDeUsina)
        else:
            # Modelos simples (sem early stopping)
            self.modelo.fit(X_train, y_train)

        # --- Etapa 5: predição e métricas ---
        y_pred = np.maximum(self.modelo.predict(X_test), 0)

        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)

        print({
            "Modelo": self.enumModelo.name,
            "MSE": round(mse, 3),
            "RMSE": round(rmse, 3),
            "MAE": round(mae, 3),
            "R²": round(r2, 3)
        })

        # --- Etapa 6: gráfico de comparação real vs previsto ---
        self.gerenciadorDeGraficos.gere_grafico_programada_real(
            y_test, y_pred, self.tipoDeUsina
        )

        # --- Etapa 7: gerar arquivo com previsões ---
        self.aplique_modelo()

    # ==========================================================
    # GERAÇÃO DE RESULTADOS
    # ==========================================================
    def aplique_modelo(self):
        """
        Aplica o modelo treinado ao conjunto de predição e salva os
        resultados em um arquivo CSV dentro de 'data/resultados/arquivos'.
        """
        X = self.df_dados_predicao[self.feature_cols]
        y_pred = np.maximum(self.modelo.predict(X), 0)
        self.df_dados_predicao[self.previsao] = y_pred

        # Cria diretório de saída, se não existir
        os.makedirs("data/resultados/arquivos", exist_ok=True)

        caminho_csv = os.path.join("data/resultados/arquivos", self.nomeArquivo)
        self.df_dados_predicao.to_csv(caminho_csv, index=False)

        print(f"Arquivo gerado: {caminho_csv}")

    # ==========================================================
    # VALIDAÇÃO CRUZADA (K-Fold)
    # ==========================================================
    def realize_validacao_cruzada_kfold(self, X, y, k_fold=5):
        """
        Executa validação cruzada K-Fold (apenas para XGBoost) e
        exibe o RMSE médio e desvio padrão.
        """
        kf = KFold(n_splits=k_fold, shuffle=True, random_state=42)
        fold_rmse = []

        for train_index, val_index in kf.split(X):
            X_train, X_val = X.iloc[train_index], X.iloc[val_index]
            y_train, y_val = y.iloc[train_index], y.iloc[val_index]

            self.modelo.fit(
                X_train, y_train,
                eval_set=[(X_train, y_train), (X_val, y_val)],
                verbose=False
            )

            results = self.modelo.evals_result()
            rmse_val = results["validation_1"]["rmse"][-1]
            fold_rmse.append(rmse_val)

        print(f"RMSE médio nos folds: {np.mean(fold_rmse):.3f} ± {np.std(fold_rmse):.3f}")
