#from optparse import TitledHelpFormatter
from  djitellopy import Tello 
import cv2
import numpy as np
from time import sleep

def findFace(img):
    """# A function that detects the faces in the image"""
    faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(imgGray, 1.2, 8)

    myFacelistC = []                                                        # A list for catching the face centers
    myFacelistArea = []                                                     # A list for catching the face areas

    # Add the detected faces (area & coord) to the lists
    for (x,y,w,h) in faces: 
        cv2.rectangle(img, (x,y), (x+w, y+h), (0,0,255),2)
        cx = x + w//2
        cy = y + h//2
        area = w*h
        cv2.circle(img, (cx,cy),5,(0,255,0),cv2.FILLED)
        myFacelistArea.append(area)
        myFacelistC.append([cx,cy])

    # Pick the largest face to follow
    if len(myFacelistArea) !=0:
        i = myFacelistArea.index(max(myFacelistArea))
        return img, [myFacelistC[i], myFacelistArea[i]]
    else:
        return img, [[0,0],0]

def trackFace(me, info, w, pid, pError):
    """# A function that follows the face that was previously detected and passed as 'info' """
    
    # Unpack face details
    x, y = info[0]
    area = info[1]                                                         
    
    # Initialize commands
    fb, ud, error = 0, 0, 0

    ## PID
    error = x - w//2                                                           # Evaluate the error
    speed = pid[0] * error + pid[1]*(error - pError)                           # Evaluate the speed of yaw of the drone
    speed = int(np.clip(speed, -100,100))                                      # Clip the speed to the [-100,100] range

    # Set the front/backward commands : if the face area is bigger than reference area, go back, otherwise if too smaller go forward, otherwise, stay put
    if area > fbRange[0] and area < fbRange[1]:                                # Green Zone                 
        fb = 0
    if area >= fbRange[1]:                                                     # Too big, move backwards
        fb = - 15
    elif area <= fbRange[0] and area != 0:                                     # Too small, move forwards
        fb =  15

    # Set the altitude controls by position of the face to the center of the image
    if y > 0.75*h:                           # Too up, move down
        ud =  - 5
    elif  y < 0.25*h:                           # Too down, move up
        ud =  5
    else :
        ud = 0

    if x == 0:                                                                 # If no face detected, set everything to 0
        speed = 0
        error = 0

    return error, fb, ud, speed

me = Tello()                                                                # Initialize the drone object
me.connect()                                                                # Connect to the drone
print("---- Battery : {}% ----".format(me.get_battery()))

me.streamon()                                                               # Start the video stream
me.takeoff()                                                                # Make the drone take 

# Define the general variables
w, h = 360, 240                                                             # Width x Height of the window we show we show
fbRange = [6200, 6800]                                                      # Define the surface range for the fb command  

pid = [0.5, 0.5, 0]                                                         # Define the PID command values
pError = 0                                                                  # Initialize the error

""" The Pipeline"""
while True:

    img = me.get_frame_read().frame                                         # Get the view of the camera
    img = cv2.resize(img, (w,h))                                            # Get the view of the camera
    img, info = findFace(img)                                               # Find the face
    pError, fb, ud, speed= trackFace(me, info, w, pid, pError)              # Track the face : get the command values
    me.send_rc_control(0,fb,ud,speed)                                       # Track the face : send the command values
    
    cv2.imshow("Output", img)
    
    if cv2.waitKey(1) and 0xFF == ord('q'):                                 # Break out of the loop and land 
        break

sleep()
me.land()
