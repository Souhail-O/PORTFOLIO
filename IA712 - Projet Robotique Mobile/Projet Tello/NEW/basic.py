from djitellopy import tello
from time import sleep
import cv2

drone = tello.Tello()
drone.connect()

print("---- Battery : {}% ----".format(drone.get_battery()))




# Video Stream
drone.streamon()
while True:
    cv2.waitKey(1000//30)
    img = drone.get_frame_read().frame
    img = cv2.resize(img, (360,240))
    cv2.imshow("Output", img)
    break

sleep(5)

# Basic commands


drone.takeoff()

#sleep(2)

#drone.send_rc_control(0,20,0,0)    # LeftRight - ForwardBackward - UpDown - Yaw
#sleep(2)

"""drone.flip_forward()
sleep(2)

drone.send_rc_control(0,0,0,100)    # LeftRight - ForwardBackward - UpDown - Yaw
sleep(2)

drone.send_rc_control(0,20,0,0)    # LeftRight - ForwardBackward - UpDown - Yaw
sleep(2)"""

while True:
    print("I am alive !")

    if cv2.waitKey(1) and 0xFF == ord('q'):
        break

drone.land()
