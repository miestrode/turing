(define (problem strips-sat-x-1)
(:domain satellite)
(:objects
	satellite0 - satellite
	instrument0 - instrument
	instrument1 - instrument
	satellite1 - satellite
	instrument2 - instrument
	instrument3 - instrument
	instrument4 - instrument
	satellite2 - satellite
	instrument5 - instrument
	instrument6 - instrument
	instrument7 - instrument
	image2 - mode
	infrared0 - mode
	image1 - mode
	GroundStation4 - direction
	Star5 - direction
	Star6 - direction
	Star3 - direction
	GroundStation9 - direction
	GroundStation7 - direction
	GroundStation8 - direction
	Star1 - direction
	Star2 - direction
	Star0 - direction
	Star10 - direction
	Planet11 - direction
	Star12 - direction
	Planet13 - direction
	Phenomenon14 - direction
	Planet15 - direction
)
(:init
	(supports instrument0 image2)
	(supports instrument0 image1)
	(calibration_target instrument0 Star3)
	(supports instrument1 infrared0)
	(supports instrument1 image1)
	(calibration_target instrument1 GroundStation8)
	(on_board instrument0 satellite0)
	(on_board instrument1 satellite0)
	(power_avail satellite0)
	(pointing satellite0 Planet15)
	(supports instrument2 image2)
	(supports instrument2 image1)
	(supports instrument2 infrared0)
	(calibration_target instrument2 Star2)
	(supports instrument3 infrared0)
	(supports instrument3 image1)
	(supports instrument3 image2)
	(calibration_target instrument3 GroundStation9)
	(calibration_target instrument3 Star2)
	(supports instrument4 image2)
	(calibration_target instrument4 GroundStation7)
	(on_board instrument2 satellite1)
	(on_board instrument3 satellite1)
	(on_board instrument4 satellite1)
	(power_avail satellite1)
	(pointing satellite1 GroundStation9)
	(supports instrument5 infrared0)
	(supports instrument5 image1)
	(calibration_target instrument5 Star2)
	(calibration_target instrument5 GroundStation8)
	(supports instrument6 infrared0)
	(supports instrument6 image1)
	(supports instrument6 image2)
	(calibration_target instrument6 Star1)
	(supports instrument7 image2)
	(supports instrument7 infrared0)
	(supports instrument7 image1)
	(calibration_target instrument7 Star0)
	(calibration_target instrument7 Star2)
	(on_board instrument5 satellite2)
	(on_board instrument6 satellite2)
	(on_board instrument7 satellite2)
	(power_avail satellite2)
	(pointing satellite2 Star5)
)
(:goal (and
	(pointing satellite0 GroundStation8)
	(pointing satellite2 Star2)
	(have_image Star10 infrared0)
	(have_image Planet11 image2)
	(have_image Star12 image2)
	(have_image Planet13 image2)
	(have_image Phenomenon14 infrared0)
	(have_image Planet15 image1)
))

)
