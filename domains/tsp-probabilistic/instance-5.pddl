(
  define
  (problem instance-5)
  (:domain tsp)
  (:objects p2 p8 p3 p15 p12 p14 p1 p4 p11 p13 p10 p7 p5 p6 p9)
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
      (visited p11)
      (visited p12)
      (visited p13)
      (visited p14)
      (visited p15)
      (injected-0)
    )
  )
)