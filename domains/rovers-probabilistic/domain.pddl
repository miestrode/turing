(
  define
  (domain rover)
  (
    :predicates
    (have_image ?r ?o ?m)
    (equipped_for_soil_analysis ?r)
    (store_of ?s ?r)
    (store______________________ ?x)
    (waypoint___________________ ?x)
    (full ?s)
    (communicated_rock_data ?w)
    (communicated_image_data ?o ?m)
    (objective__________________ ?x)
    (can_traverse ?r ?x ?y)
    (calibrated ?c ?r)
    (rover______________________ ?x)
    (communicated_soil_data ?w)
    (channel_free ?l)
    (have_soil_analysis ?r ?w)
    (at_soil_sample ?w)
    (on_board ?i ?r)
    (at ?x ?y)
    (equipped_for_rock_analysis ?r)
    (camera_____________________ ?x)
    (supports ?c ?m)
    (lander_____________________ ?x)
    (visible ?w ?p)
    (at_lander ?x ?y)
    (calibration_target ?i ?o)
    (visible_from ?o ?w)
    (empty ?s)
    (mode_______________________ ?x)
    (equipped_for_imaging ?r)
    (have_rock_analysis ?r ?w)
    (available ?r)
    (at_rock_sample ?w)
    (injected-------------------0)
  )
  (
    :action
    communicate_rock_data
    :parameters
    (?r ?l ?p ?x ?y)
    :precondition
    (
      and
      (at ?r ?x)
      (at_lander ?l ?y)
      (have_rock_analysis ?r ?p)
      (visible ?x ?y)
      (available ?r)
      (channel_free ?l)
      (rover______________________ ?r)
      (lander_____________________ ?l)
      (waypoint___________________ ?p)
      (waypoint___________________ ?x)
      (waypoint___________________ ?y)
    )
    :effect
    (
      probabilistic
      0.5
      (
        and
        (
          not
          (available ?r)
        )
        (
          not
          (channel_free ?l)
        )
        (channel_free ?l)
        (communicated_rock_data ?p)
        (available ?r)
      )
      0.4410025817325926
      (injected-------------------0)
      0.008997418267407358
      (
        not
        (injected-------------------0)
      )
    )
  )
  (
    :action
    drop
    :parameters
    (?x ?y)
    :precondition
    (
      and
      (store_of ?y ?x)
      (full ?y)
      (rover______________________ ?x)
      (store______________________ ?y)
    )
    :effect
    (
      probabilistic
      0.5
      (
        and
        (
          not
          (full ?y)
        )
        (empty ?y)
      )
      0.22438400518743115
      (injected-------------------0)
      0.22561599481256892
      (
        not
        (injected-------------------0)
      )
    )
  )
  (
    :action
    communicate_soil_data
    :parameters
    (?r ?l ?p ?x ?y)
    :precondition
    (
      and
      (at ?r ?x)
      (at_lander ?l ?y)
      (have_soil_analysis ?r ?p)
      (visible ?x ?y)
      (available ?r)
      (channel_free ?l)
      (rover______________________ ?r)
      (lander_____________________ ?l)
      (waypoint___________________ ?p)
      (waypoint___________________ ?x)
      (waypoint___________________ ?y)
    )
    :effect
    (
      probabilistic
      0.5
      (
        and
        (
          not
          (available ?r)
        )
        (
          not
          (channel_free ?l)
        )
        (channel_free ?l)
        (communicated_soil_data ?p)
        (available ?r)
      )
      0.15658586590562634
      (injected-------------------0)
      0.2934141340943736
      (
        not
        (injected-------------------0)
      )
    )
  )
  (
    :action
    sample_soil
    :parameters
    (?x ?s ?p)
    :precondition
    (
      and
      (at ?x ?p)
      (at_soil_sample ?p)
      (equipped_for_soil_analysis ?x)
      (store_of ?s ?x)
      (empty ?s)
      (rover______________________ ?x)
      (store______________________ ?s)
      (waypoint___________________ ?p)
    )
    :effect
    (
      probabilistic
      0.5
      (
        and
        (
          not
          (empty ?s)
        )
        (full ?s)
        (have_soil_analysis ?x ?p)
        (
          not
          (at_soil_sample ?p)
        )
      )
      0.15618930138607665
      (injected-------------------0)
      0.29381069861392334
      (
        not
        (injected-------------------0)
      )
    )
  )
  (
    :action
    communicate_image_data
    :parameters
    (?r ?l ?o ?m ?x ?y)
    :precondition
    (
      and
      (at ?r ?x)
      (at_lander ?l ?y)
      (have_image ?r ?o ?m)
      (visible ?x ?y)
      (available ?r)
      (channel_free ?l)
      (rover______________________ ?r)
      (lander_____________________ ?l)
      (objective__________________ ?o)
      (mode_______________________ ?m)
      (waypoint___________________ ?x)
      (waypoint___________________ ?y)
    )
    :effect
    (
      probabilistic
      0.5
      (
        and
        (
          not
          (available ?r)
        )
        (
          not
          (channel_free ?l)
        )
        (channel_free ?l)
        (communicated_image_data ?o ?m)
        (available ?r)
      )
      0.0678711662841773
      (injected-------------------0)
      0.3821288337158227
      (
        not
        (injected-------------------0)
      )
    )
  )
  (
    :action
    navigate
    :parameters
    (?x ?y ?z)
    :precondition
    (
      and
      (can_traverse ?x ?y ?z)
      (available ?x)
      (at ?x ?y)
      (visible ?y ?z)
      (rover______________________ ?x)
      (waypoint___________________ ?y)
      (waypoint___________________ ?z)
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
      0.1422501104210403
      (injected-------------------0)
      0.3077498895789597
      (
        not
        (injected-------------------0)
      )
    )
  )
  (
    :action
    sample_rock
    :parameters
    (?x ?s ?p)
    :precondition
    (
      and
      (at ?x ?p)
      (at_rock_sample ?p)
      (equipped_for_rock_analysis ?x)
      (store_of ?s ?x)
      (empty ?s)
      (rover______________________ ?x)
      (store______________________ ?s)
      (waypoint___________________ ?p)
    )
    :effect
    (
      probabilistic
      0.5
      (
        and
        (
          not
          (empty ?s)
        )
        (full ?s)
        (have_rock_analysis ?x ?p)
        (
          not
          (at_rock_sample ?p)
        )
      )
      0.30877533997806794
      (injected-------------------0)
      0.141224660021932
      (
        not
        (injected-------------------0)
      )
    )
  )
  (
    :action
    take_image
    :parameters
    (?r ?p ?o ?i ?m)
    :precondition
    (
      and
      (calibrated ?i ?r)
      (on_board ?i ?r)
      (equipped_for_imaging ?r)
      (supports ?i ?m)
      (visible_from ?o ?p)
      (at ?r ?p)
      (rover______________________ ?r)
      (waypoint___________________ ?p)
      (objective__________________ ?o)
      (camera_____________________ ?i)
      (mode_______________________ ?m)
    )
    :effect
    (
      probabilistic
      0.5
      (
        and
        (have_image ?r ?o ?m)
        (
          not
          (calibrated ?i ?r)
        )
      )
      0.34316868001462597
      (injected-------------------0)
      0.10683131998537408
      (
        not
        (injected-------------------0)
      )
    )
  )
  (
    :action
    calibrate
    :parameters
    (?r ?i ?t ?w)
    :precondition
    (
      and
      (equipped_for_imaging ?r)
      (calibration_target ?i ?t)
      (at ?r ?w)
      (visible_from ?t ?w)
      (on_board ?i ?r)
      (rover______________________ ?r)
      (camera_____________________ ?i)
      (objective__________________ ?t)
      (waypoint___________________ ?w)
    )
    :effect
    (
      probabilistic
      0.5
      (calibrated ?i ?r)
      0.2833697739318281
      (injected-------------------0)
      0.1666302260681719
      (
        not
        (injected-------------------0)
      )
    )
  )
)