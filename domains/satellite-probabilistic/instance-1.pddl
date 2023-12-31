(
  define
  (problem instance-1)
  (:domain satellite)
  (:objects star2 instrument1 star9 star0 instrument0 image2 satellite1 star11 star6 groundstation7 instrument2 star1 satellite0 planet8 star3 infrared0 groundstation4 star5 image1 planet10)
  (
    :init
    (calibration_target instrument1 groundstation4)
    (instrument_________ instrument2)
    (supports instrument1 image1)
    (calibration_target instrument1 star0)
    (direction__________ star9)
    (supports instrument2 image2)
    (instrument_________ instrument0)
    (direction__________ star11)
    (satellite__________ satellite1)
    (direction__________ groundstation7)
    (supports instrument2 infrared0)
    (mode_______________ image1)
    (pointing satellite0 groundstation7)
    (direction__________ groundstation4)
    (instrument_________ instrument1)
    (pointing satellite1 star9)
    (calibration_target instrument2 star1)
    (direction__________ planet8)
    (direction__________ star6)
    (supports instrument0 image2)
    (direction__________ star0)
    (power_avail satellite0)
    (direction__________ star3)
    (direction__________ star1)
    (on_board instrument1 satellite1)
    (supports instrument1 image2)
    (calibration_target instrument0 groundstation4)
    (direction__________ star5)
    (on_board instrument0 satellite0)
    (on_board instrument2 satellite1)
    (supports instrument1 infrared0)
    (direction__________ planet10)
    (satellite__________ satellite0)
    (supports instrument0 image1)
    (direction__________ star2)
    (mode_______________ image2)
    (power_avail satellite1)
    (mode_______________ infrared0)
    (injected-----------0)
  )
  (
    :goal
    (
      and
      (have_image planet8 infrared0)
      (have_image star9 infrared0)
      (have_image planet10 image1)
      (have_image star11 infrared0)
      (injected-----------0)
    )
  )
)