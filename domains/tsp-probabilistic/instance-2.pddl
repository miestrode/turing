(
  define
  (problem instance-2)
  (:domain tsp)
  (:objects p2 p3 p5 p6 p1 p4)
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
      (injected-0)
    )
  )
)