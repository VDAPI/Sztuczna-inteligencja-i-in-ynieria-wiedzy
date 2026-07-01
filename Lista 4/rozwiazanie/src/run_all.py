"""Orkiestrator / spine. Działa od razu jako BASELINE — punkt wyjścia do rozbudowy.

Co robi teraz:
  - wczytuje dane (bez ID/N_Days),
  - stratyfikowany split train/val,
  - trenuje GaussianNB i DecisionTree na 3 wariantach preprocessingu (domyślne hiperparametry),
  - liczy metryki, zapisuje tabelę zbiorczą + macierze pomyłek do results/.

Rozbudowa (patrz PLAN.md): strojenie ≥3 zestawów (classify.tune), bonusy, więcej metryk.

Uruchom:
    python -m src.run_all
"""
from __future__ import annotations

import warnings

import pandas as pd
from sklearn.model_selection import train_test_split

from . import config
from .classify import build_pipeline, get_estimators
from .evaluate import compute_metrics, full_report, metrics_table, save_confusion_png
from .load_data import load_data, split_X_y
from .preprocess import PREPROCESS_VARIANTS

warnings.filterwarnings("ignore", category=UserWarning)


def main() -> pd.DataFrame:
    config.RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    df = load_data()
    X, y = split_X_y(df)

    X_tr, X_val, y_tr, y_val = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=config.RANDOM_STATE
    )
    print(f"[split] train={len(X_tr)}  val={len(X_val)}  (stratyfikowany)")

    labels = config.CLASS_LABELS
    rows = []
    for variant in PREPROCESS_VARIANTS:
        for name, (estimator, _grid) in get_estimators().items():
            pipe = build_pipeline(estimator, variant=variant)
            pipe.fit(X_tr, y_tr)
            y_pred = pipe.predict(X_val)

            m = compute_metrics(y_val, y_pred, labels=labels)
            m = {"model": name, "preprocessing": variant, **m}
            rows.append(m)

            print(f"\n=== {name} | {variant} ===")
            print(f"acc={m['accuracy']}  f1_macro={m['f1_macro']}  "
                  f"f1_C={m.get('f1_C')} f1_CL={m.get('f1_CL')} f1_D={m.get('f1_D')}")
            print(full_report(y_val, y_pred, labels=labels))
            save_confusion_png(
                y_val, y_pred,
                title=f"{name} | {variant}",
                path=config.RESULTS_DIR / f"cm_{name}_{variant}.png",
                labels=labels,
            )

    table = metrics_table(rows).sort_values("f1_macro", ascending=False)
    out = config.RESULTS_DIR / "baseline_metrics.csv"
    table.to_csv(out, index=False)
    print(f"\n[zapisano] {out}")
    print("\n--- Tabela zbiorcza (baseline) ---")
    print(table.to_string(index=False))
    return table


if __name__ == "__main__":
    main()
