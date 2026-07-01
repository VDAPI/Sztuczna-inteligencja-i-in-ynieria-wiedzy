# Sprawozdanie – Lista 3, Zadanie 1 (PDDL, transport paczek)

**Autor:** Dawid Pilarski
**Kurs:** Sztuczna Inteligencja i Inżynieria Wiedzy (SIiIW)
**Planer:** Pyperplan 2.1 (A\* / GBF / BFS) + Fast Downward (dla wersji z kosztami)

---

## 1. Opis problemu

Zadanie polega na zaplanowaniu transportu paczek pomiędzy lokacjami w środowisku **multi-modalnym**: równolegle dostępne są trzy infrastruktury – **drogowa** (`truck`), **lotnicza** (`plane`) i **morska** (`ship`). Każdy typ pojazdu może poruszać się **wyłącznie** po swojej sieci połączeń, co modeluję trzema niezależnymi predykatami statycznymi (`road-connected`, `air-connected`, `water-connected`).

### Scenariusz testowy

```
                 (drogi)              (woda)              (drogi)
   warehouse ──────────── portA ════════════ portB ──────────── shop
        │                                                          │
        │           (drogi)        (powietrze)         (drogi)     │
        └──────── airportA ─────────────────── airportB ───────────┘
```

- **3 paczki**: `pkg1`, `pkg2` w `warehouse`, `pkg3` w `portA`.
- **6 pojazdów**: 4 ciężarówki rozstawione strategicznie + 1 statek w `portA` + 1 samolot w `airportA`.
- **Cel**: dostarczyć wszystkie 3 paczki do `shop`.

### Modelowanie

Domena używa rozszerzeń:

| Rozszerzenie | Wykorzystanie |
|---|---|
| `:strips` | Klasyczne preconditions/effects |
| `:typing` | Hierarchia: `vehicle` → `truck` / `plane` / `ship` |
| `:negative-preconditions` | Negatywne efekty (np. `(not (at-veh ?v ?from))`) |
| `:action-costs` (wersja rozszerzona) | Numeryczne koszty zależne od pary lokacji |

Pięć akcji: `load`, `unload`, `drive` (truck), `fly` (plane), `sail` (ship). Hierarchia typów wymusza separację – nie da się np. zastosować akcji `fly` do ciężarówki.

---

## 2. Plan wygenerowany przez planer

### 2.1. Wersja STRIPS, A\* + h<sub>max</sub> (heurystyka dopuszczalna → plan optymalny)

```
1.  (load pkg2 truck1 warehouse)
2.  (load pkg1 truck1 warehouse)
3.  (drive truck1 warehouse porta)
4.  (unload pkg2 truck1 porta)
5.  (unload pkg1 truck1 porta)
6.  (load pkg2 ship1 porta)
7.  (load pkg1 ship1 porta)
8.  (load pkg3 ship1 porta)
9.  (sail ship1 porta portb)
10. (unload pkg2 ship1 portb)
11. (unload pkg1 ship1 portb)
12. (unload pkg3 ship1 portb)
13. (load pkg2 truck2 portb)
14. (load pkg1 truck2 portb)
15. (load pkg3 truck2 portb)
16. (drive truck2 portb shop)
17. (unload pkg2 truck2 shop)
18. (unload pkg1 truck2 shop)
19. (unload pkg3 truck2 shop)
```

**Długość planu: 19 akcji.** Planer wybrał trasę morską (`portA → portB`) i konsolidował transport – jedna ciężarówka zwozi paczki z magazynu, statek przewozi całość przez morze, druga ciężarówka odbiera w `portB` i dostarcza do sklepu.

---

## 3. Eksperymenty

### 3.1. Porównanie strategii wyszukiwania i heurystyk

| Konfiguracja | Długość planu | Węzły rozwinięte | Czas |
|---|---:|---:|---:|
| A\* + h<sub>FF</sub> (niedopuszczalna) | 20 | 23 | 0.038 s |
| A\* + h<sub>max</sub> (dopuszczalna) | **19** (optymalny) | **90 500** | **140 s** |
| GBF + h<sub>FF</sub> | 19 | 20 | 0.030 s |
| BFS (blind) | 19 (optymalny) | 389 965 | 20 s |

**Obserwacje:**

- **A\* + h<sub>max</sub>** gwarantuje optymalność, ale eksploduje kombinatorycznie: 90 500 węzłów vs 23 dla h<sub>FF</sub> – ponad **3 900× więcej**. W czasie absolutnym różnica to 4 sekundy → 140 sekund (≈3700×).
- **GBF + h<sub>FF</sub>** trafił optymalny plan "przypadkiem" – greedy nie gwarantuje optymalności, ale heurystyka FF była tu wystarczająco precyzyjna.
- **BFS** w STRIPS z jednostkowymi kosztami akcji zawsze daje plan optymalny pod względem długości, ale eksploruje 400k węzłów – ślepa eksploracja jest nieopłacalna nawet w małym problemie.
- **Trade-off jest klasyczny**: optymalność kosztuje wykładniczo więcej pracy. Dla tego problemu praktycznie najlepszy jest **GBF + h<sub>FF</sub>** (najszybszy, plan suboptymalny tylko o 1 akcję).

