(
  define
  (problem instance-1)
  (:domain miconic)
  (:objects p2 p3 f6 p1 f2 f1 f3 f5 f0 p0 f4 f7)
  (
    :init
    (above f0 f2)
    (origin p3 f7)
    (passenger___ p0)
    (passenger___ p3)
    (above f5 f7)
    (destin p1 f6)
    (above f2 f7)
    (above f6 f7)
    (above f0 f5)
    (floor_______ f6)
    (above f3 f6)
    (floor_______ f3)
    (above f0 f6)
    (above f1 f2)
    (above f5 f6)
    (destin p2 f7)
    (above f0 f3)
    (lift-at f0)
    (origin p1 f3)
    (above f1 f7)
    (above f1 f5)
    (destin p0 f3)
    (above f2 f4)
    (above f2 f5)
    (origin p0 f5)
    (floor_______ f4)
    (above f3 f4)
    (above f1 f6)
    (origin p2 f1)
    (above f0 f4)
    (above f1 f3)
    (above f2 f3)
    (above f2 f6)
    (floor_______ f1)
    (destin p3 f0)
    (floor_______ f7)
    (above f3 f7)
    (above f0 f1)
    (above f4 f7)
    (above f4 f5)
    (above f0 f7)
    (passenger___ p2)
    (floor_______ f0)
    (passenger___ p1)
    (floor_______ f2)
    (above f1 f4)
    (above f4 f6)
    (floor_______ f5)
    (above f3 f5)
    (injected----0)
  )
  (
    :goal
    (
      and
      (served p0)
      (served p1)
      (served p2)
      (served p3)
      (injected----0)
    )
  )
)