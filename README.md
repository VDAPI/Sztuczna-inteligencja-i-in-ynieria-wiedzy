# Sztuczna inteligencja i inżynieria wiedzy

Rozwiązania list laboratoryjnych z przedmiotu **Sztuczna inteligencja i inżynieria wiedzy** (SIiIW)
wraz z moimi raportami.

**Autor:** Dawid Pilarski

## Uwaga o treściach zadań

W repozytorium **nie zamieszczam oryginalnych treści list** (PDF-ów z poleceniami) — są to
materiały dydaktyczne prowadzących i podlegają ich prawom autorskim. Zamiast tego w każdym
folderze `Lista N/` znajduje się `README.md` z **moim własnym streszczeniem** tego, co należało
zrobić, oraz opisem rozwiązania. Udostępniam wyłącznie **swój kod** i **swoje raporty**.

## Spis list

| Lista | Temat | Kluczowe metody | Rozwiązanie | Raport |
|------:|-------|-----------------|:-----------:|:------:|
| [1](./Lista%201) | Wyszukiwanie połączeń w rozkładzie kolejowym (GTFS) | Dijkstra, A\*, Tabu Search (TSP) | ✅ | ✅ |
| [2](./Lista%202) | Gra dwuosobowa *Breakthrough* | Minimax, przycinanie alfa-beta | ⏳ *(do uzupełnienia)* | ✅ |
| [3](./Lista%203) | Planowanie działań w PDDL | STRIPS, planery heurystyczne (hFF, hmax) | ✅ | ✅ |
| [4](./Lista%204) | Klasyfikacja przeżywalności (marskość wątroby) | Naive Bayes, drzewa decyzyjne, RF/SVM | ✅ | ✅ |
| [5](./Lista%205) | Klasyfikacja sentymentu PolEmo2.0 | encoder (HerBERT) vs decoder-LLM (Qwen) | ✅ | ✅ |

## Struktura repozytorium

Każdy folder listy ma spójny układ:

```
Lista N/
├── README.md       ← moje streszczenie zadania + opis rozwiązania i jak je uruchomić
├── raport.pdf      ← mój raport oddany na zajęcia
└── rozwiazanie/    ← kod / pliki rozwiązania (z własnym README, jeśli projekt tego wymaga)
```

> **Status Listy 2:** brakuje jeszcze kodu rozwiązania — zostanie dograny po odnalezieniu.
> Na razie dostępny jest raport i opis zadania.
