(
  define
  (domain miconic)
  (
    :predicates
    (not-boarded ?person)
    (above ?floor1 ?floor2)
    (passenger___ ?x)
    (lift-at ?floor)
    (boarded ?person)
    (served ?person)
    (not-served ?person)
    (floor_______ ?x)
    (origin ?person ?floor)
    (destin ?person ?floor)
    (injected----0)
  )
  (
    :action
    down
    :parameters
    (?f1 ?f2)
    :precondition
    (
      and
      (lift-at ?f1)
      (above ?f2 ?f1)
      (floor_______ ?f1)
      (floor_______ ?f2)
    )
    :effect
    (
      probabilistic
      0.5
      (
        and
        (lift-at ?f2)
        (
          not
          (lift-at ?f1)
        )
      )
      0.22246462731439395
      (injected----0)
      0.22753537268560603
      (
        not
        (injected----0)
      )
    )
  )
  (
    :action
    depart
    :parameters
    (?f ?p)
    :precondition
    (
      and
      (lift-at ?f)
      (destin ?p ?f)
      (boarded ?p)
      (floor_______ ?f)
      (passenger___ ?p)
    )
    :effect
    (
      probabilistic
      0.5
      (
        and
        (
          not
          (boarded ?p)
        )
        (served ?p)
      )
      0.4484513299101153
      (injected----0)
      0.0015486700898846612
      (
        not
        (injected----0)
      )
    )
  )
  (
    :action
    board
    :parameters
    (?f ?p)
    :precondition
    (
      and
      (lift-at ?f)
      (origin ?p ?f)
      (floor_______ ?f)
      (passenger___ ?p)
    )
    :effect
    (
      probabilistic
      0.5
      (boarded ?p)
      0.15329614951867268
      (injected----0)
      0.29670385048132736
      (
        not
        (injected----0)
      )
    )
  )
  (
    :action
    up
    :parameters
    (?f1 ?f2)
    :precondition
    (
      and
      (lift-at ?f1)
      (above ?f1 ?f2)
      (floor_______ ?f1)
      (floor_______ ?f2)
    )
    :effect
    (
      probabilistic
      0.5
      (
        and
        (lift-at ?f2)
        (
          not
          (lift-at ?f1)
        )
      )
      0.27630151704843237
      (injected----0)
      0.1736984829515676
      (
        not
        (injected----0)
      )
    )
  )
)