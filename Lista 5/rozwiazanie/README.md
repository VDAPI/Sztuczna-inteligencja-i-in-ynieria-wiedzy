# Lista 5 - Klasyfikacja wydzwieku PolEmo2.0-IN (encoder vs decoder)

Porownanie klasyfikacji sentymentu na `allegro/klej-polemo2-in` (split `test`) przy uzyciu
modelu **encoder-only** (HerBERT) i **decoder-only LLM** (Qwen2.5). Klasyfikujemy do 3 klas
(`negative`, `neutral`, `positive`) - klasa `ambiguous` jest wyrzucana zgodnie z trescia listy.

## Struktura projektu

```
lista5_polemo/
├── src/
│   ├── config.py      # wszystkie "pokretla": modele, parametry, sciezki
│   ├── labels.py      # mapowanie etykiet tekstowych <-> kanoniczne id (punktowany haczyk)
│   ├── data.py        # ladowanie zbioru + statystyki + przygotowanie
│   ├── metrics.py     # Accuracy/F1, macierz pomylek, tabele wynikow
│   ├── encoder.py     # klasyfikacja encoderem (HerBERT)
│   ├── decoder.py     # klasyfikacja LLM (Qwen) + LangChain/JSON
│   └── utils.py       # seed, sprzatanie pamieci, info o GPU
├── Lista5_PolEmo.ipynb  # notebook pod Colab (importuje src/)
├── run.py             # CLI: odpala caly pipeline bez notebooka
├── RAPORT.md          # szablon raportu (uzupelnij wyniki [WPISZ])
├── requirements.txt
└── README.md
```

Logika siedzi w `src/` (jedno zrodlo prawdy). Notebook i `run.py` tylko ja wolaja - dzieki
temu wygodnie pracuje sie z tym w Claude Code.

## Uruchomienie

### A) Google Colab (zalecane - darmowe GPU)

1. Wlacz GPU: **Runtime -> Change runtime type -> T4 GPU**.
2. Otworz `Lista5_PolEmo.ipynb` w Colab.
3. Wgraj projekt jednym z trzech sposobow:
   - **src obok notebooka:** wrzuc caly folder `lista5_polemo/` na Colab (panel plikow),
   - **zip:** wgraj `lista5_polemo.zip` - komorka `ensure_src()` sama go rozpakuje,
   - **git:** `!git clone <twoje-repo>` i ustaw sciezke.
4. Odpalaj komorki po kolei. Setup (sekcja 0) doinstaluje zaleznosci.

### B) Lokalnie / inny serwer z GPU

```bash
pip install -r requirements.txt
python run.py --task all                    # caly pipeline, caly zbior testowy
python run.py --task all --max-samples 200  # szybka iteracja na 200 probkach
python run.py --task 4 --llm Qwen/Qwen2.5-3B-Instruct --use-4bit
python run.py --task 2 --encoder Voicelab/herbert-base-cased-sentiment
```

Wyniki laduja w `outputs/`: `wyniki.csv`, `wyniki.md` oraz macierze pomylek (PNG).

> Bez GPU to zadziala, ale LLM bedzie **bardzo** wolny. Na CPU mocno ogranicz `--max-samples`.

## Konfiguracja (`src/config.py`)

Najwazniejsze pokretla:

- `MAX_SAMPLES` - `None` = caly zbior. Na iteracje ustaw `150-200`, do finalnego raportu wroc do `None`.
- `DEFAULT_ENCODER`, `ENCODER_MODELS` - modele encoder do baseline i eksploracji.
- `DEFAULT_LLM`, `LLM_MODELS` - modele LLM.
- `USE_4BIT` - kwantyzacja 4-bit dla LLM (wymaga `bitsandbytes`); ratuje VRAM przy wiekszych modelach.
- `LLM_MAX_NEW_TOKENS`, `LLM_BATCH`, `ENCODER_BATCH` - dlugosc generacji i rozmiary batchy.

## Jak wypelnic raport

1. Uruchom notebook (albo `run.py --task all`).
2. Przepisz liczby z komorek / z `outputs/wyniki.csv` do `RAPORT.md` w miejsca `[WPISZ]`.
3. Uzupelnij sekcje interpretacji (`_Interpretacja:_`) wlasnymi wnioskami.
4. **Nie zmyslaj liczb** - wpisuj tylko realne wyniki uruchomienia.

Raport wyslij prowadzacemu min. 24h przed oddaniem (wymog z tresci listy).

## Troubleshooting

- **`load_dataset` rzuca blad o skryptach / `trust_remote_code`** - nowe `datasets` (3.x)
  usunelo wsparcie dla skryptowych zbiorow. Zainstaluj starsza wersje:
  ```bash
  pip install "datasets<3.0"
  ```
- **Out of memory (CUDA OOM)** - zmniejsz `LLM_BATCH`, ustaw `USE_4BIT=True`, albo obnizaj
  `MAX_SAMPLES`. Wiekszy model (3B) prawie na pewno wymaga 4-bit na T4.
- **Rozklad klas w `test` wyglada zdegenerowanie** (np. wszystko jedna klasa) - sprawdz w
  zadaniu 1, co pokazuje `describe_raw` (`class_counts_raw`). Jezeli etykiety wygladaja na
  ukryte/puste w `test`, sprobuj `split="validation"` lub `split="train"` (zmien `SPLIT`
  w `config.py`) i opisz to w raporcie.
- **LLM zwraca smieci zamiast etykiety** - zobacz `n_unparsed`. Sprobuj promptu `pl_fewshot`
  lub `json` (zadanie 5a) - zwykle mocno redukuja liczbe nieparsowalnych odpowiedzi.
- **Encoder ma dziwne mapowanie klas** - `build_model_label_map` czyta `model.config.id2label`
  i wypisuje ostrzezenia, gdy trafi na nietypowe etykiety (`LABEL_0` itp.). Sprawdz wydruk
  mapy w komorce zadania 2.

## Uwagi metodyczne

- **Temperatura dotyczy tylko LLM.** Encoder robi deterministyczny forward pass - nie ma tam
  samplingu, wiec temperatura nie ma zastosowania (eksploracja encodera = porownanie modeli).
- Zbior bywa niezbalansowany, dlatego patrzymy na **F1 macro**, nie tylko accuracy.
- Mapowanie etykiet jest osobno punktowane - patrz `src/labels.py`.
