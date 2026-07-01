"""Mapowanie etykiet do jednej numeracji (config.LABEL2ID).

Trzy zrodla: target ze zbioru, etykieta modelu encoder, tekst z LLM.
"""
import re

from .config import LABEL2ID, TARGET2CANON, NEUTRAL_ID

# Warianty etykiet (PL + EN + typowe wyjscia modeli) -> klasa kanoniczna
_KEYWORD2CANON = {
    # positive
    "positive": "positive", "pos": "positive", "plus": "positive",
    "pozytywny": "positive", "pozytywna": "positive", "pozytywne": "positive",
    "label_2": "positive",
    # negative
    "negative": "negative", "neg": "negative", "minus": "negative",
    "negatywny": "negative", "negatywna": "negative", "negatywne": "negative",
    "label_0": "negative",
    # neutral
    "neutral": "neutral", "neu": "neutral", "zero": "neutral",
    "neutralny": "neutral", "neutralna": "neutral", "neutralne": "neutral",
    "label_1": "neutral",
}


def _normalize_to_canon(text):
    """Dowolny tekst -> klasa kanoniczna (positive/negative/neutral) albo None."""
    if text is None:
        return None
    t = str(text).strip().lower()
    if t in _KEYWORD2CANON:
        return _KEYWORD2CANON[t]
    # szukamy slowa kluczowego wsrod tokenow
    for tok in re.findall(r"\w+", t, flags=re.UNICODE):
        if tok in _KEYWORD2CANON:
            return _KEYWORD2CANON[tok]
    return None


def target_to_id(target):
    """Etykieta ze zbioru (__label__meta_*) -> kanoniczne id (None dla ambiguous)."""
    canon = TARGET2CANON.get(target)
    if canon is None or canon == "ambiguous":
        return None
    return LABEL2ID[canon]


def build_model_label_map(id2label):
    """Mapa: etykieta modelu (config.id2label) -> kanoniczne id.

    Niezmapowane etykiety laduja w neutral z ostrzezeniem.
    """
    mapping = {}
    raw_labels = list(id2label.values())
    if all(re.fullmatch(r"label_\d+", str(r).lower()) for r in raw_labels):
        print("[UWAGA] Model nie ma nazwanych etykiet (LABEL_0/1/2). "
              "Zakladam konwencje HF: 0=negative, 1=neutral, 2=positive. Zweryfikuj!")
    for raw in raw_labels:
        canon = _normalize_to_canon(raw)
        if canon is None:
            print(f"[UWAGA] Nie umiem zmapowac etykiety modelu {raw!r} -> fallback 'neutral'.")
            mapping[raw] = NEUTRAL_ID
        else:
            mapping[raw] = LABEL2ID[canon]
    return mapping


def parse_generated_label(text):
    """Surowy output LLM -> (kanoniczne id, czy_sie_udalo)."""
    canon = _normalize_to_canon(text)
    if canon is not None:
        return LABEL2ID[canon], True
    return None, False
