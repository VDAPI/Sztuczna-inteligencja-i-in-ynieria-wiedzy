"""Ladowanie zbioru PolEmo2.0-IN i statystyki opisowe (Zadanie 1)."""
from collections import Counter

import numpy as np
from datasets import load_dataset

from .config import DATASET_NAME, SPLIT, MAX_SAMPLES, SEED
from .labels import target_to_id


def _detect_columns(ds):
    cols = ds.column_names
    text_col = "sentence" if "sentence" in cols else ("text" if "text" in cols else cols[0])
    label_col = "target" if "target" in cols else ("label" if "label" in cols else cols[-1])
    return text_col, label_col


def load_polemo_test():
    """Laduje split testowy (z fallbackiem trust_remote_code)."""
    try:
        return load_dataset(DATASET_NAME, split=SPLIT)
    except Exception:
        try:
            return load_dataset(DATASET_NAME, split=SPLIT, trust_remote_code=True)
        except Exception as e:
            raise RuntimeError(
                f"Nie udalo sie zaladowac {DATASET_NAME} (split={SPLIT}).\n"
                f"Sprobuj: pip install 'datasets<3.0'\n"
                f"Oryginalny blad: {e}"
            )


def describe_raw(ds):
    """Statystyki surowego zbioru (przed filtrowaniem ambiguous)."""
    text_col, label_col = _detect_columns(ds)
    counts = Counter(ds[label_col])
    return {
        "n_total": len(ds),
        "columns": ds.column_names,
        "text_col": text_col,
        "label_col": label_col,
        "class_counts_raw": dict(counts),
    }


def prepare_dataset(ds, max_samples=MAX_SAMPLES, seed=SEED):
    """Filtruje ambiguous, mapuje etykiety na id. Zwraca (texts, labels, meta)."""
    text_col, label_col = _detect_columns(ds)
    texts, labels, dropped = [], [], 0
    for ex in ds:
        lid = target_to_id(ex[label_col])
        if lid is None:  # ambiguous -> pomijamy
            dropped += 1
            continue
        texts.append(ex[text_col])
        labels.append(lid)

    if max_samples is not None and max_samples < len(texts):
        rng = np.random.default_rng(seed)
        idx = sorted(rng.choice(len(texts), size=max_samples, replace=False).tolist())
        texts = [texts[i] for i in idx]
        labels = [labels[i] for i in idx]

    meta = {
        "n_used": len(texts),
        "n_ambiguous_dropped": dropped,
        "class_counts_used": dict(Counter(labels)),
    }
    return texts, labels, meta


def text_length_stats(texts):
    """Statystyki dlugosci tekstow w znakach i slowach."""
    char_lens = np.array([len(t) for t in texts])
    word_lens = np.array([len(t.split()) for t in texts])

    def s(a):
        return {"mean": float(a.mean()), "median": float(np.median(a)),
                "min": int(a.min()), "max": int(a.max()), "std": float(a.std())}

    return {
        "chars": s(char_lens),
        "words": s(word_lens),
        "char_lens": char_lens,
        "word_lens": word_lens,
    }
