;; =====================================================================
;; Zadanie 3: Problem -- 4 pilki, robot z 2 ramionami.
;; Wszystkie pilki startuja w room1, cel: wszystkie w room2.
;;
;; UWAGA: w PDF zadania w pliku problem.pddl byly literowki w nawiasach:
;; - linijka 1: "define (..." zamiast "(define (..."
;; - linijka 29: dodatkowy nawias zamykajacy
;; Tutaj poprawione.
;; =====================================================================
(define (problem move-balls)
  (:domain ball-moving-robot)

  (:objects
    room1 room2              - room
    robot                    - robot
    ball1 ball2 ball3 ball4  - ball
    arm1 arm2                - arm
  )

  (:init
    (at robot room1)
    (inroom ball1 room1)
    (inroom ball2 room1)
    (inroom ball3 room1)
    (inroom ball4 room1)
    (arm-empty arm1)
    (arm-empty arm2)
  )

  (:goal (and
    (inroom ball1 room2)
    (inroom ball2 room2)
    (inroom ball3 room2)
    (inroom ball4 room2)
  ))
)
