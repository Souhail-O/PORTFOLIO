from utils import *

import cv2


w,h = 1280, 720
pid = [0.5, 0.5, 0]  # Kd, Kp, Ki
pError = 0
startCounter = 0 # for no Flight 1 - for Flight 0

myDrone = initializeTello()

while True:
    
    ##  Flight
    if startCounter == 0:
        myDrone.takeoff()
        startCounter = 1

    ## Step 1
    img = telloGetFrame(myDrone, w, h)
    ## Step 2
    img, info = findFace(img)
    ## Step 3
    pError = trackFrace(myDrone.info, w,pid, pError)
    
    #print(info[0][0])

    cv2.imshow('Image', img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        myDrone.land()
        break

    
