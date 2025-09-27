# 🌞 Trabalho Módulo 2 - Previsão de Geração de Usinas

[![Python](https://img.shields.io/badge/python-3.11-blue)](https://www.python.org/)
[![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow)](README.md)

Este projeto tem como objetivo processar dados de usinas solares e eólicas, aplicar modelos de regressão (XGBoost e Random Forest) e gerar previsões de geração de energia.

---

## 📖 Índice

- [Descrição](#descrição)
- [Requisitos](#requisitos)
- [Instalação](#instalação)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Como Rodar](#como-rodar)
- [Contribuição](#contribuição)
- [Licença](#licença)

---

## 🔍 Descrição

O projeto permite:

- Extrair dados do Snowflake
- Limpar e preparar datasets
- Aplicar modelos de regressão (XGBoost e Random Forest)
- Gerar previsões de geração de energia
- Visualizar resultados em gráficos

---

## 🛠 Requisitos

- Python 3.11  
- Dependências listadas em `requirements.txt`

---

## ⚙️ Instalação

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


## 🗂 Estrutura do Projeto

```plaintext
trabalho_modulo_2/
│
├── data/                   
│   ├── raw/                # datasets originais (não alterar)
│   ├── processados/        # dados limpos e prontos para modelagem
│   └── resultados/         # previsões geradas
│
├── scripts/                
│   ├── processamento/      
│   │   ├── carga_informacoes_usinas_eolicas.py
│   │   └── carga_informacoes_usinas_solares.py
│   ├── modelos/            
│   │   ├── modelos_regressao.py
│   │   ├── processador_regressao_eolica.py
│   │   ├── processador_regressao_solar.py
│   │   └── processador_regressao.py
│   ├── visualizacao/      
│   │   └── gerar_graficos.py
│   └── integration/        
│       └── conexao_snow_flake.py
│
├── utils/                  
│   └── io_ugerador_arquivostils.py
│
├── requirements.txt        
├── variaveis.env           # variáveis de ambiente (não subir pro git)
├── .gitignore
└── README.md               
