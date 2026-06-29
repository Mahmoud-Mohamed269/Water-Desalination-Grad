#ifndef CONFIG_HUB_H
#define CONFIG_HUB_H

// ============================================================
//  Main Hub Configuration
//  Board: ESP32S 38-pin Development Board
//  Role:  Receives ESP-NOW from Node1 & Node2,
//         streams data to mobile app over BLE,
//         pushes merged data to FastAPI backend via HTTP.
// ============================================================

// ============================================================
//  TFT DISPLAY PINS (SPI — 5-inch TFT)
//  Adjust if using TFT_eSPI library (also set in User_Setup.h)
// ============================================================
#define PIN_TFT_CS              15
#define PIN_TFT_DC              2
#define PIN_TFT_RST             4
#define PIN_TFT_MOSI            23
#define PIN_TFT_SCLK            18
#define PIN_TFT_BL              21      // Backlight control (optional)

// ============================================================
//  STATUS LED
// ============================================================
#define PIN_STATUS_LED          2

// ============================================================
//  BLUETOOTH LOW ENERGY (BLE)
//  "AquaMonitor" is the device name the mobile app scans for.
// ============================================================
#define BLE_DEVICE_NAME         "AquaMonitor"
#define BLE_SERVICE_UUID        "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
#define BLE_NOTIFY_CHAR_UUID    "beb5483e-36e1-4688-b7f5-ea07361b26a8"  // Hub → App (sensor data)
#define BLE_WRITE_CHAR_UUID     "cba1d466-344c-4be3-ab3f-189f80dd7518"  // App → Hub (commands)

// ============================================================
//  WiFi (stored in NVS, defaults shown here as fallback)
// ============================================================
#define WIFI_SSID               "Mahmoud"
#define WIFI_PASSWORD           "Mahmoud_S23Ultra"
#define WIFI_CONNECT_TIMEOUT_MS 15000

// ============================================================
//  FastAPI Backend URL
//  If running on the same local network as the backend PC:
//  change this to the PC's local IP, e.g. "http://192.168.1.100:8000"
// ============================================================
#define BACKEND_URL             "http://192.168.1.100:8000"

// ============================================================
//  FIREBASE (for future direct push if needed)
// ============================================================
#define FIREBASE_API_KEY        "AIzaSyBVlEjmUXPUa0PJD_ASDDCKpTBP2AE5QP8"
#define FIREBASE_DATABASE_URL   "water-desalination-8638c-default-rtdb.europe-west1.firebasedatabase.app"
#define DEVICE_ID               "device_001"

// ============================================================
//  SERIAL DEBUG
// ============================================================
#define SERIAL_BAUD_RATE        115200

#endif // CONFIG_HUB_H
