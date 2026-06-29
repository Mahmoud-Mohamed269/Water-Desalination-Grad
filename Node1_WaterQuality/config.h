/*
 * ============================================================
 *  Smart Water Desalination Monitoring System
 *  Master Configuration Header
 *  File: Node1_WaterQuality/config.h
 * ============================================================
 *  Board:  ESP32S 38-pin Development Board
 *  Author: Water Desalination Project
 *  Phase:  3 — ESP32 Firmware Development
 * ============================================================
 *
 *  ⚠️  CRITICAL ESP32 ADC RULE:
 *  ADC2 pins (GPIO0,2,4,12-15,25-27) CANNOT be used for
 *  analogRead() while WiFi is active. ALL analog sensors
 *  MUST use ADC1 pins: GPIO32, GPIO33, GPIO34, GPIO35, GPIO36, GPIO39
 *
 *  ✅  GPIO27 (PIN_FLOW_PERMEATE) is ADC2 but is used ONLY as a
 *  digital hardware interrupt — NOT analogRead(). This is safe.
 * ============================================================
 */

#ifndef CONFIG_H
#define CONFIG_H

// ============================================================
// FIRMWARE VERSION
// ============================================================
#define FIRMWARE_VERSION        "1.1.0"
#define DEVICE_ID               "device_001"
#define DEVICE_NAME             "RO Unit Alpha"

// ============================================================
// ANALOG SENSOR PINS  (ADC1 ONLY — WiFi-safe)
// ============================================================
//  GPIO34 (ADC1_CH6) — pH Feed
//  GPIO35 (ADC1_CH7) — TDS Feed
//  GPIO32 (ADC1_CH4) — Turbidity Feed
//  GPIO33 (ADC1_CH5) — Pressure Feed (G1/4, via 10kΩ/20kΩ divider)
//  GPIO36 (VP/ADC1_CH0) — pH Permeate
//  GPIO39 (VN/ADC1_CH3) — TDS Permeate
//  (Turbidity Permeate not wired — only one turbidity sensor on feed line)
#define PIN_PH_FEED             34      // ADC1_CH6 — pH feed analog output
#define PIN_TDS_FEED            35      // ADC1_CH7 — TDS feed analog output
#define PIN_TURBIDITY_FEED      32      // ADC1_CH4 — Turbidity feed (5V via 10kΩ/20kΩ divider)
#define PIN_PRESSURE_FEED       33      // ADC1_CH5 — Pressure sensor G1/4 (5V via 10kΩ/20kΩ divider)
#define PIN_PH_PERMEATE         36      // ADC1_CH0 (VP) — pH permeate analog output
#define PIN_TDS_PERMEATE        39      // ADC1_CH3 (VN) — TDS permeate analog output

// ============================================================
// DIGITAL SENSOR PINS
// ============================================================
#define PIN_DS18B20             4       // OneWire — DS18B20 temperature data
#define PIN_WATER_LEVEL_FEED    5       // Digital IN — XKC-Y25 feed tank
#define PIN_WATER_LEVEL_PRODUCT 19      // Digital IN — XKC-Y25 product tank
#define PIN_FLOW_SENSOR         18      // Interrupt — YF-S201 flow feed pulse
#define PIN_FLOW_PERMEATE       27      // Interrupt — YF-S201 flow permeate pulse

// ============================================================
// ACTUATOR PINS (RELAY MODULE)
// ============================================================
#define PIN_RELAY_PUMP          26      // Digital OUT — RO Pump relay
#define PIN_RELAY_VALVE         25      // Digital OUT — Solenoid Valve relay

// ============================================================
// STATUS LED
// ============================================================
#define PIN_STATUS_LED          2       // Built-in LED

// ============================================================
// RELAY LOGIC (Change if relay module is Active-HIGH)
// ============================================================
#define RELAY_ON                LOW     // Most relay modules are Active-LOW
#define RELAY_OFF               HIGH

// ============================================================
// ADC CONFIGURATION
// ============================================================
#define ADC_RESOLUTION          4095    // 12-bit ADC (0-4095)
#define ADC_VREF                3.3f    // ESP32 ADC reference voltage (V)
#define ADC_SAMPLES             10      // Oversampling count per reading
#define ADC_SAMPLE_DELAY_MS     2       // Delay between oversamples (ms)

