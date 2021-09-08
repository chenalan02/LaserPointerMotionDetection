# LaserPointerMotionDetection
A laser pointer turret that aims at and follows moving objects within its view. The turret consists of a laser attached to two servo motors controlling horizontal and vertical aim. Uses a arduino to control the laser and a background subtraction algorithm using OpenCV for motion detection. The center of the bounding box of the largest contour detected by OpenCV is used as the target for the laser to track. The turret must first be calibrated to determine the servo angles corresponding to when the laser is aiming at the borders of the frame. These bounding angles are used to map the pixel coordinates of the target to the angles of both servos in order to point the laser at the target.

Tracking A Hand          |  Tracking A Person
:-------------------------:|:-------------------------:
![Tracking A Hand](https://github.com/chenalan02/LaserPointerMotionDetection/blob/main/Readme%20Gifs/tracking%20hand.gif)  |  ![Tracking A Person](https://github.com/chenalan02/LaserPointerMotionDetection/blob/main/Readme%20Gifs/tracking%20person.gif)

<img src="https://github.com/chenalan02/LaserPointerMotionDetection/blob/main/Readme%20Images/Laser%20Turret%20Setup.jpg" width="400">

## Calibration
The laser must first be calibrated when main.py is initialized. A joystick connected to the arduino is used to move the laser slowly. The angles of the x and y servo which correspond to the borders of the camera frame are recorded by moving the laser and clicking the joystick when the laser is on the borders. This is done in the following order: left-> right-> top-> bottom. When the arduino receives coordinates to aim at(from the python program), it maps the x and y pixel value to a servo angle depending on the angles determined during calibration.

`int x_angle = map(coordinate_X, 0, imgWidth, boundingAngles[0], boundingAngles[1]);
        servoX.write(x_angle);`
        
Although this solution for aiming the turret is flawed, as it will be inaccurate near the corners of the frame, it's good enough for my purposes. I only need the turret to point and follow the approximate central location of movement and it does not have be to be extremely accurate. An accurate solution would involve calibrating/measuring the closest distance from the laser to the wall and the actual height and width of visible wall.

## Background Subtraction Algorithm
A background subtraction algorithm was created using OpenCV to detect motion. The algorithm works on the principle that the difference from subtracting the pixel values of consecutive frames will show where movement occurs. Both frames are processed into greyscale with a threshold applied to it. A gaussian blur is also applied to reduce noise. The absolute difference of the pixel values are then taken instead of regular subtraction to prevent integer overflow since pixel values are represented by 8 bit integers(0-255). The result is a image where pixel values are white where motion occurs and black elsewhere. This can be seen in the tracking a hand gif in the description.

### Background Buffer
To reduce noise, a buffer for the previous 5 background frames were used. Instead of subtracting the previous frame, the pixel average of the previous 5 frames are used instead. This creates a more propnounced and longer lasting effect whenever something moves. Minor background movements are also detected less often as a result.

## Code Documentation

### background_subtractor.py

#### `background_subtractor.BackgroundBuffer(self, width, height, scale))`
> Container object for storing pixel average of previous 5 frames

`self.width` - pixel width of image\
`self.height` - pixel height of image\
`self.buffer` - dequeue object for storing image\
`self.background` - pixel average of previous 5 frames\

`add_frame(self, frame)` 
* adds a frame to the buffer

`update_get_background(self)` 
* updates background with new frame by taking weighted average of pixel values


#### `background_subtractor.BackgroundSubtractor(self, processing_scale, arduino)`
> Container object for storing pixel average of previous 5 frames

`self.PROCESSING_SCALE` - scale to divide dimensions of processed image for faster performance\
`self.arduino` - arduino connected by serial port\
`self.cap` - webcam capture device\
`self.width` - pixel width of image\
`self.height` - pixel height of image\
`self.background_buffer` - background buffer object to store frames\
`self.laser_coordinates` - coordinates on the image where the laser aims at\
`self.calibrated` - variable for whether the turret has calibrated yet\

`self.update(self)`
* checks if the arduino has calibrated yet
* if it has, processes frame subtraction and determines bounding box for the biggest contour found, then sends coordinate of the center of the box to the arduino

`self.check_calibration(self)`
* checks if the arduino has send the byte b'1', which means it has finished calibrating


`self.send_laser_coordinates(self)`
* sends laser coordinates to arduino
* commands start with an 'x' or 'y' byte to indicate which servo to move, and ends with a '>' to represent the command end

### Laser_Turret.ino
#### `Laser_Turret::Turret`
> Object for handling calibration and movement to the turret

`Servo servoX` - servo that handles horizontal movement\
`Servo servoY` - servo that handles vertical movement\
`int joystickXValue` - analog read values for joystick in x direction\
`int joystickYValue` - analog read values for joystick in y direction\
`int joystickClickValue` - analog read values for joystick click down\
`int joystickXAngle = 90` - angle that the x servo is currently at due to joystick movement\
`int joystickYAngle = 90` - angle that the y servo is currently at due to joystick movement\
<br/>
`bool calibrated = false` - variable for whether the turret has calibrated yet\
`int imgHeight = 480` - height of the frame\
`int imgWidth = 640` - width of the frame\
<br/>
`int boundingAnglesFound = 0` - number of bounding angles that have been set\
`int boundingAngles[4]` - stores bounding angles [left, right, top, bottom]\
> bounding angle refers to an angle a servo motor is set to when the laser is touching the edge of the frame, used to map pixel coordinates to servo angles

`char cmd_in[32]` - stores the bytes sent by the python program to form a command\
`int coordinate_X` - pixel x coordinates command send from the python program\
`int coordinate_Y` - pixel y coordinates command send from the python program\

`Laser_Turret::Turret()`
* initializes pins and servos

`void joystick_move()`
* reads the x and y joystick position and moves the respective servo 1 degree in that direction

`void recieve_cmd()`
* recieves a command from the python program through serial communication
* iteratively collects bytes which represent digits in a number when the byte 'x' or 'y' is recieved
* 'x' and 'y' denotes a command to change the x and y servo respectively, '>' denotes the end of the command
* converts string to int and moves servo to that number 

`void coordinate_move(bool move_x)`
* maps coordinates to the bounding angles to find angles needed to point laser at coordinate
* `bool move_x` - indicates whether to move the x or y servo

`void calibrate_boundaries()`
* check if the joystick button has been clicked or not to set border/boundary angle in `int boundingAngles[4]`

`void flash_laser ()`
* laser flashes multiple times, used when a new boundary is set
