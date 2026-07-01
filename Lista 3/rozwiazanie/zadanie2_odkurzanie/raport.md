# Sprawozdanie – Lista 3, Zadanie 2 (PDDL, robot odkurzający)

**Autor:** Dawid Pilarski
**Kurs:** Sztuczna Inteligencja i Inżynieria Wiedzy (SIiIW)
**Planer:** Pyperplan 2.1 (A\* + hFF)

---

## 1. Opis problemu

Robot `rumba` startuje w `pokoj1`. Wszystkie 3 pokoje (`pokoj1`, `pokoj2`, `pokoj3`) są brudne. Cel: wszystkie czyste.

Domena ma 2 akcje: `move` (przejście między dowolnymi pokojami) i `clean` (sprzątanie pokoju, w którym jest robot).

## 2. Plan

```
1. (clean rumba pokoj1)
2. (move  rumba pokoj1 pokoj3)
3. (clean rumba pokoj3)
4. (move  rumba pokoj3 pokoj2)
5. (clean rumba pokoj2)
```

**Długość: 5 akcji.**

## 3. Analiza

| Metryka | Wartość |
|---|---|
| Długość planu | 5 akcji |
| Czas wyszukiwania | 0.0006 s |
| Węzły rozwinięte | 6 |

Plan jest **optymalny**:
- 3 akcje `clean` (po jednej na pokój — nieuniknione)
- 2 akcje `move` (robot startuje w pokoj1, musi przejść do 2 pozostałych)
- Razem: **3 + 2 = 5**

Niżej zejść się nie da bo:
- Każdy pokój wymaga 1× clean (nie można sprzątnąć "naraz" — to są osobne stany).
- Robot ma 1 pozycję na raz, musi się przemieścić by sprzątać kolejne pokoje.

Kolejność wybrana przez planer (`pokoj1 → pokoj3 → pokoj2`) jest arbitralna — bez kosztów drogi planer wybiera pierwszą znalezioną sekwencję optymalnej długości.

## 4. Wnioski

1. **Akcja `clean` z preconditionem `(dirty ?p)`** zapobiega marnotrawnym akcjom czyszczenia czystego pokoju.
2. **Brak predykatu `connected`** upraszcza model — robot może przejść między dowolnymi pokojami. Dla 3 pokojów to nie ma znaczenia, ale w większych problemach (np. 20 pokojów liniowo) plan byłby drastycznie krótszy niż w wersji z ograniczeniami.
3. **STRIPS bez kosztów** minimalizuje liczbę akcji, co dla tego problemu jest tożsame z "czas pracy robota". Gdyby `clean` zajmował 5 minut a `move` 1 minutę, dla minimalizacji czasu trzeba by `:action-costs` z różnymi kosztami akcji.

## 5. Pliki

- `domain.pddl` — domena (typy, predykaty, akcje)
- `problem.pddl` — scenariusz (3 pokoje, robot w pokoj1)
- `plan.txt` — wygenerowany plan
