import cv2
import time
import numpy as np
from background_subtractor import BackgroundSubtractor

PROCESSING_SCALE = 1

background_subtractor = BackgroundSubtractor(PROCESSING_SCALE)

while True:

    background_subtractor.update()
    if cv2.waitKey(1) in [ord('q'), ord('Q')]:
        break

