(
  define
  (problem instance-1)
  (:domain gripper-strips)
  (:objects lgripper3 robot3 room2 lgripper1 room1 ball1 rgripper3 rgripper2 rgripper1 room3 robot2 ball4 lgripper2 ball3 robot1 ball2)
  (
    :init
    (at-robby robot2 room3)
    (free robot2 lgripper2)
    (free robot3 lgripper3)
    (at-robby robot1 room3)
    (at-robby robot3 room3)
    (gripper__ lgripper1)
    (room_____ room3)
    (robot____ robot3)
    (stuff____ ball4)
    (room_____ room2)
    (gripper__ rgripper3)
    (room_____ room1)
    (gripper__ lgripper3)
    (robot____ robot2)
    (free robot1 lgripper1)
    (at ball4 room1)
    (free robot1 rgripper1)
    (at ball2 room3)
    (stuff____ ball2)
    (gripper__ lgripper2)
    (at ball3 room2)
    (at ball1 room3)
    (stuff____ ball3)
    (gripper__ rgripper2)
    (stuff____ ball1)
    (free robot2 rgripper2)
    (robot____ robot1)
    (free robot3 rgripper3)
    (gripper__ rgripper1)
    (injected-0)
  )
  (
    :goal
    (
      and
      (at ball1 room3)
      (at ball2 room1)
      (at ball3 room2)
      (at ball4 room2)
      (injected-0)
    )
  )
)