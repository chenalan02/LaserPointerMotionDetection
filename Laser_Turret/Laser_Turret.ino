#include <Servo.h>
Servo servoX;
Servo servoY;

const int laserPin = 7;
const int joystickXPin = A0;
const int joystickYPin = A1;
const int joystickClickPin = 2;

class Turret{
  private:
    Servo servoX;
    Servo servoY;    

    turret(){
      servoX.attach(9);
      servoY.attach(10);

      pinMode(laserPin, OUTPUT);
      }
      
  public:
    virtual void move(servoXPos, servoYPos){
      servoX.write(servoXPos);
      servoY.write(servoYPos);
    }
}

class LaserTurret : public Turret{
  public:

    int joystickXValue;
    int joystickYValue;
    int joystickClickValue;
    
    LaserTurret(){
      pinMode(laserPin, OUTPUT);
      pinMode(joystickXPin, INPUT);
      pinMode(joystickYPin, INPUT);
      pinMode(joystickClickPin, INPUT);
      }

    void flashLaser(){
      if(joystickClickPin == 1):
      //todo

    void move override();
      joystickXValue = analogRead(joystickXPin);
      joystickYValue = analogRead(joystickYPin);

      servoX.write(map(joystickXValue, 0, 1023, 0, 179));
      servoY.write(map(joystickYValue, 0, 1023, 0, 179));
    }
}

void setup() {
  Turret turret;
  digitalWrite(laserPin, HIGH);
}

void loop() {
 
  joystickXValue = analogRead(joystickXPin);
  joystickYValue = analogRead(joystickYPin);

  servoXPos = map(joystickXValue, 0, 1023, 0, 180);
  servoYPos = map(joystickYValue, 0, 1023, 0, 180);

  servoX.write(servoXPos);
  servoY.write(servoYPos);

  delay(100);
}
