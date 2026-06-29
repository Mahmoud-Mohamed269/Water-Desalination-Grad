#ifndef STATE_MACHINE_H
#define STATE_MACHINE_H

#include <Arduino.h>
#include "sensors.h"

enum SystemState {
    STATE_BOOT,
    STATE_INIT,
    STATE_SENSE,
    STATE_TRANSMIT,
    STATE_CHECK_COMMANDS,
    STATE_EVALUATE,
    STATE_SLEEP
};

struct SystemStatus {
    bool online;
    int wifi_rssi;
    uint32_t heap_free_bytes;
    float cpu_temp_celsius;
    String last_update;
    SensorHealth sensor_health;
};

class StateMachine {
private:
    SystemState currentState;
    unsigned long stateStartTime;
    void transitionTo(SystemState newState);

    void handleBoot();
    void handleInit();
    void handleSense();
    void handleTransmit();
    void handleCheckCommands();
    void handleEvaluate();
    void handleSleep();

public:
    StateMachine();
    void begin();
    void tick();
};

#endif // STATE_MACHINE_H
