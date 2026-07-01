"""Pakiet src - klasyfikacja wydzwieku PolEmo2.0-IN (encoder vs decoder).

Moduly:
    config   - wszystkie "pokretla" (modele, parametry, sciezki)
    labels   - mapowanie etykiet tekstowych <-> kanoniczne id (punktowany haczyk listy)
    data     - ladowanie i przygotowanie zbioru + statystyki
    metrics  - Accuracy/F1, macierz pomylek, tabele wynikow
    encoder  - klasyfikacja modelem encoder-only (HerBERT)
    decoder  - klasyfikacja modelem decoder-only (Qwen LLM) + LangChain/JSON
    utils    - seed, sprzatanie pamieci, info o sprzecie
"""

from . import config, data, decoder, encoder, labels, metrics, utils
from .utils import device_info, free_memory, set_seed

__all__ = [
    "config", "labels", "data", "metrics", "encoder", "decoder", "utils",
    "set_seed", "free_memory", "device_info",
]
