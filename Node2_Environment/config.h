#ifndef CONFIG_NODE2_H
#define CONFIG_NODE2_H

// ============================================================
//  Node 2 — Environment Configuration
//  Board: ESP32S 38-pin Development Board
//
//  ⚠️  ADC RULE: ALL analog pins must be ADC1 (GPIO32-39)
//       while WiFi/ESP-NOW is active.
// ============================================================

// ============================================================
//  ULTRASONIC SENSOR PINS (HC-SR04 / JSN-SR04T)
// ============================================================
#define PIN_TRIG_TANK1          12      // Trigger — Feed Tank
#define PIN_ECHO_TANK1          13      // Echo    — Feed Tank
#define PIN_TRIG_TANK2          14      // Trigger — Product Tank
#define PIN_ECHO_TANK2          27      // Echo    — Product Tank

// Tank physical dimensions (cm) — adjust to actual tank size
#define TANK1_MAX_DEPTH_CM      50.0f   // Distance from sensor to empty tank bottom
#define TANK2_MAX_DEPTH_CM      50.0f

// ============================================================
//  DHT22 SENSOR
// ============================================================
#define PIN_DHT22               4

// ============================================================
//  DS18B20 WATER TEMPERATURE (OneWire Bus)
// ============================================================
#define PIN_DS18B20             5

// ============================================================
//  GAS SENSORS (ADC1 only)
// ============================================================
#define PIN_GAS_1               34      // ADC1_CH6 — MQ-2 or MQ-135
#define PIN_GAS_2               35      // ADC1_CH7 — Second gas sensor

// ============================================================
//  FAN RELAY PINS
// ============================================================
#define PIN_RELAY_FAN1          26
#define PIN_RELAY_FAN2          25
#define PIN_RELAY_FAN3          33

// ============================================================
//  RELAY LOGIC (Active-LOW relay modules)
// ============================================================
#define RELAY_ON                LOW
#define RELAY_OFF               HIGH

// ============================================================
//  TEMPERATURE THRESHOLDS
// ============================================================
#define TEMP_FAN_THRESHOLD      35.0f   // °C — Turn fans on above this temp

// ============================================================
//  SAMPLING INTERVAL
// ============================================================
#define SAMPLING_INTERVAL_MS    5000    // Send data every 5 seconds

// ============================================================
//  ESP-NOW — Hub MAC Address (replace with actual Hub MAC)
// ============================================================
uint8_t hubAddress[] = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF};

// ============================================================
//  SERIAL DEBUG
// ============================================================
#define SERIAL_BAUD_RATE        115200

#endif // CONFIG_NODE2_H
