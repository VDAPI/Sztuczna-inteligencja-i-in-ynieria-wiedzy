# Lista 3 — Planowanie działań w PDDL

## O co chodziło (moje streszczenie)

Zadanie dotyczyło **automatycznego planowania** w języku **PDDL** (Planning Domain Definition
Language). Dla kilku problemów należało zdefiniować **domenę** (typy, predykaty, akcje z
warunkami i efektami w stylu STRIPS) oraz **problem** (obiekty, stan początkowy, cel), a następnie
uruchomić planer, przeanalizować wygenerowany plan i opisać eksperymenty (np. wpływ heurystyki
lub kosztów akcji na długość i jakość planu).

Zrealizowane problemy:

1. **Transport paczek** — model przewożenia paczek między lokalizacjami różnymi środkami
   transportu; dodatkowo wariant z kosztami akcji (`:action-costs`) oraz eksperyment z modyfikacją
   topologii (usunięcie połączenia).
2. **Robot odkurzający** — planowanie sprzątania pól w prostym środowisku siatkowym.
3. **Robot przenoszący piłki** — klasyczny problem typu *gripper*.

Pełną treść polecenia pomijam (materiał prowadzących).

## Jak to rozwiązałem

Kod i analiza są w [`rozwiazanie/`](./rozwiazanie). Zacznij od `rozwiazanie/jak_dziala_pddl.md`
(wprowadzenie do języka i planerów), a szczegóły każdego zadania znajdziesz w podkatalogach
`zadanie1_transport/`, `zadanie2_odkurzanie/`, `zadanie3_pilki/` — każdy zawiera pliki `.pddl`,
wygenerowane plany (`plan*.txt`) oraz `opis.md`/`raport.md`.

Plany porównywałem m.in. dla heurystyk **hFF** i **hmax** (A\*), pokazując różnicę między planem
suboptymalnym a optymalnym. Szczegóły uruchamiania (edytor online `editor.planning.domains`
oraz lokalnie `pyperplan`) opisuje `rozwiazanie/README.md`.

## Raport

[`raport.pdf`](./raport.pdf) — opis problemów, zrzuty planów, analiza eksperymentów i wnioski.
