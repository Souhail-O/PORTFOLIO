from  djitellopy import tello 
import cv2
import numpy as np
from time import sleep


me = tello.Tello()
me.connect()
print("---- Battery : {}% ----".format(me.get_battery()))

me.streamon()
me.takeoff()
#me.send_rc_control = (0, 0, 25, 0)
#sleep(1)

w, h = 360, 240
fbRange = [6200, 6800]
pid = [0.4, 0.4, 0]
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

def trackFace(me, info, w, pid, pError):

    fbRange = [6200, 6800]
    pid = [20, 6, 0]  # k_rho , k_alpha
    
    area = info[1]
    x, y = info[0]
    
    rho = np.sqrt( ( w//2 - x ) ** 2 + ( h//2 - y ) ** 2)
    alpha = np.arctan2 ( ( h//2 - y) , ( w//2 - x )) - theta

    k_rho = 20
    k_alpha = 6
    u[0] = k_rho * rho
    u[1] = k_alpha * alpha

    speed = int(np.clip(speed, -100,100))

    #pError = [0,0]
    pError = 0
    area = info[1]
    x, y = info[0]
    fb = 0

    ## PID
    error = x - w//2
    speed = pid[0] * error + pid[1]*(error - pError)
    speed = int(np.clip(speed, -100,100))

    if area > fbRange[0] and area < fbRange[1]:   # Green Zone
        fb = 0
    if area >= fbRange[1]:                       # Too big, move backwards
        fb = - 20
    elif area <= fbRange[0] and area != 0:         # Too small, move forwards
        fb =  20

    if x == 0:
        speed = 0
        error = 0

    return error, fb, speed

#cap = cv2.VideoCapture(0)
while True:
    #_, img = cap.read()
    #cv2.waitKey(1000//30)
    img = me.get_frame_read().frame
    img = cv2.resize(img, (w,h))
    img, info = findFace(img)
    pError, fb, speed = trackFace(me, info=info, w=w, pid=pid, pError=pError)
    me.send_rc_control(0,fb,0,speed)
    print("Center", info[0], "Area", info[1])
    cv2.imshow("Output", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        #me.land()
        break
#sleep()
me.land()
cv2.destroyAllWindows()

