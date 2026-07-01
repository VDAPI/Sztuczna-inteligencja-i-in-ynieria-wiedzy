# PLAN IMPLEMENTACJI — SIiIW Lista 4

Plan krok-po-kroku. Każda faza mapuje się na punktację. Pułapki ML są w `CLAUDE.md` — zerknij tam, zanim ruszysz.

---

## Faza 0 — Setup i dane

1. `pip install -r requirements.txt --break-system-packages`
2. Zdobądź dane (szczegóły w `data/README.md`). Dwie drogi:
   - `ucimlrepo` → `fetch_ucirepo(id=878)` (automatycznie, wymaga sieci),
   - lokalny `data/cirrhosis.csv` (z Kaggle/UCI — wariant zgodny z treścią: 418 wierszy, `Status` jako C/CL/D).
3. Uruchom `python -m src.load_data` — powinien wydrukować kształt, typy i raport braków.

**Efekt:** czysty DataFrame, `ID` i `N_Days` usunięte, typy ustawione.

---

## Faza 1 — Eksploracja danych (EDA) · 10 pkt

Plik: `src/explore.py`. Zadanie: „podstawowe dane statystyczne i uwagi dot. cech i etykiet".

1. Kształt zbioru, liczba cech, liczba i typy kolumn.
2. **Rozkład klasy `Status`** — liczności i % (pokaż nierównowagę, zwłaszcza `CL`). Wykres słupkowy → `results/eda_target_dist.png`.
3. Statystyki opisowe cech liczbowych (`df.describe()`): średnia, mediana, min/max, odchylenie. Zapisz `results/eda_numeric_describe.csv`.
4. Rozkłady cech kategorycznych (`value_counts`).
5. **Mapa braków** — ile `NA` w każdej kolumnie i % (kluczowe dla Fazy 2). `results/eda_missingness.csv`.
6. Korelacje cech liczbowych (heatmapa) → `results/eda_corr.png`. Komentarz o współliniowości.
7. Przelicz `Age` na lata na potrzeby opisu.
8. (Opcjonalnie) histogramy/boxploty cech względem klasy — które cechy separują klasy (np. `Bilirubin`, `Albumin`, `Prothrombin` są klinicznie istotne).

**Do raportu:** 3–5 zdań obserwacji: skośność cech (bilirubina!), nierównowaga klas, skala braków, kandydaci na cechy istotne.

---

## Faza 2 — Przygotowanie danych · 30 pkt

Plik: `src/preprocess.py`. To najcięższa punktowo część — zrób ją porządnie.

### 2a. Podział train / walidacja
- `train_test_split(..., test_size=0.2, stratify=y, random_state=42)` **lub** walidacja krzyżowa `StratifiedKFold(n_splits=5)`.
- Przy małym zbiorze (418) i nierównowadze **rekomendowana walidacja krzyżowa stratyfikowana** — stabilniejsze wyniki. Możesz zrobić oba: CV do strojenia + finalny holdout do raportu.

### 2b. Braki danych (metoda(-y) postępowania)
Zastosuj ≥1 metodę (sugerowane: imputacja). Implementacja przez `ColumnTransformer`:
- liczbowe → `SimpleImputer(strategy='median')`,
- kategoryczne → `SimpleImputer(strategy='most_frequent')` lub `fill_value='Missing'` jako osobna kategoria,
- `Drug` (NA dla wszystkich 106 spoza trialu) → decyzja: osobna kategoria / usunięcie kolumny / usunięcie wierszy. Opisz wybór.
- (Bonus do interpretacji) porównaj 2 strategie braków, np. imputacja vs usunięcie wierszy — pokaż wpływ na liczność i wynik.

### 2c. Porównanie metod przetwarzania (WYMAGANE: baseline + ≥2 metody, osobno)
Zbuduj 3 pipeline'y i porównaj na tych samych klasyfikatorach:

| Wariant | Co robi | Po co |
|---|---|---|
| **Baseline** | tylko imputacja + encoding (`OneHotEncoder` kat., `passthrough` num.) | punkt odniesienia |
| **Metoda A — Selekcja cech** | + `SelectKBest(mutual_info_classif, k=...)` (≈ InfoGain) | mniej cech, redukcja szumu |
| **Metoda B — PCA** | + `StandardScaler` → `PCA(n_components=...)` | redukcja wymiaru, dekorelacja |

> ⚠️ NIE wybieraj „standaryzacja vs bez" jako metody dla NB/drzewa — patrz pułapka #3 w `CLAUDE.md` (identyczne wyniki). Dyskretyzacja (`KBinsDiscretizer` + `CategoricalNB`) to dobra alternatywa dla Metody A/B, jeśli chcesz.

Każdy wariant przepuść przez **oba** klasyfikatory (Faza 3), zbierz metryki, zrób tabelę porównawczą `results/preprocessing_comparison.csv`.

