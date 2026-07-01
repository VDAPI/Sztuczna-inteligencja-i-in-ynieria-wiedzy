;; =====================================================================
;; Domena: Transport multi-modalny z kosztami numerycznymi
;; Rozszerzenia: :strips, :typing, :negative-preconditions, :action-costs
;; UWAGA: wymaga Fast Downward lub editor.planning.domains.
;; Pyperplan NIE wspiera :functions.
;; =====================================================================
(define (domain transport-costs)

  (:requirements :strips :typing :negative-preconditions :action-costs)

  (:types
    package vehicle location - object
    truck plane ship - vehicle
  )

  (:predicates
    (at-pkg ?p - package ?l - location)
    (at-veh ?v - vehicle ?l - location)
    (in    ?p - package ?v - vehicle)
    (road-connected  ?l1 - location ?l2 - location)
    (air-connected   ?l1 - location ?l2 - location)
    (water-connected ?l1 - location ?l2 - location)
  )

  (:functions
    (total-cost)
    (road-cost  ?l1 - location ?l2 - location)
    (air-cost   ?l1 - location ?l2 - location)
    (water-cost ?l1 - location ?l2 - location)
  )

  (:action load
    :parameters (?p - package ?v - vehicle ?l - location)
    :precondition (and (at-pkg ?p ?l) (at-veh ?v ?l))
    :effect (and (not (at-pkg ?p ?l)) (in ?p ?v)
                 (increase (total-cost) 1))
  )

  (:action unload
    :parameters (?p - package ?v - vehicle ?l - location)
    :precondition (and (in ?p ?v) (at-veh ?v ?l))
    :effect (and (at-pkg ?p ?l) (not (in ?p ?v))
                 (increase (total-cost) 1))
  )

  (:action drive
    :parameters (?t - truck ?from - location ?to - location)
    :precondition (and (at-veh ?t ?from) (road-connected ?from ?to))
    :effect (and (not (at-veh ?t ?from)) (at-veh ?t ?to)
                 (increase (total-cost) (road-cost ?from ?to)))
  )

  (:action fly
    :parameters (?pl - plane ?from - location ?to - location)
    :precondition (and (at-veh ?pl ?from) (air-connected ?from ?to))
    :effect (and (not (at-veh ?pl ?from)) (at-veh ?pl ?to)
                 (increase (total-cost) (air-cost ?from ?to)))
  )

  (:action sail
    :parameters (?s - ship ?from - location ?to - location)
    :precondition (and (at-veh ?s ?from) (water-connected ?from ?to))
    :effect (and (not (at-veh ?s ?from)) (at-veh ?s ?to)
                 (increase (total-cost) (water-cost ?from ?to)))
  )
)
