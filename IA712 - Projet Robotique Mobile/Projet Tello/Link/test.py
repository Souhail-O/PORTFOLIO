from djitellopy import tello
from time import sleep
from threading import Thread
import cv2

me = tello.Tello()
me.connect()

print('Battery: ', me.get_battery(), '%')

### Image capture ###
me.streamon()

while True:
    img = me.get_frame_read().frame
    #img = cv2.resize(img, (320,240))
    cv2.imshow("Stream",img)
    cv2.waitKey(1)


## Basic commands 
me.takeoff()
#me.send_rc_control(0,30,0,0)
#sleep(2)
me.flip_right()
me.flip_left()

#sleep(2)
#me.send_rc_control(0,0,0,30)
#sleep(2)
#me.flip_back()
#sleep(2)
#me.send_rc_control(0,20,0,0)
sleep(2)
me.land()




