"""Wczytanie i wstępne czyszczenie zbioru.

Obsługuje dwa źródła:
  1. lokalny CSV (data/cirrhosis.csv) — wariant z etykietami C/CL/D (zgodny z treścią),
  2. ucimlrepo id=878 — pobranie online (etykiety bywają 0/1/2).

Po wczytaniu: usuwa ID i N_Days (wyciek), normalizuje etykiety, ustawia typy,
zwraca jeden czysty DataFrame z kolumną `Status` + 17 cech.

Uruchom samodzielnie, żeby zobaczyć raport braków:
    python -m src.load_data
"""
from __future__ import annotations

import sys

import pandas as pd

from . import config


def _load_raw() -> pd.DataFrame:
    """Zwraca surowy DataFrame z dostępnego źródła (CSV ma priorytet)."""
    if config.LOCAL_CSV.exists():
        print(f"[load] lokalny CSV: {config.LOCAL_CSV}")
        return pd.read_csv(config.LOCAL_CSV)

    print(f"[load] brak lokalnego CSV — pobieram z UCI (id={config.UCI_DATASET_ID})")
    try:
        from ucimlrepo import fetch_ucirepo
    except ImportError as exc:  # pragma: no cover
        raise SystemExit(
            "Brak pakietu 'ucimlrepo'. Zainstaluj: pip install ucimlrepo "
            "--break-system-packages  ALBO połóż data/cirrhosis.csv."
        ) from exc

    ds = fetch_ucirepo(id=config.UCI_DATASET_ID)
    # Złóż features + target w jeden DataFrame, niezależnie jak UCI je rozdzielił.
    raw = pd.concat([ds.data.features, ds.data.targets], axis=1)
    return raw


def _normalize_target(df: pd.DataFrame) -> pd.DataFrame:
    """Sprowadza Status do napisów C/CL/D (część źródeł koduje 0/1/2)."""
    if config.TARGET not in df.columns:
        # czasem target nazywa się inaczej; spróbuj wykryć
        cand = [c for c in df.columns if c.lower() in ("status", "target", "class")]
        if cand:
            df = df.rename(columns={cand[0]: config.TARGET})
        else:
            raise KeyError(f"Nie znaleziono kolumny targetu '{config.TARGET}' w {list(df.columns)}")

    col = df[config.TARGET]
    if pd.api.types.is_numeric_dtype(col):
        df[config.TARGET] = col.map(config.NUMERIC_TO_LABEL).fillna(col)
    df[config.TARGET] = df[config.TARGET].astype("string").str.strip()
    return df


def _coerce_types(df: pd.DataFrame) -> pd.DataFrame:
    """Ustawia typy: liczbowe -> numeric (NA z 'NA'), kategoryczne -> category."""
    for c in config.NUMERIC_FEATURES:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    for c in config.CATEGORICAL_FEATURES:
        if c in df.columns:
            df[c] = df[c].astype("category")
    return df


def load_data(verbose: bool = True) -> pd.DataFrame:
    """Główna funkcja: zwraca czysty DataFrame (Status + 17 cech, bez ID/N_Days)."""
    df = _load_raw()

    # usuń wyciek/identyfikatory, jeśli obecne
    drop = [c for c in config.LEAKAGE_COLS if c in df.columns]
    if drop:
        df = df.drop(columns=drop)
        if verbose:
            print(f"[clean] usunięto kolumny (wyciek/ID): {drop}")

    df = _normalize_target(df)
    df = _coerce_types(df)

    # zostaw tylko target + znane cechy (porządek przewidywalny)
    keep = [config.TARGET] + [c for c in config.ALL_FEATURES if c in df.columns]
    df = df[keep]

    if verbose:
        print(f"[ok] kształt: {df.shape}  | cechy: {df.shape[1] - 1}")
    return df


def missingness_report(df: pd.DataFrame) -> pd.DataFrame:
    """Tabela braków: liczba i % NA per kolumna (malejąco)."""
    n = len(df)
    rep = (
        pd.DataFrame({"n_missing": df.isna().sum(), "pct_missing": df.isna().mean().mul(100).round(1)})
        .sort_values("n_missing", ascending=False)
    )
    return rep[rep["n_missing"] > 0] if (rep["n_missing"] > 0).any() else rep


def split_X_y(df: pd.DataFrame):
    """Rozdziela na X (cechy) i y (Status)."""
    return df.drop(columns=[config.TARGET]), df[config.TARGET]


if __name__ == "__main__":
    df = load_data()
    print("\n--- Rozkład klas (Status) ---")
    print(df[config.TARGET].value_counts(dropna=False))
    print(df[config.TARGET].value_counts(normalize=True).mul(100).round(1).astype(str) + " %")
    print("\n--- Braki danych ---")
    rep = missingness_report(df)
    print(rep if not rep.empty else "Brak braków.")
    print("\n--- Typy ---")
    print(df.dtypes)
    sys.exit(0)
