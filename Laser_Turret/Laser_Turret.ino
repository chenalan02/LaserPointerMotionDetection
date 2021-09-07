#include <Servo.h>

const int laserPin = 7;
const int joystickXPin = A0;
const int joystickYPin = A1;
const int joystickClickPin = A2;
const int servoXPin = 9;
const int servoYPin = 10;

class Turret{
  public:
    Servo servoX;
    Servo servoY;
    
    int joystickXValue;
    int joystickYValue;
    int joystickClickValue;

    int joystickXAngle = 90;
    int joystickYAngle = 90;

    bool calibrated = false;
    int imgHeight = 480;
    int imgWidth = 640;

    int boundingAnglesFound = 0;
    //[left, right, top, bottom]
    int boundingAngles[4];

    char cmd_in[32];
    int coordinate_X;
    int coordinate_Y;

    Turret(){
      servoX.attach(servoXPin);
      servoY.attach(servoYPin);

      pinMode(laserPin, OUTPUT);
      pinMode(joystickXPin, INPUT);
      pinMode(joystickYPin, INPUT);
      pinMode(joystickClickPin, INPUT);
      }

    void joystick_move(){
      joystickXValue = analogRead(joystickXPin);
      joystickYValue = analogRead(joystickYPin);
      
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
    

    void calibrate_boundaries(){
      if (analogRead(joystickClickPin) < 10)
      {
        if (boundingAnglesFound < 2){
          boundingAngles[boundingAnglesFound] = joystickXAngle;
          boundingAnglesFound++;
        }
        else
        {
          boundingAngles[boundingAnglesFound] = joystickYAngle;
          boundingAnglesFound++;
          if (boundingAnglesFound > 3)
            calibrated = true;
            Serial.print(1);
            //while (!Serial.available()){}
            //imgHeight = Serial.read();
            //imgWidth = Serial.read();
        }
        flash_laser();
      }
    }

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
  turret->joystick_move();
  if (turret->calibrated == false)
    turret->calibrate_boundaries();
  else
  {
    turret->recieve_cmd();
  }
    

   
  delay(50);
}
