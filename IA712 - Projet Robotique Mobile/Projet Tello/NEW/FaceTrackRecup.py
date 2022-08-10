from  djitellopy import tello 
import cv2
import numpy as np
from time import sleep
#from hand_tracking_mod import *
import mediapipe as mp
from turtle import pos


class HandDetect():

    def __init__(self, model_complexity=0, min_detection_confidence=0.5, min_tracking_confidence=0.5, max_num_hands=2):
        
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(model_complexity = model_complexity , min_detection_confidence = min_detection_confidence, min_tracking_confidence = min_tracking_confidence, max_num_hands = max_num_hands)


    def detection_hand(self, img):

        results = self.hands.process(img)

        posList = []

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                for label, pos in enumerate(hand_landmarks.landmark):

                    h, w, p = img.shape
                    cx, cy = int(pos.x * w), int(pos.y * h)
                    
                    posList.append([label, cx, cy])
                    
                    self.mp_drawing.draw_landmarks(
                        img,
                        hand_landmarks,
                        self.mp_hands.HAND_CONNECTIONS,
                        self.mp_drawing_styles.get_default_hand_landmarks_style(),
                        self.mp_drawing_styles.get_default_hand_connections_style())
        
        return img, posList

    def rect_hand(self, posList):
        positions = list(zip(*posList))
        x_min, x_max = min(positions[1]), max(positions[1])
        y_min, y_max = min(positions[2]), max(positions[2])
        return [x_min, x_max, y_min, y_max]




me = tello.Tello()
me.connect()
print("---- Battery : {}% ----".format(me.get_battery()))

me.streamon()
me.takeoff()
#me.send_rc_control = (0, 0, 25, 0)
#sleep(1)

w, h = 360, 240
fbRange = [6200, 6800]
pid = [.5, .05, 1] # P : 
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

def trackFace(me, info, w, h, pError):

    fbRange = [6200, 6800]

    area = info[1]
    x, y = info[0]
    fb = 0

    #pid = [.1, .05, .001]

    pError = 0
    #pError = [0,0]

    ## PID
    error = x - w//2
    speed = pid[0] * error + pid[1]*(error - pError)
    """errorx = x - w//2
    errory = y - h//2       ###
    error = [errorx, errory]"""

    #speedx = pid[0] * errorx + pid[1]*(errorx - pError[0])
    #speedy = pid[0] * errory + pid[1]*(errory - pError[1])

    #speed = np.sqrt(speedx**2 + speedy**2)
    speed = int(np.clip(speed, -100,100))

    if area > fbRange[0] and area < fbRange[1]:   # Green Zone
        fb = 0
    if area >= fbRange[1]:                       # Too big, move backwards
        fb = - 25
    elif area <= fbRange[0] and area != 0:         # Too small, move forwards
        fb =  25

    if x == 0:
        speed = 0
        error = 0
        fb = 0

    return error, fb, speed


detecteur = HandDetect()
#cap = cv2.VideoCapture(0)
while True:
    #_, img = cap.read()
    #cv2.waitKey(1000//30)
    img = me.get_frame_read().frame
    img = cv2.resize(img, (w,h))
    img, info = findFace(img)
    cv2.rectangle(img, (x,y), (x+w, y+h), (0,0,255),2)

    img_hand, info_hand = detecteur.detection_hand(img)
    x_min, x_max, y_min, y_max = detecteur.rect_hand(info_hand)
    cv2.rectangle(img, (x_min, y_min), (x_max, y_max), (0,0,255),2)

    #x, y = info[0]

    pError, fb, speed = trackFace(me, info, w, h, pError)
    me.send_rc_control(0,fb,0,speed)
    print("Center", info[0], "Area", info[1])
    
    img = cv2.resize(img, (720,480))
    cv2.imshow("Output", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        me.land()
        break
#sleep()
#me.land()
cv2.destroyAllWindows()

