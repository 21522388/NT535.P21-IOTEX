#include <Servo.h>
#include <ArduinoJson.h>

// PINS
#define LED_PIN 2 // GPIO2
#define TRIG_PIN 5  // GPIO 5 (D1) 
#define ECHO_PIN 4  // GPIO 4 (D2)
#define SERVO_PIN 14  // GPIO 14 (D5)

// CONSTANTS
#define THRESHOLD_MIN 10
#define THRESHOLD_MID 25
#define THRESHOLD_MAX 40
#define SOUND_SPEED 0.034
#define CLOSE_ANGLE 0
#define OPEN_ANGLE 90
#define MOTION_DELAY 100

// VARIABLES
long duration;
int distance;
int userCount = 0;
bool isUpdate = false;
int servoState = 0;
bool doorAuto = true;
int doorStatus = 3;
int distanceOld;
unsigned long previousMillis = 0;
const long interval = 10000;

Servo servo;

// FUNCTIONS
void beep(int duration) {
  digitalWrite(LED_PIN, HIGH);
  delay(duration);
  digitalWrite(LED_PIN, LOW);
}

void resetServo() {
  servo.write(CLOSE_ANGLE);
}

int calculateDistance() { // Measure distance using ultrasonic sensor
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  duration = pulseIn(ECHO_PIN, HIGH, 30000);  // Read travel time

  if (duration == 0) {
    return -1;
  } else {
    distance = duration * SOUND_SPEED / 2;
    return distance;
  }

  return distance;
}

// RUNTIME
void setup() {
  resetServo();

  Serial.begin(115200);
  delay(10);

  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  servo.attach(SERVO_PIN, 500, 2400);

  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
}

void loop() {
  distance = calculateDistance();

  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;

    // Create JSON payload
    StaticJsonDocument<200> doc;
    doc["userCount"] = userCount;
    doc["doorStatus"] = doorStatus;
    doc["distance"] = distance;
    
    // Serialize JSON to string
    String jsonBuffer;
    serializeJson(doc, jsonBuffer);
    
    Serial.println(jsonBuffer);
  }

  if (doorAuto == true) {
    if (distance < THRESHOLD_MAX && distance > THRESHOLD_MIN) {
      if (distance > (THRESHOLD_MID - 5) && distance < (THRESHOLD_MID + 5)) {
        if (distance >= distanceOld && isUpdate == false) {
          if (userCount > 0)
            userCount--;

          beep(50);
          isUpdate = true;
        } else if (distance < distanceOld && isUpdate == false) {
          userCount++;
          beep(50);
          isUpdate = true;
        }
      } else {
        isUpdate = false;
      }
      servo.write(OPEN_ANGLE);
    } else {
      servo.write(CLOSE_ANGLE);
    }
    distanceOld = distance;
  }
}