;; =====================================================================
;; Zadanie 2: Robot odkurzajacy
;; Domena: robot porusza sie miedzy pokojami i je sprzata.
;; =====================================================================
(define (domain vacuum-robot)

  (:requirements :strips :typing :negative-preconditions)

  (:types robot room)

  (:predicates
    (at    ?r - robot ?p - room)   ; robot znajduje sie w pokoju
    (dirty ?p - room)              ; pokoj brudny
    (clean ?p - room)              ; pokoj czysty
  )

  ;; Akcja move: robot przemieszcza sie z jednego pokoju do drugiego.
  ;; Brak predykatu polaczen -- robot moze przejsc miedzy dowolnymi pokojami
  ;; (uproszczony model, jak w zadaniu 3).
  (:action move
    :parameters (?r - robot ?from - room ?to - room)
    :precondition (at ?r ?from)
    :effect (and (not (at ?r ?from))
                 (at ?r ?to))
  )

  ;; Akcja clean: sprzata pokoj, w ktorym aktualnie jest robot.
  ;; Wymaga, zeby pokoj byl brudny -- inaczej akcja niedostepna.
  (:action clean
    :parameters (?r - robot ?p - room)
    :precondition (and (at ?r ?p) (dirty ?p))
    :effect (and (not (dirty ?p))
                 (clean ?p))
  )
)
