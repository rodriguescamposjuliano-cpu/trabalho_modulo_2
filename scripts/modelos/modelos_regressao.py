from enum import Enum

class ModelosEnum(Enum):
    """
    Essa enum é utilizada para selecionar dinamicamente qual algoritmo
    de regressão será aplicado no processamento .
    """

    # --- Modelos disponíveis ---
    
    XGBOOST = "XGBoost"
    """Modelo baseado em árvores de decisão com boosting."""

    RANDOM_FOREST = "RandomForest"
    """Ensemble de múltiplas árvores de decisão."""

    REGRESSAO_LINEAR = "RegressaoLinear"
    """Modelo simples e interpretável."""

    MLP = "MLP"
    """Perceptron multicamada (rede neural)."""

