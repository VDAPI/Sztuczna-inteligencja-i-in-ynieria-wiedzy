"""Faza 3 — klasyfikatory, strojenie hiperparametrów, bonusy.

Główne: GaussianNB + DecisionTree. Każdy z ≥3 zestawami hiperparametrów.
Bonus: RandomForest / SVM, oraz złagodzenie przeuczenia (ccp_alpha dla drzewa).

Strojenie po f1_macro (nie accuracy!) z powodu nierównowagi klas.
"""
from __future__ import annotations

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.naive_bayes import GaussianNB
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

from . import config
from .preprocess import make_preprocessor

CV = StratifiedKFold(n_splits=5, shuffle=True, random_state=config.RANDOM_STATE)
SCORING = "f1_macro"  # macro, bo CL jest rzadka


def build_pipeline(estimator, variant: str = "baseline") -> Pipeline:
    """Składa preprocessing (wybrany wariant) + klasyfikator w jeden Pipeline."""
    steps = make_preprocessor(variant) + [("clf", estimator)]
    return Pipeline(steps)


# --- siatki hiperparametrów (≥3 zestawy każda; klucze z prefiksem 'clf__') ---

NB_GRID = {
    # GaussianNB ma mało hiperparametrów -> stroimy var_smoothing (≥3 wartości)
    "clf__var_smoothing": [1e-9, 1e-7, 1e-5, 1e-3],
}

DT_GRID = {
    "clf__criterion": ["gini", "entropy"],
    "clf__max_depth": [3, 5, 10, None],
    "clf__min_samples_leaf": [1, 5, 10],
}

RF_GRID = {  # bonus
    "clf__n_estimators": [100, 300],
    "clf__max_depth": [5, 10, None],
    "clf__min_samples_leaf": [1, 5],
}

SVM_GRID = {  # bonus — UWAGA: użyj variant='pca' albo dołóż skalowanie; SVM wymaga skalowania!
    "clf__C": [0.1, 1, 10],
    "clf__kernel": ["rbf", "linear"],
    "clf__gamma": ["scale", "auto"],
}


def tune(estimator, grid: dict, X_train, y_train, variant: str = "baseline") -> GridSearchCV:
    """GridSearchCV po f1_macro na stratyfikowanym CV. Zwraca dopasowany obiekt."""
    pipe = build_pipeline(estimator, variant=variant)
    gs = GridSearchCV(pipe, grid, scoring=SCORING, cv=CV, n_jobs=-1, refit=True)
    gs.fit(X_train, y_train)
    return gs


def get_estimators() -> dict:
    """Mapa nazwa -> (estimator, grid) dla głównych klasyfikatorów."""
    return {
        "naive_bayes": (GaussianNB(), NB_GRID),
        "decision_tree": (DecisionTreeClassifier(random_state=config.RANDOM_STATE), DT_GRID),
    }


def get_bonus_estimators() -> dict:
    """Bonus: zaawansowane algorytmy. SVM lepiej z variant='pca' (skalowanie)."""
    return {
        "random_forest": (RandomForestClassifier(random_state=config.RANDOM_STATE), RF_GRID),
        "svm": (SVC(random_state=config.RANDOM_STATE), SVM_GRID),
    }


# --- bonus: analiza/złagodzenie przeuczenia dla drzewa (ccp_alpha) ---

def cost_complexity_alphas(X_train, y_train, variant: str = "baseline"):
    """Zwraca ścieżkę ccp_alpha do przycinania drzewa (do wykresu i wyboru)."""
    pipe = build_pipeline(DecisionTreeClassifier(random_state=config.RANDOM_STATE), variant=variant)
    pipe.fit(X_train, y_train)
    # transformacja danych przez kroki preprocessingu, by policzyć ścieżkę na samym drzewie
    Xt = X_train
    for name, step in pipe.steps[:-1]:
        Xt = step.transform(Xt)
    path = pipe.named_steps["clf"].cost_complexity_pruning_path(Xt, y_train)
    return path.ccp_alphas

# TODO (Dawid):
#   3a/3b: dla NB i drzewa zrób tune(...), zaloguj cv_results_ dla ≥3 zestawów,
#          wyciągnij best_params_ i best_score_, oceń na walidacji (evaluate.compute_metrics).
#   3c (bonus): odpal RF i/lub SVM. Dla SVM użyj variant='pca' lub dołóż StandardScaler;
#          krótko wyjaśnij w raporcie, czemu SVM wymaga skalowania, a drzewo nie.
#   3d (bonus): wybierz ccp_alpha ze ścieżki, wytrenuj przycięte drzewo, pokaż train vs val
#          (overfitting gap maleje). Wykres -> results/overfitting_mitigation.png.
