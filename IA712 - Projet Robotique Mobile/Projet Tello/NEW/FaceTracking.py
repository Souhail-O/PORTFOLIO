from  djitellopy import tello 
import cv2
import numpy as np
from time import sleep
import KeyPressModule as kp

me = tello.Tello()
me.connect()
print("---- Battery : {}% ----".format(me.get_battery()))

me.streamon()
me.takeoff()
#me.send_rc_control = (0, 0, 25, 0)
#sleep(1)

w, h = 360, 240
fbRange = [6200, 6800]
pid = [.4, .4, 0]
pError = 0

def findFace(img):
    faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    #faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(imgGray, 1.2, 8)

    myFacelistC = []
    myFacelistArea = []

    for (x,y,w,h) in faces:
        cv2.rectangle(img, (x,y), (x+w, y+h), (0,0,255),2)
        cx = x + w//2
        cy = y + h//2
        area = w*h
        cv2.circle(img, (cx,cy),5,(0,255,0),cv2.FILLED)
        myFacelistArea.append(area)
        myFacelistC.append([cx,cy])

    if len(myFacelistArea) !=0:
        i = myFacelistArea.index(max(myFacelistArea))
        return img, [myFacelistC[i], myFacelistArea[i]]
    else:
        return img, [[0,0],0]

"""def control(pid, error, error_prev, error_intergral):

        error_intergral += error
        if error_prev is None:
            error_prev = error
        error_derivative = error - error_prev
        error_prev = error
        speed = pid[0]*error + pid[1]*error_intergral + pid[2]*error_derivative
        speed = int(np.clip(speed, -100,100))

        return speed, error_prev, error_intergral"""

def trackFace(me, info, w, h, pErrorx=0, pErrory=0):

    fbRange = [6200, 6800]

    area = info[1]
    x, y = info[0]
    fb = 0
    ud = 0
    
    """##############################################################################
    ## PID
    pid = [0.1, 0.00001, 0.01]
    #pid = [1, 1, 1]   # kp / ki / kd

    error = x - w//2
    error_intergral = 0
    pError = None
    speed, pError, error_intergral = control(pid, error, pError, error_intergral)
    
    #################################################################################"""

    pid = [0.2, 0.05, 0.02]

    #pError = [0,0]
    #pErrorx = 0
    #pErrory = 0
    
    #if pErrorx is None : pErrorx = 0
    #if pErrory is None : pErrory = 0

    area = info[1]
    x, y = info[0]
    fb = 0

    ## PID
    errorx = x - w//2
    errory = y - h//2
    speed = pid[0] * errorx + pid[1]*(errorx - pErrorx)
    ud = pid[0] * errory + pid[1]*(errory - pErrory)

    speed = int(np.clip(speed, -100,100))
    ud = int(np.clip(ud, -100,100))

    if area > fbRange[0] and area < fbRange[1]:   # Green Zone
        fb = 0
    if area >= fbRange[1]:                       # Too big, move backwards
        fb = - 15
    elif area <= fbRange[0] and area != 0:         # Too small, move forwards
        fb =  15

    if x == 0:
        speed = 0
        errorx = 0
        errory = 0
        ud = 0
        fb = 0

    return errorx, errory, fb, ud, speed

#cap = cv2.VideoCapture(0)
while True:
    #_, img = cap.read()
    #cv2.waitKey(1000//30)
    img = me.get_frame_read().frame
    img = cv2.resize(img, (w,h))
    img, info = findFace(img)
    x, y = info[0]

    pErrorx, pErrory, fb, ud, speed = trackFace(me, info, w, h, pErrorx, pErrory)
    me.send_rc_control(0,fb,ud,speed)
    print("Center", info[0], "Area", info[1])
    
    img = cv2.resize(img, (720,480))
    cv2.imshow("Output", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        me.land()
        break
#sleep()
#me.land()
cv2.destroyAllWindows()

