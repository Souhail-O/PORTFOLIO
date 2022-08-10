import cv2
import time
import numpy as np
import HandDetect

import tensorflow as tf
import pre_process_landmark

from  djitellopy import tello 


def main():

    cam = cv2.VideoCapture(0)

    me = tello.Tello()
    me.connect()
    print("Battery ====>>> {} %".format(me.get_battery()))

    me.streamon()
    me.takeoff()


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

        #cam2 = me.get_frame_read().frame
        #cam2 = cv2.resize(cam, (2000,2000))
        #cv2.imshow("Image", cam)
        #k = cv2.waitKey(1)  

        sucess, img = cam.read()  

        #cam2 = img

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


        img = cv2.flip(img, 1)

        rect_img = cv2.flip(rect_img, 1)

        cv2.putText(img, f'FPS:{int(fps)}', (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 100, 0), 2) 
        
        detect ='None'

        if (posList_nolabel) :
            posL = pre_process_landmark.pre_process_landmark(posList_nolabel)

            predict_result = model.predict(np.array([posL]))

            result = np.argmax(np.squeeze(predict_result))

            if result == 0 :
                detect = '0 : stop'
                me.send_rc_control(0,0,0,0)
                time.sleep(0.1)
            elif result == 1:
                detect = '1 : droite'
                me.send_rc_control(20,0,0,0)
                time.sleep(0.1)
            elif result == 2 :
                detect = '2 : gauche'
                me.send_rc_control(-20,0,0,0)
                time.sleep(0.1)
            elif result == 3 :
                detect = '3 : haut'
                me.send_rc_control(0,0,20,0)
                time.sleep(0.1)
            elif result == 4 :
                detect = '4 : bas'
                me.send_rc_control(0,0,-20,0)
                time.sleep(0.1)
            elif result == 5 :
                detect = '5 : avance'
                me.send_rc_control(0,10,0,0)
                time.sleep(0.1)
            else:
                detect ='None'     

        else:
            me.send_rc_control(0,0,0,0)
            time.sleep(0.1)
            
            cv2.putText(rect_img, f'Label detection:{detect}', (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 100, 0), 2)
        
        
        #cv2.imshow('Tello', cam2)

        cv2.imshow('MediaPipe Hands', img)

        cv2.imshow('Hand zone', rect_img) 

        

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


    me.land()
    cv2.destroyAllWindows()
    

if __name__ == "__main__":
    main()



 