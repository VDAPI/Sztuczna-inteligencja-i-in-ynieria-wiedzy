# Lista 4 — Klasyfikacja przeżywalności w marskości wątroby

## O co chodziło (moje streszczenie)

Zadanie to pełny **projekt klasyfikacji wieloklasowej** na zbiorze UCI *Cirrhosis Patient Survival
Prediction* (418 pacjentów, Mayo Clinic). Zmienną docelową jest `Status` pacjenta w trzech klasach
(przeżycie / przeszczep / zgon). Przez cały pipeline trzeba było przejść samodzielnie:

1. **Eksploracja danych (EDA)** — rozkłady cech, braki danych, korelacje.
2. **Przygotowanie danych** — podział train/test ze stratyfikacją, obsługa braków (imputacja)
   oraz porównanie **co najmniej dwóch metod przetwarzania** cech.
3. **Klasyfikacja** — **Naive Bayes** i **drzewo decyzyjne**, każdy strojony na kilku zestawach
   hiperparametrów; bonusowo algorytmy zaawansowane (**Random Forest**, **SVM**) oraz techniki
   ograniczające przeuczenie.
4. **Ewaluacja i interpretacja** — metryki (accuracy, **macro-F1**), macierze pomyłek, wnioski.

Pełną treść polecenia pomijam (materiał prowadzących).

## Na co uważałem (kluczowe decyzje metodyczne)

- **Wyciek danych:** kolumny `N_Days` i `ID` usunięte — `N_Days` praktycznie zdradza `Status`.
- **Nierównowaga klas:** klasa „przeszczep" jest bardzo rzadka, dlatego raportuję macro-F1 i
  macierze pomyłek per-klasa, a nie samą dokładność; strojenie po `f1_macro`.
- **Dobór przetwarzania:** standaryzacja nie zmienia wyników drzewa ani GaussianNB, więc jako
  realnie różnicujące metody wybrałem **selekcję cech (InfoGain)** i **PCA**; skalowanie pokazuję
  przy SVM.
- **Brak wycieku w preprocessingu:** `fit` tylko na zbiorze treningowym (pipeline'y sklearn).

Szczegóły w [`rozwiazanie/`](./rozwiazanie) — kod w `src/`, wyniki (tabele CSV + wykresy PNG) w
`results/`, dane w `data/`, notebook `lista4.ipynb`. Plik `rozwiazanie/CLAUDE.md` zawiera moje
notatki o pułapkach ML tego zadania.

## Raport

[`raport.pdf`](./raport.pdf) — opis danych, przygotowania, eksperymentów klasyfikacyjnych,
metryk i interpretacji wyników.