// ============================================================
// VOLTAGE DIVIDER COMPENSATION
// ============================================================
// Turbidity & Pressure sensors output 0-4.5V (5V powered)
// Voltage divider: R1=10kΩ series, R2=20kΩ to GND
// Vout = Vin × (20/(10+20)) = Vin × 0.6667
// To recover original: Vin = Vout / 0.6667 × 1.0
#define VDIV_RATIO_TURBIDITY    1.5f    // Multiply ADC voltage by this to get actual sensor voltage
// Pressure sensor G1/4: outputs 0.5-4.5V at 5V supply (10k/20k divider: ×1.5 recovery)
#define VDIV_RATIO_PRESSURE     1.5f    // Same divider as turbidity
// pH sensor: direct 0-3.3V output (no divider needed on this kit)
#define VDIV_RATIO_PH           1.0f
// TDS sensor V1.0: max output 2.3V (no divider needed)
#define VDIV_RATIO_TDS          1.0f

// ============================================================
// SAMPLING INTERVALS
// ============================================================
#define SAMPLING_INTERVAL_MS    5000    // Send data every 5 seconds
#define FLOW_COUNT_INTERVAL_MS  1000    // Count flow pulses every 1 second
#define DS18B20_CONVERSION_MS   750     // 12-bit DS18B20 conversion time

// ============================================================
// DEEP SLEEP CONFIGURATION
// ============================================================
#define SLEEP_ENABLED           true
#define TIMER_WAKE_INTERVAL_SEC 30      // Wake every 30s to check commands
#define IDLE_TIMEOUT_MIN        10      // Go to sleep after 10 min of no flow
#define uS_TO_S_FACTOR          1000000ULL

// ============================================================
// FLOW SENSOR (YF-S201) CALIBRATION
// ============================================================
// YF-S201: 7.5 pulses per second per litre/minute
// Flow (L/min) = pulse_count (per second) / 7.5
#define FLOW_CALIBRATION_FACTOR 7.5f   // Pulses per second per L/min

// ============================================================
// DS18B20 CONFIGURATION
// ============================================================
#define DS18B20_RESOLUTION      12      // 9, 10, 11, or 12 bit
#define DS18B20_MAX_SENSORS     2       // Maximum number of sensors on bus

// ============================================================
// pH SENSOR — DEFAULT CALIBRATION
// (Will be overwritten by stored calibration values)
// ============================================================
#define PH_VOLTAGE_AT_PH7       2.50f   // Midpoint voltage at pH 7.0 (calibrate!)
#define PH_SLOPE                -0.178f // Voltage per pH unit (negative: higher pH = lower V)
#define PH_TEMP_COEFFICIENT     0.0198f // Nernst equation temp coefficient

// ============================================================
// TDS SENSOR — DEFAULT CALIBRATION
// ============================================================
#define TDS_TEMP_COEFFICIENT    0.02f   // 2% per °C compensation
#define TDS_REFERENCE_TEMP      25.0f   // Reference temperature (°C)

// ============================================================
// TURBIDITY SENSOR — CALIBRATION
// ============================================================
// Turbidity voltage is INVERSE: high voltage = clear water (0 NTU)
// Approximate: NTU = -1120.4 × V² + 5742.3 × V − 4353.8  (manufacturer curve)
// Or simplified linear for 0-100 NTU range:
// NTU = (4.2 - V) × 1000  where 4.2V = 0 NTU
#define TURBIDITY_VOLTAGE_CLEAR 4.2f    // Voltage at 0 NTU (clear water)
#define TURBIDITY_SLOPE         1000.0f // NTU per volt change