**Do raportu:** tabela baseline vs A vs B × {NB, drzewo} + komentarz, która metoda i czemu pomogła/zaszkodziła.

---

## Faza 3 — Klasyfikacja

Plik: `src/classify.py`.

### 3a. Naiwny klasyfikator Bayesa
- `GaussianNB` (cechy liczbowe) — główny wariant.
- Strojenie ≥3 zestawy: `var_smoothing ∈ {1e-9, 1e-7, 1e-5, 1e-3}`. Dodatkowo możesz porównać `GaussianNB` vs `CategoricalNB` (na danych zdyskretyzowanych) — to ładnie pokazuje wpływ założeń modelu.
- Strojenie: `GridSearchCV(..., scoring='f1_macro', cv=StratifiedKFold(5))`.

### 3b. Drzewo decyzyjne
- `DecisionTreeClassifier(random_state=42)`.
- Strojenie ≥3 zestawy, np. siatka po: `criterion ∈ {gini, entropy}`, `max_depth ∈ {3, 5, 10, None}`, `min_samples_leaf ∈ {1, 5, 10}`.
- Zbadaj wpływ głębokości na przeuczenie (krzywa train vs val accuracy w funkcji `max_depth`) → `results/dt_depth_curve.png`.

### 3c. Bonus (+5) — zaawansowane algorytmy
- `RandomForestClassifier` (strojenie `n_estimators`, `max_depth`) i/lub `SVC`.
- **Przy SVM:** pokaż wpływ `StandardScaler` (tu skalowanie MA znaczenie!), strojenie `C`, `kernel`, `gamma`. „Ze zrozumieniem" = krótko wyjaśnij, czemu SVM wymaga skalowania, a drzewo nie.

### 3d. Bonus (+5) — złagodzenie przeuczenia (1 klasyfikator)
- Najlepszy kandydat: **drzewo** + **przycinanie kosztowo-złożonościowe** (`ccp_alpha`).
  - Wylicz ścieżkę `cost_complexity_pruning_path`, wybierz `ccp_alpha`, pokaż jak maleje różnica train–val (overfitting gap).
  - Alternatywy: ograniczenie `max_depth` / zwiększenie `min_samples_leaf`.
- Wykres train vs val przed/po → `results/overfitting_mitigation.png`. Komentarz.

**Do raportu:** dla każdego klasyfikatora tabela 3 zestawów hiperparametrów + ich metryki + wskazanie najlepszego.

---

## Faza 4 — Ewaluacja i interpretacja · 20 pkt

Plik: `src/evaluate.py` (pomocnik `compute_metrics` używaj wszędzie).

Dla każdego (wariant przetwarzania × klasyfikator × najlepsze hiperparametry) policz na zbiorze walidacyjnym:
- **Accuracy** (ACC),
- **Precision / Recall / F1** — macro ORAZ weighted (3 klasy!),
- **Per-klasa** P/R/F1 (`classification_report`),
- **Macierz pomyłek** (3×3) → `results/cm_<model>.png`.

Zbierz wszystko w jedną tabelę zbiorczą `results/final_metrics.csv`.

**Interpretacja (to jest punktowane!):**
- Czemu accuracy ≠ macro-F1 (nierównowaga, `CL`).
- Który model + preprocessing wygrał i dlaczego.
- Co macierz pomyłek mówi o myleniu klas (`CL` pewnie wpada w `C`/`D`).
- NB vs drzewo — założenia, mocne/słabe strony na tych danych.

---

## Faza 5 — Raport

Plik: `report/raport_szablon.md` (po polsku — wypełnij `# TODO (Dawid)`).
- Krótki opis każdego kroku + tabele z `results/` + interpretacja.
- Sekcja „wykorzystane biblioteki" (scikit-learn, pandas, …) i „materiały źródłowe" (UCI, DOI 10.24432/C5R02G).
- Eksport do PDF/DOCX na końcu, jeśli prowadzący chce.
- **Wyślij prowadzącemu ≥24h przed oddaniem listy** (wymóg z treści).

---

## Definicja „gotowe"

- [ ] `N_Days`, `ID` usunięte (brak wycieku).
- [ ] EDA z rozkładem klas i mapą braków.
- [ ] Split/CV stratyfikowany; preprocessing `fit` tylko na train.
- [ ] Baseline + ≥2 metody przetwarzania, porównane osobno.
- [ ] NB i drzewo, każdy z ≥3 zestawami hiperparametrów.
- [ ] Metryki: ACC + macro/weighted P-R-F1 + per-klasa + macierze pomyłek.
- [ ] Interpretacja odnosi się do nierównowagi i `CL`.
- [ ] (Bonus) RF/SVM, (Bonus) złagodzenie przeuczenia.
- [ ] Raport PL gotowy, tabele wklejone.
