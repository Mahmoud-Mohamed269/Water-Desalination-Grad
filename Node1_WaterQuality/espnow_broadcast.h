/*
 * ============================================================
 *  espnow_broadcast.h — ESP-NOW helper for Node 1
 *  Sends full SensorReading struct to the Main Hub.
 *
 *  IMPORTANT: Replace HUB_MAC_ADDRESS with the actual MAC address
 *  of your Main Hub ESP32. You can find it by running:
 *    WiFi.macAddress() on the Hub and printing to Serial.
 * ============================================================
 */
#ifndef ESPNOW_BROADCAST_H
#define ESPNOW_BROADCAST_H

#include <Arduino.h>
#include <esp_now.h>
#include <WiFi.h>
#include <esp_wifi.h>
#include "sensors.h"

// ============================================================
// IMPORTANT: Set this to your Main Hub ESP32 MAC address!
// Find it by printing WiFi.macAddress() in Hub's setup()
// ============================================================
#define HUB_MAC_ADDRESS { 0x80, 0xF3, 0xDA, 0x42, 0xCC, 0x28 }  // MAC address of the Main Hub

// Full struct matching Main Hub expectations (all Node 1 fields)
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

static uint8_t hubMac[] = HUB_MAC_ADDRESS;
static bool espnowReady = false;

inline void espnowBroadcastInit() {
    // ESP-NOW uses WiFi STA mode — must be called after WiFi.mode(WIFI_STA)
    if (esp_now_init() == ESP_OK) {
        esp_now_peer_info_t peerInfo = {};
        memcpy(peerInfo.peer_addr, hubMac, 6);
        peerInfo.channel = 0;
        peerInfo.encrypt = false;
        esp_now_add_peer(&peerInfo);
        espnowReady = true;
        Serial.println("[ESP-NOW] Node 1 broadcast ready.");
    } else {
        Serial.println("[ESP-NOW] Init failed.");
    }
}

inline void espnowBroadcastReading(const SensorReading& r) {
    if (!espnowReady) return;
    espnow_node1_t pkt;
    pkt.ph_feed              = r.ph_feed;
    pkt.ph_permeate          = r.ph_permeate;
    pkt.tds_feed             = r.tds_feed;
    pkt.tds_permeate         = r.tds_permeate;
    pkt.turbidity_feed       = r.turbidity_feed;
    pkt.temperature_feed     = r.temperature_feed;
    pkt.temperature_permeate = r.temperature_permeate;
    pkt.pressure_feed        = r.pressure_feed;
    pkt.flow_rate_feed       = r.flow_rate_feed;
    pkt.flow_rate_permeate   = r.flow_rate_permeate;
    pkt.recovery_rate        = r.recovery_rate;
    pkt.rejection_rate       = r.rejection_rate;
    pkt.level_feed_full      = (r.level_feed    == LEVEL_WATER);
    pkt.level_product_full   = (r.level_product == LEVEL_WATER);
    pkt.pump_running         = (r.pump_status  == "running");
    pkt.valve_open           = (r.valve_status == "open");
    pkt.uptime_seconds       = r.uptime_seconds;
    
    // ESP-NOW requires the sender and receiver to be on the exact same Wi-Fi channel.
    // Because the Main Hub connects to your home Wi-Fi, it adopts your router's channel.
    // Since Node 1 is asleep and doesn't connect to Wi-Fi, it doesn't know the channel.
    // We send the packet on all 13 channels in a quick burst to guarantee delivery!
    for (uint8_t ch = 1; ch <= 13; ch++) {
        esp_wifi_set_channel(ch, WIFI_SECOND_CHAN_NONE);
        esp_now_send(hubMac, (uint8_t*)&pkt, sizeof(pkt));
        delay(2);
    }
}

#endif // ESPNOW_BROADCAST_H
