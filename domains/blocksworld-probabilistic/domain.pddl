(
  define
  (domain blocksworld-3ops)
  (
    :predicates
    (on ?x ?y)
    (on-table ?x)
    (clear ?x)
    (injected-0)
  )
  (
    :action
    move-t-to-b
    :parameters
    (?bm ?bt)
    :precondition
    (
      and
      (clear ?bm)
      (clear ?bt)
      (on-table ?bm)
    )
    :effect
    (
      probabilistic
      0.5
      (
        and
        (
          not
          (clear ?bt)
        )
        (
          not
          (on-table ?bm)
        )
        (on ?bm ?bt)
      )
      0.008393596241470758
      (injected-0)
      0.4416064037585293
      (
        not
        (injected-0)
      )
    )
  )
  (
    :action
    move-b-to-b
    :parameters
    (?bm ?bf ?bt)
    :precondition
    (
      and
      (clear ?bm)
      (clear ?bt)
      (on ?bm ?bf)
    )
    :effect
    (
      probabilistic
      0.5
      (
        and
        (
          not
          (clear ?bt)
        )
        (
          not
          (on ?bm ?bf)
        )
        (on ?bm ?bt)
        (clear ?bf)
      )
      0.2849544731383964
      (injected-0)
      0.16504552686160362
      (
        not
        (injected-0)
      )
    )
  )
  (
    :action
    move-b-to-t
    :parameters
    (?bm ?bf)
    :precondition
    (
      and
      (clear ?bm)
      (on ?bm ?bf)
    )
    :effect
    (
      probabilistic
      0.5
      (
        and
        (
          not
          (on ?bm ?bf)
        )
        (on-table ?bm)
        (clear ?bf)
      )
      0.44233420924353567
      (injected-0)
      0.007665790756464333
      (
        not
        (injected-0)
      )
    )
  )
)