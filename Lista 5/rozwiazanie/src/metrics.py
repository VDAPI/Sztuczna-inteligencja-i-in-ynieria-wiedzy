"""Metryki i wizualizacje: accuracy, F1 (macro/weighted), per-class, macierz pomylek."""
import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import (accuracy_score, f1_score,
                             classification_report, confusion_matrix)

from .config import CLASS_NAMES, OUTPUT_DIR

_LABELS = [0, 1, 2]


def compute_metrics(y_true, y_pred, n_unparsed=0):
    """Liczy komplet metryk. n_unparsed = ile odpowiedzi LLM nie dalo sie sparsowac."""
    return {
        "accuracy": accuracy_score(y_true, y_pred),
        "f1_macro": f1_score(y_true, y_pred, labels=_LABELS, average="macro", zero_division=0),
        "f1_weighted": f1_score(y_true, y_pred, labels=_LABELS, average="weighted", zero_division=0),
        "n_unparsed": n_unparsed,
        "report": classification_report(y_true, y_pred, labels=_LABELS,
                                        target_names=CLASS_NAMES, zero_division=0,
                                        output_dict=True),
    }


def print_metrics(name, m):
    print(f"=== {name} ===")
    print(f"  Accuracy     : {m['accuracy']:.4f}")
    print(f"  F1 (macro)   : {m['f1_macro']:.4f}")
    print(f"  F1 (weighted): {m['f1_weighted']:.4f}")
    if m.get("n_unparsed"):
        print(f"  Nieparsowalne: {m['n_unparsed']}")
    rep = m["report"]
    print("  Per-class (precision / recall / f1 / support):")
    for c in CLASS_NAMES:
        r = rep[c]
        print(f"    {c:9s}: {r['precision']:.3f} / {r['recall']:.3f} / "
              f"{r['f1-score']:.3f} / {int(r['support'])}")
    print()


def _slug(s):
    return "".join(ch if ch.isalnum() else "_" for ch in s)[:60]


def plot_confusion(y_true, y_pred, name, save=True, show=False):
    """Rysuje (i opcjonalnie zapisuje) macierz pomylek."""
    cm = confusion_matrix(y_true, y_pred, labels=_LABELS)
    fig, ax = plt.subplots(figsize=(5, 4))
    im = ax.imshow(cm, cmap="Blues")
    ax.set_xticks(range(3)); ax.set_yticks(range(3))
    ax.set_xticklabels(CLASS_NAMES); ax.set_yticklabels(CLASS_NAMES)
    ax.set_xlabel("Predykcja"); ax.set_ylabel("Prawda")
    ax.set_title(f"Macierz pomylek\n{name}")
    thr = cm.max() / 2 if cm.max() else 0
    for i in range(3):
        for j in range(3):
            ax.text(j, i, int(cm[i, j]), ha="center", va="center",
                    color="white" if cm[i, j] > thr else "black")
    fig.colorbar(im, fraction=0.046, pad=0.04)
    fig.tight_layout()
    if save:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        path = os.path.join(OUTPUT_DIR, f"cm_{_slug(name)}.png")
        fig.savefig(path, dpi=120)
        print(f"  Zapisano macierz pomylek: {path}")
    if show:
        plt.show()
    else:
        plt.close(fig)
    return fig


def results_table(rows):
    """Lista slownikow -> DataFrame posortowany po f1_macro malejaco."""
    df = pd.DataFrame(rows)
    if "f1_macro" in df.columns:
        df = df.sort_values("f1_macro", ascending=False).reset_index(drop=True)
    return df


def save_results_markdown(rows, path, title="Wyniki"):
    """Zapisuje tabele wynikow jako markdown (do wklejenia do raportu)."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    df = results_table(rows)
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"## {title}\n\n")
        f.write(df.to_markdown(index=False))
        f.write("\n")
    print(f"Zapisano: {path}")
    return df
