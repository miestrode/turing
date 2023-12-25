(define (problem strips-sat-x-1)
(:domain satellite)
(:objects
	satellite0 - satellite
	instrument0 - instrument
	instrument1 - instrument
	instrument2 - instrument
	satellite1 - satellite
	instrument3 - instrument
	instrument4 - instrument
	instrument5 - instrument
	satellite2 - satellite
	instrument6 - instrument
	instrument7 - instrument
	instrument8 - instrument
	infrared0 - mode
	image2 - mode
	image1 - mode
	infrared3 - mode
	Star3 - direction
	GroundStation6 - direction
	GroundStation9 - direction
	GroundStation4 - direction
	Star7 - direction
	GroundStation2 - direction
	GroundStation8 - direction
	GroundStation0 - direction
	GroundStation1 - direction
	GroundStation10 - direction
	Star5 - direction
	Star11 - direction
	Phenomenon12 - direction
	Phenomenon13 - direction
	Planet14 - direction
	Planet15 - direction
	Planet16 - direction
	Star17 - direction
)
(:init
	(supports instrument0 infrared3)
	(supports instrument0 infrared0)
	(calibration_target instrument0 GroundStation4)
	(supports instrument1 infrared3)
	(calibration_target instrument1 Star5)
	(calibration_target instrument1 GroundStation0)
	(supports instrument2 infrared3)
	(calibration_target instrument2 GroundStation10)
	(calibration_target instrument2 GroundStation0)
	(calibration_target instrument2 GroundStation8)
	(on_board instrument0 satellite0)
	(on_board instrument1 satellite0)
	(on_board instrument2 satellite0)
	(power_avail satellite0)
	(pointing satellite0 Planet14)
	(supports instrument3 image1)
	(calibration_target instrument3 Star5)
	(calibration_target instrument3 GroundStation1)
	(supports instrument4 image1)
	(supports instrument4 infrared3)
	(supports instrument4 image2)
	(calibration_target instrument4 Star7)
	(supports instrument5 infrared3)
	(calibration_target instrument5 Star7)
	(on_board instrument3 satellite1)
	(on_board instrument4 satellite1)
	(on_board instrument5 satellite1)
	(power_avail satellite1)
	(pointing satellite1 GroundStation1)
	(supports instrument6 image1)
	(calibration_target instrument6 GroundStation8)
	(calibration_target instrument6 GroundStation2)
	(supports instrument7 image1)
	(supports instrument7 infrared0)
	(calibration_target instrument7 GroundStation1)
	(calibration_target instrument7 GroundStation0)
	(supports instrument8 infrared3)
	(supports instrument8 image1)
	(calibration_target instrument8 Star5)
	(calibration_target instrument8 GroundStation10)
	(on_board instrument6 satellite2)
	(on_board instrument7 satellite2)
	(on_board instrument8 satellite2)
	(power_avail satellite2)
	(pointing satellite2 Planet16)
)
(:goal (and
	(pointing satellite0 Star7)
	(pointing satellite1 Planet15)
	(pointing satellite2 Planet15)
	(have_image Star11 image1)
	(have_image Phenomenon12 image1)
	(have_image Phenomenon13 infrared3)
	(have_image Planet14 image2)
	(have_image Planet15 infrared0)
	(have_image Planet16 infrared3)
	(have_image Star17 image1)
))

)
