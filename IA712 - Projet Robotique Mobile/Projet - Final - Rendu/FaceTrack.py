from  djitellopy import Tello 
import cv2
import numpy as np
from time import sleep

class FaceTrack(Tello):

    def __init__(self):
        
        # Shape of the input image
        self.w, self.h = 360, 240

        # Initialize the command controls PID
        self.pid = [0.5, 0.5, 0]

        # Initialize the speeds
        self.fb = 0                                                                         # Forward-Backward velocity
        self.ud = 0                                                                         # Ud-Down velocity
        self.lr = 0                                                                         # Left-Right velocity
        self.speed = 0                                                                      # Yaw velocity

        # Initialize the forward-backward detection range 
        self.fbRange = [6200, 6800]
        self.udRange = [6200, 6800]


        # Initialize the previous errors on [lr, fb, ud, speed]
        #self.pError = [0,0]
        self.pError = 0


    def findFace(self, img):
        ######################
        ### Recognize faces ##
        ######################

        # Train the model to recognize faces
        faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(imgGray, 1.2, 8)                               # Detect faces in the input image

        # Create lists to store the faces and the face centers
        myFacelistC = []
        myFacelistArea = []

        # Loop thgrough the detected faces, 
        for (x, y, self.w, self.h) in faces:
            cv2.rectangle(img, (x,y), (x + self.w, y + self.h), (0,0,255),2)                # Create a rectangle around the face
            cx = x + self.w//2
            cy = y + self.h//2
            area = self.w * self.h
            cv2.circle(img, (cx,cy),5,(0,255,0),cv2.FILLED)                                 # Add a green dot to the center of the rectangle
            myFacelistArea.append(area)                                                     
            myFacelistC.append([cx,cy])

        # Return the biggest detected rectangle, otherwise return the original image
        if len(myFacelistArea) !=0:
            i = myFacelistArea.index(max(myFacelistArea))
            return img, [myFacelistC[i], myFacelistArea[i]]
        else:
            return img, [[0,0],0]
        

    def trackFace(self, info):
        x, y = info[0]
        area = info[1]

        ## Calculate the errors (x,y) between the center of the face, and the center of the drone frame.
        error_x = x - self.w//2
        error_y = y - self.h//2

        # Calculate the PID controls on x and y
        #speed_x = self.pid[0] * error_x + self.pid[1]*(error_x - self.pError[0])
        speed_x = self.pid[0] * error_x + self.pid[1]*(error_x - self.pError)

        #speed_y = self.pid[0] * error_y + self.pid[1]*(error_y - self.pError[1])

        # Calculate the speed, and clip it between -100 and 100
        #speed = np.sqrt(speed_x**2 + speed_y**2)
        speed = int(np.clip(speed_x, -100,100))
        
        #self.speed = speed
        #self.pError = [error_x, error_y]

        if area > self.fbRange[0] and area < self.fbRange[1]:                               # Green Zone
            self.fb = 0
        if area >= self.fbRange[1]:                                                         # Too big, move backwards
            self.fb = - 20
        elif area <= self.fbRange[0] and area != 0:                                         # Too small, move forwards
            self.fb =  20

        """if area > self.udRange[0] and area < self.udRange[1]:   # Green Zone
            self.ud = 0
        if area >= self.udRange[1]:                                # Too big, move backwards
            self.ud =  - 20
        elif area <= self.udRange[0] and area != 0:                # Too small, move forwards
            self.ud = - 20"""

        # If no face is detected, keep all the controls at 0
        if x == 0:
            speed = 0
            self.pError = 0
            #self.fb = 0
            #self.ud = 0
            #self.pError = [0,0]

        #return self.fb, self.ud, self.speed
        return self.fb, self.ud, speed

        #return self
