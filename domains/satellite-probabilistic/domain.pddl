(
  define
  (domain satellite)
  (
    :predicates
    (pointing ?s ?d)
    (on_board ?i ?s)
    (mode_______________ ?x)
    (supports ?i ?m)
    (have_image ?d ?m)
    (direction__________ ?x)
    (calibration_target ?i ?d)
    (instrument_________ ?x)
    (power_avail ?s)
    (calibrated ?i)
    (satellite__________ ?x)
    (power_on ?i)
    (injected-----------0)
  )
  (
    :action
    switch_off
    :parameters
    (?i ?s)
    :precondition
    (
      and
      (on_board ?i ?s)
      (power_on ?i)
      (instrument_________ ?i)
      (satellite__________ ?s)
    )
    :effect
    (
      probabilistic
      0.5
      (
        and
        (
          not
          (power_on ?i)
        )
        (power_avail ?s)
      )
      0.17030674026602394
      (injected-----------0)
      0.27969325973397613
      (
        not
        (injected-----------0)
      )
    )
  )
  (
    :action
    turn_to
    :parameters
    (?s ?d_new ?d_prev)
    :precondition
    (
      and
      (pointing ?s ?d_prev)
      (satellite__________ ?s)
      (direction__________ ?d_new)
      (direction__________ ?d_prev)
    )
    :effect
    (
      probabilistic
      0.5
      (
        and
        (pointing ?s ?d_new)
        (
          not
          (pointing ?s ?d_prev)
        )
      )
      0.2647783816248801
      (injected-----------0)
      0.1852216183751199
      (
        not
        (injected-----------0)
      )
    )
  )
  (
    :action
    take_image
    :parameters
    (?s ?d ?i ?m)
    :precondition
    (
      and
      (calibrated ?i)
      (on_board ?i ?s)
      (supports ?i ?m)
      (power_on ?i)
      (pointing ?s ?d)
      (satellite__________ ?s)
      (direction__________ ?d)
      (instrument_________ ?i)
      (mode_______________ ?m)
    )
    :effect
    (
      probabilistic
      0.5
      (have_image ?d ?m)
      0.3140672758148185
      (injected-----------0)
      0.1359327241851815
      (
        not
        (injected-----------0)
      )
    )
  )
  (
    :action
    switch_on
    :parameters
    (?i ?s)
    :precondition
    (
      and
      (on_board ?i ?s)
      (power_avail ?s)
      (instrument_________ ?i)
      (satellite__________ ?s)
    )
    :effect
    (
      probabilistic
      0.5
      (
        and
        (power_on ?i)
        (
          not
          (calibrated ?i)
        )
        (
          not
          (power_avail ?s)
        )
      )
      0.20280139293512467
      (injected-----------0)
      0.24719860706487534
      (
        not
        (injected-----------0)
      )
    )
  )
  (
    :action
    calibrate
    :parameters
    (?s ?i ?d)
    :precondition
    (
      and
      (on_board ?i ?s)
      (calibration_target ?i ?d)
      (pointing ?s ?d)
      (power_on ?i)
      (satellite__________ ?s)
      (instrument_________ ?i)
      (direction__________ ?d)
    )
    :effect
    (
      probabilistic
      0.5
      (calibrated ?i)
      0.21768172099700528
      (injected-----------0)
      0.23231827900299476
      (
        not
        (injected-----------0)
      )
    )
  )
)