# Trabalho Módulo 2 - Análise e Previsão de Geração de Energia Solar e Eólica em Goiás

[![Python](https://img.shields.io/badge/python-3.11-blue)](https://www.python.org/)
[![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow)](README.md)

Este projeto tem como objetivo analisar e prever a geração de energia solar e eólica no estado de Goiás, utilizando o modelo de regressão baseado em aprendizado de máquina (XGBoost).
Os dados são obtidos a partir de fontes públicas (ONS).

Objetivos Principais

- **Zoneamento Energético:** Identificar quais microrregiões de Goiás apresentam maior potencial para diferentes tipos de energia renovável.  
- **Sazonalidade Estratégica:** Apoiar a formulação de políticas que promovam a complementaridade energética ao longo do ano.  
- **Sinergia Hidro-Solar:** Otimizar a integração entre a geração hidrelétrica existente e o potencial solar e eólico do estado.  
- **Capacidade de Escoamento:** Avaliar como a infraestrutura atual de transmissão influencia o aproveitamento do potencial renovável.

---

## Índice

- [Descricao](#descricao)
- [Arquitetura](#arquitetura)
- [Requisitos](#requisitos)
- [Instalacao](#instalacao)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Como Rodar](#como-rodar)

---

## Descricao

O projeto realiza as seguintes etapas:

1. Extração de Dados:
   - Leitura de informações meteorológicas históricas via API Open-Meteo;
   - Integração com base de dados do Snowflake, para informações de usinas e produção real;
   - Leitura de dados geográficos via GeoJSON público.
3. Transformação e Limpeza:
   - Enriquecimento dos datasets com dados climáticos e de localização.
5. Modelagem Preditiva:
   - Aplicação de XGBoost Regressor para prever geração energética;
   - Avaliação de métricas (MAE, RMSE, R²).
7. Visualização e Insights:
   - Grafico da curva de erro;
   - Gráfico de comparação real vs previsto.
     
## Arquitetura

```plaintext
+---------------------------+
|       Dados da ONS        |
+------------+--------------+
             |
             v 
+---------------------------+
|       Aribyte             |   
+------------+--------------+
             |
             v 
+---------------------------+
|       Snowflake           |        
+------------+--------------+
             |
             v 
+---------------------------+
| Processamento de Dados    |
| (scripts/processamento)   |
+------------+--------------+
             |
             v
+---------------------------+
| Modelagem e Treinamento   |
| (scripts/modelos)         |
+------------+--------------+
             |
             v
+---------------------------+
| Visualização e Arquivos   |
| (scripts/visualizacao)    |
+---------------------------+
```
## Fone de Dados

```plaintext
| Fonte                                                                                              | Descrição                                                                           | Tipo           |
| -------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- | -------------- |
| [Dados abertos ONS](https://dados.ons.org.br)                                                      | Datasets dos anos de 2024 e até setembro de 2025                                    | XLSX           |
| [Open-Meteo API](https://archive-api.open-meteo.com/)                                              | Dados meteorológicos históricos (radiação solar, velocidade do vento, temperatura). | API            |
| [GeoData-BR](https://raw.githubusercontent.com/tbrugz/geodata-br/master/geojson/geojs-52-mun.json) | Limites geográficos dos municípios de Goiás.                                        | GeoJSON        |
| Snowflake                                                                                          | Dados de geração e cadastro das usinas.                                             | Data Warehouse |

```

## Requisitos

- Python 3.11  
- Dependências listadas em `requirements.txt`

---

## Instalacao

    1. Instale o Python 3.11

        brew install python@3.11

    2. Crie o ambiente virtual

        python3.11 -m venv venv

    3. Ative o ambiente virtual

        Mac/Linux: source venv/bin/activate
        Windows (PowerShell): .\venv\Scripts\Activate.ps1
        Windows (CMD): .\venv\Scripts\activate.bat

    4. Instale as dependências

        pip install -r requirements.txt
        
    5. Configure o acesso ao Snowflake
        Neste projeto, utilizamos a versão trial do Snowflake. Para possibilitar a execução do nosso algoritmo mesmo sem acesso ativo ao Snowflake, criamos arquivos .csv contendo os dados já preparados.
        As classes carga_informacoes_usinas_eolicas.py e carga_informacoes_usinas_solares.py são responsáveis por:
         5.1 Conectar-se ao Snowflake,
         5.2 Buscar os dados, e
         5.3 Prepará-los para o processamento pelo algoritmo.
         
        Caso o acesso do SnowFlake tenha expirado, edite o arquivo variaveis.env e informe as novas credenciais:
        
        SNOWFLAKE_USER=<usuario>
        SNOWFLAKE_PASSWORD=<senha>
        SNOWFLAKE_ACCOUNT=<conta>
        SNOWFLAKE_WAREHOUSE=<warehouse>
        SNOWFLAKE_DATABASE=<database>
        SNOWFLAKE_SCHEMA=<schema>



## Estrutura do Projeto

```plaintext
trabalho_modulo_2/
│
├── data/                   
│   ├── processados/        # Dados limpos e prontos para modelagem
│   └── resultados/Arquivos # Previsões geradas para o estado de Goiás
│   └── resultados/Graficos # Gráficos da curva de erro e real vs previsto.
│
├── scripts/
│   └── integracao/        
│   |   └── conexao_snow_flake.py
│   ├── modelos/            
│   │   ├── modelos_regressao.py            #Classe responsável por definir os possíveis modelos
│   │   ├── processador_regressao_eolica.py #Classe responsável por carregar os dados das usinas eólicas
│   │   ├── processador_regressao_solar.py  #Classe responsável por carregar os dados das usinas solares 
│   │   └── processador_regressao.py        #Classe genérica por realizar do processamento da regressão
│   │   └── tipos_de_usinas.py              #Tipo de usinas (eólica e solar)
│   ├── processamento/      
│   │   ├── carga_informacoes_usinas_eolicas.py #Classe responsável por preparar as informações das usinas eólicas
│   │   └── carga_informacoes_usinas_solares.py #Classe responsável por preparar as informações das usinas solares
│   ├── visualizacao/      
│         └── gerenciador_graficos.py #Centraliza a geração dos gráficos
│
├── utils/                  
│   └── gerenciador_arquivos.py #Centraliza a criação dos arquivos
│
├── .gitignore
├── main.py
├── README.md
├── requirements.txt        
└── variaveis.env           # variáveis de ambiente para conectar no snowflake
```
## Como Rodar

1. Treine e gere predições para usinas eólicas
   ```plaintext
   python main.py reg-eolica
   ```
3. Treine e gere predições para usinas solares
   ```plaintext
   python main.py reg-solar
   ```
 




