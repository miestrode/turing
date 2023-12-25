(
  define
  (problem instance-5)
  (:domain gripper-strips)
  (:objects lgripper3 ball12 robot8 robot9 lgripper1 rgripper9 room8 ball1 ball7 rgripper3 robot4 rgripper8 room12 rgripper7 room13 rgripper1 room3 ball3 robot1 ball2 rgripper4 lgripper7 room16 ball10 robot6 robot3 room2 room17 lgripper5 room6 room4 ball5 lgripper4 room1 room10 ball9 ball14 room11 lgripper8 ball11 room9 room7 lgripper9 rgripper2 ball13 room14 robot5 rgripper5 ball8 robot2 ball4 robot7 lgripper2 ball15 room15 lgripper6 rgripper6 ball6 room5)
  (
    :init
    (free robot3 lgripper3)
    (gripper__ lgripper1)
    (room_____ room9)
    (at-robby robot6 room13)
    (at ball4 room13)
    (stuff____ ball10)
    (robot____ robot2)
    (gripper__ lgripper5)
    (gripper__ rgripper8)
    (free robot9 rgripper9)
    (stuff____ ball2)
    (free robot4 lgripper4)
    (gripper__ lgripper7)
    (gripper__ rgripper9)
    (at-robby robot3 room15)
    (stuff____ ball1)
    (robot____ robot5)
    (room_____ room10)
    (stuff____ ball15)
    (robot____ robot1)
    (stuff____ ball14)
    (free robot5 lgripper5)
    (free robot7 rgripper7)
    (room_____ room4)
    (robot____ robot3)
    (free robot6 rgripper6)
    (robot____ robot8)
    (room_____ room2)
    (gripper__ lgripper9)
    (at ball7 room12)
    (at ball15 room9)
    (gripper__ rgripper3)
    (free robot6 lgripper6)
    (free robot1 lgripper1)
    (room_____ room5)
    (gripper__ lgripper4)
    (free robot9 lgripper9)
    (gripper__ rgripper2)
    (gripper__ lgripper6)
    (room_____ room13)
    (free robot4 rgripper4)
    (at ball10 room14)
    (at ball1 room9)
    (room_____ room7)
    (robot____ robot9)
    (at ball14 room2)
    (free robot8 rgripper8)
    (at ball12 room1)
    (stuff____ ball11)
    (stuff____ ball4)
    (room_____ room17)
    (robot____ robot6)
    (at-robby robot8 room17)
    (free robot8 lgripper8)
    (at ball5 room3)
    (room_____ room1)
    (at-robby robot7 room10)
    (robot____ robot4)
    (at ball13 room12)
    (gripper__ lgripper2)
    (at-robby robot5 room10)
    (gripper__ rgripper7)
    (stuff____ ball7)
    (gripper__ rgripper5)
    (stuff____ ball3)
    (room_____ room14)
    (free robot2 rgripper2)
    (at-robby robot9 room1)
    (gripper__ rgripper4)
    (gripper__ lgripper8)
    (room_____ room8)
    (at ball3 room16)
    (room_____ room3)
    (free robot2 lgripper2)
    (at-robby robot4 room6)
    (at-robby robot1 room3)
    (free robot7 lgripper7)
    (stuff____ ball13)
    (at ball11 room7)
    (stuff____ ball12)
    (stuff____ ball8)
    (gripper__ rgripper6)
    (gripper__ lgripper3)
    (room_____ room6)
    (at ball2 room7)
    (free robot1 rgripper1)
    (room_____ room16)
    (room_____ room15)
    (stuff____ ball6)
    (room_____ room11)
    (robot____ robot7)
    (room_____ room12)
    (at ball8 room15)
    (at ball6 room8)
    (stuff____ ball5)
    (at ball9 room15)
    (free robot5 rgripper5)
    (free robot3 rgripper3)
    (gripper__ rgripper1)
    (at-robby robot2 room1)
    (stuff____ ball9)
    (injected-0)
  )
  (
    :goal
    (
      and
      (at ball1 room1)
      (at ball2 room14)
      (at ball3 room4)
      (at ball4 room9)
      (at ball5 room15)
      (at ball6 room8)
      (at ball7 room4)
      (at ball8 room17)
      (at ball9 room9)
      (at ball10 room2)
      (at ball11 room6)
      (at ball12 room2)
      (at ball13 room15)
      (at ball14 room15)
      (at ball15 room1)
      (injected-0)
    )
  )
)