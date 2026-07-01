# Zadanie 3 — Robot przenoszący piłki

## O co chodzi w zadaniu

Z treści listy (10 pkt): **uruchom podany model PDDL, wygeneruj plan i przeanalizuj go.**

To zadanie najprostsze — kod jest **dany w treści zadania**. Wystarczy go skopiować, uruchomić i opisać co zwraca planer.

## Opis problemu (z treści)

Robot ma **dwa ramiona** i może poruszać się między dwoma pokojami. W pierwszym pokoju znajdują się **cztery piłki** oraz sam robot. Cel: **przenieść wszystkie piłki do drugiego pokoju**.

**Obiekty:**
- pokoje: `room1`, `room2`
- piłki: `ball1`, `ball2`, `ball3`, `ball4`
- ramiona: `arm1`, `arm2`
- robot

**Predykaty:**
- `(at ?r - robot ?room - room)` — robot w pokoju
- `(inroom ?b - ball ?room - room)` — piłka w pokoju
- `(holding ?a - arm ?b - ball)` — ramię trzyma piłkę
- `(arm-empty ?a - arm)` — ramię jest puste

**Akcje:**
- `move` — robot przechodzi między pokojami
- `pick-up` — bierze piłkę (wymaga: robot w pokoju, piłka w pokoju, ramię puste)
- `put-down` — kładzie piłkę (wymaga: robot w pokoju, ramię trzyma piłkę)

## Drobna poprawka w treści zadania

W PDF zadania **w pliku `problem.pddl` są literówki w nawiasach:**
- Linijka 1: `define ( problem move-balls )` — brak otwierającego `(`
- Linijka 29: dodatkowy nawias zamykający `)`

Poprawiona wersja jest w moim `problem.pddl`. Reszta dokładnie jak w treści.

## Wygenerowany plan

```
1.  (pick-up robot arm2 ball2 room1)
2.  (pick-up robot arm1 ball4 room1)
3.  (move robot room1 room2)
4.  (put-down robot arm2 ball2 room2)
5.  (put-down robot arm1 ball4 room2)
6.  (move robot room2 room1)
7.  (pick-up robot arm2 ball1 room1)
8.  (pick-up robot arm1 ball3 room1)
9.  (move robot room1 room2)
10. (put-down robot arm2 ball1 room2)
11. (put-down robot arm1 ball3 room2)
```

**11 akcji.**

## Analiza planu

### Co robi robot

Plan ma logiczną strukturę: **dwie wycieczki, w każdej po 2 piłki**.

- Wycieczka 1 (akcje 1-5): bierze ball2 i ball4, idzie do room2, kładzie obie.
- Wraca do room1 (akcja 6).
- Wycieczka 2 (akcje 7-11): bierze ball1 i ball3, idzie do room2, kładzie obie.

### Dlaczego 11 akcji?

Robot ma **2 ramiona**, więc w jednej wycieczce przenosi **2 piłki**. 4 piłki = 2 wycieczki.

Każda wycieczka: 2× pick-up + 1× move + 2× put-down = **5 akcji**.
Plus 1× move powrotu między wycieczkami.

`2 × 5 + 1 = 11 akcji.`

Optymalne — mniej się nie da. Gdyby robot miał **1 ramię**, plan miałby:
- 4 wycieczki × (1 pick + 1 move + 1 put) = 12 akcji + 3 powroty = **15 akcji.**

A gdyby miał **4 ramiona** — 1 wycieczka:
- 4× pick + 1× move + 4× put = **9 akcji** (najlepszy możliwy wynik).

To pokazuje że **liczba ramion liniowo wpływa na plan**.

### Dlaczego planer wybrał akurat takie piłki w takich ramionach?

`ball2 → arm2`, `ball4 → arm1`, `ball1 → arm2`, `ball3 → arm1`.

To **arbitralne** — z punktu widzenia planera wszystkie piłki i ramiona są wymienne. Heurystyka po prostu wzięła to co znalazła pierwsze. Inny planer (albo inna heurystyka) mógłby zwrócić plan z piłkami w innej kolejności, ale o tej samej długości.

## Jak uruchomić

### Edytor online

1. **https://editor.planning.domains/**
2. Wklej `domain.pddl` i `problem.pddl`
3. **Solve** → np. *LAMA-2011*

### Pyperplan lokalnie

```bash
pyperplan -H hff -s astar domain.pddl problem.pddl
cat problem.pddl.soln
```

## Pliki

| Plik | Co to jest |
|---|---|
| `domain.pddl` | Domena z treści zadania |
| `problem.pddl` | Problem z treści zadania (z poprawionymi nawiasami) |
| `plan.txt` | Wygenerowany plan (11 akcji) |
| `raport.md` | Krótkie sprawozdanie |
