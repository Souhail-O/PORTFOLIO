from djitellopy import Tello
from time import sleep
import cv2

drone = Tello()
drone.connect()

print("---- Battery : {}% ----".format(drone.get_battery()))

### Image capture ###
drone.streamon()

while True:
    cv2.waitKey(1000//30)
    img = drone.get_frame_read().frame
    img = cv2.resize(img, (320,240))
    cv2.imshow("Stream",img)
    cv2.waitKey(1)
