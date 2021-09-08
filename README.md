# LaserPointerMotionDetection
A laser pointer turret that aims at and follows moving objects within its view. Uses a arduino to control the laser and a background subtraction algorithm using OpenCV for motion detection. The center of the bounding box of the largest contour detected by OpenCV is used as the target for the laser to track. The turret must first be calibrated to determine the servo angles which correspond to aiming at the borders of the frame.

Tracking A Hand          |  Tracking A Person
:-------------------------:|:-------------------------:
![Tracking A Hand](https://github.com/chenalan02/LaserPointerMotionDetection/blob/main/Readme%20Gifs/tracking%20hand.gif)  |  ![Tracking A Person](https://github.com/chenalan02/LaserPointerMotionDetection/blob/main/Readme%20Gifs/tracking%20person.gif)

<img src="https://github.com/chenalan02/LaserPointerMotionDetection/blob/main/Readme%20Images/Laser%20Turret%20Setup.jpg" width="400">
https://github.com/chenalan02/LaserPointerMotionDetection/blob/main/Readme%20Images/Laser%20Turret%20Setup.jpg

## Calibration
The laser must first be calibrated when main.py is initialized. A joystick connected to the arduino is used to move the laser slowly. The angles of the x and y servo which correspond to the borders of the camera frame are recorded by moving the laser and clicking the joystick when the laser is on the borders. This is done in the following order: left-> right-> top-> bottom. When the arduino receives coordinates to aim at(from the python program), it maps the x and y pixel value to a servo angle depending on the angles determined during calibration.

`int x_angle = map(coordinate_X, 0, imgWidth, boundingAngles[0], boundingAngles[1]);
        servoX.write(x_angle);`
Although this solution for aiming the turret is flawed, as it will be inaccurate near the corners of the frame, it is good enough for my purposes. I only need the turret to point and follow the central location of movement and it does not be to be extremely accurate. An accurate solution would involve calibrating/measuring the closest distance from the laser to the wall and the actual height and width of visible wall.

## Background Subtraction Algorithm
A backgorund subtraction algorithm was created using OpenCV to detect motion. The algorithm works on the principle that the difference from subtracting the pixel values of consecutive frames will show where movement occurs. Both frames are processed into greyscale with a threshold applied to it. A gaussian blur is also applied to reduce noise. The absolute difference of the pixel values are then taken instead of regular subtraction to prevent integer overflow since pixel values are represented by 8 bit integers(0-255). The result is a image where pixel values are white where motion occurs and black elsewhere. This can be seen in the tracking a hand gif in the description.

### Background Buffer
To reduce noise, a buffer for the previous 5 background frames were used. Instead of subtracting the previous frame, the pixel average of the previous 5 frames are used instead. This creates a more propnounced and longer lasting effect whenever something moves. Minor background movements are also detected less often as a result.
