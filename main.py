import cv2
import time
import numpy as np
import serial
from background_subtractor import BackgroundSubtractor

PROCESSING_SCALE = 2

arduino = serial.Serial(port='COM3', baudrate= 9600, timeout=0, write_timeout = 0)
time.sleep(2)
background_subtractor = BackgroundSubtractor(PROCESSING_SCALE, arduino)


while True:

    background_subtractor.update()

    if cv2.waitKey(1) in [ord('q'), ord('Q')]:
        break

