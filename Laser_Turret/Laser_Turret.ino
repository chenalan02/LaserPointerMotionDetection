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

    int boundingAnglesFound = 0;
    //[left, right, top, bottom]
    int boundingAngles[4];

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
        joystickXAngle += 2;
      else if (joystickXValue < 200)
        joystickXAngle -= 2;
      if (joystickYValue > 900)
        joystickYAngle += 2;
      else if (joystickYValue < 200)
        joystickYAngle -= 2;

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

    void calibrate_boundaries(){
      if (analogRead(joystickClickPin) < 10)
      {
        if (boundingAnglesFound < 3){
          boundingAngles[boundingAnglesFound] = joystickXValue;
          boundingAnglesFound++;
        }
        else
        {
          boundingAngles[boundingAnglesFound] = joystickYValue;
          boundingAnglesFound++;
          if (boundingAnglesFound > 3)
            calibrated = true;
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
  //if(Serial.available()){
  //      input = Serial.read();
  // }

  delay(100);
}
