#ifndef FIREBASE_CLIENT_HUB_H
#define FIREBASE_CLIENT_HUB_H

#include <Arduino.h>

// Initializes Firebase connection and authenticates
void firebaseInit();

// Pushes the fully merged JSON payload to the live data node
void pushLiveData(const String& jsonPayload);

// Pushes the fully merged JSON payload to the historical logs
void pushHistoricalLog(const String& jsonPayload);

// Optional: Push system status (health, uptime)
void pushSystemStatus(const String& jsonPayload);

// Ensure the system time is set via NTP (required for SSL/Firebase)
void ntpInit();
String getISOTimestamp();

#endif // FIREBASE_CLIENT_HUB_H
