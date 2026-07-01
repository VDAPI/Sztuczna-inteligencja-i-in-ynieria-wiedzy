# Sprawozdanie – Lista 3, Zadanie 3 (PDDL, robot z piłkami)

**Autor:** Dawid Pilarski
**Kurs:** Sztuczna Inteligencja i Inżynieria Wiedzy (SIiIW)
**Planer:** Pyperplan 2.1 (A\* + hFF)

---

## 1. Opis problemu

Domena i problem podane w treści listy. Robot ma 2 ramiona, znajduje się w `room1` razem z 4 piłkami (`ball1..ball4`). Cel: wszystkie piłki w `room2`.

**Drobna poprawka:** w PDF zadania plik `problem.pddl` miał błędy w nawiasach (brak otwierającego `(define` i nadmiarowy `)` na końcu). W moim pliku poprawione.

## 2. Plan

```
1.  (pick-up robot arm2 ball2 room1)
2.  (pick-up robot arm1 ball4 room1)
3.  (move    robot room1 room2)
4.  (put-down robot arm2 ball2 room2)
5.  (put-down robot arm1 ball4 room2)
6.  (move    robot room2 room1)
7.  (pick-up robot arm2 ball1 room1)
8.  (pick-up robot arm1 ball3 room1)
9.  (move    robot room1 room2)
10. (put-down robot arm2 ball1 room2)
11. (put-down robot arm1 ball3 room2)
```

**Długość: 11 akcji.**

## 3. Analiza

| Metryka | Wartość |
|---|---|
| Długość planu | 11 akcji |
| Czas wyszukiwania | 0.017 s |
| Węzły rozwinięte | 82 |

### Struktura planu

Plan składa się z **dwóch wycieczek** po 2 piłki:
- Akcje 1-5: zabranie ball2 i ball4 do room2
- Akcja 6: powrót do room1
- Akcje 7-11: zabranie ball1 i ball3 do room2

Każda wycieczka: 2× pick-up + 1× move + 2× put-down = **5 akcji**, plus 1 powrót pomiędzy = **11 akcji**.

### Czy plan jest optymalny

**Tak.** Robot ma 2 ramiona, więc maksymalnie przenosi 2 piłki na raz. 4 piłki = minimum 2 wycieczki. Mniej akcji się nie da.

### Wpływ liczby ramion na plan (analiza teoretyczna)

| Liczba ramion | Liczba wycieczek | Długość planu |
|---:|---:|---:|
| 1 | 4 | 15 |
| 2 | 2 | **11** |
| 4 | 1 | 9 |

Wzór: `długość = ceil(4 / liczba_ramion) × 5 - 1`. Pokazuje, że **zwiększanie liczby ramion ma malejący zysk** — z 1 do 2 ramion zysk 4 akcje, z 2 do 4 zysk tylko 2 akcje.

### Czemu planer wybrał akurat te kombinacje piłka-ramię

`ball2→arm2, ball4→arm1, ball1→arm2, ball3→arm1` — to **arbitralne**. Wszystkie piłki są w tym problemie wymienne (mają identyczne predykaty), tak samo ramiona. A* z heurystyką hFF wybiera pierwszą sekwencję optymalnej długości. Inny planer mógłby dać plan z innymi przypisaniami, ale o tej samej długości.

## 4. Wnioski

1. **PDDL nie wymaga określenia kolejności** wykonywania akcji `pick-up` w tej samej lokacji — planer sam je porządkuje. Akcje 1 i 2 mogą być wykonane w dowolnej kolejności (planer wybiera jedną).

2. **Niezmiennik `(arm-empty ?a)` ↔ ¬`(holding ?a ?b)`** jest pilnowany ręcznie przez efekty akcji (`pick-up` ustawia `not arm-empty`, `put-down` ustawia `arm-empty`). Brak tych efektów spowodowałby, że ramię mogłoby "trzymać dwie piłki naraz".

3. **Brak predykatu `connected`** dla pokoi — robot może iść z dowolnego do dowolnego. W realnym problemie z N pokojami i topologią (np. graf korytarzy) dodanie takiego predykatu wymagałoby modyfikacji akcji `move`:
```
:precondition (and (at ?r ?from) (connected ?from ?to))
```

## 5. Pliki

- `domain.pddl` — domena z treści zadania
- `problem.pddl` — problem z treści zadania (z poprawionymi nawiasami)
- `plan.txt` — wygenerowany plan (11 akcji)
