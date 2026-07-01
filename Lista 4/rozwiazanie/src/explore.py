"""Faza 1 — eksploracja danych (EDA). 10 pkt.

Generuje statystyki i wykresy do results/. Uruchom:
    python -m src.explore
"""
from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

import numpy as np

from . import config
from .load_data import load_data, missingness_report


def _save_md(df, name: str, index: bool = True) -> None:
    """Zapis tabeli do results/: <name>.md (markdown do raportu) + <name>.csv."""
    df.to_csv(config.RESULTS_DIR / f"{name}.csv", index=index)
    (config.RESULTS_DIR / f"{name}.md").write_text(df.to_markdown(index=index), encoding="utf-8")


def run_eda() -> None:
    config.RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    df = load_data()

    # 1. rozkład klasy docelowej (pokazuje nierównowagę — zwłaszcza CL)
    dist = df[config.TARGET].value_counts()
    print("\nRozkład klas:\n", dist)
    print((df[config.TARGET].value_counts(normalize=True) * 100).round(1))
    fig, ax = plt.subplots(figsize=(4.5, 3.2))
    sns.barplot(x=dist.index.astype(str), y=dist.values, ax=ax)
    ax.set_title("Rozkład klas (Status)")
    ax.set_ylabel("liczność")
    fig.tight_layout()
    fig.savefig(config.RESULTS_DIR / "eda_target_dist.png", dpi=130)
    plt.close(fig)

    _save_md(dist.rename("liczność").to_frame(), "eda_target_dist")

    # 2. statystyki cech liczbowych (describe — TYLKO dla liczbowych)
    num = [c for c in config.NUMERIC_FEATURES if c in df.columns]
    desc = df[num].describe().T
    _save_md(desc.round(2), "eda_numeric_describe")
    print("\nStatystyki liczbowe zapisane.")

    # 2b. rozkłady cech KATEGORYCZNYCH — value_counts per cecha (tabela + wykres słupkowy).
    #     Cech kategorycznych nie opisujemy liczbowo (describe ich nie dotyczy), tylko rozkładem.
    cat = [c for c in config.CATEGORICAL_FEATURES if c in df.columns]
    cat_long = []
    for c in cat:
        cnt = df[c].value_counts(dropna=False)
        pct = (cnt / len(df) * 100).round(1)
        tbl = pd.DataFrame({"liczność": cnt.astype(int), "udział_%": pct})
        tbl.index.name = c
        _save_md(tbl, f"eda_cat_{c.lower()}")
        for (k, v), p in zip(cnt.items(), pct.tolist()):
            cat_long.append({"cecha": c, "wartość": str(k), "liczność": int(v), "udział_%": p})
    cat_tbl = pd.DataFrame(cat_long)
    _save_md(cat_tbl, "eda_categorical_all", index=False)
    print("Rozkłady cech kategorycznych zapisane:", ", ".join(cat))

    ncol = 4
    nrow = int(np.ceil(len(cat) / ncol))
    fig, axes = plt.subplots(nrow, ncol, figsize=(4 * ncol, 3.4 * nrow))
    axes = np.array(axes).reshape(-1)
    for ax, c in zip(axes, cat):
        vc = df[c].value_counts(dropna=False)
        order = [str(i) for i in vc.index]
        sns.barplot(x=order, y=vc.values, hue=order, palette="crest", legend=False, ax=ax)
        ax.set(title=c, xlabel="", ylabel="liczność")
    for ax in axes[len(cat):]:
        ax.set_visible(False)
    fig.suptitle("Rozkłady cech kategorycznych", fontsize=13)
    fig.tight_layout()
    fig.savefig(config.RESULTS_DIR / "eda_categorical_dist.png", dpi=130)
    plt.close(fig)

    # 3. mapa braków
    miss = missingness_report(df)
    _save_md(miss, "eda_missingness")
    print("\nBraki:\n", miss if not miss.empty else "brak")

    # 4. korelacje cech liczbowych
    fig, ax = plt.subplots(figsize=(7, 6))
    sns.heatmap(df[num].corr(), annot=False, cmap="coolwarm", center=0, ax=ax)
    ax.set_title("Korelacje cech liczbowych")
    fig.tight_layout()
    fig.savefig(config.RESULTS_DIR / "eda_corr.png", dpi=130)
    plt.close(fig)

    # 5. Age w latach (do opisu)
    if "Age" in df.columns:
        print("\nWiek [lata]:", (df["Age"] / 365.25).describe()[["mean", "min", "max"]].round(1).to_dict())

    # TODO (Dawid):
    #   - boxploty wybranych cech (Bilirubin, Albumin, Prothrombin) względem Status,
    #   - 3-5 zdań obserwacji do raportu: skośność, nierównowaga, skala braków,
    #     cechy kandydujące na istotne.


if __name__ == "__main__":
    run_eda()
