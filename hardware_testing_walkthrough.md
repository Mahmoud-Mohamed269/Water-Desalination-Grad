# Hardware & Software Testing Walkthrough

This guide walks you through the end-to-end testing of your Water Desalination system, ensuring the ESP32 hardware, Mobile App, and Web Dashboard all communicate correctly.

## Prerequisites
1. **Node 1 (Water Quality)** and **Main Hub** ESP32s are flashed with the updated firmware.
2. The FastAPI backend and Web Dashboard are installed.
3. The Mobile App dependencies (`flet`, `bleak`, etc.) are installed.

---

## Step 1: Start the Local Servers
First, start your backend API and web dashboard. 

Open a terminal in the root of your project folder (`D:\Projects\Arduino Projects\Water Desalination`) and run:
```bash
python run.py
```
> [!NOTE]
> This command starts the FastAPI backend on `http://127.0.0.1:8000` and the web dashboard on `http://127.0.0.1:54321`. Leave this terminal running in the background.

## Step 2: Power on the Hardware
1. Power up **Node 1**. It will immediately wake up, take sensor readings, broadcast them via ESP-NOW, and go back to deep sleep.
2. Power up the **Main Hub**. It will begin advertising its BLE service (named `AquaMonitor`) and wait for WiFi credentials if it doesn't already have them.

## Step 3: Launch the Mobile App
Open a new terminal, navigate to the mobile source directory, and start the app:
```bash
cd mobile/src
python main.py
```

> [!TIP]
> If you don't have Bluetooth enabled on your PC, you can test the UI by going to the **Settings** tab in the mobile app and enabling **Use Virtual BLE (Testing)**, then restarting the app.

## Step 4: Configure Hub WiFi via Mobile App
We need to tell the Main Hub how to connect to your local router (e.g., `Mahmoud`).

1. In the mobile app, navigate to the **WiFi Setup** tab.
2. Enter your router's **SSID** and **Password**.
3. Click **Send via BLE**.
4. **Expected Result**: The app should confirm the credentials were sent. If you monitor the Main Hub's serial output via Arduino IDE, you should see it receive the JSON command over BLE and attempt to connect to your Wi-Fi.

> [!IMPORTANT]
> The Main Hub *must* connect to the same Wi-Fi router that your computer (running the backend) is connected to!

## Step 5: Verify Data Flow
Once the Main Hub connects to Wi-Fi, the full pipeline will activate:

1. **ESP-NOW Link**: Node 1 wakes up (every ~30s), reads sensors, and blasts the data across all channels. The Main Hub intercepts this data.
2. **Backend Ingestion**: The Main Hub forwards the payload to your local FastAPI backend (`http://<YOUR_PC_IP>:8000/api/v1/sensors/ingest`).
3. **Web Dashboard**: Open your browser to [http://127.0.0.1:54321](http://127.0.0.1:54321). 
   - **Expected Result**: You should see the live sensor values (pH, TDS, Turbidity, etc.) updating dynamically.
4. **Mobile App Dashboard**: Navigate to the **Dashboard** tab on the mobile app. 
   - **Expected Result**: The mobile app fetches the latest readings from the backend and updates the UI.

## Troubleshooting

> [!WARNING]
> **Firebase Errors:** You may see `WARNING: serviceAccountKey.json not found! Running backend without Firebase sync.` in your backend logs. This is normal if you haven't set up the backend admin SDK key yet; the local pipeline (Hardware → Local Backend → Dashboard) will still work perfectly.

> [!CAUTION]
> **No Data on Dashboard?** 
> - Ensure your `config.h` in the Main Hub has `BACKEND_URL` set to your PC's actual local IP address (e.g., `192.168.1.X`), not `127.0.0.1`. The ESP32 cannot resolve `127.0.0.1` to your computer.
> - Verify Node 1 and Main Hub are close enough for ESP-NOW range.
