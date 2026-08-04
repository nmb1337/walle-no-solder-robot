// WALLE controller for ESP32 DevKitC + TB6612FNG + PCA9685.
// Install libraries: ArduinoJson 6 and Adafruit PWM Servo Driver Library.
// Keep motor battery and 5V logic rails separate, with a common ground.
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

const char* WIFI_SSID = "CHANGE_ME";
const char* WIFI_PASSWORD = "CHANGE_ME";
const char* GATEWAY = "http://192.168.1.20:8100";

// TB6612FNG: AIN1/AIN2/PWMA, BIN1/BIN2/PWMB, STBY.
const int AIN1=25, AIN2=26, PWMA=27;
const int BIN1=32, BIN2=33, PWMB=14, STBY=13;
const int PWMA_CHANNEL = 0, PWMB_CHANNEL = 1;
Adafruit_PWMServoDriver pwm(0x40);
const int servoChannels[6] = {0,1,2,3,4,5};
unsigned long lastCommandMs = 0;
unsigned long lastPollMs = 0;
long lastEventId = 0;

// Arduino-ESP32 2.x addresses LEDC by channel; 3.x addresses it by pin.
// Keep one source compatible with both commonly shipped ESP32 board packages.
void setupMotorPwm() {
#if ESP_ARDUINO_VERSION_MAJOR >= 3
  ledcAttachChannel(PWMA, 20000, 8, PWMA_CHANNEL);
  ledcAttachChannel(PWMB, 20000, 8, PWMB_CHANNEL);
#else
  ledcSetup(PWMA_CHANNEL, 20000, 8); ledcAttachPin(PWMA, PWMA_CHANNEL);
  ledcSetup(PWMB_CHANNEL, 20000, 8); ledcAttachPin(PWMB, PWMB_CHANNEL);
#endif
}

void writeMotorPwm(int pin, int channel, int duty) {
  duty = constrain(duty, 0, 255);
#if ESP_ARDUINO_VERSION_MAJOR >= 3
  ledcWrite(pin, duty);
#else
  ledcWrite(channel, duty);
#endif
}

void motor(int in1, int in2, int pwmChannel, int speed) {
  digitalWrite(in1, speed > 0); digitalWrite(in2, speed < 0);
  writeMotorPwm(pwmChannel == PWMA_CHANNEL ? PWMA : PWMB, pwmChannel, abs(speed));
}
void stopMotors() { motor(AIN1,AIN2,PWMA_CHANNEL,0); motor(BIN1,BIN2,PWMB_CHANNEL,0); digitalWrite(STBY, LOW); }
void moveAction(const char* action) {
  const int speed = 150;
  digitalWrite(STBY, HIGH);
  if (!strcmp(action,"forward")) { motor(AIN1,AIN2,PWMA_CHANNEL,speed); motor(BIN1,BIN2,PWMB_CHANNEL,speed); }
  else if (!strcmp(action,"back")) { motor(AIN1,AIN2,PWMA_CHANNEL,-speed); motor(BIN1,BIN2,PWMB_CHANNEL,-speed); }
  else if (!strcmp(action,"left")) { motor(AIN1,AIN2,PWMA_CHANNEL,-speed); motor(BIN1,BIN2,PWMB_CHANNEL,speed); }
  else if (!strcmp(action,"right")) { motor(AIN1,AIN2,PWMA_CHANNEL,speed); motor(BIN1,BIN2,PWMB_CHANNEL,-speed); }
  else { stopMotors(); }
  lastCommandMs = millis();
}
void setServoAngle(uint8_t channel, int angle) {
  angle = constrain(angle, 10, 170);
  int pulse = map(angle, 0, 180, 150, 600);
  pwm.setPWM(channel, 0, pulse);
}
void applyEvent(JsonObject event) {
  JsonObject payload = event["payload"];
  const char* kind = event["kind"] | "";
  if (!strcmp(kind,"move")) moveAction(payload["action"] | "stop");
  if (!strcmp(kind,"action")) {
    const char* head = payload["head"] | "";
    const char* arm = payload["arm"] | "";
    if (!strcmp(head,"left")) setServoAngle(servoChannels[0], 55);
    if (!strcmp(head,"center")) setServoAngle(servoChannels[0], 90);
    if (!strcmp(head,"right")) setServoAngle(servoChannels[0], 125);
    if (!strcmp(head,"up")) setServoAngle(servoChannels[1], 65);
    if (!strcmp(head,"down")) setServoAngle(servoChannels[1], 118);
    if (!strcmp(head,"center")) setServoAngle(servoChannels[1], 90);
    if (!strcmp(arm,"raise")) { setServoAngle(servoChannels[2], 125); setServoAngle(servoChannels[3], 75); setServoAngle(servoChannels[4], 55); setServoAngle(servoChannels[5], 105); }
    if (!strcmp(arm,"stow")) { setServoAngle(servoChannels[2], 70); setServoAngle(servoChannels[3], 110); setServoAngle(servoChannels[4], 110); setServoAngle(servoChannels[5], 70); }
  }
}
void pollEvents() {
  HTTPClient http; http.begin(String(GATEWAY) + "/api/events");
  int code = http.GET();
  if (code == 200) {
    DynamicJsonDocument doc(8192);
    if (!deserializeJson(doc, http.getString())) {
      for (JsonObject event : doc["events"].as<JsonArray>()) {
        long id = event["id"] | 0;
        if (id > lastEventId) { applyEvent(event); lastEventId = id; }
      }
    }
  }
  http.end();
}
void setup() {
  pinMode(AIN1,OUTPUT); pinMode(AIN2,OUTPUT); pinMode(BIN1,OUTPUT); pinMode(BIN2,OUTPUT); pinMode(STBY,OUTPUT);
  setupMotorPwm(); stopMotors();
  Wire.begin(); pwm.begin(); pwm.setOscillatorFrequency(27000000); pwm.setPWMFreq(50);
  for (int ch : servoChannels) setServoAngle(ch, 90);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) delay(300);
  lastCommandMs = millis();
}
void loop() {
  if (millis() - lastPollMs > 250 && WiFi.status() == WL_CONNECTED) { lastPollMs = millis(); pollEvents(); }
  if (millis() - lastCommandMs > 1000) stopMotors();
  delay(10);
}
