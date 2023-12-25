(
  define
  (domain zeno-travel)
  (
    :predicates
    (canat______ ?x)
    (flevel_____ ?x)
    (in ?p ?a)
    (next ?l1 ?l2)
    (fuel-level ?a ?l)
    (at ?x ?c)
    (city_______ ?x)
    (person_____ ?x)
    (aircraft___ ?x)
    (injected---0)
  )
  (
    :action
    debark
    :parameters
    (?p ?a ?c)
    :precondition
    (
      and
      (in ?p ?a)
      (at ?a ?c)
      (person_____ ?p)
      (aircraft___ ?a)
      (city_______ ?c)
    )
    :effect
    (
      probabilistic
      0.5
      (
        and
        (
          not
          (in ?p ?a)
        )
        (at ?p ?c)
      )
      0.195599259322809
      (injected---0)
      0.254400740677191
      (
        not
        (injected---0)
      )
    )
  )
  (
    :action
    refuel
    :parameters
    (?a ?c ?l ?l1)
    :precondition
    (
      and
      (fuel-level ?a ?l)
      (next ?l ?l1)
      (at ?a ?c)
      (aircraft___ ?a)
      (city_______ ?c)
      (flevel_____ ?l)
      (flevel_____ ?l1)
    )
    :effect
    (
      probabilistic
      0.5
      (
        and
        (fuel-level ?a ?l1)
        (
          not
          (fuel-level ?a ?l)
        )
      )
      0.2217661093621078
      (injected---0)
      0.22823389063789218
      (
        not
        (injected---0)
      )
    )
  )
  (
    :action
    fly
    :parameters
    (?a ?c1 ?c2 ?l1 ?l2)
    :precondition
    (
      and
      (at ?a ?c1)
      (fuel-level ?a ?l1)
      (next ?l2 ?l1)
      (aircraft___ ?a)
      (city_______ ?c1)
      (city_______ ?c2)
      (flevel_____ ?l1)
      (flevel_____ ?l2)
    )
    :effect
    (
      probabilistic
      0.5
      (
        and
        (
          not
          (at ?a ?c1)
        )
        (at ?a ?c2)
        (
          not
          (fuel-level ?a ?l1)
        )
        (fuel-level ?a ?l2)
      )
      0.36673339177704606
      (injected---0)
      0.083266608222954
      (
        not
        (injected---0)
      )
    )
  )
  (
    :action
    board
    :parameters
    (?p ?a ?c)
    :precondition
    (
      and
      (at ?p ?c)
      (at ?a ?c)
      (person_____ ?p)
      (aircraft___ ?a)
      (city_______ ?c)
    )
    :effect
    (
      probabilistic
      0.5
      (
        and
        (
          not
          (at ?p ?c)
        )
        (in ?p ?a)
      )
      0.22241909154565942
      (injected---0)
      0.22758090845434056
      (
        not
        (injected---0)
      )
    )
  )
  (
    :action
    zoom
    :parameters
    (?a ?c1 ?c2 ?l1 ?l2 ?l3)
    :precondition
    (
      and
      (at ?a ?c1)
      (fuel-level ?a ?l1)
      (next ?l2 ?l1)
      (next ?l3 ?l2)
      (aircraft___ ?a)
      (city_______ ?c1)
      (city_______ ?c2)
      (flevel_____ ?l1)
      (flevel_____ ?l2)
      (flevel_____ ?l3)
    )
    :effect
    (
      probabilistic
      0.5
      (
        and
        (
          not
          (at ?a ?c1)
        )
        (at ?a ?c2)
        (
          not
          (fuel-level ?a ?l1)
        )
        (fuel-level ?a ?l3)
      )
      0.28222091899637275
      (injected---0)
      0.1677790810036273
      (
        not
        (injected---0)
      )
    )
  )
)