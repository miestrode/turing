(
  define
  (domain storage-propositional)
  (
    :predicates
    (in ?x ?p)
    (surface____ ?x)
    (at ?h ?a)
    (clear ?s)
    (place______ ?x)
    (lifting ?h ?c)
    (storearea__ ?x)
    (container__ ?x)
    (connected ?a1 ?a2)
    (transitarea ?x)
    (area_______ ?x)
    (hoist______ ?x)
    (on ?c ?s)
    (depot______ ?x)
    (crate______ ?x)
    (compatible ?c1 ?c2)
    (available ?h)
    (injected---0)
  )
  (
    :action
    move
    :parameters
    (?h ?from ?to)
    :precondition
    (
      and
      (at ?h ?from)
      (clear ?to)
      (connected ?from ?to)
      (hoist______ ?h)
      (storearea__ ?from)
      (storearea__ ?to)
    )
    :effect
    (
      probabilistic
      0.5
      (
        and
        (
          not
          (at ?h ?from)
        )
        (at ?h ?to)
        (
          not
          (clear ?to)
        )
        (clear ?from)
      )
      0.3903210415706493
      (injected---0)
      0.05967895842935072
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
    (?h ?c ?a1 ?a2 ?p)
    :precondition
    (
      and
      (connected ?a1 ?a2)
      (at ?h ?a2)
      (available ?h)
      (on ?c ?a1)
      (in ?a1 ?p)
      (hoist______ ?h)
      (crate______ ?c)
      (storearea__ ?a1)
      (area_______ ?a2)
      (place______ ?p)
    )
    :effect
    (
      probabilistic
      0.5
      (
        and
        (
          not
          (on ?c ?a1)
        )
        (clear ?a1)
        (
          not
          (available ?h)
        )
        (lifting ?h ?c)
        (
          not
          (in ?c ?p)
        )
      )
      0.01415064347717997
      (injected---0)
      0.43584935652282003
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
    (?h ?c ?a1 ?a2 ?p)
    :precondition
    (
      and
      (connected ?a1 ?a2)
      (at ?h ?a2)
      (lifting ?h ?c)
      (clear ?a1)
      (in ?a1 ?p)
      (hoist______ ?h)
      (crate______ ?c)
      (storearea__ ?a1)
      (area_______ ?a2)
      (place______ ?p)
    )
    :effect
    (
      probabilistic
      0.5
      (
        and
        (
          not
          (lifting ?h ?c)
        )
        (available ?h)
        (
          not
          (clear ?a1)
        )
        (on ?c ?a1)
        (in ?c ?p)
      )
      0.1708556169753937
      (injected---0)
      0.2791443830246063
      (
        not
        (injected---0)
      )
    )
  )
  (
    :action
    go-out
    :parameters
    (?h ?from ?to)
    :precondition
    (
      and
      (at ?h ?from)
      (connected ?from ?to)
      (hoist______ ?h)
      (storearea__ ?from)
      (transitarea ?to)
    )
    :effect
    (
      probabilistic
      0.5
      (
        and
        (
          not
          (at ?h ?from)
        )
        (at ?h ?to)
        (clear ?from)
      )
      0.22977950661402777
      (injected---0)
      0.2202204933859722
      (
        not
        (injected---0)
      )
    )
  )
  (
    :action
    go-in
    :parameters
    (?h ?from ?to)
    :precondition
    (
      and
      (at ?h ?from)
      (connected ?from ?to)
      (clear ?to)
      (hoist______ ?h)
      (transitarea ?from)
      (storearea__ ?to)
    )
    :effect
    (
      probabilistic
      0.5
      (
        and
        (
          not
          (at ?h ?from)
        )
        (at ?h ?to)
        (
          not
          (clear ?to)
        )
      )
      0.3957461715225732
      (injected---0)
      0.05425382847742683
      (
        not
        (injected---0)
      )
    )
  )
)