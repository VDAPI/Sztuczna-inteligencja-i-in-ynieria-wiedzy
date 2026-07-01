"""Faza 4 — metryki i ewaluacja.

`compute_metrics` to JEDEN pomocnik używany wszędzie — gwarantuje spójność.
Dla 3 klas raportujemy ACC + macro/weighted P-R-F1 + per-klasa + macierz pomyłek.

Dlaczego nie sama accuracy: przy CL ≈ 6% model ignorujący CL i tak ma wysokie ACC.
Macro-F1 ujawnia ten problem.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

from . import config


def compute_metrics(y_true, y_pred, labels=None) -> dict:
    """Zwraca dict z kompletem metryk dla klasyfikacji wieloklasowej."""
    labels = labels or sorted(pd.unique(pd.Series(y_true).astype(str)))
    yt = pd.Series(y_true).astype(str)
    yp = pd.Series(y_pred).astype(str)

    out = {
        "accuracy": accuracy_score(yt, yp),
        "precision_macro": precision_score(yt, yp, average="macro", zero_division=0),
        "recall_macro": recall_score(yt, yp, average="macro", zero_division=0),
        "f1_macro": f1_score(yt, yp, average="macro", zero_division=0),
        "f1_weighted": f1_score(yt, yp, average="weighted", zero_division=0),
    }
    # per-klasa F1 (przydatne, żeby zobaczyć jak leży CL)
    per_class = f1_score(yt, yp, average=None, labels=labels, zero_division=0)
    for lab, val in zip(labels, per_class):
        out[f"f1_{lab}"] = val
    return {k: round(float(v), 4) for k, v in out.items()}


def confusion_df(y_true, y_pred, labels=None) -> pd.DataFrame:
    """Macierz pomyłek jako DataFrame (wiersze=rzeczywiste, kolumny=predykcja)."""
    labels = labels or sorted(pd.unique(pd.Series(y_true).astype(str)))
    cm = confusion_matrix(pd.Series(y_true).astype(str), pd.Series(y_pred).astype(str), labels=labels)
    return pd.DataFrame(cm, index=[f"true_{l}" for l in labels], columns=[f"pred_{l}" for l in labels])


def full_report(y_true, y_pred, labels=None) -> str:
    """Tekstowy classification_report (per-klasa P/R/F1) — do logów."""
    labels = labels or sorted(pd.unique(pd.Series(y_true).astype(str)))
    return classification_report(
        pd.Series(y_true).astype(str), pd.Series(y_pred).astype(str),
        labels=labels, zero_division=0,
    )


def save_confusion_png(y_true, y_pred, title: str, path: Path, labels=None) -> None:
    """Zapisuje heatmapę macierzy pomyłek do PNG."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import seaborn as sns

    labels = labels or sorted(pd.unique(pd.Series(y_true).astype(str)))
    cm = confusion_matrix(pd.Series(y_true).astype(str), pd.Series(y_pred).astype(str), labels=labels)
    fig, ax = plt.subplots(figsize=(4.5, 4))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=labels, yticklabels=labels, ax=ax, cbar=False)
    ax.set_xlabel("Predykcja")
    ax.set_ylabel("Rzeczywistość")
    ax.set_title(title)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=130)
    plt.close(fig)


def metrics_table(rows: list[dict]) -> pd.DataFrame:
    """Składa listę wyników (z polem 'model'/'variant') w tabelę zbiorczą."""
    return pd.DataFrame(rows)


# TODO (Dawid): w raporcie zinterpretuj:
#   - różnicę accuracy vs f1_macro (skąd się bierze, rola CL),
#   - co macierz pomyłek mówi o myleniu klas,
#   - który model + preprocessing wygrał i dlaczego.
