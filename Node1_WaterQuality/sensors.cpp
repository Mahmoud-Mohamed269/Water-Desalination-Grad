#include "sensors.h"
#include "filters.h"
#include <OneWire.h>
#include <DallasTemperature.h>

// ============================================================
// Kalman Filters (pH & TDS — high-noise analog sensors)
// ============================================================
KalmanFilter phFeedKalman(KALMAN_Q, KALMAN_R, 1.0f, 7.0f);
KalmanFilter phPermeateKalman(KALMAN_Q, KALMAN_R, 1.0f, 7.0f);
KalmanFilter tdsFeedKalman(KALMAN_Q, KALMAN_R, 1.0f, 0.0f);
KalmanFilter tdsPermeateKalman(KALMAN_Q, KALMAN_R, 1.0f, 0.0f);

// ============================================================
// Moving Average Filters (Flow Rate)
// ============================================================
MovingAverage flowFeedAvg(FLOW_AVG_WINDOW);
MovingAverage flowPermeateAvg(FLOW_AVG_WINDOW);

// ============================================================
// OneWire & DallasTemperature (DS18B20)
// Two sensors on the same bus: index 0 = feed, index 1 = permeate
// ============================================================
OneWire oneWire(PIN_DS18B20);
DallasTemperature ds18b20(&oneWire);

// ============================================================
// Sensor Initialisation
// ============================================================
void sensorsInit() {
    ds18b20.begin();
    ds18b20.setResolution(DS18B20_RESOLUTION);
    flowFeedAvg.reset();
    flowPermeateAvg.reset();
}

// ============================================================
// ADC Helper — Oversampled average (reduces quantisation noise)
// ============================================================
float readADC_Voltage(uint8_t pin, uint8_t samples) {
    uint32_t sum = 0;
    for (uint8_t i = 0; i < samples; i++) {
        sum += analogRead(pin);
        delay(ADC_SAMPLE_DELAY_MS);
    }
    return ((float)sum / samples / ADC_RESOLUTION) * ADC_VREF;
}

// ============================================================
// pH Sensor — Analog kit (0–14 pH, 0–5V output)
// ============================================================
float readPH(uint8_t pin, KalmanFilter& filter, float temperature) {
    float voltage = readADC_Voltage(pin);
    voltage *= VDIV_RATIO_PH;
    // pH calibration line: pH = 7 + (V - V@pH7) / slope
    float ph = 7.0f + ((voltage - PH_VOLTAGE_AT_PH7) / PH_SLOPE);
    // Nernst equation temperature compensation
    ph = ph + (25.0f - temperature) * PH_TEMP_COEFFICIENT;
    // Clamp to physically meaningful range
    ph = constrain(ph, 0.0f, 14.0f);
    return filter.update(ph);
}

// ============================================================
// TDS Sensor V1.0 — Analog (0–1000 ppm, max 2.3V output)
// ============================================================
float readTDS(uint8_t pin, KalmanFilter& filter, float temperature) {
    float voltage = readADC_Voltage(pin);
    voltage *= VDIV_RATIO_TDS;
    
    // Temperature compensation
    float compensationCoefficient = 1.0f + TDS_TEMP_COEFFICIENT * (temperature - TDS_REFERENCE_TEMP);
    float compensationVoltage = voltage / compensationCoefficient;
    
    // Polynomial voltage-to-TDS conversion (manufacturer curve fit)
    float tdsValue = (133.42f * compensationVoltage * compensationVoltage * compensationVoltage 
                      - 255.86f * compensationVoltage * compensationVoltage 
                      + 857.39f * compensationVoltage) * 0.5f;
                      
    if (tdsValue < 0) tdsValue = 0;
    return filter.update(tdsValue);
}

// ============================================================
// Turbidity Sensor — Analog (0–3000 NTU, 0–4.5V output @ 5V)
// Requires 10kΩ/20kΩ voltage divider (VDIV_RATIO_TURBIDITY = 1.5)
// ============================================================
float readTurbidity(uint8_t pin) {
    float voltage = readADC_Voltage(pin);
    voltage *= VDIV_RATIO_TURBIDITY; // Recover actual sensor voltage

    // Inverse relationship: higher voltage = clearer water
    float ntu = (TURBIDITY_VOLTAGE_CLEAR - voltage) * TURBIDITY_SLOPE;
    if (ntu < 0) ntu = 0;
    return ntu;
}

// ============================================================
// Pressure Sensor G1/4 — Analog (0–1.2 MPa / 0–12 bar, 0.5–4.5V @ 5V)
// Requires 10kΩ/20kΩ voltage divider (VDIV_RATIO_PRESSURE = 1.5)
// ============================================================
float readPressure(uint8_t pin) {
    float voltage = readADC_Voltage(pin);
    voltage *= VDIV_RATIO_PRESSURE; // Recover actual sensor voltage

    // Linear conversion: P(bar) = (Vin - 0.5V) / (4.5V - 0.5V) × MAX_BAR
    float pressureBar = (voltage - PRESSURE_OFFSET_V) / (PRESSURE_SCALE_V - PRESSURE_OFFSET_V) * PRESSURE_MAX_BAR;
    if (pressureBar < 0) pressureBar = 0;
    return pressureBar;
}