// ============================================================
// PRESSURE SENSOR (G1/4 Analog) — CALIBRATION
// ============================================================
// Sensor: 0–1.2 MPa (0–12 bar) output 0.5–4.5V at 5V supply
// After 10kΩ/20kΩ divider: Vout = Vin × 0.6667
// Recovery in software: Vin = Vout × VDIV_RATIO_PRESSURE (×1.5)
// Pressure (bar) = ((Vin - PRESSURE_OFFSET_V) / (PRESSURE_SCALE_V - PRESSURE_OFFSET_V)) × PRESSURE_MAX_BAR
#define PRESSURE_OFFSET_V       0.5f    // Voltage at 0 bar (sensor output at zero pressure)
#define PRESSURE_SCALE_V        4.5f    // Voltage at full-scale pressure
#define PRESSURE_MAX_BAR        12.0f   // Full-scale pressure in bar (0–1.2 MPa = 0–12 bar)

// ============================================================
// ALERT THRESHOLDS
// ============================================================
// pH
#define ALERT_PH_MIN            6.5f
#define ALERT_PH_MAX            8.5f
#define ALERT_PH_CRITICAL_MIN   6.0f
#define ALERT_PH_CRITICAL_MAX   9.0f

// TDS (ppm)
#define ALERT_TDS_WARNING       500
#define ALERT_TDS_MAX           1000
#define ALERT_TDS_CRITICAL      1500

// Turbidity (NTU)
#define ALERT_TURBIDITY_WARNING 1.0f
#define ALERT_TURBIDITY_MAX     4.0f
#define ALERT_TURBIDITY_CRITICAL 10.0f

// Temperature (°C)
#define ALERT_TEMP_MIN          5.0f
#define ALERT_TEMP_MAX          40.0f
#define ALERT_TEMP_CRITICAL     50.0f

// Flow Rate (L/min)
#define ALERT_FLOW_MIN          0.5f    // Below this = possible blockage
#define ALERT_FLOW_MAX          20.0f   // Above this = possible leak

// Pressure (bar)
#define ALERT_PRESSURE_MAX      8.0f    // Above this = high operating pressure (warning)
#define ALERT_PRESSURE_CRITICAL 10.0f   // Above this = dangerously high pressure

// ============================================================
// WIFI & FIREBASE CONFIG
// ============================================================
#define WIFI_CONNECT_TIMEOUT_MS 15000   // 15 seconds WiFi timeout
#define FIREBASE_SEND_TIMEOUT_MS 5000   // 5 seconds Firebase POST timeout
#define FIREBASE_CHECK_COMMANDS_MS 2000 // Check /commands within 2s of wake

#define FIREBASE_PATH_LIVE_DATA "/devices/" DEVICE_ID "/live_data"
#define FIREBASE_PATH_HISTORY   "/historical_logs/" DEVICE_ID
#define FIREBASE_PATH_STATUS    "/system_status/" DEVICE_ID
#define FIREBASE_PATH_ALERTS    "/alerts/" DEVICE_ID
#define FIREBASE_PATH_COMMANDS  "/devices/" DEVICE_ID "/commands/pending"

// ============================================================
// NTP & TIME
// ============================================================
#define NTP_SERVER              "pool.ntp.org"
#define NTP_OFFSET_SEC          10800   // UTC+3 (Arabia Standard Time)
#define NTP_SYNC_INTERVAL_MS    3600000 // Sync once per hour

// ============================================================
// FILTER CONSTANTS
// ============================================================
#define KALMAN_Q                0.01f   // Process noise variance
#define KALMAN_R                0.1f    // Measurement noise variance
#define FLOW_AVG_WINDOW         5       // Moving average window size for flow rate

// ============================================================
// SERIAL DEBUG
// ============================================================
#define SERIAL_BAUD_RATE        115200
#define DEBUG_ENABLED           true

#if DEBUG_ENABLED
  #define DEBUG_PRINT(x)    Serial.print(x)
  #define DEBUG_PRINTLN(x)  Serial.println(x)
  #define DEBUG_PRINTF(...) Serial.printf(__VA_ARGS__)
#else
  #define DEBUG_PRINT(x)
  #define DEBUG_PRINTLN(x)
  #define DEBUG_PRINTF(...)
#endif

// ============================================================
// SYSTEM STATUS CODES
// ============================================================
#define STATUS_OK               0
#define STATUS_SENSOR_ERROR     1
#define STATUS_WIFI_ERROR       2
#define STATUS_FIREBASE_ERROR   3
#define STATUS_SLEEP_PENDING    4

#endif // CONFIG_H
