(define (problem strips-sat-x-1)
(:domain satellite)
(:objects
	satellite0 - satellite
	instrument0 - instrument
	satellite1 - satellite
	instrument1 - instrument
	instrument2 - instrument
	instrument3 - instrument
	infrared0 - mode
	image2 - mode
	image1 - mode
	Star2 - direction
	GroundStation4 - direction
	Star6 - direction
	GroundStation8 - direction
	GroundStation7 - direction
	Star3 - direction
	Star1 - direction
	Star5 - direction
	GroundStation9 - direction
	Star0 - direction
	Star10 - direction
	Planet11 - direction
	Star12 - direction
	Planet13 - direction
	Phenomenon14 - direction
	Planet15 - direction
	Star16 - direction
)
(:init
	(supports instrument0 image1)
	(supports instrument0 infrared0)
	(calibration_target instrument0 Star3)
	(calibration_target instrument0 GroundStation7)
	(on_board instrument0 satellite0)
	(power_avail satellite0)
	(pointing satellite0 Star16)
	(supports instrument1 image1)
	(supports instrument1 infrared0)
	(supports instrument1 image2)
	(calibration_target instrument1 Star3)
	(calibration_target instrument1 Star1)
	(supports instrument2 image2)
	(supports instrument2 image1)
	(supports instrument2 infrared0)
	(calibration_target instrument2 Star0)
	(calibration_target instrument2 Star1)
	(supports instrument3 image1)
	(calibration_target instrument3 Star0)
	(calibration_target instrument3 GroundStation9)
	(calibration_target instrument3 Star5)
	(on_board instrument1 satellite1)
	(on_board instrument2 satellite1)
	(on_board instrument3 satellite1)
	(power_avail satellite1)
	(pointing satellite1 Phenomenon14)
)
(:goal (and
	(pointing satellite0 Star6)
	(have_image Star10 infrared0)
	(have_image Planet11 image2)
	(have_image Star12 image2)
	(have_image Planet13 image2)
	(have_image Phenomenon14 infrared0)
	(have_image Planet15 image1)
	(have_image Star16 image2)
))

)
