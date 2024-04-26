#include <Servo.h>

// Create a Servo object
Servo servoMotor;

// Define the pin to which your servo motor is connected
const int servoPin = 9; // Change this to the pin your servo motor is connected to
int incomingByte;

void setup() {
  // Attach the servo to the pin
  servoMotor.attach(servoPin);
  Serial.begin(9600);
}

void loop() {
  // Rotate the servo motor to a specific angle
  if (Serial.available() > 0) {
    incomingByte = Serial.read();
    if (incomingByte == 'H') {
      servoMotor.write(180);
    }
  }
  delay(3000); // Delay to avoid reading the motion sensor too frequently
}
