#include "state_machine.h"
#include "config.h"
#include "sensors.h"
#include "alert_engine.h"
#include "espnow_broadcast.h"
#include <esp_sleep.h>

// RTC Memory variables to survive deep sleep
RTC_DATA_ATTR int boot_count = 0;
RTC_DATA_ATTR bool system_running = false; // Start/Stop flag
RTC_DATA_ATTR uint32_t uptime_seconds = 0;

extern volatile uint32_t flowFeedPulseCount; // From main sketch
extern volatile uint32_t flowPermeatePulseCount; // From main sketch

SensorReading currentReading;
SystemStatus currentStatus;
String timestamp;

StateMachine::StateMachine() {
    currentState = STATE_BOOT;
    stateStartTime = 0;
}

void StateMachine::begin() {
    transitionTo(STATE_BOOT);
}

void StateMachine::transitionTo(SystemState newState) {
    currentState = newState;
    stateStartTime = millis();
}

void StateMachine::tick() {
    switch (currentState) {
        case STATE_BOOT: handleBoot(); break;
        case STATE_INIT: handleInit(); break;
        case STATE_SENSE: handleSense(); break;
        case STATE_TRANSMIT: handleTransmit(); break;
        case STATE_CHECK_COMMANDS: handleCheckCommands(); break;
        case STATE_EVALUATE: handleEvaluate(); break;
        case STATE_SLEEP: handleSleep(); break;
    }
}

void StateMachine::handleBoot() {
    boot_count++;
    DEBUG_PRINTF("Boot count: %d\n", boot_count);
    
    esp_sleep_wakeup_cause_t wakeup_reason = esp_sleep_get_wakeup_cause();
    switch(wakeup_reason) {
        case ESP_SLEEP_WAKEUP_EXT0:     DEBUG_PRINTLN("Wakeup caused by external signal using RTC_IO (Level Sensor)"); break;
        case ESP_SLEEP_WAKEUP_TIMER:    DEBUG_PRINTLN("Wakeup caused by timer"); break;
        default:                        DEBUG_PRINTF("Wakeup was not caused by deep sleep: %d\n", wakeup_reason); break;
    }
    
    transitionTo(STATE_INIT);
}

void StateMachine::handleInit() {
    DEBUG_PRINTLN("Initializing...");
    sensorsInit();
    alertEngineInit();
    
    // Turn on WiFi radio in STA mode (required for ESP-NOW) but do not connect to AP
    WiFi.mode(WIFI_STA);

    // Initialize ESP-NOW broadcast to Main Hub
    espnowBroadcastInit();
    
    transitionTo(STATE_SENSE);
}

extern volatile uint32_t flowFeedPulseCount;
extern volatile uint32_t flowPermeatePulseCount;

void StateMachine::handleSense() {
    DEBUG_PRINTLN("Reading sensors...");
    uint32_t currentFeedPulses = flowFeedPulseCount;
    uint32_t currentPermeatePulses = flowPermeatePulseCount;
    flowFeedPulseCount = 0; // reset
    flowPermeatePulseCount = 0; // reset
    
    unsigned long interval = millis() - stateStartTime;
    if(interval < 1000) interval = 1000; // avoid div by 0 or artificially high initial
    
    readAllSensors(currentReading, currentFeedPulses, currentPermeatePulses, interval);
    
    // Update uptime
    currentReading.uptime_seconds = uptime_seconds;
    
    transitionTo(STATE_TRANSMIT);
}

void StateMachine::handleTransmit() {
    DEBUG_PRINTLN("Transmitting data...");

    // Always broadcast to Main Hub via ESP-NOW
    espnowBroadcastReading(currentReading);
    
    transitionTo(STATE_CHECK_COMMANDS);
}

void StateMachine::handleCheckCommands() {
    DEBUG_PRINTLN("Checking commands... (Currently handled by Main Hub)");
    // Note: Remote commands (START/STOP) should now be received by Main Hub via BLE,
    // and then sent to Node 1 via ESP-NOW. Node 1 currently only broadcasts.
    // For now, rely on evaluate() logic to sleep/run.
    
    transitionTo(STATE_EVALUATE);
}

void StateMachine::handleEvaluate() {
    DEBUG_PRINTLN("Evaluating next state...");
    
    // Evaluate if we should go to sleep
    bool tankEmpty = (currentReading.level_feed == LEVEL_EMPTY);
    
    if (!system_running || tankEmpty) {
        if(tankEmpty) {
            DEBUG_PRINTLN("Feed tank empty. Preparing to sleep.");
        } else {
            DEBUG_PRINTLN("System stopped. Preparing to sleep.");
        }
        digitalWrite(PIN_RELAY_PUMP, RELAY_OFF);
        digitalWrite(PIN_RELAY_VALVE, RELAY_OFF);
        transitionTo(STATE_SLEEP);
    } else {
        // Continue running, delay to meet sampling interval, then SENSE
        unsigned long elapsed = millis() - stateStartTime;
        if (elapsed < SAMPLING_INTERVAL_MS) {
            delay(SAMPLING_INTERVAL_MS - elapsed);
        }
        uptime_seconds += (SAMPLING_INTERVAL_MS / 1000);
        transitionTo(STATE_SENSE);
    }
}

void StateMachine::handleSleep() {
    DEBUG_PRINTLN("Entering deep sleep...");
    
    // Wake up on timer
    esp_sleep_enable_timer_wakeup(TIMER_WAKE_INTERVAL_SEC * uS_TO_S_FACTOR);
    
    // Wake up on EXT0 (Water level sensor)
    // Assuming XKC-Y25 gives LOW when water is present (since INPUT_PULLUP)
    esp_sleep_enable_ext0_wakeup((gpio_num_t)PIN_WATER_LEVEL_FEED, 0); 
    
    esp_deep_sleep_start();
}
