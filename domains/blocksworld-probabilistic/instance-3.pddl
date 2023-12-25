(
  define
  (problem instance-3)
  (:domain blocksworld-3ops)
  (:objects b6 b4 b8 b2 b1 b7 b9 b3 b5)
  (
    :init
    (on b6 b7)
    (clear b2)
    (clear b4)
    (on b2 b1)
    (on b7 b3)
    (on b1 b5)
    (on-table b3)
    (on b9 b6)
    (on-table b5)
    (on b4 b8)
    (on b8 b9)
    (injected-0)
  )
  (
    :goal
    (
      and
      (on b1 b3)
      (on b4 b8)
      (on b6 b4)
      (on b7 b5)
      (on b8 b1)
      (on b9 b2)
      (injected-0)
    )
  )
)