from  djitellopy import Tello 
import cv2
import numpy as np
from time import sleep


me = Tello()
me.connect()
print("---- Battery : {}% ----".format(me.get_battery()))

me.streamon()
me.takeoff()

w, h = 360, 240
fbRange = [6200, 6800]
udRange = [6200, 6800]

pid = [0.5, 0.5, 0]
pError = [0,0]

def findFace(img):
    
    #(H, W) = image.shape[:2] #w:image-width and h:image-height
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

def trackFace(me, info, w,h, pid, pError):
    area = info[1]
    x, y = info[0]
    fb = 0
    ud = 0
    lr = 0

    ## PID
    error=[0, 0]#, 0]
    error[0] = x - w//2 
    error[1] = y - h//2
    speed = pid[0] * error[0] + pid[1]*(error[0] - pError[0])
    speed = int(np.clip(speed, -100,100))

    # FORWARD-BACKWARD
    if area > fbRange[0] and area < fbRange[1]:   # Green Zone
        fb = 0
    if area >= fbRange[1]:                        # Too big, move backwards
        fb = - 20
    elif area <= fbRange[0] and area != 0:        # Too small, move forwards
        fb =  20
    
    # UP-DOWN
    if np.abs(y - h//2) <= 50:
        ud = 0
    if y > h/2 :   
        ud = -20
    else:
        ud = 20

    # LEFT-RIGHT
    if np.abs(x - w//2) < 50:
        lr = 0
    if x > w/2 :   
        lr = -20
    else:
        lr = 20

    if x == 0 or y == 0:
        speed = 0
        error = [0,0]

    return error, lr, fb, ud, speed

#cap = cv2.VideoCapture(0)
while True:
    #_, img = cap.read()
    #cv2.waitKey(1000//30)
    img = me.get_frame_read().frame
    img = cv2.resize(img, (w,h))
    #sleep(2)
    img, info = findFace(img)
    pError, lr, fb, ud, speed= trackFace(me, info, w,h, pid, pError)
    #me.send_rc_control(lr,fb,ud,speed)
    print("Center", info[0], "Area", info[1])
    #img = cv2.resize(img, (720,480))
    cv2.imshow("Output", img)
    
    if cv2.waitKey(1) and 0xFF == ord('q'):
        break
#sleep(2)
me.land()

cv2.destroyAllWindows()