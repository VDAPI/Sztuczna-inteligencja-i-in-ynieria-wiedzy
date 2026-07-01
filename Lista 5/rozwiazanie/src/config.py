"""Konfiguracja eksperymentow - Lista 5 (PolEmo2.0-IN)."""

# Kanoniczne mapowanie klas (3 klasy, bez ambiguous)
LABEL2ID = {"negative": 0, "neutral": 1, "positive": 2}
ID2LABEL = {v: k for k, v in LABEL2ID.items()}
CLASS_NAMES = ["negative", "neutral", "positive"]
NEUTRAL_ID = LABEL2ID["neutral"]  # fallback przy nieparsowalnym wyjsciu

# Etykiety PolEmo -> kanoniczne
TARGET2CANON = {
    "__label__meta_minus_m": "negative",
    "__label__meta_zero": "neutral",
    "__label__meta_plus_m": "positive",
    "__label__meta_amb": "ambiguous",  # wykluczane z zadania
}

# Zbior danych
DATASET_NAME = "allegro/klej-polemo2-in"
SPLIT = "test"
MAX_SAMPLES = None  # None = wszystkie

# Encoder (BERT-like)
DEFAULT_ENCODER = "Voicelab/herbert-base-cased-sentiment"
ENCODER_MODELS = [
    "Voicelab/herbert-base-cased-sentiment",         # polski sentyment (rekomendowany)
    "cardiffnlp/twitter-xlm-roberta-base-sentiment",  # multilingual baseline
]
ENCODER_MAX_LEN = 512
ENCODER_BATCH = 32

# Decoder (LLM)
DEFAULT_LLM = "Qwen/Qwen2.5-1.5B-Instruct"
LLM_MODELS = [
    "Qwen/Qwen2.5-1.5B-Instruct",
    "Qwen/Qwen2.5-3B-Instruct",  # wiekszy - rozwaz USE_4BIT=True
]
LLM_MAX_NEW_TOKENS = 16
LLM_JSON_MAX_NEW_TOKENS = 40
LLM_BATCH = 16
LLM_MAX_INPUT_TOKENS = 1024
USE_4BIT = False  # kwantyzacja 4-bit (wymaga bitsandbytes)

# Inne
SEED = 42
OUTPUT_DIR = "outputs"
