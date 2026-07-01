;; =====================================================================
;; Wariant problemu: BEZ trasy morskiej
;; Cel eksperymentu: pokazac wplyw topologii -- planer musi uzyc samolotu.
;; =====================================================================
(define (problem transport-3pkg-no-water)
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

    (road-connected warehouse portA)    (road-connected portA warehouse)
    (road-connected warehouse airportA) (road-connected airportA warehouse)
    (road-connected portB shop)         (road-connected shop portB)
    (road-connected airportB shop)      (road-connected shop airportB)

    ;; BRAK polaczen wodnych (zerwany szlak morski)

    (air-connected airportA airportB)   (air-connected airportB airportA)
  )

  (:goal (and
    (at-pkg pkg1 shop)
    (at-pkg pkg2 shop)
    (at-pkg pkg3 shop)
  ))
)
