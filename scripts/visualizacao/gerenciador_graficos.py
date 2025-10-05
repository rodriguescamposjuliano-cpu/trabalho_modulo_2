import matplotlib.pyplot as plt
import os

class GerenciadorDeGraficos:
    
    def __init__(self, enumModelo):
        self.enumModelo = enumModelo
        self.output_dir = os.path.join("data/resultados/graficos", self.enumModelo.name.lower())
        os.makedirs(self.output_dir, exist_ok=True)

    def salvar_grafico(self, plt, nome: str):
        """ Salva gráfico na pasta visualizacao/nome_modelo """
        caminho = os.path.join(self.output_dir, f"{nome}.png")
        plt.savefig(caminho, bbox_inches="tight", dpi=150)
        print(f"Gráfico salvo: {caminho}")
        #Caso precise visualizar só retirar o comentário
        #plt.show()
                 
    def gere_grafico_curva_de_erro(self, resultado, tipo_usina):
        # Plotando curva de erro
        epochs = len(resultado['validation_0']['rmse'])
        x_axis = range(0, epochs)

        plt.figure(figsize=(8,5))
        plt.plot(x_axis, resultado['validation_0']['rmse'], label="Treino", color="blue")
        plt.plot(x_axis, resultado['validation_1']['rmse'], label="Validação", color="red")
        plt.xlabel("Iterações (árvores adicionadas)")
        plt.ylabel("RMSE")
        plt.title(f"Curva de Erro {tipo_usina.value} (RMSE) - XGBoost")
        plt.legend()
        plt.grid(True)

        self.salvar_grafico(plt, f"curva_erro_{tipo_usina.value}")

    def gere_grafico_programada_real(self, y_test, y_pred, tipo_usina):
        plt.figure(figsize=(8,6))
        plt.scatter(y_test, y_pred, alpha=0.3, s=20)
        plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--')  # linha y=x
        plt.xlim(0, 2)  
        plt.ylim(0, 2)  
        plt.xlabel("Fator de Capacidade Real")
        plt.ylabel("Fator de Capacidade Predito")
        plt.title(F"Predito vs Real - Fator de Capacidade ({tipo_usina.value})")

        self.salvar_grafico(plt, f"geracao_real_predita_{tipo_usina.value}")