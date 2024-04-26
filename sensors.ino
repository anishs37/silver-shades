#include <DHT.h>

// Define the type of DHT sensor you're using (DHT11 or DHT22)
#define DHT_TYPE DHT11 // Change this to DHT22 if you're using DHT22

// Define the pin to which your DHT sensor is connected
const int dhtPin = 3; // Change this to the pin your DHT sensor is connected to

// Define the pin to which your LDR is connected
const int ldrPin = A3; // Change this to the pin your LDR sensor is connected to

// Define the pin to which your PIR sensor is connected
const int pirPin = 2; // Change this to the pin your PIR sensor is connected to

// Initialize DHT sensor
DHT dht(dhtPin, DHT_TYPE);

void setup() {
  // Start serial communication
  Serial.begin(9600);
  
  // Initialize DHT sensor
  dht.begin();
  
  // Set the PIR pin as input
  pinMode(pirPin, INPUT);
}

void loop() {
  // Read humidity value from DHT sensor
  float humidity = dht.readHumidity();
  
  // Read temperature value from DHT sensor
  float temperature = dht.readTemperature();
  
  // Read the value from the LDR
  int ldrValue = analogRead(ldrPin);
  
  // Read the value from the PIR sensor
  int motionDetected = digitalRead(pirPin);
  
  // Print sensor readings to serial monitor
  Serial.print("Humidity: ");
  Serial.print(humidity);
  Serial.print("% - Temperature: ");
  Serial.print(1.8 * temperature + 32);
  Serial.print(", °F - LDR Value: ");
  Serial.print(ldrValue);
  Serial.print("; Motion Detected: ");
  Serial.println(motionDetected ? "Yes" : "No");
  
  // Delay for a short period to avoid flooding the serial monitor
  delay(2000);
}
