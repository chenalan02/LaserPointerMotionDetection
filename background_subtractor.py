from collections import deque
import cv2
import numpy as np
import serial
import time

#class to store the last 5 frames
class BackgroundBuffer:
    def __init__(self, width, height, scale):
        self.width = width
        self.height= height
        self.buffer = deque(maxlen=5)
        self.background = np.zeros((self.height//scale, self.width//scale), dtype='float32')

    def add_frame(self, frame):
        self.buffer.append(frame)
    
    #updates background by taking a weighted average of the new frame and previous background
    def update_get_background(self):
        self.background = (self.background//3)*2 + self.buffer[0]//3
        return self.background.astype('uint8')
 
#object which processes frames for background subtraction
class BackgroundSubtractor:
    def __init__(self, processing_scale, arduino):
        self.PROCESSING_SCALE = processing_scale
        self.arduino = arduino

        #determines frame dimensions
        self.cap = cv2.VideoCapture(0)
        _, frame = self.cap.read()
        frame_shape = frame.shape
        self.height = frame_shape[0]
        self.width = frame_shape[1]
        
        #initializes background buffer
        self.background_buffer = BackgroundBuffer(self.width, self.height, self.PROCESSING_SCALE)

        #presents laser coordinates to be middle of frame
        self.laser_coordinates = (self.height//2, self.width//2)

        #switch variable for calibration
        self.calibrated = False

    #processes frame subtraction and determines bounding box for the biggest contour found
    #sends coordinate of the center of the box to the arduino
    def update(self):
        #read and process frame with flip, resize, greyscale and gaussian blur
        _, unprocessed_frame = self.cap.read()
        unprocessed_frame = cv2.flip(unprocessed_frame, 1)
        frame = cv2.resize(unprocessed_frame, (self.width//self.PROCESSING_SCALE, self.height//self.PROCESSING_SCALE))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame = cv2.GaussianBlur(frame, (5, 5), 0)
        
        #updates background buffer, add mask to subtracted frame
        self.background_buffer.add_frame(frame)
        foreground = cv2.absdiff(self.background_buffer.update_get_background(), frame)
        _, mask = cv2.threshold(foreground, 15, 255, cv2.THRESH_BINARY)

        #check if turret is finished calibrating yet 
        if not self.calibrated:
            self.check_calibration()
        else:
            #find biggest contour and its bounding box
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if (contours):
                biggest_contour = max(contours, key = cv2.contourArea)
                if (cv2.contourArea(biggest_contour) > 800):
                    x, y, w, h = cv2.boundingRect(biggest_contour)
                    x, y, w, h = x*self.PROCESSING_SCALE, y*self.PROCESSING_SCALE, w*self.PROCESSING_SCALE, h*self.PROCESSING_SCALE
                    cv2.rectangle(unprocessed_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    #calculate center of bounding box
                    self.laser_coordinates = (y + h//2, x + w//2)
            #send updated coordinates to arduino
            self.send_laser_coordinates()

        cv2.imshow("processed", mask)
        cv2.imshow("Webcam", unprocessed_frame)

    #checks if the aruinod has send the byte b'1' which is send to mean it has finished calibrating
    def check_calibration(self):
        data = self.arduino.read()
        if data == b'1':
            self.calibrated = True

    #sends laser coordinates to arduino
    def send_laser_coordinates(self):
        self.arduino.write(("x"+str(self.laser_coordinates[1])+">").encode())
        self.arduino.write(("y"+str(self.laser_coordinates[0])+">").encode())
        
    #groups byte data sent from arduino and prints it for debugging purposes
    def receive_data(self):
        word = ""
        while (self.arduino.in_waiting > 0):
            char = self.arduino.read().decode()
            word += char
        print(word)