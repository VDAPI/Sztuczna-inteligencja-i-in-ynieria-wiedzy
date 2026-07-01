# Sztuczna inteligencja i inżynieria wiedzy — Lista 4
## Klasyfikacja przeżywalności pacjentów z marskością wątroby

**Autor:** Dawid Pilarski
**Data:**  `# TODO`
**Zbiór danych:** Cirrhosis Patient Survival Prediction (UCI ML Repository, id=878)

> Szablon do wypełnienia. Tabele wklejaj z `results/`. W miejscach `# TODO (Dawid)` wpisz własne obserwacje i wnioski — interpretacja jest punktowana.

---

## 1. Eksploracja danych *(10 pkt)*

**Zbiór:** 418 obserwacji, 17 cech + zmienna docelowa `Status`. Pochodzenie: badanie Mayo Clinic 1974–1984.

**Zmienna docelowa — 3 klasy:**
- `C`  — censored (wynik inny niż śmierć z powodu choroby)
- `CL` — censored due to liver transplantation
- `D`  — death

Rozkład klas (z `results/eda_target_dist.png` / loadera):

| Klasa | Liczność | % |
|---|---|---|
| C | `# TODO` | `# TODO` |
| D | `# TODO` | `# TODO` |
| CL | `# TODO` | `# TODO` |

**Statystyki cech liczbowych:** `results/eda_numeric_describe.csv`.

**Braki danych:** `results/eda_missingness.csv` — najwięcej w `Drug` (ok. 25%, pacjenci spoza badania klinicznego) oraz w cechach laboratoryjnych.

**Obserwacje:**
`# TODO (Dawid)` — np.: silna nierównowaga klas (CL ~6%), prawostronna skośność `Bilirubin`/`Alk_Phos`, korelacje cech (z `eda_corr.png`), cechy klinicznie istotne (Bilirubin, Albumin, Prothrombin), `Age` przeliczony na lata.

---

## 2. Przygotowanie danych *(30 pkt)*

### 2.1 Podział danych
`# TODO` — opis: stratyfikowany podział train/val (test_size=0.2) lub walidacja krzyżowa `StratifiedKFold(5)`. Uzasadnienie stratyfikacji (rzadka klasa CL).

### 2.2 Postępowanie z brakami
`# TODO` — zastosowana metoda (imputacja medianą dla liczbowych, „Missing"/moda dla kategorycznych; decyzja co do `Drug`). Uzasadnienie wyboru względem usuwania wierszy.

### 2.3 Porównanie metod przetwarzania (baseline + 2 metody)

| Klasyfikator | Przetwarzanie | Accuracy | F1-macro | F1 (C) | F1 (CL) | F1 (D) |
|---|---|---|---|---|---|---|
| NB | baseline | | | | | |
| NB | selekcja cech | | | | | |
| NB | PCA | | | | | |
| Drzewo | baseline | | | | | |
| Drzewo | selekcja cech | | | | | |
| Drzewo | PCA | | | | | |

*(źródło: `results/preprocessing_comparison.csv`)*

**Wnioski:** `# TODO (Dawid)` — która metoda pomogła/zaszkodziła i dlaczego. (Uwaga: standaryzacja celowo nie była porównywana dla NB/drzewa — nie zmienia ich wyników.)

---

## 3. Klasyfikacja

### 3.1 Naiwny klasyfikator Bayesa — strojenie (≥3 zestawy)

| Lp. | Hiperparametry | F1-macro (CV) | Accuracy (val) |
|---|---|---|---|
| 1 | `var_smoothing=1e-9` | | |
| 2 | `var_smoothing=1e-7` | | |
| 3 | `var_smoothing=1e-5` | | |

Najlepszy: `# TODO`.

### 3.2 Drzewo decyzyjne — strojenie (≥3 zestawy)

| Lp. | Hiperparametry | F1-macro (CV) | Accuracy (val) |
|---|---|---|---|
| 1 | `criterion=gini, max_depth=3` | | |
| 2 | `criterion=entropy, max_depth=5` | | |
| 3 | `criterion=entropy, max_depth=None` | | |

Wpływ głębokości na przeuczenie: `results/dt_depth_curve.png`. Komentarz: `# TODO`.

### 3.3 Bonus — zaawansowane algorytmy *(+5)*
`# TODO` — Random Forest i/lub SVM. Dla SVM: opis roli skalowania (StandardScaler) i czemu drzewo go nie wymaga.

### 3.4 Bonus — złagodzenie przeuczenia *(+5)*
`# TODO` — drzewo + przycinanie `ccp_alpha`. Wykres train vs val przed/po: `results/overfitting_mitigation.png`. Komentarz o zmniejszeniu różnicy train–val.

---

## 4. Ewaluacja klasyfikacji *(20 pkt)*

Tabela zbiorcza (najlepsze konfiguracje), źródło `results/final_metrics.csv`:

| Model | Przetwarzanie | ACC | P-macro | R-macro | F1-macro | F1-weighted |
|---|---|---|---|---|---|---|
| | | | | | | |

Macierze pomyłek: `results/cm_*.png`.

**Interpretacja:** `# TODO (Dawid)`
- dlaczego accuracy ≠ F1-macro (rola nierównowagi i klasy CL),
- z czym mylona jest klasa CL (analiza macierzy pomyłek),
- NB vs drzewo — założenia, mocne/słabe strony na tych danych,
- wygrana konfiguracja i uzasadnienie.

---

## 5. Wykorzystane materiały i biblioteki

**Biblioteki:**
- **scikit-learn** — modele (`GaussianNB`, `DecisionTreeClassifier`, `RandomForestClassifier`, `SVC`), preprocessing (`SimpleImputer`, `OneHotEncoder`, `StandardScaler`, `PCA`, `SelectKBest`), strojenie (`GridSearchCV`, `StratifiedKFold`), metryki.
- **pandas / numpy** — wczytanie i obróbka danych.
- **matplotlib / seaborn** — wizualizacje.
- **ucimlrepo** — pobranie zbioru z UCI.

**Materiały źródłowe:**
- Dickson, E., Grambsch, P., Fleming, T., Fisher, L., & Langworthy, A. (1989). *Cirrhosis Patient Survival Prediction* [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5R02G
- `# TODO` — dokumentacja scikit-learn / inne, jeśli korzystano.
