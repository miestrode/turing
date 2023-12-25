(
  define
  (problem instance-1)
  (:domain tsp)
  (:objects p2 p1 p4 p3)
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
      (injected-0)
    )
  )
)