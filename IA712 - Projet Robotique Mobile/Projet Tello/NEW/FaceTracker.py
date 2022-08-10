from optparse import TitledHelpFormatter
from  djitellopy import Tello 
import cv2
import numpy as np
from time import sleep

class FaceTrack(Tello):
    def __init__(self):
        # Shape of the rectangle
        self.w, self.h = 360, 240

        self.fb = 0
        self.fbRange = [6200, 6800]
        self.ud = 0
        self.udRange = [6200, 6800]

        self.pid = [0.5, 0.5, 0]
        self.pError = [0,0]
        return

    def vidstream(self):
        return

    def findFace(self, img):
        
        # Train the model to recognize faces
        faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = faceCascade.detectMultiScale(img, 1.2, 8)

        #imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        #faces = faceCascade.detectMultiScale(imgGray, 1.2, 8)

        myFacelistC = []
        myFacelistArea = []

        for (x, y, self.w, self.h) in faces:
            cv2.rectangle(img, (x,y), (x + self.w, y + self.h), (0,0,255),2)
            cx = x + self.w//2
            cy = y + self.h//2
            area = self.w * self.h
            cv2.circle(img, (cx,cy),5,(0,255,0),cv2.FILLED)
            myFacelistArea.append(area)
            myFacelistC.append([cx,cy])

        if len(myFacelistArea) !=0:
            i = myFacelistArea.index(max(myFacelistArea))
            return img, [myFacelistC[i], myFacelistArea[i]]
        else:
            return img, [[0,0],0]
        

    def trackFace(self, me, w, pError=[0,0]):
        face, info = self.findFace(self, img)
        area = info[1]
        x, y = info[0] 

        ## PID
        error[0] = x - self.w//2
        error[1] = y - self.h//2
        speed = self.pid[0] * error[0] + self.pid[1]*(error[0] - pError[0])
        alt = self.pid[0] * error[1] + self.pid[1]*(error[1] - pError[1])

        speed = int(np.clip(speed, -100,100))
        alt = int(np.clip(alt, -100,100))

        if area > self.fbRange[0] and area < self.fbRange[1]:   # Green Zone
            self.fb = 0
        if area >= self.fbRange[1]:                       # Too big, move backwards
            self.fb = - 20
        elif area <= self.fbRange[0] and area != 0:         # Too small, move forwards
            self.fb =  20

        if area > udRange[0] and area < udRange[1]:   # Green Zone
            self.ud = 0
        if area >= udRange[1]:                       # Too big, move backwards
            self.ud = - 20
        elif area <= udRange[0] and area != 0:         # Too small, move forwards
            self.ud =  20

        if x == 0:
            speed = 0
            error = 0
        return error, self.fb, self.ud, speed
        

me = Tello()
me.connect()
print("---- Battery : {}% ----".format(me.get_battery()))

me.streamon()
me.takeoff()
#me.send_rc_control = (0, 0, 25, 0)
#sleep(1)

w, h = 360, 240
fbRange = [6200, 6800]
udRange = [6200, 6800]

pid = [0.5, 0.5, 0]
pError = [0,0]

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
    area = info[1]
    x, y = info[0]
    fb = 0
    ud = 0

    ## PID
    error[0] = x - w//2
    error[1] = y - h//2
    speed = pid[0] * error[0] + pid[1]*(error[0] - pError[0])
    alt = pid[0] * error[1] + pid[1]*(error[1] - pError[1])

    speed = int(np.clip(speed, -100,100))
    alt = int(np.clip(alt, -100,100))


    if area > fbRange[0] and area < fbRange[1]:   # Green Zone
        fb = 0
    if area >= fbRange[1]:                       # Too big, move backwards
        fb = - 20
    elif area <= fbRange[0] and area != 0:         # Too small, move forwards
        fb =  20

    if area > udRange[0] and area < udRange[1]:   # Green Zone
        ud = 0
    if area >= udRange[1]:                       # Too big, move backwards
        ud = - 20
    elif area <= udRange[0] and area != 0:         # Too small, move forwards
        ud =  20

    if x == 0:
        speed = 0
        error = 0

    #me.send_rc_control = (0, fb, 0, speed)
    return error, fb, ud, speed

#cap = cv2.VideoCapture(0)
while True:
    #_, img = cap.read()
    #cv2.waitKey(1000//30)
    img = me.get_frame_read().frame
    img = cv2.resize(img, (w,h))
    img, info = findFace(img)
    pError, fb, ud, speed= trackFace(me, info, w, pid, pError)
    me.send_rc_control(0,fb,ud,speed)
    #print("Center", info[0], "Area", info[1])
    cv2.imshow("Output", img)
    if cv2.waitKey(1) and 0xFF == ord('q'):
        
        break
#sleep()
me.land()