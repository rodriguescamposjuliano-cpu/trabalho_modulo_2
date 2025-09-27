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
│   ├── processados/          # dados limpos e prontos para modelagem
│   ├── resultados/         # dados com as devidas previsões
│
├── scripts/                # scripts principais (separados por etapa)
│   ├── processamento/      # scripts para obter os dados do snowflake e gerar .csv para treinar o model de regressão
│   │   └── carga_informacoes_usinas_eolicas.py
│   │   └── carga_informacoes_usinas_solares.py
│   ├── modelos/           # scripts utilizados para aplicar os models XGBoost e HandomForest
│   │   └── modelos_regressao.py
│   │   └── processador_regressao_eolica.py #faz a predição para os dados das usinas eólicas
│   │   └── processador_regressao_solar.py  #faz a predição para os dados das usinas solares
│   │   └── processador_regressao.py    #script necessário para orquestrar e centralizar o processamento do modelo escolhido.
│   ├── visualizacao/      # geração de gráficos/plots
│   │   └── gerar_graficos.py
│   └── integration/        # integrações externas
│       └── conexao_snow_flake.py
│
├── utils/                  # funções auxiliares reutilizáveis
│   ├── io_ugerador_arquivostils.py         # leitura/escrita de arquivos
│
├── requirements.txt        # dependências do projeto
├── variaveis.env           # variáveis de ambiente (não subir pro git)
├── .gitignore
└── README.md               # documentação do projeto