### 3.2. Wpływ topologii: zerwanie szlaku morskiego

Drugi wariant problemu (`problem_no_water.pddl`) różni się tylko brakiem faktów `(water-connected portA portB)`. Wszystko inne identyczne.

| Wariant | Długość planu | Trasa | Czas (A\*+h<sub>FF</sub>) |
|---|---:|---|---:|
| Pełna topologia | 20 | przez morze (`sail`) | 0.038 s |
| Bez wody | **23** | przez powietrze (`fly`) | 0.044 s |

Plan w wariancie bez wody (skrót):

```
load pkg1, pkg2 → truck1 (warehouse)
drive truck1 warehouse → porta              ← truck musi pojechać po pkg3
load pkg3 → truck1
drive truck1 porta → warehouse → airporta   ← nadkładanie drogi
unload + load wszystkie 3 paczki → plane1
fly plane1 airporta → airportb
unload + load wszystkie 3 → truck3
drive truck3 airportb → shop
unload × 3
```

**Wnioski:** zerwanie jednego połączenia w grafie transportu wymusza:
1. Zmianę środka transportu (statek → samolot).
2. **Nadkładanie drogi**: pkg3 startuje w `portA`, więc ciężarówka musi tam pojechać, wrócić, i pojechać do `airportA` – dodatkowe 2 akcje `drive`.
3. Wzrost długości planu o 15% (20 → 23).

Pokazuje to, że **topologia siatki transportowej ma większy wpływ niż wybór heurystyki** – złe rozmieszczenie połączeń zwiększa koszt znacznie bardziej niż suboptymalność heurystyki (15% vs 5%).

### 3.3. Wersja rozszerzona z kosztami numerycznymi

W pliku `domain_costs.pddl` zdefiniowano funkcje numeryczne:
- `(road-cost ?l1 ?l2)` – koszt drogowy
- `(water-cost ?l1 ?l2)` – koszt morski (najtańszy: 5)
- `(air-cost ?l1 ?l2)` – koszt lotniczy (najdroższy: 30)

Planer minimalizuje `(total-cost)`. Pyperplan tego nie wspiera (brak `:functions`), ale Fast Downward (`astar(lmcut())`) lub edytor online z planerem optymalnym pokaże, że:

- **Plan przez morze** ma koszt: 10 (drive)+ 5 (sail) + 10 (drive) + 19 (akcje load/unload) = **44**.
- **Plan przez samolot** ma koszt: 8 + 30 + 8 + 19 = **65**.

Różnica ~30% w koszcie – mimo tej samej długości w akcjach (gdyby paczki pkg3 nie było w `portA`).

---

## 4. Wnioski

1. **Hierarchia typów pojazdów** w PDDL elegancko modeluje multi-modalność – nie trzeba mnożyć akcji `move` ze warunkami "jeśli pojazd-to-ciężarówka-to-droga...". Wystarczą trzy proste akcje `drive`/`fly`/`sail` parametryzowane podtypem.

2. **Heurystyki niedopuszczalne (h<sub>FF</sub>) są praktyczne**: zwykle dają plany 5–10% gorsze, ale o rzędy wielkości szybciej niż dopuszczalne. W produkcji "dobrze wystarczy" wygrywa z "perfekcyjnie".

3. **Topologia dominuje koszt**: zmiana grafu połączeń wpływa na plan silniej niż wybór algorytmu. Modelowanie sieci transportowej (gdzie postawić port, gdzie lotnisko) jest decyzją projektową krytyczniejszą niż dobór planera.

4. **Akcje `load`/`unload` są kosztem nieusuwalnym**: w optymalnym planie 19 akcji aż 12 to load/unload (po 4 razy na paczkę: warehouse→truck, truck→ship, ship→truck, truck→shop, ale jeden raz pkg3 omija pierwszy etap). Multi-modalność płaci się przeładunkami – im więcej środków transportu w łańcuchu, tym więcej akcji obsługowych.

5. **Optymalizacja długości vs koszt**: wersja STRIPS optymalizuje liczbę akcji, wersja z `:action-costs` minimalizuje sumę kosztów. To **różne plany** w tym problemie – dlatego rozszerzenie o numeric fluents jest niezbędne, żeby model odpowiadał rzeczywistemu logistycznemu trade-offowi (statek wolny ale tani vs samolot szybki ale drogi).

---

## 5. Pliki .pddl

- `domain.pddl` – domena STRIPS
- `problem.pddl` – problem główny (3 paczki, pełna topologia)
- `problem_no_water.pddl` – wariant bez trasy morskiej
- `domain_costs.pddl` – domena rozszerzona o `:action-costs`
- `problem_costs.pddl` – problem z numerycznymi kosztami

### Uruchomienie

```bash
# Pyperplan (STRIPS, dostępny przez pip)
pyperplan -H hff -s astar domain.pddl problem.pddl

# Fast Downward (z kosztami)
fast-downward.py domain_costs.pddl problem_costs.pddl --search "astar(lmcut())"

# Online editor
# https://editor.planning.domains  → wklej oba pliki → Solve
```
