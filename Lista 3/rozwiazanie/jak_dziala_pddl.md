# Jak działa PDDL — szybki wstęp

## Co to w ogóle jest

**PDDL** (Planning Domain Definition Language) to język do opisu **problemów planowania**. Sam nie planujesz — opisujesz świat, a **planer** (gotowy program) wymyśla sekwencję akcji prowadzących do celu.

To trochę jak SQL: nie piszesz algorytmu, mówisz **co chcesz**, a silnik sam wymyśla **jak**.

## Z czego składa się każde zadanie PDDL

Zawsze masz **dwa pliki**:

### `domain.pddl` — opis świata (czym świat jest, jakie są reguły)

Składa się z 3 części:

**1. Typy** — kategorie obiektów. Przykład z transportu:
```
(:types
    package vehicle location - object
    truck plane ship - vehicle           ← truck/plane/ship to podtypy vehicle
)
```
Po polsku: "istnieją paczki, pojazdy i lokacje. Pojazdy dzielą się na ciężarówki, samoloty i statki."

**2. Predykaty** — fakty jakie mogą być prawdziwe.
```
(:predicates
    (at-pkg ?p - package ?l - location)   ← paczka jest w lokacji
    (in    ?p - package ?v - vehicle)     ← paczka jest w pojeździe
)
```
Po polsku: "fakt 'paczka P jest w lokacji L' istnieje". To są **schematy** — `?p` i `?l` to placeholdery.

**3. Akcje** — co da się zrobić.
```
(:action drive
    :parameters (?t - truck ?from - location ?to - location)
    :precondition (and (at-veh ?t ?from)
                       (road-connected ?from ?to))
    :effect      (and (not (at-veh ?t ?from))
                       (at-veh ?t ?to))
)
```
Po polsku: "Akcja `drive` bierze ciężarówkę, miejsce-skąd, miejsce-dokąd. Wymaga: ciężarówka jest w `from`, droga łączy `from` z `to`. Po wykonaniu: ciężarówka NIE jest już w `from`, JEST w `to`."

To wszystko. Każda akcja to **co musi być spełnione przed** + **co się zmieni po**.

### `problem.pddl` — konkretny scenariusz

Też 3 części:

**1. Obiekty** — konkretne rzeczy:
```
(:objects
    pkg1 pkg2 - package
    truck1    - truck
    warehouse shop - location
)
```

**2. Init** — co jest prawdą na początku:
```
(:init
    (at-pkg pkg1 warehouse)
    (at-veh truck1 warehouse)
    (road-connected warehouse shop)
)
```

**3. Goal** — co ma być prawdą na końcu:
```
(:goal (and (at-pkg pkg1 shop)))
```

Tyle. Planer dostaje oba pliki, czyta typy/predykaty/akcje, patrzy na init i goal, i sam wymyśla sekwencję akcji która z init prowadzi do goal.

## Jak to uruchomić

### Najprościej: edytor online

1. Wchodzisz na **https://editor.planning.domains/**
2. Wklejasz `domain.pddl` do lewego pola, `problem.pddl` do prawego
3. Klikasz **Solve** → wybierasz dowolny planer
4. Po 1-3 sekundach wyświetla plan

To wystarczy do zrobienia listy. Żadnej instalacji.

### Lokalnie: pyperplan (Python)

```bash
pip install pyperplan
pyperplan -H hff -s astar domain.pddl problem.pddl
```

Wynik zapisuje się do pliku `problem.pddl.soln`. Pyperplan jest prosty (czysto STRIPS, bez `:functions` czyli kosztów liczbowych) ale wystarczy do zadań 2 i 3.

### Pełne PDDL: Fast Downward

Najmocniejszy planer. Obsługuje wszystko (w tym koszty z zadania 1):
```bash
fast-downward.py domain.pddl problem.pddl --search "astar(lmcut())"
```

## Co czytasz w wyniku

Plan to **lista akcji w kolejności**. Każda linijka to jedna akcja z parametrami. Przykład:
```
(pick-up robot arm1 ball1 room1)
(move robot room1 room2)
(put-down robot arm1 ball1 room2)
```
To znaczy: "robot bierze ball1 ramieniem arm1 w pokoju 1, przechodzi do pokoju 2, kładzie ball1 ramieniem arm1 w pokoju 2".

## Co analizujesz w sprawozdaniu

1. **Długość planu** — ile akcji. Im mniej, tym lepiej.
2. **Czy plan jest sensowny** — czy nie ma marnotrawnych kroków (np. ruch tam i z powrotem bez powodu).
3. **Wpływ zmian w problemie** — np. usuwasz jakieś połączenie z `init` → jak zmienia się plan? Dodajesz przeszkodę → planer szuka obejścia?
4. **Heurystyki/strategie wyszukiwania** — np. A\* z różnymi heurystykami daje różne plany i różny czas. Tutaj można porównać `hff` vs `hmax`.

## Rozszerzenia PDDL użyte w tych zadaniach

| Rozszerzenie | Co dodaje | Gdzie używam |
|---|---|---|
| `:strips` | Bazowy model akcji | Wszystkie zadania |
| `:typing` | Typy obiektów (`?p - package`) | Wszystkie zadania |
| `:negative-preconditions` | Warunki typu "X NIE jest prawdą" | Zadanie 1, 2 |
| `:action-costs` | Koszty liczbowe akcji | Zadanie 1 (wersja `_costs`) |

---

**To wszystko czego potrzebujesz żeby zacząć.** Teraz przejdź do `zadanieN/opis.md` dla konkretnego zadania.
