# Zadanie 1 — Transport paczek

## O co chodzi w zadaniu

Z treści listy: zaprojektuj plan transportu paczek w PDDL, użyj **rozszerzeń** (typing, koszty, durative-actions, multi-modalność), uruchom planer, przeanalizuj plan (długość, koszt, wpływ topologii).

To największe zadanie z listy (25 pkt) i ma być **otwarte** — sam wymyślasz scenariusz.

## Co zrobiłem

**Scenariusz:** transport 3 paczek z magazynu do sklepu w środowisku **multi-modalnym** — równolegle dostępne są trzy infrastruktury transportu:
- **drogowa** (ciężarówki)
- **lotnicza** (samolot, między lotniskami)
- **morska** (statek, między portami)

Każdy typ pojazdu może poruszać się wyłącznie po swojej sieci (ciężarówka po drogach, samolot powietrzem itd.).

**Topologia:**
```
                 (drogi)              (woda)              (drogi)
   warehouse ──────────── portA ════════════ portB ──────────── shop
        │                                                          │
        │           (drogi)        (powietrze)         (drogi)     │
        └──────── airportA ─────────────────── airportB ───────────┘
```

Paczki `pkg1`, `pkg2` startują w `warehouse`, `pkg3` startuje w `portA`. Cel: wszystkie 3 w `shop`. Planer musi sam zdecydować: jechać przez morze czy przez lotnisko?

## Jak działa domena

Klucz to **hierarchia typów**. Definiuję:
```
(:types
    package vehicle location - object
    truck plane ship - vehicle
)
```

A potem mam 3 osobne akcje ruchu — `drive` przyjmuje tylko `truck`, `fly` tylko `plane`, `sail` tylko `ship`:
```
(:action drive
    :parameters (?t - truck ?from - location ?to - location)
    :precondition (and (at-veh ?t ?from) (road-connected ?from ?to))
    ...
)
```

Hierarchia typów wymusza separację — **nie da się zastosować `fly` do ciężarówki**, bo parametr `?pl - plane` przyjmuje tylko obiekty typu `plane`. PDDL pilnuje tego sam, bez kombinatorycznych warunków typu "jeśli pojazd to ciężarówka i jest droga...".

## Pliki

| Plik | Co to jest |
|---|---|
| `domain.pddl` | Domena STRIPS (bez kosztów liczbowych). Odpalisz w pyperplanie. |
| `problem.pddl` | Główny scenariusz z 3 paczkami. |
| `problem_no_water.pddl` | Wariant **bez połączenia morskiego** — do eksperymentu z topologią. |
| `domain_costs.pddl` | **Rozszerzona** domena z `:action-costs` — koszty drogi/wody/powietrza są liczbowe. Wymaga Fast Downward lub edytora online. |
| `problem_costs.pddl` | Problem do wersji z kosztami (woda = tania, lot = drogi). |
| `plan_hff.txt` | Plan z A* + heurystyką hFF (20 akcji, szybki). |
| `plan_hmax.txt` | Plan z A* + heurystyką hmax (19 akcji, optymalny). |
| `plan_no_water.txt` | Plan dla wariantu bez wody (23 akcje). |
| `raport.md` | Pełne sprawozdanie z analizą. |

## Jak uruchomić

### Wariant A: edytor online (najszybciej)

1. Wejdź na **https://editor.planning.domains/**
2. Wklej `domain.pddl` do pola "Domain"
3. Wklej `problem.pddl` do pola "Problem"
4. Kliknij **Solve** → wybierz np. *LAMA-2011* lub *Optimal Planner*
5. Zrób screenshot planu

Powtórz z `problem_no_water.pddl` — zobaczysz **dłuższy plan**, bo planer musi użyć samolotu.

Dla wersji z kosztami — wklej `domain_costs.pddl` + `problem_costs.pddl`, wybierz *Optimal Planner*.

### Wariant B: pyperplan lokalnie

```bash
pip install pyperplan

# Plan suboptymalny ale szybki (0.04s)
pyperplan -H hff -s astar domain.pddl problem.pddl

# Plan optymalny (140s — uwaga, długo!)
pyperplan -H hmax -s astar domain.pddl problem.pddl

# Wariant bez wody
pyperplan -H hff -s astar domain.pddl problem_no_water.pddl
```

Wynik zapisuje się jako `problem.pddl.soln` w katalogu.

**Uwaga:** pyperplan **nie obsługuje** plików `*_costs.pddl` (brak `:functions`). Dla nich użyj edytora online albo Fast Downward.

## Czego się dowiedziałem (najważniejsze wnioski)

1. **Z wodą plan ma 19 akcji, bez wody 23.** Sama zmiana topologii (usunięcie jednej krawędzi w grafie) zwiększa plan o 21%. To pokazuje, że projekt sieci transportowej dominuje nad wyborem algorytmu.

2. **Planer wybiera morze.** Mimo że samolot też jest dostępny, statek już stoi w `portA` razem z `pkg3` — krócej go użyć niż wozić paczki do lotniska.

3. **Optymalne vs szybkie:** A* z hFF (niedopuszczalna heurystyka) znajduje plan 20 w 0.04s. A* z hmax (dopuszczalna) znajduje plan 19 w 140s. Cena za optymalność: 3500× wolniej.

4. **Z kosztami liczbowymi to inny problem.** Bez kosztów planer minimalizuje **liczbę akcji**. Z kosztami minimalizuje **sumę kosztów**. To może dać **różne plany** — szybka trasa lotnicza vs tania morska.

Wszystko rozpisane w `raport.md`.
