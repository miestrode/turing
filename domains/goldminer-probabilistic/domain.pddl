(
  define
  (domain gold-miner-typed)
  (
    :predicates
    (connected ?x ?y)
    (holds-laser)
    (laser-at ?x)
    (hard-rock-at ?x)
    (holds-gold)
    (soft-rock-at ?x)
    (clear ?x)
    (robot-at ?x)
    (bomb-at ?x)
    (holds-bomb)
    (loc__________ ?x)
    (arm-empty)
    (gold-at ?x)
    (injected-----0)
  )
  (
    :action
    pickup-bomb
    :parameters
    (?x)
    :precondition
    (
      and
      (robot-at ?x)
      (bomb-at ?x)
      (arm-empty)
      (loc__________ ?x)
    )
    :effect
    (
      probabilistic
      0.5
      (
        and
        (
          not
          (arm-empty)
        )
        (holds-bomb)
      )
      0.2648955490834308
      (injected-----0)
      0.18510445091656919
      (
        not
        (injected-----0)
      )
    )
  )
  (
    :action
    fire-laser
    :parameters
    (?x ?y)
    :precondition
    (
      and
      (robot-at ?x)
      (holds-laser)
      (connected ?x ?y)
      (loc__________ ?x)
      (loc__________ ?y)
    )
    :effect
    (
      probabilistic
      0.5
      (
        and
        (clear ?y)
        (
          not
          (soft-rock-at ?y)
        )
        (
          not
          (gold-at ?y)
        )
        (
          not
          (hard-rock-at ?y)
        )
      )
      0.20957314998946489
      (injected-----0)
      0.24042685001053515
      (
        not
        (injected-----0)
      )
    )
  )
  (
    :action
    detonate-bomb
    :parameters
    (?x ?y)
    :precondition
    (
      and
      (robot-at ?x)
      (holds-bomb)
      (connected ?x ?y)
      (soft-rock-at ?y)
      (loc__________ ?x)
      (loc__________ ?y)
    )
    :effect
    (
      probabilistic
      0.5
      (
        and
        (
          not
          (holds-bomb)
        )
        (arm-empty)
        (clear ?y)
        (
          not
          (soft-rock-at ?y)
        )
      )
      0.18236349126643403
      (injected-----0)
      0.26763650873356604
      (
        not
        (injected-----0)
      )
    )
  )
  (
    :action
    putdown-laser
    :parameters
    (?x)
    :precondition
    (
      and
      (robot-at ?x)
      (holds-laser)
      (loc__________ ?x)
    )
    :effect
    (
      probabilistic
      0.5
      (
        and
        (arm-empty)
        (
          not
          (holds-laser)
        )
        (laser-at ?x)
      )
      0.3177978964614338
      (injected-----0)
      0.13220210353856623
      (
        not
        (injected-----0)
      )
    )
  )
  (
    :action
    pick-gold
    :parameters
    (?x)
    :precondition
    (
      and
      (robot-at ?x)
      (arm-empty)
      (gold-at ?x)
      (loc__________ ?x)
    )
    :effect
    (
      probabilistic
      0.5
      (
        and
        (
          not
          (arm-empty)
        )
        (holds-gold)
      )
      0.1288057200940479
      (injected-----0)
      0.3211942799059521
      (
        not
        (injected-----0)
      )
    )
  )
  (
    :action
    move
    :parameters
    (?x ?y)
    :precondition
    (
      and
      (robot-at ?x)
      (connected ?x ?y)
      (clear ?y)
      (loc__________ ?x)
      (loc__________ ?y)
    )
    :effect
    (
      probabilistic
      0.5
      (
        and
        (robot-at ?y)
        (
          not
          (robot-at ?x)
        )
      )
      0.4273114658312948
      (injected-----0)
      0.022688534168705237
      (
        not
        (injected-----0)
      )
    )
  )
  (
    :action
    pickup-laser
    :parameters
    (?x)
    :precondition
    (
      and
      (robot-at ?x)
      (laser-at ?x)
      (arm-empty)
      (loc__________ ?x)
    )
    :effect
    (
      probabilistic
      0.5
      (
        and
        (
          not
          (arm-empty)
        )
        (holds-laser)
        (
          not
          (laser-at ?x)
        )
      )
      0.29838061739790545
      (injected-----0)
      0.1516193826020945
      (
        not
        (injected-----0)
      )
    )
  )
)