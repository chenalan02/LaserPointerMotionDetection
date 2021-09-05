#include <Servo.h>
Servo servoX;
Servo servoY;

const int laserPin = 7;
const int joystickXPin = A0;
const int joystickYPin = A1;

int joystickXValue;
int joystickYValue;
int servoXPos;
int servoYPos;

void setup() {
  
  Serial.begin(9600);

  servoX.attach(9);
  servoY.attach(10);
  
  digitalWrite(laserPin, HIGH); 
  
  pinMode(laserPin, OUTPUT);
  pinMode(joystickXPin, INPUT);
  pinMode(joystickYPin, INPUT);
}

void loop() {
 
  joystickXValue = analogRead(joystickXPin);
  joystickYValue = analogRead(joystickYPin);

  servoXPos = map(joystickXValue, 0, 1023, 0, 180);
  servoYPos = map(joystickYValue, 0, 1023, 0, 180);

  servoX.write(servoXPos);
  servoY.write(servoYPos);
  Serial.println(servoXPos);
  Serial.println(servoYPos);

  delay(100);
}
