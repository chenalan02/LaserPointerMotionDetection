import cv2
import time
import numpy as np
from collections import deque

class BackgroundBuffer:
    def __init__(self, width, height, scale):
        self.width = width
        self.height= height
        self.buffer = deque(maxlen=5)
        self.background = np.zeros((self.height//scale, self.width//scale), dtype='float32')
 
    def update_frame(self, frame):
        self.buffer.append(frame)
 
    def update_get_background(self):
        self.background = (self.background//3)*2 + self.buffer[0]//3
        return self.background.astype('uint8')
 

PROCESSING_SCALE = 1

cap = cv2.VideoCapture(0)

_, frame = cap.read()
frame_shape = frame.shape
height = frame_shape[0]
width = frame_shape[1]

background_buffer = BackgroundBuffer(width, height, PROCESSING_SCALE)

while True:

    _, unprocessed_frame = cap.read()
    unprocessed_frame = cv2.flip(unprocessed_frame, 1)

    frame = cv2.resize(unprocessed_frame, (width//PROCESSING_SCALE, height//PROCESSING_SCALE))
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame = cv2.GaussianBlur(frame, (5, 5), 0)
    
    background_buffer.update_frame(frame)
    foreground = cv2.absdiff(background_buffer.update_get_background(), frame)
    _, mask = cv2.threshold(foreground, 15, 255, cv2.THRESH_BINARY)
    #mask = cv2.dilate(mask, None, iterations=2)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        if cv2.contourArea(contour) < 800//(PROCESSING_SCALE**2):
            continue
        x, y, w, h = cv2.boundingRect(contour)
        x, y, w, h = x*PROCESSING_SCALE, y*PROCESSING_SCALE, w*PROCESSING_SCALE, h*PROCESSING_SCALE
        cv2.rectangle(unprocessed_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    cv2.imshow("processed", mask)
    cv2.imshow("Webcam", unprocessed_frame)
    

    last_frame = frame

    if cv2.waitKey(1) == ord('q'):
        break

