import cv2
import FaceTrack


from  djitellopy import tello

def main():
    me = tello.Tello()
    me.connect()
    print("---- Battery : {}% ----".format(me.get_battery()))

    me.streamon()
    me.takeoff()
    tracker = FaceTrack.FaceTrack()

    while (True):
    
        img = me.get_frame_read().frame
        img = cv2.resize(img, (360,240))
        img, info = tracker.findFace(img)
        fb, ud, speed= tracker.trackFace(info)
        me.send_rc_control(0,fb,ud,speed)
        #print("Center", info[0], "Area", info[1])
        cv2.imshow("Output", img)

        if cv2.waitKey(1) and 0xFF == ord('h'):
            break
    
    me.land()
    cv2.destroyAllWindows()
    

if __name__ == "__main__":
    main()

