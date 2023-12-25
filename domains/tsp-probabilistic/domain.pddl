(
  define
  (domain tsp)
  (
    :predicates
    (visited ?x)
    (at ?x)
    (injected-0)
  )
  (
    :action
    move
    :parameters
    (?x ?y)
    :precondition
    (at ?x)
    :effect
    (
      probabilistic
      0.5
      (
        and
        (
          not
          (at ?x)
        )
        (at ?y)
        (visited ?y)
      )
      0.14651978059294501
      (injected-0)
      0.303480219407055
      (
        not
        (injected-0)
      )
    )
  )
)