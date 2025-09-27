Instale a versão 3.11 do Python
brew install python@3.11

Crie o ambiente virtual
python3.11 -m venv venv 

Ative o ambiente virtual
source venv/bin/activate

Faça a instalação das dependências
pip install -r requirements.txt  


trabalho_modulo_2/
│
├── data/                   # dados brutos e processados
│   ├── raw/                # datasets originais (não alterar)
│   ├── processed/          # dados limpos e prontos para modelagem
│   ├── resultados/         # dados com as devidas previsões
│
├── scripts/                # scripts principais (separados por etapa)
│   ├── ingestao/           # scripts para coleta/extração de dados
│   │   └── obter_datasets.py
│   ├── preprocessing/      # scripts de limpeza e transformação
│   │   └── preparar_dados.py
│   ├── modeling/           # scripts de treino/avaliação de modelos
│   │   └── regressao.py
│   ├── visualization/      # geração de gráficos/plots
│   │   └── gerar_graficos.py
│   └── integration/        # integrações externas
│       └── conexao_snowflake.py
│
├── utils/                  # funções auxiliares reutilizáveis
│   ├── io_utils.py         # leitura/escrita de arquivos
│   ├── plot_utils.py       # funções para gráficos
│   ├── model_utils.py      # funções de treino/avaliação
│
├── tests/                  # testes automatizados (pytest/unittest)
│
├── requirements.txt        # dependências do projeto
├── variaveis.env           # variáveis de ambiente (não subir pro git)
├── .gitignore
└── README.md               # documentação do projeto

