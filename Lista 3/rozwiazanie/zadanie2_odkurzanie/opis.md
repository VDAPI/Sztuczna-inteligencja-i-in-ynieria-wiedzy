# Zadanie 2 — Robot odkurzający

## O co chodzi w zadaniu

Z treści listy (15 pkt): napisz `domain.pddl` i `problem.pddl` dla robota, który ma odwiedzić wszystkie pokoje i je odkurzyć. Treść daje gotowe predykaty i akcje, trzeba je zaimplementować.

## Specyfikacja z zadania (dosłownie z listy)

**Obiekty:**
- robot: `robot`
- pokoje: `pokoj1`, `pokoj2`, `pokoj3`

**Predykaty:**
- `(at ?r - robot ?p - room)` — robot znajduje się w pokoju
- `(dirty ?p - room)` — pokój jest brudny
- `(clean ?p - room)` — pokój jest czysty

**Akcje:**
- `move` — przemieszcza robota między pokojami
- `clean` — sprząta aktualny pokój

**Cel:** `(and (clean pokoj1) (clean pokoj2) (clean pokoj3))`

## Jak to zaimplementowałem

### Akcja `move`

```
(:action move
    :parameters (?r - robot ?from - room ?to - room)
    :precondition (at ?r ?from)
    :effect (and (not (at ?r ?from))
                 (at ?r ?to))
)
```

**Decyzja projektowa:** robot może przejść między **dowolnymi** pokojami (brak predykatu `connected`). Treść tego nie precyzuje, a model z zadania 3 też używa wolnego ruchu — więc dla spójności robię tak samo.

Gdyby trzeba było ograniczyć ruch do sąsiednich pokojów, dodałbym predykat `(connected ?r1 ?r2)` w precondition (jak w zadaniu 1).

### Akcja `clean`

```
(:action clean
    :parameters (?r - robot ?p - room)
    :precondition (and (at ?r ?p) (dirty ?p))
    :effect (and (not (dirty ?p))
                 (clean ?p))
)
```

**Decyzja projektowa:** wymagam `(dirty ?p)` w precondition. Bez tego robot mógłby "czyścić" pokój, który już jest czysty (akcja bezsensowna, ale planer mógłby ją wstawić, marnując kroki). Dirty/clean wzajemnie się wykluczają.

## Init i goal

- Robot startuje w `pokoj1`
- Wszystkie 3 pokoje są brudne na start
- Cel: wszystkie 3 czyste

## Wygenerowany plan

```
(clean rumba pokoj1)
(move rumba pokoj1 pokoj3)
(clean rumba pokoj3)
(move rumba pokoj3 pokoj2)
(clean rumba pokoj2)
```

**5 akcji** = 3× clean + 2× move. To **optymalne** — żeby posprzątać 3 pokoje trzeba je odwiedzić, a robot startuje już w jednym. Minimum: 3 sprzątania + 2 przejścia.

Ciekawe: planer wybrał kolejność `pokoj1 → pokoj3 → pokoj2`, a nie `1 → 2 → 3`. To **bez znaczenia** — bez kosztów drogi obie kolejności są równie dobre. Planer wybiera pierwszą znalezioną.

## Jak uruchomić

### Edytor online

1. **https://editor.planning.domains/**
2. Wklej `domain.pddl` i `problem.pddl`
3. **Solve** → wybierz dowolny planer

### Pyperplan lokalnie

```bash
pip install pyperplan
pyperplan -H hff -s astar domain.pddl problem.pddl
cat problem.pddl.soln
```

## Możliwe rozszerzenia (jeśli chcesz więcej punktów)

Można dorzucić:
- **Predykat połączeń** `(connected ?r1 ?r2)` — robot porusza się tylko między sąsiednimi pokojami
- **Bateria** `(:functions (battery-level))` — sprzątanie i ruch zużywa baterię, robot musi się ładować
- **Więcej pokojów** — 5, 10, 20 — i porównanie czasu planowania
- **Wiele robotów** — kilka robotów Roomba, które dzielą pracę

Zostawiam podstawową wersję bo zadanie nie wymaga rozszerzeń.

## Pliki

| Plik | Co to jest |
|---|---|
| `domain.pddl` | Definicja domeny (typy, predykaty, akcje move/clean) |
| `problem.pddl` | Scenariusz: 3 brudne pokoje, robot w pokoj1 |
| `plan.txt` | Wygenerowany plan (5 akcji) |
| `raport.md` | Krótkie sprawozdanie z analizą |
