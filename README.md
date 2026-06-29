# 🌊 AquaMonitor — Smart Water Desalination Monitoring System

A full-stack IoT monitoring and analytics platform for Reverse Osmosis (RO) desalination systems. Combines ESP32 edge nodes, Firebase real-time cloud storage, a FastAPI ML backend, a web dashboard, and a cross-platform mobile app.

---

## 🏗️ System Architecture

```
┌─────────────┐   ESP-NOW    ┌──────────────┐   Firebase RTDB   ┌─────────────┐
│  Node 1     │ ──────────── │   Main Hub   │ ────────────────── │   Firebase  │
│  (Water Q.) │              │   (ESP32)    │                    │  Realtime   │
│  Node 2     │              │              │                    │  Database   │
│  (Environ.) │              └──────┬───────┘                    └──────┬──────┘
└─────────────┘                     │ BLE                               │
                              ┌─────▼──────┐                     ┌──────▼──────┐
                              │ Mobile App │  ←── HTTP sync ────▶│  FastAPI    │
                              │  (Python/  │                      │  Backend    │
                              │   Flet)    │                      │  + ML Models│
                              └────────────┘                      └──────┬──────┘
                                                                         │
                                                                  ┌──────▼──────┐
                                                                  │    Web      │
                                                                  │  Dashboard  │
                                                                  │  (HTML/JS)  │
                                                                  └─────────────┘
```

---

## 📁 Project Structure

```
Water Desalination/
├── Node1_WaterQuality/     # ESP32 firmware — pH, TDS, turbidity, pressure, flow
├── Node2_Environment/      # ESP32 firmware — temperature, humidity, gas, ultrasonic
├── Main_Hub/               # ESP32 firmware — ESP-NOW receiver, BLE server, Firebase uploader
├── backend/                # FastAPI backend — ML predictions, alerts, Firebase proxy
│   ├── app/api/v1/         # REST endpoints (sensors, predict, alerts, chat, status)
│   ├── app/core/           # Config, Firebase client, security
│   ├── app/services/       # ML inference service
│   ├── ml/                 # Trained .pkl model files
│   ├── Procfile            # Railway deployment
│   └── railway.json        # Railway config
├── dashboard/web/          # Web dashboard (HTML + CSS + JS, Firebase direct)
├── mobile/src/             # Flet mobile app (Python)
│   ├── pages/              # Live, History, Alerts, WiFi, Settings
│   ├── ble/                # Real + Virtual BLE client
│   └── db/                 # SQLite offline storage + sync
└── Water Desalination.html # Standalone single-file web dashboard
```

---

## 🔧 Hardware (Bill of Materials)

| Component | Model | Qty | Node |
|---|---|---|---|
| Microcontroller | ESP32 38-pin | 3 | All |
| pH Sensor | Analog pH Kit (BNC) | 2 | Node 1 (feed + permeate) |
| TDS Sensor | TDS Meter V1.0 | 2 | Node 1 (feed + permeate) |
| Turbidity Sensor | Analog module | 1 | Node 1 |
| Pressure Sensor | G1/4 0–1.2 MPa analog | 1 | Node 1 |
| Temperature Sensor | DS18B20 | 2 | Node 1 |
| Flow Sensor | YF-S201 | 2 | Node 1 (feed + permeate) |
| Water Level Sensor | XKC-Y25 (non-contact) | 2 | Node 1 |
| Relay Module | 2-channel 5V | 1 | Node 1 (pump + valve) |
| Temp + Humidity | DHT22 | 1 | Node 2 |
| Gas Sensor | MQ series | 2 | Node 2 |
| Ultrasonic | HC-SR04 | 2 | Node 2 |
| TFT Display | 5" SPI | 1 | Main Hub |

---

## 🚀 Setup Instructions

