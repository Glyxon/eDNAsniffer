#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h> 

// Control Layout
const int FAN_PIN = 14; // GPIO pin driving the Gate of the N-Channel MOSFET or Relay

// Target Environmental Thresholds (Adjustable)
const float TEMP_MAX_THRESHOLD = 25.0; // Do not sample if ambient temp exceeds 25°C
const float HUM_MIN_THRESHOLD  = 65.0; // Only initiate sampling if humidity is >= 65%
const float HYSTERESIS_TEMP    = 1.5;  // Temperature safety offset
const float HYSTERESIS_HUM     = 3.0;  // Humidity safety offset

// Non-blocking Timing Control
unsigned long prevMillis = 0;
const long interval = 5000; // Poll the telemetry cluster every 5 seconds

// State Machine Variables
enum SystemState { IDLE, SAMPLING, COOLDOWN };
SystemState currentState = IDLE;
unsigned long cooldownStart = 0;
const long cooldownDuration = 900000; // 15-minute lock-out period in milliseconds

Adafruit_BME280 bme; 

void setup() {
  Serial.begin(115200);
  pinMode(FAN_PIN, OUTPUT);
  digitalWrite(FAN_PIN, LOW); // Enforce safe state on boot

  if (!bme.begin(0x76)) {
    Serial.println("Error: BME280 sensor cluster not found on I2C bus!");
    while (1);
  }
  
  Serial.println("Glyxon eDNA Node Active. Commencing climate monitoring...");
}

void loop() {
  unsigned long currentMillis = millis();

  // Asynchronous Polling Loop
  if (currentMillis - prevMillis >= interval) {
    prevMillis = currentMillis;

    float currentTemp = bme.readTemperature();
    float currentHum  = bme.readHumidity();

    Serial.print("Temp: "); Serial.print(currentTemp);
    Serial.print("°C | Hum: "); Serial.print(currentHum); Serial.println("%");

    // Finite State Machine Logic
    switch (currentState) {
      
      case IDLE:
        // Core Trigger Matrix: Low Temperature AND High Humidity
        if (currentTemp <= TEMP_MAX_THRESHOLD && currentHum >= HUM_MIN_THRESHOLD) {
          Serial.println("➔ [BIOLOGICAL ALERT] Target environmental window hit. Commencing capture...");
          digitalWrite(FAN_PIN, HIGH); // Spin up the 3010 fan / centrifugal blower
          currentState = SAMPLING;
        }
        break;

      case SAMPLING:
        // Safe Shut-down Sequence utilizing Hysteresis parameters to damp jitter
        if (currentTemp > (TEMP_MAX_THRESHOLD + HYSTERESIS_TEMP) || 
            currentHum < (HUM_MIN_THRESHOLD - HYSTERESIS_HUM)) {
          Serial.println("➔ [NOTICE] Atmospheric conditions degrading. Aborting sampling run...");
          digitalWrite(FAN_PIN, LOW); // Cut motor power
          cooldownStart = millis();
          currentState = COOLDOWN;
        }
        break;

      case COOLDOWN:
        // Hardware lock-out phase to let the sampling micro-environment settle
        if (millis() - cooldownStart >= cooldownDuration) {
          Serial.println("➔ Cooldown complete. Re-entering IDLE surveillance loop.");
          currentState = IDLE;
        }
        break;
    }
  }
}