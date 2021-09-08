#include <Servo.h>

//pin values
const int laserPin = 7;
const int joystickXPin = A0;
const int joystickYPin = A1;
const int joystickClickPin = A2;
const int servoXPin = 9;
const int servoYPin = 10;


//laser turret object
class Turret{
  public:
    Servo servoX;
    Servo servoY;

    //analog read values for joystick
    int joystickXValue;
    int joystickYValue;
    int joystickClickValue;

    //angle to set the servos to
    int joystickXAngle = 90;
    int joystickYAngle = 90;

    //switch value for calibration
    bool calibrated = false;

    //dimensions of frame
    int imgHeight = 480;
    int imgWidth = 640;
    
    /*
    bounding angle refers to an angle a servo motor is set to 
    when the laser is touching the edge of the frame
    */

    //number of bounding angles that have been found 
    int boundingAnglesFound = 0;
    
    //stores bounding angles [left, right, top, bottom]
    int boundingAngles[4];

    //stores the bytes sent by the python program to form a command
    char cmd_in[32];
    //laser coordinates send from the python program
    int coordinate_X;
    int coordinate_Y;

    //initialize pins
    Turret(){
      servoX.attach(servoXPin);
      servoY.attach(servoYPin);

      pinMode(laserPin, OUTPUT);
      pinMode(joystickXPin, INPUT);
      pinMode(joystickYPin, INPUT);
      pinMode(joystickClickPin, INPUT);
      }
      
    //method to move joystick when calibrating turret
    void joystick_move(){
      //reads joystick values
      joystickXValue = analogRead(joystickXPin);
      joystickYValue = analogRead(joystickYPin);

      //if joystick is moved in any extreme, change the angle by one degree
      if (joystickXValue > 900)
        joystickXAngle++;
      else if (joystickXValue < 200)
        joystickXAngle--;
      if (joystickYValue > 900)
        joystickYAngle++;
      else if (joystickYValue < 200)
        joystickYAngle--;

      if (joystickYAngle > 180)
        joystickYAngle = 180;
      else if (joystickYAngle < 0)
        joystickYAngle = 0;
      if (joystickXAngle > 180)
        joystickXAngle = 180;
      else if (joystickXAngle < 0)
        joystickXAngle = 0;
        
      servoX.write(joystickXAngle);
      servoY.write(joystickYAngle);
    }

    //method to recieve a command from the python program through serial communication
    //iteratively collects bytes which represent digits in a number when the byte 'x' or 'y' is recieved
    //'x' and 'y' denotes a command to change the x and y servo respectively
    //'>' denotes the end of the command
    //converts string to int and moves servo to that number 
    void recieve_cmd(){
      static boolean recvInProgress = false;
      static byte idx = 0;
      char startMarkerX = 'x';
      char startMarkerY = 'y';
      char endMarker = '>';
      char char_in;
      bool cmd_is_x;
    
      while(Serial.available() > 0)
      {
        char_in = Serial.read();

        if (recvInProgress){
          if (char_in != endMarker){
            cmd_in[idx] = char_in;
            idx++;
            if (idx >= 32) {
              idx = 31;
              }
          }
          else{
            cmd_in[idx] = '\0';
            recvInProgress = false;
            idx = 0;
            if (cmd_is_x){
              coordinate_X = atoi(cmd_in);
              coordinate_move(true);
            }
            else{
              coordinate_Y = atoi(cmd_in);
              coordinate_move(false);
            }
              
          }
        }
        
        else if (char_in == startMarkerX){
          recvInProgress = true;
          cmd_is_x = true;
        }

        else if(char_in == startMarkerY){
          recvInProgress = true;
          cmd_is_x = false;
        }
        }
      
      }    
    //maps coordinates to the bounding angles to find angles needed to point laser at coordinate
    void coordinate_move(bool move_x){
      if (move_x)
      {
        int x_angle = map(coordinate_X, 0, imgWidth, boundingAngles[0], boundingAngles[1]);
        servoX.write(x_angle);
      }
      else
      {
        int y_angle = map(coordinate_Y, 0, imgHeight, boundingAngles[2], boundingAngles[3]);
        servoY.write(y_angle);
      }
    }
    
    //check if the joystick button has been clicked or not to set border/boundary angle
    void calibrate_boundaries(){
      //check if joystick button click
      if (analogRead(joystickClickPin) < 10)
      {
        //setting the left and right bounding angles with respect to x servo
        if (boundingAnglesFound < 2){
          boundingAngles[boundingAnglesFound] = joystickXAngle;
          boundingAnglesFound++;
        }
        //setting the top and bottom bounding angles with respect to y servo
        else{
          boundingAngles[boundingAnglesFound] = joystickYAngle;
          boundingAnglesFound++;
          //if all 4 bounding angles have been found, set turret to calibrated and communicate such to python program
          if (boundingAnglesFound > 3)
            calibrated = true;
            Serial.print(1);
        }
        //visible laser flash when bounding angle set
        flash_laser();
      }
    }
    //laser flashes multiple times
    void flash_laser (){
      digitalWrite(laserPin, LOW);
      delay(100);
      digitalWrite(laserPin, HIGH);
      delay(100);
      digitalWrite(laserPin, LOW);
      delay(100);
      digitalWrite(laserPin, HIGH);
      delay(100);
      digitalWrite(laserPin, LOW);
      delay(100);
      digitalWrite(laserPin, HIGH);
      delay(100);
    }
};

Turret* turret;

void setup() {
  turret = new Turret();
  digitalWrite(laserPin, HIGH);

  Serial.begin(9600);
}

void loop() {
  //use joystick move until turret is calibrated
  turret->joystick_move();
  if (turret->calibrated == false)
    turret->calibrate_boundaries();
  //recieves coordinate commands for turret when calibrated
  else
  {
    turret->recieve_cmd();
  }
    

   
  delay(50);
}
