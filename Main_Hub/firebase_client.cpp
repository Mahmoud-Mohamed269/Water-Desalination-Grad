#include "firebase_client.h"
#include "config.h"
#include <WiFi.h>
#include <Firebase_ESP_Client.h>
#include <addons/TokenHelper.h>
#include <addons/RTDBHelper.h>

FirebaseData fbdo;
FirebaseAuth auth;
FirebaseConfig config;
bool firebase_ready = false;

// ─────────────────────────────────────────────
//  NTP Time Initialization
// ─────────────────────────────────────────────
void ntpInit() {
    Serial.print("[NTP] Syncing time... ");
    configTime(0, 0, "pool.ntp.org", "time.nist.gov");
    
    time_t now = time(nullptr);
    int retries = 0;
    while (now < 8 * 3600 * 2 && retries < 15) {
        delay(500);
        Serial.print(".");
        now = time(nullptr);
        retries++;
    }
    Serial.println(now < 8 * 3600 * 2 ? " FAILED" : " OK");
}

String getISOTimestamp() {
    time_t now;
    time(&now);
    struct tm timeinfo;
    gmtime_r(&now, &timeinfo);
    
    char buf[30];
    strftime(buf, sizeof(buf), "%Y-%m-%dT%H:%M:%SZ", &timeinfo);
    return String(buf);
}

// ─────────────────────────────────────────────
//  Firebase Initialization
// ─────────────────────────────────────────────
void firebaseInit() {
    Serial.println("[Firebase] Initializing...");
    
    // Set up Firebase config
    config.api_key = FIREBASE_API_KEY;
    config.database_url = FIREBASE_DATABASE_URL;

    // Sign up anonymously
    if (Firebase.signUp(&config, &auth, "", "")) {
        Serial.println("[Firebase] Anonymous auth OK.");
    } else {
        Serial.printf("[Firebase] Auth Error: %s\n", config.signer.signupError.message.c_str());
    }

    // Recommended token generation callback
    config.token_status_callback = tokenStatusCallback;
    
    // Initialize
    Firebase.begin(&config, &auth);
    Firebase.reconnectWiFi(true);

    fbdo.setBSSLBufferSize(1024, 1024);
    fbdo.setResponseSize(1024);
    
    firebase_ready = true;
    Serial.println("[Firebase] Init complete.");
}

// ─────────────────────────────────────────────
//  Push Functions
// ─────────────────────────────────────────────
void pushLiveData(const String& jsonPayload) {
    if (!firebase_ready || WiFi.status() != WL_CONNECTED) return;
    
    String path = String("/devices/") + DEVICE_ID + "/live_data";
    
    // Firebase_ESP_Client accepts raw JSON string via setJSON
    FirebaseJson fbJson;
    fbJson.setJsonData(jsonPayload);
    
    if (Firebase.RTDB.setJSON(&fbdo, path.c_str(), &fbJson)) {
        Serial.println("[Firebase] Live data pushed OK.");
    } else {
        Serial.printf("[Firebase] Live data failed: %s\n", fbdo.errorReason().c_str());
    }
}

void pushHistoricalLog(const String& jsonPayload) {
    if (!firebase_ready || WiFi.status() != WL_CONNECTED) return;
    
    String path = String("/historical_logs/") + DEVICE_ID;
    
    FirebaseJson fbJson;
    fbJson.setJsonData(jsonPayload);
    
    if (Firebase.RTDB.pushJSON(&fbdo, path.c_str(), &fbJson)) {
        Serial.println("[Firebase] Historical log pushed OK.");
    } else {
        Serial.printf("[Firebase] Historical log failed: %s\n", fbdo.errorReason().c_str());
    }
}

void pushSystemStatus(const String& jsonPayload) {
    if (!firebase_ready || WiFi.status() != WL_CONNECTED) return;
    
    String path = String("/system_status/") + DEVICE_ID;
    
    FirebaseJson fbJson;
    fbJson.setJsonData(jsonPayload);
    
    if (Firebase.RTDB.setJSON(&fbdo, path.c_str(), &fbJson)) {
        Serial.println("[Firebase] System status pushed OK.");
    } else {
        Serial.printf("[Firebase] System status failed: %s\n", fbdo.errorReason().c_str());
    }
}
