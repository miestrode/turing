(
  define
  (domain logistics-strips)
  (
    :predicates
    (location ?loc)
    (obj ?obj)
    (in ?obj1 ?obj2)
    (truck ?truck)
    (at ?obj ?loc)
    (airplane ?airplane)
    (city ?city)
    (airport ?airport)
    (in-city ?obj ?city)
    (injected-0)
  )
  (
    :action
    load-truck
    :parameters
    (?obj ?truck ?loc)
    :precondition
    (
      and
      (obj ?obj)
      (truck ?truck)
      (location ?loc)
      (at ?truck ?loc)
      (at ?obj ?loc)
    )
    :effect
    (
      probabilistic
      0.5
      (
        and
        (
          not
          (at ?obj ?loc)
        )
        (in ?obj ?truck)
      )
      0.14692926456993996
      (injected-0)
      0.3030707354300601
      (
        not
        (injected-0)
      )
    )
  )
  (
    :action
    unload-airplane
    :parameters
    (?obj ?airplane ?loc)
    :precondition
    (
      and
      (obj ?obj)
      (airplane ?airplane)
      (location ?loc)
      (in ?obj ?airplane)
      (at ?airplane ?loc)
    )
    :effect
    (
      probabilistic
      0.5
      (
        and
        (
          not
          (in ?obj ?airplane)
        )
        (at ?obj ?loc)
      )
      0.1815070140787075
      (injected-0)
      0.26849298592129245
      (
        not
        (injected-0)
      )
    )
  )
  (
    :action
    drive-truck
    :parameters
    (?truck ?loc-from ?loc-to ?city)
    :precondition
    (
      and
      (truck ?truck)
      (location ?loc-from)
      (location ?loc-to)
      (city ?city)
      (at ?truck ?loc-from)
      (in-city ?loc-from ?city)
      (in-city ?loc-to ?city)
    )
    :effect
    (
      probabilistic
      0.5
      (
        and
        (
          not
          (at ?truck ?loc-from)
        )
        (at ?truck ?loc-to)
      )
      0.33196760844812
      (injected-0)
      0.11803239155187993
      (
        not
        (injected-0)
      )
    )
  )
  (
    :action
    load-airplane
    :parameters
    (?obj ?airplane ?loc)
    :precondition
    (
      and
      (obj ?obj)
      (airplane ?airplane)
      (location ?loc)
      (at ?obj ?loc)
      (at ?airplane ?loc)
    )
    :effect
    (
      probabilistic
      0.5
      (
        and
        (
          not
          (at ?obj ?loc)
        )
        (in ?obj ?airplane)
      )
      0.21145045764698195
      (injected-0)
      0.23854954235301806
      (
        not
        (injected-0)
      )
    )
  )
  (
    :action
    fly-airplane
    :parameters
    (?airplane ?loc-from ?loc-to)
    :precondition
    (
      and
      (airplane ?airplane)
      (airport ?loc-from)
      (airport ?loc-to)
      (at ?airplane ?loc-from)
    )
    :effect
    (
      probabilistic
      0.5
      (
        and
        (
          not
          (at ?airplane ?loc-from)
        )
        (at ?airplane ?loc-to)
      )
      0.1986111620105034
      (injected-0)
      0.2513888379894966
      (
        not
        (injected-0)
      )
    )
  )
  (
    :action
    unload-truck
    :parameters
    (?obj ?truck ?loc)
    :precondition
    (
      and
      (obj ?obj)
      (truck ?truck)
      (location ?loc)
      (at ?truck ?loc)
      (in ?obj ?truck)
    )
    :effect
    (
      probabilistic
      0.5
      (
        and
        (
          not
          (in ?obj ?truck)
        )
        (at ?obj ?loc)
      )
      0.05004037445457915
      (injected-0)
      0.39995962554542086
      (
        not
        (injected-0)
      )
    )
  )
)