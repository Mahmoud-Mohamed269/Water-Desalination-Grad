/*
 * ============================================================
 *  Smart Water Desalination Monitoring System
 *  Firmware: Main Hub — Communication & BLE Server
 *  Version:  2.0.0
 *  Role:
 *    - Receives full sensor data from Node 1 via ESP-NOW
 *    - Receives environment data from Node 2 via ESP-NOW
 *    - Merges all data into one JSON payload
 *    - Streams merged JSON to mobile app over BLE (notify)
 *    - Receives BLE commands from app (write):
 *        {"cmd":"set_wifi","ssid":"...","pass":"..."} → reconnect WiFi
 *        {"cmd":"pump_on"} / {"cmd":"pump_off"}       → future relay
 *    - When WiFi is connected, pushes merged data to FastAPI backend
 *  Phase: 3 — ESP32 Firmware Development
 * ============================================================
 */

#include <WiFi.h>
#include <esp_now.h>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
#include <ArduinoJson.h>
#include <Preferences.h>
#include "config.h"
#include "firebase_client.h"
typedef struct __attribute__((packed)) espnow_node1_t {
    float ph_feed;
    float ph_permeate;
    float tds_feed;
    float tds_permeate;
    float turbidity_feed;
    float temperature_feed;
    float temperature_permeate;
    float pressure_feed;
    float flow_rate_feed;
    float flow_rate_permeate;
    float recovery_rate;
    float rejection_rate;
    bool  level_feed_full;
    bool  level_product_full;
    bool  pump_running;
    bool  valve_open;
    uint32_t uptime_seconds;
} espnow_node1_t;

// ============================================================
//  Node 2 — Environment struct (must match Node2 firmware)
// ============================================================
typedef struct __attribute__((packed)) espnow_node2_t {
    float tank1_level_cm;
    float tank2_level_cm;
    float ambient_temp;
    float ambient_humidity;
    float gas_1_ppm;
    float gas_2_ppm;
    float water_temp_1;
    float water_temp_2;
    bool  fan_1_status;
    bool  fan_2_status;
    bool  fan_3_status;
} espnow_node2_t;

// ============================================================
//  Global State
// ============================================================
espnow_node1_t dataNode1 = {};
espnow_node2_t dataNode2 = {};
bool node1Updated = false;
bool node2Updated = false;
unsigned long lastBleNotify    = 0;
unsigned long lastFirebasePush = 0;
const unsigned long BLE_INTERVAL_MS      = 3000;
const unsigned long FIREBASE_INTERVAL_MS = 5000;
unsigned int push_counter = 0;

// ============================================================
//  BLE
// ============================================================
BLEServer*         pServer         = nullptr;
BLECharacteristic* pNotifyChar     = nullptr;  // App reads sensor data
BLECharacteristic* pWriteChar      = nullptr;  // App sends commands
bool deviceConnected = false;

Preferences prefs;

// ============================================================
//  BLE Server Callbacks
// ============================================================
class HubServerCallbacks : public BLEServerCallbacks {
    void onConnect(BLEServer*) override {
        deviceConnected = true;
        Serial.println("[BLE] Mobile app connected.");
    }
    void onDisconnect(BLEServer* s) override {
        deviceConnected = false;
        Serial.println("[BLE] Mobile app disconnected. Re-advertising...");
        BLEDevice::startAdvertising();
    }
};

