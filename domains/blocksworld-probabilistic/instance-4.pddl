(
  define
  (problem instance-4)
  (:domain blocksworld-3ops)
  (:objects b6 b11 b4 b8 b2 b10 b12 b1 b7 b9 b3 b5)
  (
    :init
    (clear b3)
    (on b5 b7)
    (on-table b11)
    (on b1 b6)
    (on-table b8)
    (on b9 b4)
    (on b6 b2)
    (clear b8)
    (on-table b4)
    (on b2 b9)
    (on b3 b10)
    (on b7 b11)
    (on b10 b12)
    (on b12 b1)
    (clear b5)
    (injected-0)
  )
  (
    :goal
    (
      and
      (on b2 b10)
      (on b3 b12)
      (on b4 b2)
      (on b5 b8)
      (on b6 b1)
      (on b7 b11)
      (on b8 b9)
      (on b9 b6)
      (injected-0)
    )
  )
)