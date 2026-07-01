"""Klasyfikacja modelem encoder-only (Zadania 2-3), np. HerBERT.

Forward pass jest deterministyczny - temperatura nie ma tu zastosowania.
"""
import torch
from transformers import pipeline

from .config import ENCODER_MAX_LEN, ENCODER_BATCH, NEUTRAL_ID, LABEL2ID
from .labels import build_model_label_map, _normalize_to_canon


def load_encoder(model_name):
    """Laduje pipeline klasyfikacji + buduje mape etykiet modelu -> kanoniczne id."""
    device = 0 if torch.cuda.is_available() else -1
    pipe = pipeline("text-classification", model=model_name, device=device)
    label_map = build_model_label_map(pipe.model.config.id2label)
    return pipe, label_map


def classify_encoder(pipe, label_map, texts, batch_size=ENCODER_BATCH,
                     max_len=ENCODER_MAX_LEN):
    """Zwraca liste predykcji (kanoniczne id) dla listy tekstow."""
    outputs = pipe(texts, batch_size=batch_size, truncation=True, max_length=max_len)
    preds = []
    for o in outputs:
        raw = o["label"]
        if raw in label_map:
            preds.append(label_map[raw])
        else:
            canon = _normalize_to_canon(raw)
            preds.append(LABEL2ID[canon] if canon else NEUTRAL_ID)
    return preds
