import cv2
import numpy as np
from collections import deque
from ultralytics import YOLO

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
    def __init__(self, processing_scale, arduino, yolo:bool):
        self.PROCESSING_SCALE = processing_scale
        self.arduino = arduino
        self.yolo = yolo
        if yolo:
            self.model = YOLO("yolov8n.pt")

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
    
    def box_label(self, image, box, label='', color=(128, 128, 128), txt_color=(255, 255, 255)):
        lw = max(round(sum(image.shape) / 2 * 0.003), 2)
        p1, p2 = (int(box[0]), int(box[1])), (int(box[2]), int(box[3]))
        cv2.rectangle(image, p1, p2, color, thickness=lw, lineType=cv2.LINE_AA)
        if label:
            tf = max(lw - 1, 1)  # font thickness
            w, h = cv2.getTextSize(label, 0, fontScale=lw / 3, thickness=tf)[0]  # text width, height
            outside = p1[1] - h >= 3
            p2 = p1[0] + w, p1[1] - h - 3 if outside else p1[1] + h + 3
            cv2.rectangle(image, p1, p2, color, -1, cv2.LINE_AA)  # filled
            cv2.putText(image,
                        label, (p1[0], p1[1] - 2 if outside else p1[1] + h + 2),
                        0,
                        lw / 3,
                        txt_color,
                        thickness=tf,
                        lineType=cv2.LINE_AA)
        
    def plot_bboxes(self, image, boxes, labels=[], colors=[], score=True, conf=None):
        #Define COCO Labels
        if labels == []:
            labels = {0: u'__background__', 1: u'person', 2: u'bicycle',3: u'car', 4: u'motorcycle', 5: u'airplane', 6: u'bus', 7: u'train', 8: u'truck', 9: u'boat', 10: u'traffic light', 11: u'fire hydrant', 12: u'stop sign', 13: u'parking meter', 14: u'bench', 15: u'bird', 16: u'cat', 17: u'dog', 18: u'horse', 19: u'sheep', 20: u'cow', 21: u'elephant', 22: u'bear', 23: u'zebra', 24: u'giraffe', 25: u'backpack', 26: u'umbrella', 27: u'handbag', 28: u'tie', 29: u'suitcase', 30: u'frisbee', 31: u'skis', 32: u'snowboard', 33: u'sports ball', 34: u'kite', 35: u'baseball bat', 36: u'baseball glove', 37: u'skateboard', 38: u'surfboard', 39: u'tennis racket', 40: u'bottle', 41: u'wine glass', 42: u'cup', 43: u'fork', 44: u'knife', 45: u'spoon', 46: u'bowl', 47: u'banana', 48: u'apple', 49: u'sandwich', 50: u'orange', 51: u'broccoli', 52: u'carrot', 53: u'hot dog', 54: u'pizza', 55: u'donut', 56: u'cake', 57: u'chair', 58: u'couch', 59: u'potted plant', 60: u'bed', 61: u'dining table', 62: u'toilet', 63: u'tv', 64: u'laptop', 65: u'mouse', 66: u'remote', 67: u'keyboard', 68: u'cell phone', 69: u'microwave', 70: u'oven', 71: u'toaster', 72: u'sink', 73: u'refrigerator', 74: u'book', 75: u'clock', 76: u'vase', 77: u'scissors', 78: u'teddy bear', 79: u'hair drier', 80: u'toothbrush'}
        #Define colors
        if colors == []:
            colors = [(89, 161, 197),(67, 161, 255),(19, 222, 24),(186, 55, 2),(167, 146, 11),(190, 76, 98),(130, 172, 179),(115, 209, 128),(204, 79, 135),(136, 126, 185),(209, 213, 45),(44, 52, 10),(101, 158, 121),(179, 124, 12),(25, 33, 189),(45, 115, 11),(73, 197, 184),(62, 225, 221),(32, 46, 52),(20, 165, 16),(54, 15, 57),(12, 150, 9),(10, 46, 99),(94, 89, 46),(48, 37, 106),(42, 10, 96),(7, 164, 128),(98, 213, 120),(40, 5, 219),(54, 25, 150),(251, 74, 172),(0, 236, 196),(21, 104, 190),(226, 74, 232),(120, 67, 25),(191, 106, 197),(8, 15, 134),(21, 2, 1),(142, 63, 109),(133, 148, 146),(187, 77, 253),(155, 22, 122),(218, 130, 77),(164, 102, 79),(43, 152, 125),(185, 124, 151),(95, 159, 238),(128, 89, 85),(228, 6, 60),(6, 41, 210),(11, 1, 133),(30, 96, 58),(230, 136, 109),(126, 45, 174),(164, 63, 165),(32, 111, 29),(232, 40, 70),(55, 31, 198),(148, 211, 129),(10, 186, 211),(181, 201, 94),(55, 35, 92),(129, 140, 233),(70, 250, 116),(61, 209, 152),(216, 21, 138),(100, 0, 176),(3, 42, 70),(151, 13, 44),(216, 102, 88),(125, 216, 93),(171, 236, 47),(253, 127, 103),(205, 137, 244),(193, 137, 224),(36, 152, 214),(17, 50, 238),(154, 165, 67),(114, 129, 60),(119, 24, 48),(73, 8, 110)]
        
        #plot each boxes
        for box in boxes:
            #add score in label if score=True
            if score :
                label = labels[int(box[-1])+1] + " " + str(round(100 * float(box[-2]),1)) + "%"
            else :
                label = labels[int(box[-1])+1]
                #filter every box under conf threshold if conf threshold setted
                if conf :
                    if box[-2] > conf:
                        color = colors[int(box[-1])]
                        self.box_label(image, box, label, color)
                else:
                    color = colors[int(box[-1])]
                    self.box_label(image, box, label, color)

        else :
            cv2.imshow("processed", image) #if used in Python

    #processes frame subtraction and determines bounding box for the biggest contour found
    #sends coordinate of the center of the box to the arduino
    def update(self):
        #get frame from webcam
        _, unprocessed_frame = self.cap.read()
        unprocessed_frame = cv2.flip(unprocessed_frame, 1)

        #case for yolo algorithm
        if self.yolo:
            #get prediction
            preds = self.model.predict(unprocessed_frame, verbose=False)
            #plot bounding boxes and labels of predictions
            self.plot_bboxes(unprocessed_frame, preds[0].boxes.data, score=False)
            #check for any people detected to send laser coordinates to turret
            for box in preds[0].boxes.data:
                x1, y1, x2, y2, score, label = box
                if label == 1:
                    self.laser_coordinates = (y1 + (y2-y1)//2, x1 + (x2-x1)//2)
                    self.send_laser_coordinates()
        #case for background subtraction algorithm
        else: 
            #read and process frame with flip, resize, greyscale and gaussian blur
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