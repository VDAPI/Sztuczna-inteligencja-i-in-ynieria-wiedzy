;; =====================================================================
;; Problem z kosztami: trasa morska tansza niz lotnicza
;; Wymaga Fast Downward (np. astar(lmcut())) lub online editora.
;; =====================================================================
(define (problem transport-3pkg-costs)
  (:domain transport-costs)

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

    (road-connected warehouse portA)    (road-connected portA warehouse)
    (road-connected warehouse airportA) (road-connected airportA warehouse)
    (road-connected portB shop)         (road-connected shop portB)
    (road-connected airportB shop)      (road-connected shop airportB)
    (water-connected portA portB)       (water-connected portB portA)
    (air-connected airportA airportB)   (air-connected airportB airportA)

    ;; KOSZTY
    (= (road-cost warehouse portA) 10)    (= (road-cost portA warehouse) 10)
    (= (road-cost warehouse airportA) 8)  (= (road-cost airportA warehouse) 8)
    (= (road-cost portB shop) 10)         (= (road-cost shop portB) 10)
    (= (road-cost airportB shop) 8)       (= (road-cost shop airportB) 8)

    (= (water-cost portA portB) 5)        (= (water-cost portB portA) 5)
    (= (air-cost airportA airportB) 30)   (= (air-cost airportB airportA) 30)

    (= (total-cost) 0)
  )

  (:goal (and
    (at-pkg pkg1 shop)
    (at-pkg pkg2 shop)
    (at-pkg pkg3 shop)
  ))

  (:metric minimize (total-cost))
)
