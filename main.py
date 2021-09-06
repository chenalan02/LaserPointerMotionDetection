import cv2
import time
import numpy as np
import serial
from background_subtractor import BackgroundSubtractor

PROCESSING_SCALE = 1

background_subtractor = BackgroundSubtractor(PROCESSING_SCALE)
arduino = serial.Serial(port='COM3', baudraet= 9600, timeout=.1)

while True:

    background_subtractor.update()
    
    if cv2.waitKey(1) in [ord('q'), ord('Q')]:
        break

