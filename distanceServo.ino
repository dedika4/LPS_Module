// Includes the Servo library
#include <Servo.h>. 

// Defines Tirg and Echo pins of the Ultrasonic Sensor
//const int trigPin = 10;
//const int echoPin = 11;
// Variables for the duration and the distance
long duration;
float distance;

Servo myServo; // Creates a servo object for controlling the servo motor

void setup() {
  Serial.begin(9600);
  myServo.attach(12); // Defines on which pin is the servo motor attached
}

void loop() {
  // rotates the servo motor from 15 to 165 degrees
  for(int i=0;i<=180;i++){  
    myServo.write(i);
    delay(100);
    Serial.println(i); // Sends the current degree into the Serial Port
    Serial.print(","); // Sends addition character right next to the previous value needed later in the Processing IDE for indexing
  }
  
  // Repeats the previous lines from 165 to 15 degrees
  for(int i=180;i>0;i--){  
    myServo.write(i);
    delay(100);
    Serial.println(i);
    Serial.print(",");
  }
}
