# Dane — „Cirrhosis Patient Survival Prediction"

Zbiór: UCI ML Repository, **id = 878**. 418 przypadków (Mayo Clinic, 1974–1984).

## Dwie drogi zdobycia danych

### A) Automatycznie przez `ucimlrepo` (wymaga internetu)
Loader (`src/load_data.py`) zrobi to sam:
```python
from ucimlrepo import fetch_ucirepo
ds = fetch_ucirepo(id=878)
X = ds.data.features
y = ds.data.targets
```
> Uwaga: wersja UCI id=878 bywa „przygotowana pod zadanie" — etykiety `Status` jako `0=D, 1=C, 2=CL`, a część braków/kolumn może być już ruszona. Loader normalizuje etykiety i typy, więc oba warianty zadziałają.

### B) Lokalny CSV (wariant zgodny 1:1 z treścią zadania)
Pobierz `cirrhosis.csv` i połóż w `data/cirrhosis.csv`. Ten wariant ma **418 wierszy**, `Status` jako napisy `C`/`CL`/`D`, braki oznaczone `NA` — dokładnie jak opisano w PDF.
- Kaggle: „Cirrhosis Patient Survival Prediction" (joebeachcapital) — plik `cirrhosis.csv`.
- UCI: strona zbioru id=878 → sekcja Download.

Loader wykrywa lokalny plik automatycznie, jeśli istnieje (`config.LOCAL_CSV`).

## Kolumny (20 w surowym CSV)

`ID, N_Days, Status, Drug, Age, Sex, Ascites, Hepatomegaly, Spiders, Edema, Bilirubin, Cholesterol, Albumin, Copper, Alk_Phos, SGOT, Tryglicerides, Platelets, Prothrombin, Stage`

- **Target:** `Status` ∈ {C, CL, D}
- **Wyrzucane:** `ID` (identyfikator), `N_Days` (⚠️ wyciek targetu — czas przeżycia)
- **17 cech** = reszta. Pisownia `Tryglicerides` (z błędem) jest oryginalna.

## Cytowanie
Dickson, E., Grambsch, P., Fleming, T., Fisher, L., & Langworthy, A. (1989). *Cirrhosis Patient Survival Prediction* [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5R02G — licencja CC BY 4.0.