// ============================================================
//  BLE Write Characteristic Callbacks (commands from app)
// ============================================================
class CommandCallbacks : public BLECharacteristicCallbacks {
    void onWrite(BLECharacteristic* pChar) override {
        String raw = pChar->getValue();
        if (raw.isEmpty()) return;
        Serial.printf("[BLE CMD] Received: %s\n", raw.c_str());

        StaticJsonDocument<256> doc;
        if (deserializeJson(doc, raw.c_str()) != DeserializationError::Ok) {
            Serial.println("[BLE CMD] Invalid JSON");
            return;
        }

        const char* cmd = doc["cmd"] | "";

        if (strcmp(cmd, "set_wifi") == 0) {
            const char* ssid = doc["ssid"] | "";
            const char* pass = doc["pass"] | "";
            Serial.printf("[BLE CMD] Setting WiFi: SSID=%s\n", ssid);
            prefs.begin("hub_cfg", false);
            prefs.putString("wifi_ssid", ssid);
            prefs.putString("wifi_pass", pass);
            prefs.end();
            // Reconnect
            WiFi.disconnect(true);
            delay(500);
            WiFi.begin(ssid, pass);
            Serial.println("[WiFi] Reconnecting with new credentials...");

        } else if (strcmp(cmd, "pump_on") == 0) {
            Serial.println("[BLE CMD] pump_on → (future: relay control)");
            // TODO: if Hub has a relay, control it here

        } else if (strcmp(cmd, "pump_off") == 0) {
            Serial.println("[BLE CMD] pump_off → (future: relay control)");

        } else {
            Serial.printf("[BLE CMD] Unknown command: %s\n", cmd);
        }
    }
};

// ============================================================
//  ESP-NOW Receive Callback
// ============================================================
void OnDataRecv(const esp_now_recv_info* info, const uint8_t* data, int len) {
    if (len == sizeof(espnow_node1_t)) {
        memcpy(&dataNode1, data, sizeof(dataNode1));
        node1Updated = true;
        Serial.println("[ESP-NOW] Node 1 data received.");
    } else if (len == sizeof(espnow_node2_t)) {
        memcpy(&dataNode2, data, sizeof(dataNode2));
        node2Updated = true;
        Serial.println("[ESP-NOW] Node 2 data received.");
    } else {
        Serial.printf("[ESP-NOW] Unknown packet len=%d\n", len);
    }
}

// ============================================================
//  Build merged JSON payload from Node1 + Node2
// ============================================================
String buildMergedJson() {
    StaticJsonDocument<1024> doc;
    // Node 1 fields
    doc["ph_feed"]                = dataNode1.ph_feed;
    doc["ph_permeate"]            = dataNode1.ph_permeate;
    doc["tds_feed"]               = dataNode1.tds_feed;
    doc["tds_permeate"]           = dataNode1.tds_permeate;
    doc["turbidity_feed"]         = dataNode1.turbidity_feed;
    doc["temperature_feed"]       = dataNode1.temperature_feed;
    doc["temperature_permeate"]   = dataNode1.temperature_permeate;
    doc["pressure_feed"]          = dataNode1.pressure_feed;
    doc["flow_rate_feed"]         = dataNode1.flow_rate_feed;
    doc["flow_rate_permeate"]     = dataNode1.flow_rate_permeate;
    doc["recovery_rate"]          = dataNode1.recovery_rate;
    doc["rejection_rate"]         = dataNode1.rejection_rate;
    doc["level_feed_full"]        = dataNode1.level_feed_full;
    doc["level_product_full"]     = dataNode1.level_product_full;
    doc["pump_status"]            = dataNode1.pump_running;
    doc["valve_status"]           = dataNode1.valve_open;
    doc["uptime_seconds"]         = dataNode1.uptime_seconds;
    // Node 2 fields
    doc["tank1_level_cm"]         = dataNode2.tank1_level_cm;
    doc["tank2_level_cm"]         = dataNode2.tank2_level_cm;
    doc["ambient_temp"]           = dataNode2.ambient_temp;
    doc["ambient_humidity"]       = dataNode2.ambient_humidity;
    doc["gas_1_ppm"]              = dataNode2.gas_1_ppm;
    doc["gas_2_ppm"]              = dataNode2.gas_2_ppm;
    doc["water_temp_1"]           = dataNode2.water_temp_1;
    doc["water_temp_2"]           = dataNode2.water_temp_2;
    doc["fan_1_status"]           = dataNode2.fan_1_status;
    doc["fan_2_status"]           = dataNode2.fan_2_status;
    doc["fan_3_status"]           = dataNode2.fan_3_status;

    String out;
    serializeJson(doc, out);
    return out;
}

