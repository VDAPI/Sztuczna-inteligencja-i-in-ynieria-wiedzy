# Lista 3 – Planowanie z wykorzystaniem PDDL

**Kurs:** Sztuczna Inteligencja i Inżynieria Wiedzy (SIiIW)
**Autor:** Dawid Pilarski

---

## Struktura paczki

```
lab3_pddl/
├── README.md                ← TEN PLIK (jak czytać, jak uruchomić, co gdzie)
├── jak_dziala_pddl.md       ← WSTĘP: co to PDDL, składnia, jak działa planer
│
├── zadanie1_transport/      (25 pkt)
│   ├── opis.md              ← opis zadania, co zrobiłem, decyzje projektowe
│   ├── raport.md            ← pełne sprawozdanie z analizą
│   ├── domain.pddl          ← domena STRIPS
│   ├── problem.pddl         ← główny scenariusz (3 paczki)
│   ├── problem_no_water.pddl ← wariant bez połączenia morskiego (eksperyment)
│   ├── domain_costs.pddl    ← rozszerzona domena z :action-costs
│   ├── problem_costs.pddl   ← problem z kosztami liczbowymi
│   ├── plan_hff.txt         ← plan z A* + hFF (20 akcji)
│   ├── plan_hmax.txt        ← plan optymalny z A* + hmax (19 akcji)
│   └── plan_no_water.txt    ← plan dla wariantu bez wody (23 akcje)
│
├── zadanie2_odkurzanie/     (15 pkt)
│   ├── opis.md
│   ├── raport.md
│   ├── domain.pddl
│   ├── problem.pddl
│   └── plan.txt             ← 5 akcji
│
└── zadanie3_pilki/          (10 pkt)
    ├── opis.md
    ├── raport.md
    ├── domain.pddl          ← z treści zadania
    ├── problem.pddl         ← z treści zadania (poprawione nawiasy)
    └── plan.txt             ← 11 akcji
```

## Po co kolejne pliki

| Plik | Kogo dotyczy | Co znajdziesz |
|---|---|---|
| `jak_dziala_pddl.md` | **Przeczytaj najpierw** | Co to PDDL, jak czytać `domain.pddl`/`problem.pddl`, jak uruchomić planer |
| `zadanieN/opis.md` | Zrozumienie zadania | Treść zadania, co zrobiłem, kluczowe decyzje, jak uruchomić |
| `zadanieN/raport.md` | Do oddania | Sprawozdanie z analizą — to jest to co ma znaleźć się w finalnym dokumencie |
| `zadanieN/*.pddl` | Do oddania | Pliki kodu PDDL |
| `zadanieN/plan*.txt` | Do oddania (zrzut planu) | Wygenerowane plany |

## Jak uruchomić któreś zadanie — najprościej

1. Wejdź na **https://editor.planning.domains/**
2. Otwórz plik `domain.pddl` z danego zadania, **skopiuj całą zawartość**, wklej do lewego pola edytora ("Domain")
3. To samo z `problem.pddl` → prawe pole ("Problem")
4. Klik **Solve** u góry, wybierz planer:
   - **LAMA-2011** — szybki, sub-optymalny (dobry domyślny)
   - **Optimal Planner** — gwarancja optymalności (wolniejszy)
5. Po 1-3 sek zobaczysz plan
6. **Zrób screenshot do sprawozdania**

Bez żadnej instalacji. Tylko przeglądarka.

## Jak uruchomić lokalnie (opcjonalnie)

```bash
# Zainstaluj raz
pip install pyperplan

# Odpal któreś zadanie
cd zadanie2_odkurzanie
pyperplan -H hff -s astar domain.pddl problem.pddl

# Plan zapisuje się do problem.pddl.soln
cat problem.pddl.soln
```

**Uwaga:** pyperplan **nie obsługuje** plików `*_costs.pddl` z zadania 1 (brak wsparcia dla `:functions`). Dla tych użyj edytora online albo Fast Downward.

## Status zadań

| Zadanie | Punkty | Status | Długość planu |
|---|---:|---|---:|
| 1. Transport paczek | 25 | ✓ gotowe (3 warianty problemu, wersja z kosztami) | 19/20/23 |
| 2. Robot odkurzający | 15 | ✓ gotowe | 5 |
| 3. Robot z piłkami | 10 | ✓ gotowe | 11 |

## Workflow do złożenia sprawozdania

Lista wymaga: **opis problemu + zrzut planu + analiza eksperymentów + wnioski + pliki .pddl**.

Dla każdego zadania:

1. Skopiuj treść `zadanieN/raport.md` do swojego sprawozdania (Word/PDF)
2. Uruchom `domain.pddl` + `problem.pddl` w editor.planning.domains, **zrób screenshot planu**
3. Wklej screenshot do sprawozdania
4. Załącz pliki `.pddl` (na końcu albo jako załącznik)

Zadanie 1 dodatkowo: powtórz krok 2 dla `problem_no_water.pddl` (eksperyment z topologią) i dla wersji z kosztami.

---

**Zacznij od `jak_dziala_pddl.md`** — to wprowadzenie do języka, bez którego pliki PDDL wyglądają jak abrakadabra.
