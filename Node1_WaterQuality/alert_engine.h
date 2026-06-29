#ifndef ALERT_ENGINE_H
#define ALERT_ENGINE_H

#include <Arduino.h>
#include "sensors.h"

struct Alert {
    String type;
    String severity;
    String parameter;
    float value;
    float threshold;
    String message;
    String timestamp;
};

void alertEngineInit();
void checkAlerts(const SensorReading& r, const String& timestamp);

#endif // ALERT_ENGINE_H
