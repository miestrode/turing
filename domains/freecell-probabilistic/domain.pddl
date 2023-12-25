(
  define
  (domain freecell)
  (
    :predicates
    (suit ?c ?s)
    (cellspace ?n)
    (canstack ?c1 ?c2)
    (bottomcol ?c)
    (suit______ ?x)
    (successor ?n1 ?n0)
    (incell ?c)
    (num_______ ?x)
    (clear ?c)
    (value ?c ?v)
    (card______ ?x)
    (on ?c1 ?c2)
    (home ?c)
    (colspace ?n)
    (injected--0)
  )
  (
    :action
    sendtofree-b
    :parameters
    (?card ?cells ?ncells ?cols ?ncols)
    :precondition
    (
      and
      (clear ?card)
      (bottomcol ?card)
      (cellspace ?cells)
      (successor ?cells ?ncells)
      (colspace ?cols)
      (successor ?ncols ?cols)
      (card______ ?card)
      (num_______ ?cells)
      (num_______ ?ncells)
      (num_______ ?cols)
      (num_______ ?ncols)
    )
    :effect
    (
      probabilistic
      0.5
      (
        and
        (incell ?card)
        (colspace ?ncols)
        (cellspace ?ncells)
        (
          not
          (bottomcol ?card)
        )
        (
          not
          (clear ?card)
        )
        (
          not
          (colspace ?cols)
        )
        (
          not
          (cellspace ?cells)
        )
      )
      0.2205942463201735
      (injected--0)
      0.22940575367982652
      (
        not
        (injected--0)
      )
    )
  )
  (
    :action
    sendtohome
    :parameters
    (?card ?oldcard ?suit ?vcard ?homecard ?vhomecard)
    :precondition
    (
      and
      (clear ?card)
      (on ?card ?oldcard)
      (home ?homecard)
      (suit ?card ?suit)
      (suit ?homecard ?suit)
      (value ?card ?vcard)
      (value ?homecard ?vhomecard)
      (successor ?vcard ?vhomecard)
      (card______ ?card)
      (card______ ?oldcard)
      (suit______ ?suit)
      (num_______ ?vcard)
      (card______ ?homecard)
      (num_______ ?vhomecard)
    )
    :effect
    (
      probabilistic
      0.5
      (
        and
        (home ?card)
        (clear ?oldcard)
        (
          not
          (on ?card ?oldcard)
        )
        (
          not
          (home ?homecard)
        )
        (
          not
          (clear ?card)
        )
      )
      0.38804099917782753
      (injected--0)
      0.061959000822172455
      (
        not
        (injected--0)
      )
    )
  )
  (
    :action
    homefromfreecell
    :parameters
    (?card ?suit ?vcard ?homecard ?vhomecard ?cells ?ncells)
    :precondition
    (
      and
      (incell ?card)
      (home ?homecard)
      (suit ?card ?suit)
      (suit ?homecard ?suit)
      (value ?card ?vcard)
      (value ?homecard ?vhomecard)
      (successor ?vcard ?vhomecard)
      (cellspace ?cells)
      (successor ?ncells ?cells)
      (card______ ?card)
      (suit______ ?suit)
      (num_______ ?vcard)
      (card______ ?homecard)
      (num_______ ?vhomecard)
      (num_______ ?cells)
      (num_______ ?ncells)
    )
    :effect
    (
      probabilistic
      0.5
      (
        and
        (home ?card)
        (cellspace ?ncells)
        (
          not
          (incell ?card)
        )
        (
          not
          (cellspace ?cells)
        )
        (
          not
          (home ?homecard)
        )
      )
      0.2703757102364126
      (injected--0)
      0.17962428976358738
      (
        not
        (injected--0)
      )
    )
  )
  (
    :action
    sendtofree
    :parameters
    (?card ?oldcard ?cells ?ncells)
    :precondition
    (
      and
      (clear ?card)
      (on ?card ?oldcard)
      (cellspace ?cells)
      (successor ?cells ?ncells)
      (card______ ?card)
      (card______ ?oldcard)
      (num_______ ?cells)
      (num_______ ?ncells)
    )
    :effect
    (
      probabilistic
      0.5
      (
        and
        (incell ?card)
        (clear ?oldcard)
        (cellspace ?ncells)
        (
          not
          (on ?card ?oldcard)
        )
        (
          not
          (clear ?card)
        )
        (
          not
          (cellspace ?cells)
        )
      )
      0.2776145063098678
      (injected--0)
      0.17238549369013223
      (
        not
        (injected--0)
      )
    )
  )
  (
    :action
    newcolfromfreecell
    :parameters
    (?card ?cols ?ncols ?cells ?ncells)
    :precondition
    (
      and
      (incell ?card)
      (colspace ?cols)
      (cellspace ?cells)
      (successor ?cols ?ncols)
      (successor ?ncells ?cells)
      (card______ ?card)
      (num_______ ?cols)
      (num_______ ?ncols)
      (num_______ ?cells)
      (num_______ ?ncells)
    )
    :effect
    (
      probabilistic
      0.5
      (
        and
        (bottomcol ?card)
        (clear ?card)
        (colspace ?ncols)
        (cellspace ?ncells)
        (
          not
          (incell ?card)
        )
        (
          not
          (colspace ?cols)
        )
        (
          not
          (cellspace ?cells)
        )
      )
      0.37660028677594604
      (injected--0)
      0.07339971322405396
      (
        not
        (injected--0)
      )
    )
  )
  (
    :action
    move-b
    :parameters
    (?card ?newcard ?cols ?ncols)
    :precondition
    (
      and
      (clear ?card)
      (bottomcol ?card)
      (clear ?newcard)
      (canstack ?card ?newcard)
      (colspace ?cols)
      (successor ?ncols ?cols)
      (card______ ?card)
      (card______ ?newcard)
      (num_______ ?cols)
      (num_______ ?ncols)
    )
    :effect
    (
      probabilistic
      0.5
      (
        and
        (on ?card ?newcard)
        (colspace ?ncols)
        (
          not
          (bottomcol ?card)
        )
        (
          not
          (clear ?newcard)
        )
        (
          not
          (colspace ?cols)
        )
      )
      0.3588764732069421
      (injected--0)
      0.09112352679305792
      (
        not
        (injected--0)
      )
    )
  )
  (
    :action
    move
    :parameters
    (?card ?oldcard ?newcard)
    :precondition
    (
      and
      (clear ?card)
      (clear ?newcard)
      (canstack ?card ?newcard)
      (on ?card ?oldcard)
      (card______ ?card)
      (card______ ?oldcard)
      (card______ ?newcard)
    )
    :effect
    (
      probabilistic
      0.5
      (
        and
        (on ?card ?newcard)
        (clear ?oldcard)
        (
          not
          (on ?card ?oldcard)
        )
        (
          not
          (clear ?newcard)
        )
      )
      0.2959609699296453
      (injected--0)
      0.15403903007035472
      (
        not
        (injected--0)
      )
    )
  )
  (
    :action
    sendtohome-b
    :parameters
    (?card ?suit ?vcard ?homecard ?vhomecard ?cols ?ncols)
    :precondition
    (
      and
      (clear ?card)
      (bottomcol ?card)
      (home ?homecard)
      (suit ?card ?suit)
      (suit ?homecard ?suit)
      (value ?card ?vcard)
      (value ?homecard ?vhomecard)
      (successor ?vcard ?vhomecard)
      (colspace ?cols)
      (successor ?ncols ?cols)
      (card______ ?card)
      (suit______ ?suit)
      (num_______ ?vcard)
      (card______ ?homecard)
      (num_______ ?vhomecard)
      (num_______ ?cols)
      (num_______ ?ncols)
    )
    :effect
    (
      probabilistic
      0.5
      (
        and
        (home ?card)
        (colspace ?ncols)
        (
          not
          (home ?homecard)
        )
        (
          not
          (clear ?card)
        )
        (
          not
          (bottomcol ?card)
        )
        (
          not
          (colspace ?cols)
        )
      )
      0.356815126342315
      (injected--0)
      0.09318487365768502
      (
        not
        (injected--0)
      )
    )
  )
  (
    :action
    colfromfreecell
    :parameters
    (?card ?newcard ?cells ?ncells)
    :precondition
    (
      and
      (incell ?card)
      (clear ?newcard)
      (canstack ?card ?newcard)
      (cellspace ?cells)
      (successor ?ncells ?cells)
      (card______ ?card)
      (card______ ?newcard)
      (num_______ ?cells)
      (num_______ ?ncells)
    )
    :effect
    (
      probabilistic
      0.5
      (
        and
        (cellspace ?ncells)
        (clear ?card)
        (on ?card ?newcard)
        (
          not
          (incell ?card)
        )
        (
          not
          (cellspace ?cells)
        )
        (
          not
          (clear ?newcard)
        )
      )
      0.1891651499020473
      (injected--0)
      0.26083485009795265
      (
        not
        (injected--0)
      )
    )
  )
  (
    :action
    sendtonewcol
    :parameters
    (?card ?oldcard ?cols ?ncols)
    :precondition
    (
      and
      (clear ?card)
      (colspace ?cols)
      (successor ?cols ?ncols)
      (on ?card ?oldcard)
      (card______ ?card)
      (card______ ?oldcard)
      (num_______ ?cols)
      (num_______ ?ncols)
    )
    :effect
    (
      probabilistic
      0.5
      (
        and
        (bottomcol ?card)
        (clear ?oldcard)
        (colspace ?ncols)
        (
          not
          (on ?card ?oldcard)
        )
        (
          not
          (colspace ?cols)
        )
      )
      0.17469746860920918
      (injected--0)
      0.27530253139079086
      (
        not
        (injected--0)
      )
    )
  )
)