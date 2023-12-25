(
  define
  (domain grid-visit-all)
  (
    :predicates
    (connected ?x ?y)
    (visited ?x)
    (at-robot ?x)
    (place_____ ?x)
    (injected--0)
  )
  (
    :action
    move
    :parameters
    (?curpos ?nextpos)
    :precondition
    (
      and
      (at-robot ?curpos)
      (connected ?curpos ?nextpos)
      (place_____ ?curpos)
      (place_____ ?nextpos)
    )
    :effect
    (
      probabilistic
      0.5
      (
        and
        (at-robot ?nextpos)
        (
          not
          (at-robot ?curpos)
        )
        (visited ?nextpos)
      )
      0.14473228868151664
      (injected--0)
      0.30526771131848335
      (
        not
        (injected--0)
      )
    )
  )
)