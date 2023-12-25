(
  define
  (problem instance-4)
  (:domain tsp)
  (:objects p2 p8 p3 p1 p4 p10 p7 p5 p6 p9)
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
      (visited p9)
      (visited p10)
      (injected-0)
    )
  )
)