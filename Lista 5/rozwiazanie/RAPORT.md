# Raport - Lista 5: Klasyfikacja wydzwieku (PolEmo2.0-IN)

**Przedmiot:** Sztuczna inteligencja i inzynieria wiedzy
**Autor:** Dawid Pilarski
**Indeks:** 280468
**Data:** _[uzupelnij]_

> Wyniki liczbowe w tabelach oznaczone `[WPISZ]` uzupelnij po uruchomieniu notebooka /
> `run.py`. Metodyka, opis bibliotek i zrodla sa gotowe. **Nie wpisuj wynikow z palca** -
> przepisz je z `outputs/wyniki.csv` lub z komorek notebooka.

---

## 1. Cel

Celem zadania jest porownanie dwoch rodzin modeli jezykowych w zadaniu klasyfikacji
wydzwieku tekstu (sentiment analysis) na zbiorze `allegro/klej-polemo2-in`:

- **encoder-only** (BERT-like) - z dedykowana glowa klasyfikujaca,
- **decoder-only LLM** - klasyfikacja zero-shot sterowana promptem.

Dla obu podejsc raportujemy Accuracy oraz F1 (macro/weighted) i analizujemy jakosc
klasyfikacji per klasa. Osobny nacisk kladziemy na poprawne **mapowanie etykiet tekstowych
generowanych przez modele na numeryczne identyfikatory zgodne ze struktura zbioru**.

## 2. Zbior danych

PolEmo2.0-IN to czesc benchmarku KLEJ - recenzje internetowe z domen medycyny i hotelarstwa.
Pola: `sentence` (tekst recenzji) oraz `target` (etykieta). Oryginalnie 4 klasy:

| target (oryginalny)      | znaczenie     | nasze kanoniczne id |
|--------------------------|---------------|---------------------|
| `__label__meta_minus_m`  | negatywny     | 0 (`negative`)      |
| `__label__meta_zero`     | neutralny     | 1 (`neutral`)       |
| `__label__meta_plus_m`   | pozytywny     | 2 (`positive`)      |
| `__label__meta_amb`      | mieszany      | wykluczony z zadania|

Zgodnie z trescia listy uzywamy **wylacznie zbioru testowego** i **wyrzucamy klase
`ambiguous`** - klasyfikujemy do 3 klas.

**Statystyki (uzupelnij po uruchomieniu - zadanie 1):**

- Liczba probek (surowo, split test): `[WPISZ]`
- Liczba probek po wyrzuceniu `ambiguous`: `[WPISZ]`
- Rozklad klas (uzyty): negative=`[WPISZ]`, neutral=`[WPISZ]`, positive=`[WPISZ]`
- Dlugosc tekstu [znaki]: srednia=`[WPISZ]`, mediana=`[WPISZ]`, max=`[WPISZ]`
- Dlugosc tekstu [slowa]: srednia=`[WPISZ]`, mediana=`[WPISZ]`, max=`[WPISZ]`

_Komentarz do zrownowazenia klas:_ `[WPISZ - np. czy dominuje jakas klasa? jak to wplywa na dobor metryki - F1 macro vs accuracy]`

## 3. Metodyka

Caly kod jest zorganizowany w pakiecie `src/` (jedno zrodlo prawdy), wolanym przez notebook
oraz skrypt `run.py`. Kluczowe elementy:

- **Kanoniczna numeracja klas** (`src/config.py`): `negative=0, neutral=1, positive=2`,
  spojna w calym projekcie. Dzieki temu predykcje encodera i LLM trafiaja do tej samej
  przestrzeni etykiet.
- **Mapowanie etykiet** (`src/labels.py`) - punktowany element listy:
  - dla encodera czytamy `model.config.id2label` i mapujemy etykiety modelu (np. `POSITIVE`,
    `LABEL_2`, polskie warianty) na kanoniczne id funkcja `build_model_label_map` - bez
    hardkodowania kolejnosci klas;
  - dla LLM parsujemy wolny tekst odpowiedzi funkcja `parse_generated_label` (slownik
    slow kluczowych PL/EN + warianty), a w trybie JSON - `parse_json_label`;
  - gdy etykiety nie da sie rozpoznac, stosujemy fallback na `neutral` i **zliczamy** takie
    przypadki (`n_unparsed`), zeby uczciwie raportowac jakosc parsowania.
- **Encoder** (`src/encoder.py`): `transformers.pipeline("text-classification")`, batchowanie,
  ucinanie tekstu do `ENCODER_MAX_LEN=512` tokenow (limit BERT/RoBERTa).
- **Decoder/LLM** (`src/decoder.py`): `AutoModelForCausalLM` w `float16` (lub 4-bit przez
  `bitsandbytes`), `apply_chat_template`, generacja batchowana z **left-paddingiem**
  (poprawne dla modeli causal), `do_sample` wlaczany tylko gdy `temperature > 0`.
