# LaserPointerMotionDetection
A laser pointer turret that aims at and follows moving objects within its view. Uses a arduino to control the laser and a background subtraction algorithm using OpenCV for motion detection. The center of the bounding box of the largest contour detected by OpenCV is used as the target for the laser to track. 

Hand Tracking            |  Person Tracking
:-------------------------:|:-------------------------:
![Hand Tracking](https://github.com/chenalan02/LaserPointerMotionDetection/blob/main/Readme%20Gifs/tracking%20hand.gif)  |  ![Person Tracking](https://github.com/chenalan02/LaserPointerMotionDetection/blob/main/Readme%20Gifs/tracking%20person.gif)

## Calibration
The laser must first be calibrated when main.py is initialized. A joystick connected to the arduino is used to move the laser slowly. The angles of the x and y servo which correspond to the borders of the camera frame are recorded by moving the laser and clicking the joystick when the laser is on the borders. This is done in the following order: left-> right-> top-> bottom. 

## Background Subtraction Algorithm

## Code Documentation
