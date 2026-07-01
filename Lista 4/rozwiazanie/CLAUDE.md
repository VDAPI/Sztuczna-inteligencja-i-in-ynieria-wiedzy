# CLAUDE.md — brief dla Claude Code

> Ten plik czytasz na starcie. Zawiera kontekst projektu, konwencje i **kluczowe pułapki ML**, których łatwo nie zauważyć. Szczegółowy plan krok-po-kroku jest w `PLAN.md`.

## Cel projektu

SIiIW (Sztuczna inteligencja i inżynieria wiedzy) — **Lista 4**. Klasyfikacja przeżywalności pacjentów z marskością wątroby na zbiorze UCI „Cirrhosis Patient Survival Prediction" (418 przypadków, Mayo Clinic 1974–1984).

**Problem:** klasyfikacja wieloklasowa (3 klasy), zmienna docelowa `Status`:
- `C`  — censored (wynik inny niż śmierć z powodu choroby)
- `CL` — censored due to liver transplantation (przeszczep)
- `D`  — death (śmierć)

W wersji UCI id=878 etykiety bywają zakodowane jako `0=D, 1=C, 2=CL` — loader obsługuje oba warianty.

## Stack

Python 3.10+, scikit-learn, pandas, numpy, matplotlib/seaborn. Zależności w `requirements.txt`.
Instalacja: `pip install -r requirements.txt --break-system-packages` (lub w venv).

## Punktacja (mapuj pracę na to!)

| Część | Punkty | Plik |
|---|---|---|
| 1. Eksploracja danych (EDA) | 10 | `src/explore.py` |
| 2. Przygotowanie danych (split + braki + ≥2 metody przetwarzania) | 30 | `src/preprocess.py` |
| 3. Klasyfikacja (NB + drzewo, ≥3 zestawy hiperparametrów każdy) | — | `src/classify.py` |
| Bonus: zaawansowane algorytmy (RF / SVM) | +5 | `src/classify.py` |
| Bonus: złagodzenie przeuczenia (1 klasyfikator) | +5 | `src/classify.py` |
| 4. Ewaluacja + interpretacja metryk | 20 | `src/evaluate.py` |
| Raport (PL, do prowadzącego ≥24h przed oddaniem) | — | `report/raport_szablon.md` |

## ⚠️ KLUCZOWE PUŁAPKI (przeczytaj zanim zaczniesz)

### 1. Wyciek danych: `N_Days` i `ID`
Surowy zbiór ma 20 kolumn, ale lista cech w treści zadania liczy **dokładnie 17 cech** — `N_Days` i `ID` NIE są na liście.
- `N_Days` = czas od rejestracji do śmierci/przeszczepu/końca badania → **bezpośrednio determinuje `Status`**. To wyciek targetu (data leakage). **Wyrzuć tę kolumnę.** Jeśli ją zostawisz, modele osiągną sztucznie wysokie wyniki, które nie znaczą nic.
- `ID` = identyfikator, brak wartości predykcyjnej → wyrzuć.

Loader (`src/load_data.py`) usuwa obie automatycznie (`config.LEAKAGE_COLS`).

### 2. Silna nierównowaga klas — `CL` to ~6%
Rozkład w przybliżeniu: `C` ≈ 232, `D` ≈ 161, `CL` ≈ 25. Klasa `CL` jest rzadka.
- **Accuracy jest myląca** — model ignorujący `CL` i tak ma wysoką dokładność. ZAWSZE raportuj też **macro-F1** i **macierz pomyłek per-klasa**.
- Podział i walidacja krzyżowa: **stratyfikowane** (`stratify=y`, `StratifiedKFold`).
- Strojenie hiperparametrów: optymalizuj po `scoring='f1_macro'`, nie po accuracy.
- W interpretacji koniecznie opisz, dlaczego `CL` jest trudna (mało próbek) — to świadomy komentarz, którego prowadzący szuka.

### 3. Przetwarzanie danych — które metody w ogóle COKOLWIEK zmieniają
To jest najczęstszy błąd na tej liście. Zadanie wymaga porównania „bez przetwarzania" vs ≥2 metody **osobno**. Ale uwaga:

- **Normalizacja / standaryzacja NIE zmienia wyników `GaussianNB` ani drzewa decyzyjnego.** Drzewa są niezmiennicze na monotoniczne transformacje cech; GaussianNB modeluje rozkład każdej cechy osobno, więc przeskalowanie nic nie daje. Jeśli porównasz „standaryzacja vs bez" na tych dwóch klasyfikatorach, dostaniesz **identyczne liczby** i wyjdziesz na osobę, która nie rozumie czemu.
- Metody, które **realnie** zmieniają wyniki NB / drzewa:
  - **Dyskretyzacja** (`KBinsDiscretizer`) → pozwala użyć `CategoricalNB`/`MultinomialNB` zamiast `GaussianNB`, zmienia model założeniowo.
  - **PCA** → obraca i redukuje przestrzeń cech, zmienia wszystko.
  - **Selekcja cech** (`SelectKBest` z `mutual_info_classif` ≈ InfoGain z treści zadania) → mniej cech, inny wynik.
