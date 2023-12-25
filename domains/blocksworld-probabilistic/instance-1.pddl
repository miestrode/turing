(
  define
  (problem instance-1)
  (:domain blocksworld-3ops)
  (:objects b4 b2 b1 b3)
  (
    :init
    (clear b3)
    (on-table b2)
    (on b3 b4)
    (clear b1)
    (on b1 b2)
    (on-table b4)
    (injected-0)
  )
  (
    :goal
    (
      and
      (on b2 b3)
      (on b3 b1)
      (injected-0)
    )
  )
)