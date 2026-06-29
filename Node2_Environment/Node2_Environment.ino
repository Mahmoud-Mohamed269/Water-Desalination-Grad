/*
 * ============================================================
 *  Smart Water Desalination Monitoring System
 *  Firmware: Node 2 — Environment
 *  Role:     Reads ultrasonic tank levels, DHT22, gas sensors,
 *            DS18B20 water temperatures. Controls 3x cooling
 *            fan relays. Transmits data to Main Hub via ESP-NOW.
 *  Phase:    3 — ESP32 Firmware Development
 * ============================================================
 */

#include <WiFi.h>
#include <esp_now.h>
#include "config.h"

// ─────────────────────────────────────────────
//  Data Structure sent to Hub via ESP-NOW
// ─────────────────────────────────────────────
typedef struct struct_node2 {
    float tank1_level_cm;       // Ultrasonic — Feed tank fill level
    float tank2_level_cm;       // Ultrasonic — Product tank fill level
    float ambient_temp;         // DHT22 — Ambient temperature (°C)
    float ambient_humidity;     // DHT22 — Ambient humidity (%)
    float gas_1_ppm;            // MQ Gas Sensor 1 (ppm)
    float gas_2_ppm;            // MQ Gas Sensor 2 (ppm)
    float water_temp_1;         // DS18B20 — Water temperature sensor 1 (°C)
    float water_temp_2;         // DS18B20 — Water temperature sensor 2 (°C)
    bool fan_1_status;
    bool fan_2_status;
    bool fan_3_status;
} struct_node2;

struct_node2 myData;
esp_now_peer_info_t peerInfo;

// ─────────────────────────────────────────────
//  ESP-NOW Send Callback
// ─────────────────────────────────────────────
void OnDataSent(const uint8_t *mac_addr, esp_now_send_status_t status) {
    Serial.print("\r\nLast Packet Send Status:\t");
    Serial.println(status == ESP_NOW_SEND_SUCCESS ? "Delivery Success" : "Delivery Fail");
}

// ─────────────────────────────────────────────
//  Setup
// ─────────────────────────────────────────────
void setup() {
    Serial.begin(115200);

    // TODO: Initialize ultrasonic trigger/echo pins
    // TODO: Initialize DHT22
    // TODO: Initialize DS18B20 (OneWire bus)
    // TODO: Initialize MQ gas sensor analog pins

    pinMode(PIN_RELAY_FAN1, OUTPUT);
    pinMode(PIN_RELAY_FAN2, OUTPUT);
    pinMode(PIN_RELAY_FAN3, OUTPUT);
    digitalWrite(PIN_RELAY_FAN1, RELAY_OFF);
    digitalWrite(PIN_RELAY_FAN2, RELAY_OFF);
    digitalWrite(PIN_RELAY_FAN3, RELAY_OFF);

    WiFi.mode(WIFI_STA);

    if (esp_now_init() != ESP_OK) {
        Serial.println("Error initializing ESP-NOW");
        return;
    }

    esp_now_register_send_cb(OnDataSent);

    memcpy(peerInfo.peer_addr, hubAddress, 6);
    peerInfo.channel = 0;
    peerInfo.encrypt = false;

    if (esp_now_add_peer(&peerInfo) != ESP_OK) {
        Serial.println("Failed to add peer");
        return;
    }

    Serial.println("Node 2 — Environment ready.");
}

// ─────────────────────────────────────────────
//  Loop
// ─────────────────────────────────────────────
void loop() {
    // TODO: Read ultrasonic sensors → myData.tank1_level_cm / tank2_level_cm
    // TODO: Read DHT22 → myData.ambient_temp / ambient_humidity
    // TODO: Read DS18B20 → myData.water_temp_1 / water_temp_2
    // TODO: Read gas sensors → myData.gas_1_ppm / gas_2_ppm

    // Auto fan control based on temperature threshold
    bool fanOn = (myData.ambient_temp > TEMP_FAN_THRESHOLD || myData.water_temp_1 > TEMP_FAN_THRESHOLD);
    digitalWrite(PIN_RELAY_FAN1, fanOn ? RELAY_ON : RELAY_OFF);
    myData.fan_1_status = fanOn;

    // Send via ESP-NOW
    esp_now_send(hubAddress, (uint8_t *)&myData, sizeof(myData));

    delay(5000);
}