// ============================================================
//  Build merged JSON payload specifically for Firebase
//  Injects NTP timestamp.
// ============================================================
String buildFirebaseJson() {
    StaticJsonDocument<1024> doc;
    // Node 1 fields
    doc["ph_feed"]                = dataNode1.ph_feed;
    doc["ph_permeate"]            = dataNode1.ph_permeate;
    doc["tds_feed"]               = dataNode1.tds_feed;
    doc["tds_permeate"]           = dataNode1.tds_permeate;
    doc["turbidity_feed"]         = dataNode1.turbidity_feed;
    doc["temperature_feed"]       = dataNode1.temperature_feed;
    doc["temperature_permeate"]   = dataNode1.temperature_permeate;
    doc["pressure_feed"]          = dataNode1.pressure_feed;
    doc["flow_rate_feed"]         = dataNode1.flow_rate_feed;
    doc["flow_rate_permeate"]     = dataNode1.flow_rate_permeate;
    doc["recovery_rate"]          = dataNode1.recovery_rate;
    doc["rejection_rate"]         = dataNode1.rejection_rate;
    doc["level_feed_full"]        = dataNode1.level_feed_full;
    doc["level_product_full"]     = dataNode1.level_product_full;
    doc["pump_status"]            = dataNode1.pump_running ? "running" : "stopped";
    doc["valve_status"]           = dataNode1.valve_open ? "open" : "closed";
    doc["uptime_seconds"]         = dataNode1.uptime_seconds;
    doc["timestamp"]              = getISOTimestamp();
    
    // Node 2 fields
    doc["tank1_level_cm"]         = dataNode2.tank1_level_cm;
    doc["tank2_level_cm"]         = dataNode2.tank2_level_cm;
    doc["ambient_temp"]           = dataNode2.ambient_temp;
    doc["ambient_humidity"]       = dataNode2.ambient_humidity;
    doc["gas_1_ppm"]              = dataNode2.gas_1_ppm;
    doc["gas_2_ppm"]              = dataNode2.gas_2_ppm;
    doc["water_temp_1"]           = dataNode2.water_temp_1;
    doc["water_temp_2"]           = dataNode2.water_temp_2;
    doc["fan_1_status"]           = dataNode2.fan_1_status;
    doc["fan_2_status"]           = dataNode2.fan_2_status;
    doc["fan_3_status"]           = dataNode2.fan_3_status;

    String out;
    serializeJson(doc, out);
    return out;
}

// ============================================================
//  Firebase Push (Replaced Backend HTTP push)
// ============================================================
// Removed pushToBackend. Logic shifted to loop.

// ============================================================
//  WiFi Setup — tries NVS stored credentials, then config.h defaults
// ============================================================
void wifiSetup() {
    prefs.begin("hub_cfg", true);  // read-only
    String storedSSID = prefs.getString("wifi_ssid", WIFI_SSID);
    String storedPass = prefs.getString("wifi_pass",  WIFI_PASSWORD);
    prefs.end();

    Serial.printf("[WiFi] Connecting to %s ...\n", storedSSID.c_str());
    WiFi.mode(WIFI_STA);
    WiFi.begin(storedSSID.c_str(), storedPass.c_str());

    unsigned long start = millis();
    while (WiFi.status() != WL_CONNECTED && millis() - start < WIFI_CONNECT_TIMEOUT_MS) {
        delay(250);
        Serial.print(".");
    }
    Serial.println();
    if (WiFi.status() == WL_CONNECTED) {
        Serial.printf("[WiFi] Connected! IP: %s\n", WiFi.localIP().toString().c_str());
        Serial.printf("[WiFi] MAC: %s\n", WiFi.macAddress().c_str());
    } else {
        Serial.println("[WiFi] Not connected — running BLE-only mode.");
    }
}

