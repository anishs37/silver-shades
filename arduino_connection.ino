#include <RTCZero.h>

int photoresistorPin = A0;
int temperaturePin = A1;
int motionPin = 2;

void setup() {
  pinMode(photoresistorPin, INPUT);
  pinMode(motionPin, INPUT);
  pinMode(tempPin, INPUT);
}

void loop() {
//   int phtoresistorValue = analogRead(photoresistorPin);
//   int motionValue = digitalRead(motionPin);
//   int temperatureIn = analogRead(temperaturePin);
  int photoresistorValue = 800;
  int motion_detected = 1;
  int temp_in = 75;
  int temp_out = 90; // read in value from keyboard

  Serial.print(photoresistorValue);
  Serial.print(", ");
  Serial.print(motion_detected);
  Serial.print(", ");
  Serial.print(temp_in);
  Serial.print(", ");
  Serial.print(temp_out);

  // Delay for 55 seconds before the next reading
  delay(55000);
}