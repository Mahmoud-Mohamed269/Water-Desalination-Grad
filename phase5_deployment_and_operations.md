# 🚢 Phase 5 — Deployment, Testing, and Operations

This phase provides a comprehensive guide on how to deploy and test the entire Smart Water Desalination System from end-to-end, covering the Hardware, Backend, Web Dashboard, and Mobile App.

---

## 📋 Table of Contents
1. [Hardware Deployment & Testing](#1-hardware-deployment--testing)
2. [Backend API Deployment & Testing](#2-backend-api-deployment--testing)
3. [Web Dashboard Deployment & Testing](#3-web-dashboard-deployment--testing)
4. [Mobile App Testing & Usage](#4-mobile-app-testing--usage)
5. [End-to-End System Test Flow](#5-end-to-end-system-test-flow)

---

## 1. Hardware Deployment & Testing

The hardware consists of 3 ESP32 nodes. You must flash them in order and verify their connections.

### 1.1 Preparing the Main Hub
1. Open the `Main_Hub` folder in Arduino IDE or PlatformIO.
2. Ensure you have installed the required libraries: `Firebase ESP Client`, `ArduinoJson`, `BLEDevice`.
3. Open `config.h` and verify your `FIREBASE_API_KEY` and `FIREBASE_DATABASE_URL` are correct.
4. **Flash the Main Hub** to an ESP32.
5. **Testing**: 
   - Open the Serial Monitor at `115200` baud.
   - You should see it attempt to connect to WiFi. If it fails, it will fall back to BLE-only mode.
   - You should see `[ESP-NOW] Ready.` indicating the receiver is active.

### 1.2 Preparing Node 1 and Node 2
1. Open `Node1_WaterQuality` and `Node2_Environment`.
2. In each project's `config.h`, ensure the `hubAddress` matches the actual MAC address of your Main Hub ESP32.
   *(You can find the Hub's MAC address in its serial monitor during boot: `[WiFi] MAC: XX:XX:XX...`)*
3. **Flash Node 1 and Node 2**.
4. **Testing**:
   - Open the Serial Monitor for Node 1. You should see it reading mock/real sensors and outputting `[ESP-NOW] Delivery Success`.
   - Look back at the **Main Hub Serial Monitor**. You should see `[ESP-NOW] Node 1 data received` every 5 seconds.

### 1.3 Testing Hardware Internet Connection
1. With the Hub connected to your local WiFi, watch its Serial Monitor.
2. Every 5 seconds (when it receives data), it should print `[Firebase] Live data pushed OK.`
3. Go to your Firebase Console online and verify the data is appearing under `/devices/device_001/live_data`.

---

## 2. Backend API Deployment & Testing

The FastAPI backend handles ML predictions, historical alerts, and offline sync ingestion.

### 2.1 Local Testing
1. Navigate to the `backend` folder in your terminal.
2. Ensure your `.env` file contains `FIREBASE_DATABASE_URL` and `FIREBASE_SERVICE_ACCOUNT_PATH`.
3. Start the server:
   ```bash
   uvicorn app.main:app --reload
   ```
4. **Testing**:
   - Open `http://127.0.0.1:8000/docs` in your browser.
   - Test the `GET /api/v1/sensors/live` endpoint. It should successfully fetch the data that the Main Hub just pushed to Firebase.
   - Test the `GET /api/v1/alerts/history` endpoint to see if the alert engine is evaluating the data.

### 2.2 Vercel Deployment
To deploy the backend to the cloud permanently:
1. Install the Vercel CLI: `npm i -g vercel`
2. Run `vercel login` and authenticate.
3. Run `vercel` in the `backend` directory.
4. Add your `.env` variables in the Vercel project settings dashboard.
5. Your API will be live at `https://your-project.vercel.app`.

---

## 3. Web Dashboard Deployment & Testing

The Web Dashboard visualizes the data sitting in Firebase via your FastAPI backend.

### 3.1 Local Testing
1. Ensure your FastAPI backend is running locally at `http://127.0.0.1:8000`.
2. Open the `dashboard/web/index.html` file in any modern browser.
3. **Testing**:
   - The dashboard should say "Live" (pulsing green indicator) in the bottom left.
   - The KPIs (pH, TDS, Turbidity) should update every 5 seconds as the Main Hub pushes new data.
   - Click the **History** tab. You should see a multi-line chart populating.
   - If the Hardware pushes a high TDS value (e.g., > 1000), an **Alert Toast** should slide in from the top right.

---

## 4. Mobile App Testing & Usage

The Flet mobile app provides offline viewing, BLE connection to the Hub, and WiFi provisioning.

### 4.1 Running the App on PC (Desktop Mode)
1. Navigate to the `mobile/src` folder.
2. Run `python main.py`.
3. The app will open in a window shaped like a mobile phone.

### 4.2 Testing Virtual BLE (No Hardware Needed)
1. Go to the **Settings** tab (gear icon).
2. Ensure "Use Virtual BLE (Testing)" is toggled **ON**.
3. Go back to the **Live** tab. The app will simulate incoming BLE data, display it, and save it to the local SQLite database.
4. Go to the **History** tab to view the SQLite chart.

### 4.3 Testing Real Hardware BLE
1. Ensure your Main Hub ESP32 is powered on.
2. In the App **Settings** tab, toggle "Use Virtual BLE" to **OFF** and set the BLE Device Name to `AquaMonitor`.
3. Restart the app.
4. The app will scan for the ESP32, connect, and stream the live JSON payload.

### 4.4 Provisioning WiFi to the Hardware
If the Main Hub loses WiFi, you can fix it from the App:
1. Ensure the app is connected to the Hub via BLE.
2. Go to the **WiFi** tab in the app.
3. Enter your Home SSID and Password.
4. Click **Send via BLE**. The Hub's Serial Monitor will show `[BLE CMD] Setting WiFi: SSID=...` and it will automatically reconnect.

---

## 5. End-to-End System Test Flow

To prove the entire system works together flawlessly, run this final integration test:

1. **Power up Node 1 and Node 2**.
2. **Power up the Main Hub** (Ensure it is out of WiFi range or given the wrong password initially).
3. **Open the Mobile App** and connect to the Hub via BLE.
   - *Result*: You should see live sensor data streaming to your phone, proving Node1 -> ESP-NOW -> Hub -> BLE -> Phone works.
4. **Go to the WiFi Tab** in the App and send the correct WiFi credentials.
   - *Result*: The Hub connects to WiFi.
5. **Open the Web Dashboard** on your PC.
   - *Result*: The dashboard immediately starts showing the live data, proving Hub -> Firebase -> Backend -> Dashboard works.
6. **Disconnect the Hub from WiFi** temporarily.
   - *Result*: The mobile app continues to receive BLE data and saves it locally.
7. **Reconnect the Hub to WiFi**.
   - *Result*: The mobile app's background worker senses the internet connection and automatically uploads the saved offline data to the FastAPI `/ingest` endpoint, updating the cloud history.

**🎉 System Validation Complete!**
