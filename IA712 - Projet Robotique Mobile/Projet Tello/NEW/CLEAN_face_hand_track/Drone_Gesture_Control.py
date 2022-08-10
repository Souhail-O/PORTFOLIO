from cmath import rect
from turtle import pos
import cv2
import mediapipe as mp
import time
import numpy as np
import HandDetect

import tensorflow as tf
import pre_process_landmark

from  djitellopy import tello 

from time import sleep


'''class HandDetect():

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
'''


def main():

    me = tello.Tello()
    me.connect()
    print("---- Battery : {}% ----".format(me.get_battery()))

    me.streamon()
    me.takeoff()

    # if image feed is Drone : 
    w, h = 360, 240
    cam = me.get_frame_read().frame
    cam = cv2.resize(img, (w,h))
    
    # if image from Webcam
    cam = cv2.VideoCapture(0)

    detecteur = HandDetect.HandDetect(max_num_hands=1)

    cTime = 0
    pTime = 0
    
    print('\n ########## Activate Hand Detect ########## \n')

    detecteur = HandDetect.HandDetect(max_num_hands=1)

    print('\n ########## OK ! ########## \n')

    model = tf.keras.models.load_model('model_save_path')

    print('\n ########## Model Load !! ########## \n')

    print('\n ########## OK ! ########## \n')

    while(True):

        # if Webcam
        _, img = cam.read()

        # if Drone:
        img = cam

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
 
        color = (0,0,255)
        pt1=(50,200)
        pt2=(600,950)

        rect_img = img[pt1[1] : pt2[1], pt1[0] : pt2[0]]


        img[pt1[1] : pt2[1], pt1[0] : pt2[0]] = rect_img


        cv2.rectangle(img, pt1=pt1, pt2=pt2, color= color, thickness=2)


        rect_img, _ , posList_nolabel = detecteur.detection_hand(rect_img)


        '''if posList : 
            print(posList[9])
            if 200 < posList[9][1] < 500 and 300 < posList[9][2] < 800:
                color = (255,0,0)
                pt1=(80,220)
                pt2=(580,920)

            x1, y1 = posList[4][1], posList[4][2]
            x2, y2 = posList[8][1], posList[8][2]
            cx, cy = (x1+x2)//2 , (y1+y2)//2

            cv2.circle(rect_img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
            cv2.circle(rect_img, (x2, y2), 15, (255, 0, 255), cv2.FILLED)
            cv2.line(rect_img,  (x1,y1), (x2,y2), (255,0,255), 3)
            cv2.circle(rect_img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

            length = math.hypot(x2 - x1, y2-y1)

            print(length)
 
            if length<50:
                cv2.circle(rect_img, (cx, cy), 15, (0, 255, 255), cv2.FILLED)

            if length:
                l = length
                cv2.rectangle(rect_img, (50,150), (85,400), (0, 255, 100), 3)
                cv2.rectangle(rect_img, (50,int(l)), (85,400), (0, 255, 0), 3)'''



        img = cv2.flip(img, 1)

        rect_img = cv2.flip(rect_img, 1)

        #cv2.putText(img, f'FPS:{int(fps)}', (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 100, 0), 2) 
        cv2.putText(img, 'FPS:{}'.format(int(fps)), (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 100, 0), 2) 
       
        detect ='None'

        if (posList_nolabel) :
            posL = pre_process_landmark.pre_process_landmark(posList_nolabel)

            predict_result = model.predict(np.array([posL]))

            result = np.argmax(np.squeeze(predict_result))

            if result == 0 :
                detect = '0 : stop'
                me.land()
            elif result == 1:
                detect = '1 : droite'
                me.send_rc_control(20,0,0,0)
            elif result == 2 :
                detect = '2 : gauche'
                me.send_rc_control(-20,0,0,0)
            elif result == 3 :
                detect = '3 : haut'
                me.send_rc_control(0,0,20,0)
            elif result == 4 :
                detect = '4 : bas'
                me.send_rc_control(0,0,-20,0)
            elif result == 5 :
                detect = '5 : avance'
                me.send_rc_control(0,10,0,0)
            else:
                detect ='None'

            
            #cv2.putText(rect_img, f'Label detection:{detect}', (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 100, 0), 2)
            cv2.putText(rect_img, 'Label detection:{}'.format(detect), (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 100, 0), 2)
        

        cv2.imshow('MediaPipe Hands', img)

        cv2.imshow('Hand zone', rect_img) 

        

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()



 