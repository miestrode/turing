

(define (problem BW-rand-12)
(:domain blocksworld-3ops)
(:objects b1 b2 b3 b4 b5 b6 b7 b8 b9 b10 b11 b12 )
(:init
(on b1 b6)
(on b2 b9)
(on b3 b10)
(on-table b4)
(on b5 b7)
(on b6 b2)
(on b7 b11)
(on-table b8)
(on b9 b4)
(on b10 b12)
(on-table b11)
(on b12 b1)
(clear b3)
(clear b5)
(clear b8)
)
(:goal
(and
(on b2 b10)
(on b3 b12)
(on b4 b2)
(on b5 b8)
(on b6 b1)
(on b7 b11)
(on b8 b9)
(on b9 b6))
)
)


