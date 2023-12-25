(
  define
  (problem instance-2)
  (:domain blocksworld-3ops)
  (:objects b6 b4 b2 b3 b5 b1)
  (
    :init
    (clear b3)
    (on-table b2)
    (on b3 b4)
    (on b6 b1)
    (on b4 b6)
    (on-table b1)
    (clear b5)
    (on b5 b2)
    (injected-0)
  )
  (
    :goal
    (
      and
      (on b3 b1)
      (on b4 b6)
      (on b5 b4)
      (on b6 b2)
      (injected-0)
    )
  )
)