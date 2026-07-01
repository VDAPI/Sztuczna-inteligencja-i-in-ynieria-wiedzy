# Lista 2 — Gra *Breakthrough* (Minimax + alfa-beta)

## O co chodziło (moje streszczenie)

Celem było praktyczne zapoznanie się z algorytmami grania w **gry dwuosobowe o sumie zerowej**:
algorytmem **Minimax** oraz jego przyspieszeniem przez **przycinanie alfa-beta**.

Poligonem była gra planszowa **Breakthrough** (Dan Troyka, 2000) na szachownicy 8×8. Piony
poruszają się o jedno pole prosto lub na skos (na puste pole), a bicie przeciwnika możliwe jest
wyłącznie po skosie. Wygrywa gracz, który jako pierwszy dotrze pionem do przeciwległej krawędzi
planszy.

Program miał:

- wczytywać planszę startową ze standardowego wejścia (`B`/`W`/`_`, gdzie `o` znaczy pole
  ostatniego ruchu), pozwalać wybrać **heurystykę** i **maksymalną głębokość przeszukiwania `d`**,
- **wersja podstawowa:** rozegrać całą partię algorytmem Minimax z perspektywy gracza pierwszego
  (przeciwnik gra optymalnie tą samą heurystyką),
- na wyjściu podać końcową planszę, liczbę rund i zwycięzcę, a na `stderr` liczbę odwiedzonych
  węzłów drzewa i czas działania,
- dodatkowo: **przycinanie alfa-beta**, zestaw **≥3 heurystyk** oceny stanu dla każdego gracza,
  oraz **wersja rozszerzona** — partia między dwoma niezależnymi agentami z adaptacyjną zmianą
  strategii.

Pełną treść polecenia pomijam (materiał prowadzących).

## Status

⏳ **Kod rozwiązania do uzupełnienia** — zostanie dograny po odnalezieniu.
Na razie w folderze znajduje się mój raport.

## Raport

[`raport.pdf`](./raport.pdf) — opis teoretyczny Minimax i alfa-beta, formalne ujęcie stanu gry
i drzewa decyzyjnego, idea rozwiązania z przykładem, użyte materiały i biblioteki oraz napotkane
problemy implementacyjne.
