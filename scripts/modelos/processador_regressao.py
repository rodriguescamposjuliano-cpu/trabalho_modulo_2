from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import pandas as pd
import numpy as np
from scripts.modelos.modelos_regressao import ModelosEnum
from sklearn.linear_model import LinearRegression
from utils.gerador_arquivos import GeradorDeArquivos

import os
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt

class ProcessadorDeRegressao:

    feature_cols = []
          
    def __init__(self, modelo_enum: ModelosEnum, df_dados_treino, df_dados_predicao, nome_arquivo, previsao):
        self.df_dados_treino = df_dados_treino
        self.df_dados_predicao = df_dados_predicao
        self.nomeArquivo = nome_arquivo
        self.enumModelo = modelo_enum
        self.previsao = previsao

    
    @staticmethod
    def obter_modelo(modelo_enum: ModelosEnum):
        modelos = {
            ModelosEnum.REGRESSAO_LINEAR: LinearRegression(),
            ModelosEnum.RANDOM_FOREST: RandomForestRegressor(
                n_estimators=100, 
                random_state=42
            ),
            ModelosEnum.XGBOOST: XGBRegressor(
                n_estimators=1000,
                learning_rate=0.1,
                max_depth=10,
                subsample=0.9,
                colsample_bytree=1.0,
                reg_alpha=1,
                reg_lambda=2,
                random_state=42,
                n_jobs=-1,
                eval_metric="rmse",
                early_stopping_rounds=50
            )
        }

        return modelos[modelo_enum]
    
    def aplique_modelo(self):
        
        X = self.df_dados_predicao[self.feature_cols]
        y_pred = self.modelo.predict(X)
        y_pred = np.maximum(y_pred, 0)
        self.df_dados_predicao[self.previsao] = y_pred

        # Salva resultados
        caminho_csv = os.path.join("data/resultados", self.nomeArquivo)
        self.df_dados_predicao.to_csv(caminho_csv, index=False)

        print(f"Arquivo gerado: {self.nomeArquivo}")

    def prepare_data_sets(self):
        self.df_dados_treino["din_instante"] = pd.to_datetime(self.df_dados_treino["din_instante"])

        # Extração de variáveis temporais
        self.df_dados_treino["ano"] = self.df_dados_treino["din_instante"].dt.year
        self.df_dados_treino["mes"] = self.df_dados_treino["din_instante"].dt.month
        self.df_dados_treino["dia"] = self.df_dados_treino["din_instante"].dt.day
        self.df_dados_treino["hora"] = self.df_dados_treino["din_instante"].dt.hour
        self.df_dados_treino["dia_da_semana"] = self.df_dados_treino["din_instante"].dt.weekday

        self.df_dados_treino.fillna(0, inplace=True)

        # --- Aplicando em Goiás ---
        self.df_dados_predicao["din_instante"] = pd.to_datetime(self.df_dados_predicao["din_instante"])

        self.df_dados_predicao["ano"] = self.df_dados_predicao["din_instante"].dt.year
        self.df_dados_predicao["mes"] = self.df_dados_predicao["din_instante"].dt.month
        self.df_dados_predicao["dia"] = self.df_dados_predicao["din_instante"].dt.day
        self.df_dados_predicao["hora"] = self.df_dados_predicao["din_instante"].dt.hour
        self.df_dados_predicao["dia_da_semana"] = self.df_dados_predicao["din_instante"].dt.weekday

    def processe_regressao(self):
        self.prepare_data_sets()
        self.modelo = ProcessadorDeRegressao.obter_modelo(self.enumModelo)

        X = self.df_dados_treino[self.feature_cols]
        y = self.df_dados_treino[self.previsao]

        # 20% de testes e 80% de Treino
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        if (self.enumModelo == ModelosEnum.XGBOOST):
            self.modelo.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=True)
        else:
            self.modelo.fit(X_train, y_train)

        y_pred = self.modelo.predict(X_test)
        y_pred = np.maximum(y_pred, 0)

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

        import matplotlib.pyplot as plt

        plt.figure(figsize=(8,6))
        plt.scatter(y_test, y_pred, alpha=0.5)
        plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--')  # linha y=x
        plt.xlabel(f"{self.previsao} (MW)")
        plt.ylabel(f"{self.previsao} Predita (MW)")
        plt.title("Predito vs Real")
        plt.show()
        
        self.aplique_modelo()