- **Standaryzacja MA znaczenie** dla bonusowego **SVM** (i KNN). Jeśli robisz SVM, pokaż tam efekt skalowania — to dobry, sensowny przykład.

**Rekomendacja:** jako 2 metody do porównania wybierz np. **(A) selekcja cech (InfoGain)** i **(B) PCA** — obie realnie ruszają wyniki dla NB i drzewa. Standaryzację pokaż osobno przy SVM.

### 4. Brak wyciekania przy preprocessingu (fit tylko na train!)
Imputer, scaler, PCA, dyskretyzer — **`fit` WYŁĄCZNIE na zbiorze treningowym**, potem `transform` na walidacyjnym/testowym. Inaczej statystyki ze zbioru testowego „przeciekają" do treningu.
- Używaj `sklearn.pipeline.Pipeline` + `ColumnTransformer` — to załatwia problem automatycznie i czysto, szczególnie wewnątrz `cross_val_score`/`GridSearchCV`.

### 5. Braki danych — nie usuwaj pochopnie wierszy
106 z 418 pacjentów (ci spoza badania klinicznego) ma dużo `NA`:
- `Drug` jest `NA` dla **wszystkich** 106 → rozważ: osobna kategoria „Missing"/„NotInTrial", albo usunięcie kolumny `Drug`, albo (wariant z treści UCI) usunięcie tych wierszy.
- Liczbowe (`Cholesterol`, `Copper`, `Alk_Phos`, `SGOT`, `Tryglicerides`, `Platelets`) — imputacja medianą.
- Zadanie premiuje zachowanie informacji → **imputacja > usuwanie**. Pokaż minimum 1 metodę (sugerowane: imputacja medianą dla liczbowych, moda/„Missing" dla kategorycznych). Możesz porównać 2 strategie braków, ale to nie jest wymagane.

### 6. Typy kolumn
- **Kategoryczne (7):** `Drug, Sex, Ascites, Hepatomegaly, Spiders, Edema, Stage`
  - `Stage` (1–4) jest porządkowa; `Edema` jest porządkowa (N < S < Y). Można je tak potraktować, ale one-hot też jest OK — wspomnij wybór w raporcie.
- **Liczbowe (10):** `Age, Bilirubin, Cholesterol, Albumin, Copper, Alk_Phos, SGOT, Tryglicerides, Platelets, Prothrombin`
- **UWAGA na pisownię:** kolumna to `Tryglicerides` (tak literuje oryginalny CSV, z błędem). Nie `Triglycerides`.
- `Age` jest w **dniach** → w EDA przelicz na lata (`/365.25`) dla czytelności. Model może użyć którejkolwiek wersji (drzewo i tak jest niezmiennicze na skalę).

## Konwencje

- Reprodukowalność: wszędzie `RANDOM_STATE = 42` (jest w `config.py`).
- Wyniki zapisuj do `results/` jako CSV (tabele do raportu) i PNG (wykresy). Nazwy mówiące, np. `results/metrics_baseline_nb.csv`.
- Każdy eksperyment = jedna funkcja zwracająca dict/DataFrame z metrykami; nie kopiuj-wklejaj.
- Wykresy: zapisuj do plików, nie polegaj na `plt.show()` (środowisko bywa headless).
- Metryki licz pomocnikiem `evaluate.compute_metrics(...)` — spójność w całym projekcie.

## Kolejność budowy

Idź fazami z `PLAN.md`. Szybki sanity-check, że spine działa:
```bash
pip install -r requirements.txt --break-system-packages
python -m src.load_data        # pobiera/wczytuje dane, drukuje raport braków
python -m src.run_all          # baseline NB + drzewo, zapis metryk do results/
```
Potem rozbudowuj: preprocessing (2 metody), strojenie (≥3 zestawy), bonusy, raport.

## Czego NIE robić

- Nie zostawiaj `N_Days` „bo poprawia wynik" — to dyskwalifikujący błąd metodologiczny.
- Nie raportuj samej accuracy przy tej nierównowadze klas.
- Nie porównuj „standaryzacja vs bez" na NB/drzewie jako jednej z 2 metod (identyczne wyniki).
- Nie rób `fit` preprocessingu na całym zbiorze przed splitem.
- Nie pisz interpretacji za studenta w raporcie — zostaw `# TODO (Dawid)` tam, gdzie trzeba wpisać własne wnioski z liczb. To jego praca zaliczeniowa.
