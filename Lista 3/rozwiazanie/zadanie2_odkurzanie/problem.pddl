;; =====================================================================
;; Problem: 3 brudne pokoje, robot startuje w pokoj1.
;; Cel: wszystkie pokoje czyste.
;; =====================================================================
(define (problem clean-three-rooms)
  (:domain vacuum-robot)

  (:objects
    rumba                 - robot
    pokoj1 pokoj2 pokoj3  - room
  )

  (:init
    (at rumba pokoj1)
    (dirty pokoj1)
    (dirty pokoj2)
    (dirty pokoj3)
  )

  (:goal (and
    (clean pokoj1)
    (clean pokoj2)
    (clean pokoj3)
  ))
)
