(define (problem strips-sat-x-1)
(:domain satellite)
(:objects
	satellite0 - satellite
	instrument0 - instrument
	satellite1 - satellite
	instrument1 - instrument
	instrument2 - instrument
	image1 - mode
	infrared0 - mode
	image2 - mode
	Star2 - direction
	Star3 - direction
	Star5 - direction
	Star6 - direction
	GroundStation7 - direction
	Star0 - direction
	GroundStation4 - direction
	Star1 - direction
	Planet8 - direction
	Star9 - direction
	Planet10 - direction
	Star11 - direction
)
(:init
	(supports instrument0 image1)
	(supports instrument0 image2)
	(calibration_target instrument0 GroundStation4)
	(on_board instrument0 satellite0)
	(power_avail satellite0)
	(pointing satellite0 GroundStation7)
	(supports instrument1 infrared0)
	(supports instrument1 image1)
	(supports instrument1 image2)
	(calibration_target instrument1 GroundStation4)
	(calibration_target instrument1 Star0)
	(supports instrument2 image2)
	(supports instrument2 infrared0)
	(calibration_target instrument2 Star1)
	(on_board instrument1 satellite1)
	(on_board instrument2 satellite1)
	(power_avail satellite1)
	(pointing satellite1 Star9)
)
(:goal (and
	(have_image Planet8 infrared0)
	(have_image Star9 infrared0)
	(have_image Planet10 image1)
	(have_image Star11 infrared0)
))

)
