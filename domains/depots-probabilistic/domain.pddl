(
  define
  (domain depots)
  (
    :predicates
    (lifting ?x ?y)
    (depot_____ ?x)
    (on ?x ?y)
    (pallet____ ?x)
    (crate_____ ?x)
    (surface___ ?x)
    (in ?x ?y)
    (locatable_ ?x)
    (available ?x)
    (truck_____ ?x)
    (clear ?x)
    (place_____ ?x)
    (distributor ?x)
    (at ?x ?y)
    (hoist_____ ?x)
    (injected---0)
  )
  (
    :action
    drive
    :parameters
    (?x ?y ?z)
    :precondition
    (
      and
      (at ?x ?y)
      (truck_____ ?x)
      (place_____ ?y)
      (place_____ ?z)
    )
    :effect
    (
      probabilistic
      0.5
      (
        and
        (
          not
          (at ?x ?y)
        )
        (at ?x ?z)
      )
      0.17115119406860632
      (injected---0)
      0.2788488059313937
      (
        not
        (injected---0)
      )
    )
  )
  (
    :action
    unload
    :parameters
    (?x ?y ?z ?p)
    :precondition
    (
      and
      (at ?x ?p)
      (at ?z ?p)
      (available ?x)
      (in ?y ?z)
      (hoist_____ ?x)
      (crate_____ ?y)
      (truck_____ ?z)
      (place_____ ?p)
    )
    :effect
    (
      probabilistic
      0.5
      (
        and
        (
          not
          (in ?y ?z)
        )
        (
          not
          (available ?x)
        )
        (lifting ?x ?y)
      )
      0.11144680150179324
      (injected---0)
      0.33855319849820675
      (
        not
        (injected---0)
      )
    )
  )
  (
    :action
    load
    :parameters
    (?x ?y ?z ?p)
    :precondition
    (
      and
      (at ?x ?p)
      (at ?z ?p)
      (lifting ?x ?y)
      (hoist_____ ?x)
      (crate_____ ?y)
      (truck_____ ?z)
      (place_____ ?p)
    )
    :effect
    (
      probabilistic
      0.5
      (
        and
        (
          not
          (lifting ?x ?y)
        )
        (in ?y ?z)
        (available ?x)
      )
      0.2991889139718278
      (injected---0)
      0.15081108602817217
      (
        not
        (injected---0)
      )
    )
  )
  (
    :action
    lift
    :parameters
    (?x ?y ?z ?p)
    :precondition
    (
      and
      (at ?x ?p)
      (available ?x)
      (at ?y ?p)
      (on ?y ?z)
      (clear ?y)
      (hoist_____ ?x)
      (crate_____ ?y)
      (surface___ ?z)
      (place_____ ?p)
    )
    :effect
    (
      probabilistic
      0.5
      (
        and
        (
          not
          (at ?y ?p)
        )
        (lifting ?x ?y)
        (
          not
          (clear ?y)
        )
        (
          not
          (available ?x)
        )
        (clear ?z)
        (
          not
          (on ?y ?z)
        )
      )
      0.19684948121024096
      (injected---0)
      0.253150518789759
      (
        not
        (injected---0)
      )
    )
  )
  (
    :action
    drop
    :parameters
    (?x ?y ?z ?p)
    :precondition
    (
      and
      (at ?x ?p)
      (at ?z ?p)
      (clear ?z)
      (lifting ?x ?y)
      (hoist_____ ?x)
      (crate_____ ?y)
      (surface___ ?z)
      (place_____ ?p)
    )
    :effect
    (
      probabilistic
      0.5
      (
        and
        (available ?x)
        (
          not
          (lifting ?x ?y)
        )
        (at ?y ?p)
        (
          not
          (clear ?z)
        )
        (clear ?y)
        (on ?y ?z)
      )
      0.1872789777363056
      (injected---0)
      0.2627210222636943
      (
        not
        (injected---0)
      )
    )
  )
)