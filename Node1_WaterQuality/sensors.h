#ifndef SENSORS_H
#define SENSORS_H

#include <Arduino.h>
#include "config.h"
#include "filters.h"

// Define an enum for water level sensor states
enum WaterLevelState {
    LEVEL_EMPTY = 1, // Usually HIGH when empty for INPUT_PULLUP with active-LOW
    LEVEL_WATER = 0  // Usually LOW when water detected
};

struct SensorHealth {
    String ph;
    String tds;
    String turbidity;
    String temperature;
    String pressure;
    String flow;
    String level;
};

struct SensorReading {
    float ph_feed;
    float ph_permeate;
    float tds_feed;
    float tds_permeate;
    float turbidity_feed;
    float temperature_feed;
    float temperature_permeate;
    float pressure_feed;        // Bar — G1/4 analog pressure sensor on feed line
    float flow_rate_feed;
    float flow_rate_permeate;
    WaterLevelState level_feed;
    WaterLevelState level_product;
    
    // Computed
    float recovery_rate; 
    float rejection_rate; 

    String pump_status;
    String valve_status;
    uint32_t uptime_seconds;
    
    SensorHealth health;
};

void sensorsInit();
void readAllSensors(SensorReading& reading, uint32_t flowFeedPulseCount, uint32_t flowPermeatePulseCount, uint32_t intervalMs);
void checkSensorHealth(SensorReading& r);

float readADC_Voltage(uint8_t pin, uint8_t samples = ADC_SAMPLES);
float readPH(uint8_t pin, KalmanFilter& filter, float temperature);
float readTDS(uint8_t pin, KalmanFilter& filter, float temperature);
float readTurbidity(uint8_t pin);
float readPressure(uint8_t pin);
float readTemperature(uint8_t index);
float readFlowRate(MovingAverage& avgFilter, uint32_t pulseCount, uint32_t intervalMs);
WaterLevelState readWaterLevel(uint8_t pin);

#endif // SENSORS_H
