;; =====================================================================
;; Problem: 3 paczki, transport multi-modalny (wersja STRIPS)
;;
;; Topologia:
;;
;;     warehouse --(road)-- portA ==(water)== portB --(road)-- shop
;;          |                                                     |
;;          \--(road)-- airportA --(air)-- airportB --(road)-----/
;;
;; Cel: pkg1, pkg2 (z warehouse) i pkg3 (z portA) maja trafic do shop.
;; =====================================================================
(define (problem transport-3pkg-strips)
  (:domain transport-strips)

  (:objects
    pkg1 pkg2 pkg3                  - package
    warehouse portA portB shop
    airportA airportB               - location
    truck1 truck2 truck3 truck4     - truck
    plane1                          - plane
    ship1                           - ship
  )

  (:init
    (at-pkg pkg1 warehouse)
    (at-pkg pkg2 warehouse)
    (at-pkg pkg3 portA)

    (at-veh truck1 warehouse)
    (at-veh truck2 portB)
    (at-veh truck3 airportB)
    (at-veh truck4 shop)
    (at-veh ship1  portA)
    (at-veh plane1 airportA)

    ;; drogi -- dwukierunkowe
    (road-connected warehouse portA)    (road-connected portA warehouse)
    (road-connected warehouse airportA) (road-connected airportA warehouse)
    (road-connected portB shop)         (road-connected shop portB)
    (road-connected airportB shop)      (road-connected shop airportB)

    ;; trasa morska
    (water-connected portA portB)       (water-connected portB portA)

    ;; trasa lotnicza
    (air-connected airportA airportB)   (air-connected airportB airportA)
  )

  (:goal (and
    (at-pkg pkg1 shop)
    (at-pkg pkg2 shop)
    (at-pkg pkg3 shop)
  ))
)
