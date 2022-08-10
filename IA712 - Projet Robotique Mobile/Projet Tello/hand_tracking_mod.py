from turtle import pos
import cv2
import mediapipe as mp
import time
import math

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



def main():

    cam = cv2.VideoCapture(0)

    cTime = 0
    pTime = 0
    
    print('\n ########## Activate ########## \n')

    detecteur = HandDetect()

    print('\n ########## OK ! ########## \n')

    while(True):

        sucess, img = cam.read()


        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
 
        color = (0,0,255)
        pt1=(100,200)
        pt2=(600,900)

        rect_img = img[pt1[1] : pt2[1], pt1[0] : pt2[0]]

        rect_img, posList = detecteur.detection_hand(rect_img)

        img[pt1[1] : pt2[1], pt1[0] : pt2[0]] = rect_img



        cv2.rectangle(img, pt1=pt1, pt2=pt2, color= color, thickness=2)


        if posList : 
            '''print(posList[9])
            if 200 < posList[9][1] < 500 and 300 < posList[9][2] < 800:
                color = (255,0,0)
                pt1=(80,220)
                pt2=(580,920)'''

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


        img = cv2.flip(img, 1)

        cv2.putText(img, f'FPS:{int(fps)}', (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 100, 0), 2)

        cv2.imshow('MediaPipe Hands', img)

        cv2.imshow('Hand zone', cv2.flip(rect_img, 1))

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()



 