- **Metryki** (`src/metrics.py`): Accuracy, F1 macro, F1 weighted, raport per-klasa,
  macierz pomylek. Metryki liczone na ustalonym zbiorze etykiet `[0, 1, 2]`.
- **Powtarzalnosc**: ustawione ziarno (`SEED=42`).

Srodowisko: Google Colab + GPU NVIDIA T4, modele w `float16`.

## 4. Zadanie 2 - encoder baseline (HerBERT)

Model bazowy: `Voicelab/herbert-base-cased-sentiment`.

| metryka       | wartosc   |
|---------------|-----------|
| Accuracy      | `[WPISZ]` |
| F1 macro      | `[WPISZ]` |
| F1 weighted   | `[WPISZ]` |

**Jakosc per klasa (z `classification_report`):**

| klasa     | precision | recall | f1  | support |
|-----------|-----------|--------|-----|---------|
| negative  | `[WPISZ]` | `[WPISZ]` | `[WPISZ]` | `[WPISZ]` |
| neutral   | `[WPISZ]` | `[WPISZ]` | `[WPISZ]` | `[WPISZ]` |
| positive  | `[WPISZ]` | `[WPISZ]` | `[WPISZ]` | `[WPISZ]` |

_Interpretacja:_ `[WPISZ - ktora klasa najtrudniejsza? gdzie najwiecej pomylek wg macierzy? czy model myli neutral z pozostalymi?]`

## 5. Zadanie 3 - encoder, eksploracja

**Uwaga metodyczna o temperaturze:** temperatura dotyczy *generacji* (samplingu tokenow).
Encoder wykonuje deterministyczny forward pass z softmaxem na glowie klasyfikujacej - nie
ma tu samplingu, wiec temperatura **nie ma zastosowania**. Eksploracje encodera prowadzimy
przez **porownanie roznych modeli**.

| model                                           | Accuracy | F1 macro | F1 weighted |
|-------------------------------------------------|----------|----------|-------------|
| Voicelab/herbert-base-cased-sentiment           | `[WPISZ]`| `[WPISZ]`| `[WPISZ]`   |
| cardiffnlp/twitter-xlm-roberta-base-sentiment   | `[WPISZ]`| `[WPISZ]`| `[WPISZ]`   |
| _[ewentualnie kolejny model]_                   | `[WPISZ]`| `[WPISZ]`| `[WPISZ]`   |

_Interpretacja:_ `[WPISZ - czy model dedykowany polskiemu (HerBERT) bije model multilingual? o ile? czemu?]`

## 6. Zadanie 4 - decoder baseline (Qwen LLM)

Model bazowy: `Qwen/Qwen2.5-1.5B-Instruct`, prompt po angielsku (`en_basic`), temperatura 0.0.

| metryka                 | wartosc   |
|-------------------------|-----------|
| Accuracy                | `[WPISZ]` |
| F1 macro                | `[WPISZ]` |
| F1 weighted             | `[WPISZ]` |
| Nieparsowalne (n_unparsed) | `[WPISZ]` |

**Jakosc per klasa:**

| klasa     | precision | recall | f1  | support |
|-----------|-----------|--------|-----|---------|
| negative  | `[WPISZ]` | `[WPISZ]` | `[WPISZ]` | `[WPISZ]` |
| neutral   | `[WPISZ]` | `[WPISZ]` | `[WPISZ]` | `[WPISZ]` |
| positive  | `[WPISZ]` | `[WPISZ]` | `[WPISZ]` | `[WPISZ]` |

_Interpretacja:_ `[WPISZ - jak LLM zero-shot wypada wzgledem encodera? ile odpowiedzi bylo nieparsowalnych i co to mowi o prompt-engineeringu?]`

## 7. Zadanie 5 - decoder, eksploracja (>= 2 aspekty)

### 7a. Wplyw promptu (temp = 0.0)

| prompt      | opis                                  | Accuracy | F1 macro | n_unparsed |
|-------------|---------------------------------------|----------|----------|------------|
| en_basic    | prosty, po angielsku                  | `[WPISZ]`| `[WPISZ]`| `[WPISZ]`  |
| pl_basic    | prosty, po polsku                     | `[WPISZ]`| `[WPISZ]`| `[WPISZ]`  |
| pl_fewshot  | po polsku z przykladami (few-shot)    | `[WPISZ]`| `[WPISZ]`| `[WPISZ]`  |
| json        | wymuszony format JSON                  | `[WPISZ]`| `[WPISZ]`| `[WPISZ]`  |

_Interpretacja:_ `[WPISZ - czy polski prompt pomaga przy polskim tekscie? czy few-shot redukuje bledy? czy JSON poprawia parsowalnosc?]`

### 7b. Wplyw temperatury (prompt = pl_fewshot)

| temperatura | Accuracy | F1 macro | n_unparsed |
|-------------|----------|----------|------------|
| 0.0         | `[WPISZ]`| `[WPISZ]`| `[WPISZ]`  |
| 0.3         | `[WPISZ]`| `[WPISZ]`| `[WPISZ]`  |
| 0.7         | `[WPISZ]`| `[WPISZ]`| `[WPISZ]`  |
| 1.0         | `[WPISZ]`| `[WPISZ]`| `[WPISZ]`  |

