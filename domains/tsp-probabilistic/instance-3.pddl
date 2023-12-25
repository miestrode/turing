(
  define
  (problem instance-3)
  (:domain tsp)
  (:objects p2 p8 p3 p1 p4 p7 p5 p6)
  (
    :init
    (at p1)
    (injected-0)
  )
  (
    :goal
    (
      and
      (visited p1)
      (visited p2)
      (visited p3)
      (visited p4)
      (visited p5)
      (visited p6)
      (visited p7)
      (visited p8)
      (injected-0)
    )
  )
)