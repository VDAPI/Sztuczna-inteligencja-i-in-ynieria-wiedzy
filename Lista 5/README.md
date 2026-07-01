# Lista 5 — Klasyfikacja sentymentu PolEmo2.0 (encoder vs decoder)

## O co chodziło (moje streszczenie)

Zadanie polegało na porównaniu dwóch podejść do **klasyfikacji wydźwięku (sentymentu)** tekstów
po polsku, na zbiorze **PolEmo2.0** (wariant `klej-polemo2-in`). Klasyfikujemy do trzech klas
(`negative`, `neutral`, `positive`); klasa `ambiguous` jest odrzucana zgodnie z treścią listy.

Porównywane modele:

- **encoder-only** — HerBERT (klasyfikacja przez deterministyczny forward pass),
- **decoder-only LLM** — Qwen2.5 (klasyfikacja przez odpowiedni prompt + parsowanie odpowiedzi,
  m.in. warianty few-shot i JSON, kwantyzacja 4-bit dla oszczędności VRAM).

Osobno punktowane było poprawne **mapowanie etykiet** modelu na kanoniczne klasy zbioru. Ze
względu na niezbalansowanie zbioru główną metryką jest **F1 macro**, nie sama dokładność.

Pełną treść polecenia pomijam (materiał prowadzących).

## Jak to rozwiązałem

Kod w [`rozwiazanie/`](./rozwiazanie) — cała logika w `src/` (jedno źródło prawdy), a notebook
`Lista5_PolEmo.ipynb` i skrypt `run.py` tylko ją wołają:

| Moduł | Rola |
|-------|------|
| `config.py` | parametry: modele, rozmiary batchy, ścieżki, `MAX_SAMPLES`, 4-bit |
| `labels.py` | mapowanie etykiet tekstowych ↔ kanoniczne id (punktowane) |
| `data.py` | wczytanie zbioru, statystyki, przygotowanie |
| `encoder.py` | klasyfikacja modelem encoder (HerBERT) |
| `decoder.py` | klasyfikacja LLM (Qwen) + prompty/JSON |
| `metrics.py` | Accuracy / F1 macro, macierz pomyłek, tabele wyników |

Uruchomienie (najlepiej na GPU, np. Colab T4):

```bash
cd rozwiazanie
pip install -r requirements.txt
python run.py --task all                    # cały pipeline na całym zbiorze testowym
python run.py --task all --max-samples 200  # szybka iteracja
```

Wyniki (CSV + macierze pomyłek PNG) trafiają do `rozwiazanie/outputs/`. Szczegóły konfiguracji i
troubleshooting w `rozwiazanie/README.md`.

## Raport

[`raport.pdf`](./raport.pdf) — porównanie obu podejść, wyniki liczbowe, macierze pomyłek,
interpretacja i wnioski.
