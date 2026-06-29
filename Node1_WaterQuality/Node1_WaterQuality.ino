/*
 * ============================================================
 *  Smart Water Desalination Monitoring System
 *  Firmware: Node 1 — Water Quality
 *  Version:  1.2.0
 *  Role:     Reads pH (feed+permeate), TDS (feed+permeate),
 *            Turbidity (feed), Temperature (feed+permeate),
 *            Pressure (feed), Flow (feed+permeate), Level (feed+product).
 *            Controls RO Pump & Solenoid Valve relays.
 *            Transmits data to Firebase via WiFi every 5 seconds.
 *            Broadcasts full sensor struct to Main Hub via ESP-NOW.
 *  Phase:    3 — ESP32 Firmware Development
 * ============================================================
 */

#include "config.h"
#include "state_machine.h"
#include "espnow_broadcast.h"
#include <Arduino.h>

StateMachine stateMachine;

volatile uint32_t flowFeedPulseCount = 0;
volatile uint32_t flowPermeatePulseCount = 0;

void IRAM_ATTR flowFeedPulseISR() {
    flowFeedPulseCount++;
}

void IRAM_ATTR flowPermeatePulseISR() {
    flowPermeatePulseCount++;
}

void setup() {
    Serial.begin(SERIAL_BAUD_RATE);
    delay(1000);

    DEBUG_PRINTLN("\n=============================================");
    DEBUG_PRINTF("🚀 %s starting...\n", DEVICE_NAME);
    DEBUG_PRINTF("Firmware Version: %s\n", FIRMWARE_VERSION);
    DEBUG_PRINTLN("=============================================");

    // Initialize GPIO for basic needs before state machine handles complex init
    pinMode(PIN_STATUS_LED, OUTPUT);
    pinMode(PIN_RELAY_PUMP, OUTPUT);
    pinMode(PIN_RELAY_VALVE, OUTPUT);
    pinMode(PIN_WATER_LEVEL_FEED, INPUT_PULLUP);
    pinMode(PIN_WATER_LEVEL_PRODUCT, INPUT_PULLUP);
    pinMode(PIN_FLOW_SENSOR, INPUT_PULLUP);
    pinMode(PIN_FLOW_PERMEATE, INPUT_PULLUP);

    // Initial safe state
    digitalWrite(PIN_RELAY_PUMP, RELAY_OFF);
    digitalWrite(PIN_RELAY_VALVE, RELAY_OFF);

    // ADC setup
    analogReadResolution(12);
    analogSetAttenuation(ADC_11db);

    // Interrupts
    attachInterrupt(digitalPinToInterrupt(PIN_FLOW_SENSOR), flowFeedPulseISR, FALLING);
    attachInterrupt(digitalPinToInterrupt(PIN_FLOW_PERMEATE), flowPermeatePulseISR, FALLING);

    stateMachine.begin();
}

void loop() {
    stateMachine.tick();
}