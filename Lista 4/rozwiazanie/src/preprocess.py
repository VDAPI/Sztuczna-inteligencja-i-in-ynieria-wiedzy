"""Faza 2 — przygotowanie danych: braki + warianty przetwarzania.

Wszystko jako sklearn Pipeline / ColumnTransformer, więc `fit` jest robiony
WYŁĄCZNIE na train (brak wycieku) także wewnątrz cross_val_score / GridSearchCV.

Budujemy 3 warianty preprocessingu do porównania (baseline + 2 metody):
  - baseline       : imputacja + one-hot (punkt odniesienia)
  - feature_select : + SelectKBest(mutual_info_classif)  ≈ InfoGain
  - pca            : + StandardScaler -> PCA

⚠️ NIE używamy "standaryzacja vs bez" jako osobnej metody dla NB/drzewa —
   to nie zmienia ich wyników (patrz CLAUDE.md, pułapka #3).
"""
from __future__ import annotations

import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.decomposition import PCA
from sklearn.feature_selection import SelectKBest, mutual_info_classif
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, StandardScaler

from . import config


def _as_str(X):
    """Ujednolica typy kolumn kategorycznych do napisów.

    Stage (1-4) jest kategoryczne, ale liczbowe; po imputacji 'Missing' kolumna
    miesza float i str, co OneHotEncoder (sklearn >=1.4) odrzuca. Rzutowanie na
    str po imputacji daje jednorodny typ. Funkcja nazwana (nie lambda), żeby
    Pipeline był picklowalny dla GridSearchCV(n_jobs=-1).
    """
    return np.asarray(X).astype(str)

# kolumny faktycznie obecne ustala loader; tu zakładamy pełną listę z config
NUM = config.NUMERIC_FEATURES
CAT = config.CATEGORICAL_FEATURES


def _num_pipe(scale: bool = False) -> Pipeline:
    steps = [("imputer", SimpleImputer(strategy="median"))]
    if scale:
        steps.append(("scaler", StandardScaler()))
    return Pipeline(steps)


def _cat_pipe() -> Pipeline:
    return Pipeline([
        # 'Missing' jako osobna kategoria zachowuje informację o braku (np. Drug dla 106 pacjentów)
        ("imputer", SimpleImputer(strategy="constant", fill_value="Missing")),
        # po imputacji ujednolicamy typy do str (Stage jest liczbowo-kategoryczne)
        ("to_str", FunctionTransformer(_as_str)),
        ("onehot", OneHotEncoder(handle_unknown="ignore")),
    ])


def base_column_transformer(scale_numeric: bool = False) -> ColumnTransformer:
    """Imputacja + encoding. scale_numeric=True dodaje StandardScaler (potrzebne dla SVM/PCA)."""
    return ColumnTransformer([
        ("num", _num_pipe(scale=scale_numeric), NUM),
        ("cat", _cat_pipe(), CAT),
    ])


# --- 3 warianty preprocessingu (zwracają listę kroków do wstawienia przed klasyfikatorem) ---

def make_preprocessor(variant: str = "baseline", k_best: int = 12, n_pca: int = 8):
    """Zwraca listę (name, transformer) do złożenia z klasyfikatorem w Pipeline.

    variant ∈ {"baseline", "feature_select", "pca"}.
    """
    if variant == "baseline":
        return [("prep", base_column_transformer(scale_numeric=False))]

    if variant == "feature_select":
        # mutual_info_classif ≈ przyrost informacji (InfoGain) z treści zadania
        return [
            ("prep", base_column_transformer(scale_numeric=False)),
            ("select", SelectKBest(score_func=mutual_info_classif, k=k_best)),
        ]

    if variant == "pca":
        # PCA wymaga skalowania -> scale_numeric=True
        return [
            ("prep", base_column_transformer(scale_numeric=True)),
            ("pca", PCA(n_components=n_pca, random_state=config.RANDOM_STATE)),
        ]

    raise ValueError(f"Nieznany wariant preprocessingu: {variant!r}")


PREPROCESS_VARIANTS = ["baseline", "feature_select", "pca"]

# TODO (Dawid):
#   - dobierz k_best (SelectKBest) i n_pca (PCA) — np. patrząc na wariancję wyjaśnioną PCA
#     albo na ranking cech z mutual_info; uzasadnij w raporcie.
#   - (opcjonalnie) dodaj 4. wariant: dyskretyzacja (KBinsDiscretizer) + CategoricalNB,
#     żeby pokazać wpływ założeń modelu Bayesa.
#   - (opcjonalnie) porównaj 2 strategie braków: imputacja vs usunięcie wierszy z NA w Drug.
