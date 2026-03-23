#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>

const char* ssid = "new";
const char* password = "12345678";

ESP8266WebServer server(80);

// Rover motors
int IN1 = 5;   // D1
int IN2 = 4;   // D2
int IN3 = 0;   // D3
int IN4 = 2;   // D4
int speedVal = 100;

// Blades
int BLADE1 = 14;  // D5
int BLADE2 = 12;  // D6

// Indicators - EXACT LOGIC
int LED_RED = 13; // D7 - motion indicator
int BUZZER  = 15; // D8 - cutting sound

void setup() {
  Serial.begin(115200);

  pinMode(IN1, OUTPUT); 
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT); 
  pinMode(IN4, OUTPUT);
  pinMode(BLADE1, OUTPUT); 
  pinMode(BLADE2, OUTPUT);
  pinMode(LED_RED, OUTPUT); 
  pinMode(BUZZER, OUTPUT);

  // ALL OFF initially
  analogWrite(IN1, 0); 
  analogWrite(IN2, 0); 
  analogWrite(IN3, 0); 
  analogWrite(IN4, 0);
  digitalWrite(BLADE1, LOW); 
  digitalWrite(BLADE2, LOW);
  digitalWrite(LED_RED, LOW);   // LED off
  digitalWrite(BUZZER, LOW);    // Buzzer off

  WiFi.begin(ssid, password);
  Serial.print("Connecting WiFi...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500); Serial.print(".");
  }
  Serial.println("\nIP: " + WiFi.localIP().toString());

  // 🌱 GREEN = WEED DETECTED → CUT (BUZZER HIGH)
  server.on("/green", []() {
    // Stop rover
    analogWrite(IN1, 0); 
    analogWrite(IN2, 0);
    analogWrite(IN3, 0); 
    analogWrite(IN4, 0);
    
    // Blades ON
    digitalWrite(BLADE1, HIGH); digitalWrite(BLADE2, HIGH);
    
    // WEED LOGIC: Buzzer HIGH, LED LOW
    digitalWrite(BUZZER, HIGH);   // Buzzer ON
    digitalWrite(LED_RED, LOW);   // LED OFF
    
    Serial.println("🟢 WEED - CUTTING (Buzzer ON)");
    server.send(200, "text/plain", "CUTTING");
  });

  // 🔴 RED = NO WEED → MOVE (LED HIGH)
  server.on("/red", []() {
    // Blades OFF
    digitalWrite(BLADE1, LOW); 
    digitalWrite(BLADE2, LOW);
    
    // Move forward
    analogWrite(IN1, speedVal); 
    analogWrite(IN2, 0);
    analogWrite(IN3, speedVal); 
    analogWrite(IN4, 0);
    
    // NO WEED LOGIC: LED HIGH, Buzzer LOW/OFF
    digitalWrite(LED_RED, HIGH);  // LED ON (moving)
    digitalWrite(BUZZER, LOW);    // Buzzer OFF
    
    Serial.println("🔴 NO WEED - MOVING (LED ON)");
    server.send(200, "text/plain", "MOVING");
  });

  // Debug
  server.on("/status", []() {
    String s = "LED:" + String(digitalRead(LED_RED)) + 
               " BUZZ:" + String(digitalRead(BUZZER)) + 
               " Blades:" + String(digitalRead(BLADE1)) +
               " IP:" + WiFi.localIP().toString();
    server.send(200, "text/plain", s);
  });

  server.begin();
  Serial.println("Server ready! Test: /status /green /red");
}

void loop() {
  server.handleClient();
}
