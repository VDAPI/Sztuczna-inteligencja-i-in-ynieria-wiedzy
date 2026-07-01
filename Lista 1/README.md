# Lista 1 — Wyszukiwanie połączeń w rozkładzie kolejowym

## O co chodziło (moje streszczenie)

Zadanie polegało na napisaniu wyszukiwarki połączeń działającej na realnym rozkładzie jazdy
Kolei Dolnośląskich, dostarczonym w formacie **GTFS** (zestaw plików `.txt` opisujących
przystanki, trasy, kursy i godziny). Z tych danych trzeba było zbudować **skierowany graf
zależny od czasu** i szukać w nim najlepszych tras.

Zakres, który realizowałem:

1. **Trasa A → B** przyjmująca cztery parametry: przystanek startowy, przystanek docelowy,
   kryterium optymalizacji (czas przejazdu albo liczba przesiadek) oraz godzinę rozpoczęcia
   podróży. Program wypisuje kolejne odcinki trasy (przystanki, linia, godziny) oraz na
   `stderr` wartość zminimalizowanego kryterium i czas obliczeń.
   - wariant z **algorytmem Dijkstry** (kryterium czasu),
   - wariant z **algorytmem A\*** (kryterium czasu, z heurystyką dopuszczalną),
   - wariant z **A\*** dla kryterium liczby przesiadek,
   - **modyfikacje A\*** poprawiające czas obliczeń lub jakość trasy.
2. **Wariant komiwojażera:** start z przystanku A, odwiedzenie wszystkich przystanków z zadanej
   listy i powrót do A, z minimalizacją tego samego kryterium — rozwiązywany metaheurystyką
   **Tabu Search** (m.in. z ograniczanym rozmiarem listy tabu, aspiracją i próbkowaniem
   sąsiedztwa).

Pełną treść polecenia pomijam (materiał prowadzących).

## Jak to rozwiązałem

Kod jest w [`rozwiazanie/`](./rozwiazanie):

| Plik | Rola |
|------|------|
| `parser.py` | wczytanie plików GTFS, konwersje czasu (`HH:MM:SS` ↔ sekundy, obsługa godzin > 24:00), normalizacja nazw przystanków, kalendarz kursowania |
| `graph.py` | budowa grafu połączeń dla wybranej daty: dla każdego kursu tworzy krawędzie między kolejnymi przystankami; listy odjazdów posortowane po czasie (do szybkiego wyszukiwania binarnego) |
| `pathfinder.py` | Dijkstra i A\* na grafie czasowym; heurystyki: `zero` (= Dijkstra), **haversine/prędkość maks.** dla czasu oraz heurystyka dla liczby przesiadek |
| `tsp.py` | `TSPSolver` — Tabu Search dla wariantu odwiedzania wielu przystanków, z cache'owaniem kosztów odcinków |
| `main.py` | interfejs CLI, składanie całości, pomiar czasu |

Heurystyka czasowa liczy odległość haversine do celu i dzieli ją przez maksymalną prędkość
pociągu (160 km/h) — dzięki temu nigdy nie przeszacowuje kosztu, więc A\* pozostaje optymalny.

## Uruchomienie

```bash
cd rozwiazanie
# Trasa A -> B, kryterium czasu (t) / przesiadek (p), godzina startu, [data]
python main.py "Wrocław Główny" "Jelenia Góra" t 08:00:00 2026-03-10
```

Dane GTFS znajdują się w `rozwiazanie/data/google_transit/`.

## Raport

[`raport.pdf`](./raport.pdf) — tło teoretyczne (Dijkstra, A\*, Tabu Search), przykłady użycia,
opis wprowadzonych modyfikacji, wykorzystane biblioteki i napotkane problemy.
