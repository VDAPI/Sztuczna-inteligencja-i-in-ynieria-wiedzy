# SIiIW — Lista 4: Klasyfikacja przeżywalności w marskości wątroby

Projekt na przedmiot **Sztuczna inteligencja i inżynieria wiedzy**. Klasyfikacja wieloklasowa (3 klasy) na zbiorze UCI „Cirrhosis Patient Survival Prediction".

## Szybki start

```bash
# 1. zależności
pip install -r requirements.txt --break-system-packages   # lub w venv

# 2. dane — patrz data/README.md (ucimlrepo automatycznie albo lokalny CSV)
python -m src.load_data        # sprawdza wczytanie, drukuje raport braków

# 3. baseline (NB + drzewo), zapis metryk do results/
python -m src.run_all
```

## Mapa plików

```
.
├── CLAUDE.md              # brief dla Claude Code + KLUCZOWE pułapki ML (czytaj najpierw)
├── PLAN.md                # plan fazowy zmapowany na punktację
├── requirements.txt
├── data/
│   └── README.md          # jak zdobyć zbiór danych
├── src/
│   ├── config.py          # stałe: kolumny, typy, RANDOM_STATE, ścieżki
│   ├── load_data.py        # wczytanie + czyszczenie (usuwa ID, N_Days)
│   ├── explore.py          # Faza 1: EDA            (10 pkt)
│   ├── preprocess.py       # Faza 2: braki + pipeline'y przetwarzania (30 pkt)
│   ├── classify.py         # Faza 3: NB, drzewo, strojenie, bonusy
│   ├── evaluate.py         # Faza 4: metryki + interpretacja (20 pkt)
│   └── run_all.py          # orkiestrator / spine
├── results/               # generowane CSV + PNG (tabele i wykresy do raportu)
└── report/
    └── raport_szablon.md  # szablon raportu PO POLSKU (do wypełnienia)
```

## Workflow z Claude Code

1. Otwórz repo w CC, poproś o przeczytanie `CLAUDE.md` i `PLAN.md`.
2. Idź fazami z `PLAN.md`. Spine (`run_all.py`) już działa jako baseline — rozbudowuj.
3. Tam, gdzie w kodzie/raporcie jest `# TODO (Dawid)` — to miejsca na Twoje własne decyzje i interpretacje (to praca zaliczeniowa, wnioski piszesz sam).

## Zbiór danych

Dickson, E., Grambsch, P., Fleming, T., Fisher, L., & Langworthy, A. (1989). *Cirrhosis Patient Survival Prediction* [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5R02G