### 1. Firebase Setup
1. Create a project at [console.firebase.google.com](https://console.firebase.google.com)
2. Enable **Realtime Database** (Europe West region)
3. Download the **service account JSON** → save as `backend/serviceAccountKey.json`
4. Copy your database URL to `backend/.env`:
   ```
   FIREBASE_DATABASE_URL=https://your-project-rtdb.europe-west1.firebasedatabase.app
   ```

### 2. Flash Hardware
```bash
# In Arduino IDE:
# 1. Flash Main_Hub to the hub ESP32 first — note its MAC address from Serial Monitor
# 2. Update hubAddress in Node1/config.h and Node2/config.h
# 3. Flash Node 1 and Node 2
# 4. Open Serial Monitor (115200 baud) — you should see:
#    [ESP-NOW] Node 1 data received
#    [Firebase] Live data pushed OK
```

### 3. Run the Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
# API docs: http://127.0.0.1:8000/docs
```

### 4. Open the Web Dashboard
```bash
# Option A — standalone file (no server needed):
open "Water Desalination.html"

# Option B — from the dashboard folder:
open dashboard/web/index.html
```

### 5. Run the Mobile App
```bash
cd mobile/src
pip install flet bleak requests
python main.py
```
- Use **Settings** tab to toggle Virtual BLE (for testing without hardware)
- Use **WiFi** tab to provision WiFi credentials to the Hub over BLE

---

## ☁️ Cloud Deployment (Vercel)

Full step-by-step guide: **[phase10_cloud_deployment.md](phase10_cloud_deployment.md)**

### Quick Summary

**1. Encode your Firebase service account as base64 (PowerShell):**
```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("backend\serviceAccountKey.json")) | Set-Clipboard
```

**2. Push to GitHub, then import to [vercel.com](https://vercel.com):**
- Set Root Directory → `backend`
- Framework Preset → `Other`

**3. Add these Environment Variables in Vercel:**
| Variable | Value |
|---|---|
| `FIREBASE_DATABASE_URL` | Your Firebase RTDB URL |
| `FIREBASE_SERVICE_ACCOUNT_BASE64` | Paste the base64 string from step 1 |
| `GEMINI_API_KEY` | Your Gemini API key |
| `API_KEY` | Your chosen API key |

**4. Deploy → get your URL → update mobile app Settings.**

> See [phase10_cloud_deployment.md](phase10_cloud_deployment.md) for the full tutorial including verification steps and troubleshooting.

---

## 🔐 Security

| Layer | Mechanism |
|---|---|
| Backend write endpoints | `X-API-Key` header required |
| Firebase Database | Security Rules (auth-gated in production) |
| Secrets | `.env` file only — `.gitignore`'d |
| CORS | Restricted to known origins |

The API key is set via `API_KEY` in `backend/.env`. The mobile app and ESP32 Hub include it in `X-API-Key` headers for POST requests.

---

## 🤖 ML Models

Two Random Forest models trained on synthetic RO system data:

| Model | Output | File |
|---|---|---|
| Water Quality Classifier | good / acceptable / poor / bad | `water_quality_rf.pkl` |
| Membrane Status Classifier | good / warning / critical / fouled | `membrane_status_rf.pkl` |

**Input features (13):** pH before/after, TDS before/after, Turbidity before/after, Temperature before/after, Pressure, Efficiency (recovery rate), TDS Reduction %, Turbidity Reduction %, pH Change.

**Auto-prediction endpoint:** `GET /api/v1/predict/run` — fetches live Firebase data and derives all features automatically. Call it from the mobile app's Dashboard → ML Analysis → ↻ button.

---

## 📡 API Reference

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/v1/sensors/live` | Public | Latest live sensor snapshot |
| GET | `/api/v1/sensors/history` | Public | Last N historical readings |
| POST | `/api/v1/sensors/ingest` | API Key | Push sensor data to Firebase |
| GET | `/api/v1/predict/run` | Public | Auto-run ML from live data |
| POST | `/api/v1/predict/` | Public | Manual ML prediction |
| GET | `/api/v1/alerts/history` | Public | Recent alerts |
| POST | `/api/v1/alerts/evaluate` | Public | Evaluate snapshot against thresholds |
| POST | `/api/v1/chat/` | Public | Gemini AI chatbot |
| GET | `/api/v1/status/` | Public | System health |

Full interactive docs: `http://127.0.0.1:8000/docs`

---

## 🛠️ Development

```bash
# Backend tests
cd backend
python -m pytest

# Mobile app (desktop mode)
cd mobile/src
python main.py

# Generate synthetic training data
python generate_data.py

# Retrain ML models
python ML_models.py
```

---

## 📋 Phase Completion Status

| Phase | Description | Status |
|---|---|---|
| 1 | Requirements & Architecture | ✅ |
| 2 | Hardware Design & BOM | ✅ |
| 3 | ESP32 Firmware | ✅ |
| 4 | FastAPI Backend + ML | ✅ |
| 5 | Deployment Guide | ✅ |
| 6 | Hardware Assembly & Real Testing | ✅ Node 1 + Hub verified |
| 8 | Mobile App Polish | ✅ |
| 9 | Security (API Key) | ✅ |
| 10 | Cloud Deployment (Railway) | ⏳ Ready to deploy |
| 11 | Documentation | ✅ |

---

## 👥 Team

Built as part of the TVI Water Desalination Monitoring Project.

---

*Last updated: June 2026*