// ============================================================
// DS18B20 Temperature — OneWire (−55 to +125°C)
// Call ds18b20.requestTemperatures() before reading!
// ============================================================
float readTemperature(uint8_t index) {
    float tempC = ds18b20.getTempCByIndex(index);
    if (tempC == DEVICE_DISCONNECTED_C) {
        DEBUG_PRINTF("DS18B20[%d] disconnected, using fallback 25°C\n", index);
        return 25.0f;
    }
    return tempC;
}

// ============================================================
// Flow Rate — YF-S201 (1–30 L/min, interrupt-counted pulses)
// intervalMs: time window over which pulses were counted
// ============================================================
float readFlowRate(MovingAverage& avgFilter, uint32_t pulseCount, uint32_t intervalMs) {
    float pulsesPerSec = ((float)pulseCount * 1000.0f) / (float)intervalMs;
    float lPerMin = pulsesPerSec / FLOW_CALIBRATION_FACTOR;
    return avgFilter.update(lPerMin);
}

// ============================================================
// Water Level — XKC-Y25 Non-Contact (Digital HIGH/LOW)
// INPUT_PULLUP: LOW = water present, HIGH = empty
// ============================================================
WaterLevelState readWaterLevel(uint8_t pin) {
    return (digitalRead(pin) == LOW) ? LEVEL_WATER : LEVEL_EMPTY;
}

// ============================================================
// readAllSensors — Master function: populates a SensorReading
// Call this once per sampling cycle
// ============================================================
void readAllSensors(SensorReading& reading, uint32_t feedPulseCount, uint32_t permeatePulseCount, uint32_t intervalMs) {
    // --- Temperature (must be first: used for pH/TDS compensation) ---
    ds18b20.requestTemperatures();
    delay(DS18B20_CONVERSION_MS);
    reading.temperature_feed    = readTemperature(0);
    reading.temperature_permeate = readTemperature(1);

    // --- pH ---
    reading.ph_feed     = readPH(PIN_PH_FEED,     phFeedKalman,     reading.temperature_feed);
    reading.ph_permeate = readPH(PIN_PH_PERMEATE,  phPermeateKalman, reading.temperature_permeate);

    // --- TDS ---
    reading.tds_feed     = readTDS(PIN_TDS_FEED,    tdsFeedKalman,    reading.temperature_feed);
    reading.tds_permeate = readTDS(PIN_TDS_PERMEATE, tdsPermeateKalman, reading.temperature_permeate);

    // --- Turbidity (feed line only) ---
    reading.turbidity_feed = readTurbidity(PIN_TURBIDITY_FEED);

    // --- Pressure (feed line) ---
    reading.pressure_feed = readPressure(PIN_PRESSURE_FEED);

    // --- Flow Rate ---
    reading.flow_rate_feed     = readFlowRate(flowFeedAvg,     feedPulseCount,    intervalMs);
    reading.flow_rate_permeate = readFlowRate(flowPermeateAvg, permeatePulseCount, intervalMs);

    // --- Water Level ---
    reading.level_feed    = readWaterLevel(PIN_WATER_LEVEL_FEED);
    reading.level_product = readWaterLevel(PIN_WATER_LEVEL_PRODUCT);

    // --- Computed KPIs ---
    if (reading.flow_rate_feed > 0.0f) {
        reading.recovery_rate = (reading.flow_rate_permeate / reading.flow_rate_feed) * 100.0f;
    } else {
        reading.recovery_rate = 0.0f;
    }
    
    if (reading.tds_feed > 0.0f) {
        reading.rejection_rate = (1.0f - (reading.tds_permeate / reading.tds_feed)) * 100.0f;
    } else {
        reading.rejection_rate = 0.0f;
    }

    // --- Actuator Status ---
    reading.pump_status  = (digitalRead(PIN_RELAY_PUMP)  == RELAY_ON) ? "running" : "stopped";
    reading.valve_status = (digitalRead(PIN_RELAY_VALVE) == RELAY_ON) ? "open"    : "closed";

    // --- Sensor Health ---
    checkSensorHealth(reading);
}

// ============================================================
// checkSensorHealth — Validates readings against physical bounds
// ============================================================
void checkSensorHealth(SensorReading& r) {
    r.health.ph          = (r.ph_feed < 0 || r.ph_feed > 14.0f ||
                             r.ph_permeate < 0 || r.ph_permeate > 14.0f) ? "error" : "ok";
    r.health.tds         = (r.tds_feed < 0 || r.tds_feed > 10000.0f ||
                             r.tds_permeate < 0 || r.tds_permeate > 10000.0f) ? "error" : "ok";
    r.health.turbidity   = (r.turbidity_feed < 0) ? "error" : "ok";
    r.health.temperature = (r.temperature_feed < -10.0f || r.temperature_feed > 80.0f ||
                             r.temperature_permeate < -10.0f || r.temperature_permeate > 80.0f) ? "error" : "ok";
    r.health.pressure    = (r.pressure_feed < 0 || r.pressure_feed > PRESSURE_MAX_BAR) ? "error" : "ok";
    r.health.flow        = (r.flow_rate_feed < 0 || r.flow_rate_permeate < 0) ? "error" : "ok";
    r.health.level       = "ok"; // XKC-Y25 is digital — no range check needed
}