_Interpretacja:_ `[WPISZ - czy wzrost temperatury pogarsza wyniki/zwieksza n_unparsed? dla zadania klasyfikacji oczekujemy, ze niska temperatura jest lepsza - potwierdz lub zaprzecz]`

### 7c. (Opcjonalnie) Inny model / kwantyzacja 4-bit

`[WPISZ jesli robione - np. Qwen2.5-3B-Instruct w 4-bit: Accuracy/F1 oraz uwaga o czasie i zuzyciu VRAM wzgledem modelu 1.5B]`

### 7d. Parsowanie przez LangChain JsonOutputParser

Uzyty stos: `HuggingFacePipeline` + `PromptTemplate` + `JsonOutputParser` + `pydantic`
(zgodnie z lista). Uruchomione na podzbiorze `[WPISZ N]` probek (tryb one-by-one jest wolniejszy).

- Accuracy: `[WPISZ]`, F1 macro: `[WPISZ]`, nieparsowalne: `[WPISZ]`

_Komentarz:_ `[WPISZ - czy strukturalne parsowanie (pydantic + JsonOutputParser) jest pewniejsze niz parsowanie wolnego tekstu?]`

## 8. Porownanie encoder vs decoder

| podejscie                  | najlepszy model / config | Accuracy | F1 macro |
|----------------------------|--------------------------|----------|----------|
| encoder-only               | `[WPISZ]`                | `[WPISZ]`| `[WPISZ]`|
| decoder-only (LLM)         | `[WPISZ]`                | `[WPISZ]`| `[WPISZ]`|

_Wnioski z porownania:_ `[WPISZ - ktore podejscie wygrywa na tym zbiorze? jak wypada koszt/szybkosc (maly encoder vs LLM)? kiedy ktore ma sens w praktyce?]`

## 9. Wnioski

`[WPISZ 3-5 zdan podsumowania - co dziala najlepiej, dlaczego, co zaskoczylo, czego nauczyl Cie eksperyment z prompt-engineeringiem i temperatura]`

## 10. Wykorzystane biblioteki

- **PyTorch (`torch`)** - silnik obliczen tensorowych i wsparcie GPU (inferencja modeli w `float16`).
- **Transformers (`transformers`)** - dostep do gotowych modeli (HerBERT, Qwen), `pipeline`
  klasyfikacji, `AutoModelForCausalLM`/`AutoTokenizer`, szablony czatu (`apply_chat_template`).
- **Datasets (`datasets`)** - pobranie i obsluga zbioru `allegro/klej-polemo2-in`.
- **Accelerate (`accelerate`)** - rozmieszczenie modelu na urzadzeniach (`device_map`).
- **bitsandbytes** - kwantyzacja 4-bit (`BitsAndBytesConfig`) dla wiekszych LLM.
- **LangChain (`langchain-huggingface`, `langchain-core`)** - `HuggingFacePipeline`,
  `PromptTemplate`, `JsonOutputParser` do ustrukturyzowanego parsowania odpowiedzi LLM.
- **Pydantic (`pydantic`)** - schemat wyjscia (walidacja pola z etykieta) wspolpracujacy
  z `JsonOutputParser`.
- **scikit-learn (`scikit-learn`)** - metryki: `accuracy_score`, `f1_score`,
  `classification_report`, `confusion_matrix`.
- **pandas / numpy** - tabele wynikow i operacje numeryczne.
- **matplotlib (+ seaborn)** - wykresy: rozklad klas, histogram dlugosci, macierze pomylek.
- **tqdm** - paski postepu przy dlugiej inferencji LLM.
- **sentencepiece / protobuf** - tokenizacja wymagana przez modele (HerBERT/Qwen).

## 11. Zrodla

- Kocon, Milkowski, Zasko-Zielinska (2019). *Multi-Level Sentiment Analysis of PolEmo 2.0:
  Extended Corpus of Multi-Domain Consumer Reviews.* CoNLL 2019. (zbior PolEmo2.0)
- Rybak i in. (2020). *KLEJ: Comprehensive Benchmark for Polish Language Understanding.* ACL 2020.
  (benchmark KLEJ)
- Mroczkowski i in. (2021). *HerBERT: Efficiently Pretrained Transformer-based Language Model
  for Polish.* (model HerBERT)
- Qwen Team (2024). *Qwen2.5 Technical Report* oraz karta modelu
  `Qwen/Qwen2.5-1.5B-Instruct` na Hugging Face. (model LLM)
- Dokumentacja Hugging Face Transformers - https://huggingface.co/docs/transformers
- Dokumentacja LangChain - https://python.langchain.com
- Tresc listy: Pawel Walkowiak, *Sztuczna inteligencja i inzynieria wiedzy - Lista 5* (2026).