// ============================================================
//  BLE Setup
// ============================================================
void bleSetup() {
    BLEDevice::init(BLE_DEVICE_NAME);
    pServer = BLEDevice::createServer();
    pServer->setCallbacks(new HubServerCallbacks());

    BLEService* pService = pServer->createService(BLE_SERVICE_UUID);

    // Notify characteristic — hub → app (sensor data)
    pNotifyChar = pService->createCharacteristic(
        BLE_NOTIFY_CHAR_UUID,
        BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_NOTIFY
    );
    pNotifyChar->addDescriptor(new BLE2902());

    // Write characteristic — app → hub (commands)
    pWriteChar = pService->createCharacteristic(
        BLE_WRITE_CHAR_UUID,
        BLECharacteristic::PROPERTY_WRITE | BLECharacteristic::PROPERTY_WRITE_NR
    );
    pWriteChar->setCallbacks(new CommandCallbacks());

    pService->start();

    BLEAdvertising* pAdv = BLEDevice::getAdvertising();
    pAdv->addServiceUUID(BLE_SERVICE_UUID);
    pAdv->setScanResponse(true);
    BLEDevice::startAdvertising();

    Serial.printf("[BLE] Advertising as \"%s\"\n", BLE_DEVICE_NAME);
}

// ============================================================
//  Setup
// ============================================================
void setup() {
    Serial.begin(SERIAL_BAUD_RATE);
    delay(500);
    Serial.println("\n=== AquaMonitor Main Hub v2.0 ===");

    // WiFi must be configured before ESP-NOW
    wifiSetup();

    // ESP-NOW (runs on top of WiFi STA mode)
    if (esp_now_init() != ESP_OK) {
        Serial.println("[ESP-NOW] Init FAILED");
    } else {
        esp_now_register_recv_cb(OnDataRecv);
        Serial.println("[ESP-NOW] Ready.");
    }

    if (WiFi.status() == WL_CONNECTED) {
        ntpInit();
        firebaseInit();
    }

    // BLE Server
    bleSetup();

    Serial.println("[Hub] Ready. Waiting for ESP-NOW data from nodes...");
}

// ============================================================
//  Loop
// ============================================================
void loop() {
    unsigned long now = millis();

    // Send BLE notification every BLE_INTERVAL_MS
    if (deviceConnected && (now - lastBleNotify >= BLE_INTERVAL_MS)) {
        lastBleNotify = now;
        String payload = buildMergedJson();
        pNotifyChar->setValue(payload.c_str());
        pNotifyChar->notify();
        Serial.println("[BLE] Notified app.");
    }

    // Push to Firebase every FIREBASE_INTERVAL_MS (when WiFi available)
    if (WiFi.status() == WL_CONNECTED && (now - lastFirebasePush >= FIREBASE_INTERVAL_MS)) {
        lastFirebasePush = now;
        if (node1Updated || node2Updated) {  // Only push if we have new data
            String fbPayload = buildFirebaseJson();
            pushLiveData(fbPayload);
            
            // Push historical log every ~10 cycles (e.g., 50 seconds)
            push_counter++;
            if (push_counter % 10 == 0) {
                pushHistoricalLog(fbPayload);
                
                // Construct a mock system status
                StaticJsonDocument<256> sysDoc;
                sysDoc["online"] = true;
                sysDoc["wifi_rssi"] = WiFi.RSSI();
                sysDoc["heap_free_bytes"] = ESP.getFreeHeap();
                sysDoc["last_update"] = getISOTimestamp();
                String sysPayload;
                serializeJson(sysDoc, sysPayload);
                pushSystemStatus(sysPayload);
            }
            
            node1Updated = false;
            node2Updated = false;
        }
    }

    delay(50);
}
