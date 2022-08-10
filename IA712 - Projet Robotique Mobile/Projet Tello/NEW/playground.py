from  djitellopy import tello 
import cv2
import numpy as np
from time import sleep


me = tello.Tello()
me.connect()
print("---- Battery : {}% ----".format(me.get_battery()))
