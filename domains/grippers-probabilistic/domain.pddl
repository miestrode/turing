(
  define
  (domain gripper-strips)
  (
    :predicates
    (at-robby ?r ?x)
    (at ?o ?x)
    (free ?r ?g)
    (stuff____ ?x)
    (robot____ ?x)
    (gripper__ ?x)
    (carry ?r ?o ?g)
    (room_____ ?x)
    (injected-0)
  )
  (
    :action
    move
    :parameters
    (?r ?from ?to)
    :precondition
    (
      and
      (at-robby ?r ?from)
      (robot____ ?r)
      (room_____ ?from)
      (room_____ ?to)
    )
    :effect
    (
      probabilistic
      0.5
      (
        and
        (at-robby ?r ?to)
        (
          not
          (at-robby ?r ?from)
        )
      )
      0.2550860260008176
      (injected-0)
      0.19491397399918245
      (
        not
        (injected-0)
      )
    )
  )
  (
    :action
    pick
    :parameters
    (?r ?obj ?room ?g)
    :precondition
    (
      and
      (at ?obj ?room)
      (at-robby ?r ?room)
      (free ?r ?g)
      (robot____ ?r)
      (stuff____ ?obj)
      (room_____ ?room)
      (gripper__ ?g)
    )
    :effect
    (
      probabilistic
      0.5
      (
        and
        (carry ?r ?obj ?g)
        (
          not
          (at ?obj ?room)
        )
        (
          not
          (free ?r ?g)
        )
      )
      0.2679064080603458
      (injected-0)
      0.18209359193965416
      (
        not
        (injected-0)
      )
    )
  )
  (
    :action
    drop
    :parameters
    (?r ?obj ?room ?g)
    :precondition
    (
      and
      (carry ?r ?obj ?g)
      (at-robby ?r ?room)
      (robot____ ?r)
      (stuff____ ?obj)
      (room_____ ?room)
      (gripper__ ?g)
    )
    :effect
    (
      probabilistic
      0.5
      (
        and
        (at ?obj ?room)
        (free ?r ?g)
        (
          not
          (carry ?r ?obj ?g)
        )
      )
      0.21864268343057067
      (injected-0)
      0.23135731656942934
      (
        not
        (injected-0)
      )
    )
  )
)