# ☁️ Phase 10 — Cloud Deployment on Vercel

This phase walks you through deploying the FastAPI backend to **Vercel** so the system is accessible from anywhere — not just your local WiFi network.

---

## 📋 Table of Contents
1. [Objectives](#1-objectives)
2. [Why Vercel](#2-why-vercel)
3. [Pre-Deployment Checklist](#3-pre-deployment-checklist)
4. [Step 1 — Encode Your Firebase Service Account](#step-1--encode-your-firebase-service-account)
5. [Step 2 — Push Code to GitHub](#step-2--push-code-to-github)
6. [Step 3 — Create a Vercel Project](#step-3--create-a-vercel-project)
7. [Step 4 — Set Environment Variables](#step-4--set-environment-variables)
8. [Step 5 — Deploy](#step-5--deploy)
9. [Step 6 — Verify the Deployment](#step-6--verify-the-deployment)
10. [Step 7 — Update Mobile App & Dashboard](#step-7--update-mobile-app--dashboard)
11. [Auto-Deployment on Push](#auto-deployment-on-push)
12. [Troubleshooting](#troubleshooting)
13. [New Backend Endpoint: /predict/run](#new-backend-endpoint-predictrun)

---

## 1. Objectives

| # | Objective | Priority |
|---|---|---|
| 1 | Deploy FastAPI backend to Vercel (accessible globally) | 🔴 Critical |
| 2 | Securely inject Firebase credentials via env var (no file upload) | 🔴 Critical |
| 3 | Verify all API endpoints work on the live URL | 🔴 Critical |
| 4 | Update mobile app to point to cloud API URL | 🟠 High |
| 5 | Update web dashboard to use cloud API URL | 🟠 High |
| 6 | Enable auto-deploy on every `git push` | 🟡 Medium |

---

## 2. Why Vercel

| Feature | Vercel | Railway | Notes |
|---|---|---|---|
| Free tier | ✅ Generous | ✅ Limited hours/month | Vercel better for low-traffic APIs |
| Python support | ✅ @vercel/python | ✅ Native | Both work |
| Serverless (no persistent processes) | ✅ | ❌ | Vercel is stateless per request |
| Execution timeout | 10s (hobby), 60s (pro) | None | Fine for our API — all calls < 5s |
| Automatic HTTPS | ✅ | ✅ | Both |
| Custom domain | ✅ | ✅ | Both |
| Git integration | ✅ Excellent | ✅ Good | Vercel marginally better |
| `requirements.txt` support | ✅ | ✅ | Both |

> [!NOTE]
> Vercel's 10-second function timeout is not a concern for this project. Our heaviest operation is ML inference which takes ~100ms, and Firebase reads which take ~200–500ms. All endpoints complete well within 10 seconds.

---

## 3. Pre-Deployment Checklist

Before deploying, confirm:
- [ ] `backend/vercel.json` exists (created in this phase)
- [ ] `backend/requirements.txt` is up to date (includes `pydantic-settings`)
- [ ] `backend/ml/` contains all 4 `.pkl` files
- [ ] `serviceAccountKey.json` is **not** committed to Git
- [ ] `.env` is **not** committed to Git
- [ ] You have a GitHub account and the project is in a repository

---

## Step 1 — Encode Your Firebase Service Account

Vercel cannot read files uploaded alongside your code (no persistent filesystem). Instead, we encode the `serviceAccountKey.json` as a **base64 string** and store it as an environment variable.

### On Windows (PowerShell):
```powershell
# Navigate to the backend folder
cd "d:\Projects\Arduino Projects\Water Desalination\backend"

# Encode the file
[Convert]::ToBase64String([IO.File]::ReadAllBytes("serviceAccountKey.json")) | Set-Clipboard

# The base64 string is now in your clipboard — paste it into Vercel's env vars in Step 4
```

### On macOS / Linux:
```bash
cd backend
base64 -i serviceAccountKey.json | tr -d '\n' | pbcopy
# Clipboard now contains the base64 string
```

### Manual way (any OS via Python):
```python
import base64

with open("backend/serviceAccountKey.json", "rb") as f:
    encoded = base64.b64encode(f.read()).decode("utf-8")

print(encoded)  # Copy this entire output
```

> [!IMPORTANT]
> The base64 string will be very long (several KB). Make sure you copy the **entire** string with no line breaks.

---

## Step 2 — Push Code to GitHub

If you haven't already:

```powershell
# In the project root
cd "d:\Projects\Arduino Projects\Water Desalination"

# Initialize git (if not done)
git init
git add .
git commit -m "Initial commit — Phase 10 cloud deployment ready"

# Create a GitHub repo at github.com, then:
git remote add origin https://github.com/YOUR_USERNAME/water-desalination.git
git push -u origin main
```

> [!WARNING]
> Run `git status` before committing and verify that `serviceAccountKey.json` and `.env` do **not** appear in the list. If they do, your `.gitignore` is misconfigured — stop and fix it first.

---

## Step 3 — Create a Vercel Project

1. Go to **[vercel.com](https://vercel.com)** and sign in (or create an account — it's free)
2. Click **"Add New… → Project"**
3. Click **"Import Git Repository"** and select your GitHub repo
4. In the **"Configure Project"** screen:
   - **Framework Preset:** `Other`
   - **Root Directory:** Click **Edit** → type `backend` → click **Continue**

   > This tells Vercel to deploy only the `backend/` folder, where `vercel.json` and `main.py` are.

5. **Do NOT click Deploy yet** — first set environment variables in Step 4.

---

## Step 4 — Set Environment Variables

Still in the Vercel project setup screen, scroll to **"Environment Variables"** and add the following:

| Variable Name | Value | Where to find it |
|---|---|---|
| `FIREBASE_DATABASE_URL` | `https://your-project-rtdb.europe-west1.firebasedatabase.app` | Firebase Console → Realtime Database → copy URL |
| `FIREBASE_SERVICE_ACCOUNT_BASE64` | (the base64 string from Step 1) | Output of the encode command |
| `GEMINI_API_KEY` | Your Gemini API key | [aistudio.google.com](https://aistudio.google.com) |
| `API_KEY` | `aquamonitor-secret-key-2024` | Choose your own — keep it secret |

> [!IMPORTANT]
> Set each variable for **all environments** (Production, Preview, Development) by checking all three checkboxes.

---

## Step 5 — Deploy

1. Click **"Deploy"**
2. Vercel will:
   - Clone your repo
   - Install packages from `backend/requirements.txt`
   - Run `@vercel/python` builder on `main.py`
   - Deploy to a URL like `https://water-desalination-abc123.vercel.app`
3. Wait for the build to complete (usually 1–3 minutes)
4. A green ✓ "Congratulations!" screen confirms success

---

## Step 6 — Verify the Deployment

Open your browser and test these URLs (replace with your actual Vercel URL):

### 6.1 Root health check
```
https://your-project.vercel.app/
```
Expected response:
```json
{"message": "Water Desalination API is running.", "docs": "/docs"}
```

### 6.2 Interactive API docs
```
https://your-project.vercel.app/docs
```
This opens Swagger UI — you can test every endpoint interactively.

### 6.3 Live sensor data
```
https://your-project.vercel.app/api/v1/sensors/live
```
Expected: your latest Firebase data, or `{"status": "no_data"}` if no hardware has pushed yet.

### 6.4 ML auto-prediction
```
https://your-project.vercel.app/api/v1/predict/run
```
Expected: water quality + membrane status labels with confidence percentages.

### 6.5 Test protected endpoint (should fail without key)
```bash
curl -X POST https://your-project.vercel.app/api/v1/sensors/ingest \
  -H "Content-Type: application/json" \
  -d '{"ph_feed": 7.2}'
# Expected: 403 Forbidden
```

```bash
curl -X POST https://your-project.vercel.app/api/v1/sensors/ingest \
  -H "Content-Type: application/json" \
  -H "X-API-Key: aquamonitor-secret-key-2024" \
  -d '{"ph_feed": 7.2, "tds_feed": 300}'
# Expected: 200 OK {"status":"ok","timestamp":"..."}
```

---

## Step 7 — Update Mobile App & Dashboard

### 7.1 Mobile App (Flet)

1. Launch the app → tap **Settings** tab
2. In **"FastAPI Backend URL"**, change from `http://127.0.0.1:8000` to:
   ```
   https://your-project.vercel.app
   ```
3. Tap **"Save Settings"**
4. The app now syncs to the cloud backend even when not on your local WiFi

### 7.2 Web Dashboard (`Water Desalination.html`)

Open the dashboard HTML file and find the API base URL variable (near the top of the `<script>` section). Update it:

```javascript
// ❌ Old
const API_BASE = "http://127.0.0.1:8000";

// ✅ New
const API_BASE = "https://your-project.vercel.app";
```

### 7.3 Update CORS in backend

Now that you know your Vercel URL, add it to the allowed origins in `backend/main.py`:

```python
ALLOWED_ORIGINS = [
    "http://localhost",
    "http://127.0.0.1",
    "https://your-project.vercel.app",      # ← Add this
    # Also add your dashboard URL if hosted separately:
    # "https://your-dashboard.vercel.app",
]
```

Commit and push — Vercel will auto-redeploy.

### 7.4 Update ESP32 Main Hub (if posting directly)

If the Main Hub firmware posts directly to FastAPI (vs. through the mobile app), update `Main_Hub/config.h`:

```cpp
// ❌ Old
const char* API_ENDPOINT = "http://192.168.1.100:8000/api/v1/sensors/ingest";

// ✅ New
const char* API_ENDPOINT = "https://your-project.vercel.app/api/v1/sensors/ingest";
const char* API_KEY = "aquamonitor-secret-key-2024";
```

---

## Auto-Deployment on Push

After the initial setup, **every `git push` to `main` automatically triggers a new Vercel deployment**. You can see the deployment history in the Vercel dashboard.

Workflow:
```
Edit code locally → git add . → git commit → git push → Vercel auto-redeploys in ~90 seconds
```

---

## Troubleshooting

### Build fails: "ModuleNotFoundError: No module named 'pydantic_settings'"
**Cause:** `pydantic-settings` was not in `requirements.txt`
**Fix:** It was added in Phase 10. Verify `backend/requirements.txt` contains `pydantic-settings>=2.2.0`

### Build fails: "File too large" or bundle size error
**Cause:** The `.pkl` ML model files (~7MB total) exceed Vercel's default limit
**Fix:** `backend/vercel.json` has `"maxLambdaSize": "50mb"` — verify this is present

### Firebase error: "Invalid credential type"
**Cause:** The base64 string was copied incorrectly (truncated or has line breaks)
**Fix:** Re-encode using the Python method and copy the full output carefully

### Firebase error: "Failed to determine project ID"
**Cause:** The encoded service account JSON is malformed
**Fix:** Decode and verify: `python -c "import base64,json; json.loads(base64.b64decode('YOUR_STRING'))"`

### 403 on all endpoints
**Cause:** `API_KEY` env var is set in Vercel but you're not sending it in requests
**Fix:** Add `X-API-Key: your-key` header, or temporarily set `API_KEY=` (empty) in Vercel to disable protection

### ML prediction returns 404 "No live data in Firebase yet"
**Cause:** No hardware has pushed data to Firebase
**Fix:** Run the Mobile App in Virtual BLE mode → go to Settings → disable Virtual BLE and ensure your Main Hub is online, or manually POST some data to `/ingest`

---

## New Backend Endpoint: /predict/run

Added in this phase — `GET /api/v1/predict/run`:

```
GET /api/v1/predict/run
```

No request body needed. The endpoint:
1. Reads `live_data` from Firebase (`/devices/device_001/live_data`)
2. Derives all 13 ML features:
   - `TDS_Reduction = (tds_feed - tds_permeate) / tds_feed × 100`
   - `Turbidity_Reduction = (turbidity_feed - turbidity_permeate) / turbidity_feed × 100`
   - `pH_Change = ph_permeate - ph_feed`
   - `Efficiency = recovery_rate`
3. Runs both Random Forest classifiers
4. Returns:

```json
{
  "status": "ok",
  "predictions": {
    "water_quality": {
      "label": "good",
      "confidence": 94.2,
      "probabilities": {"good": 94.2, "acceptable": 4.1, "poor": 1.7, "bad": 0.0}
    },
    "membrane_status": {
      "label": "good",
      "confidence": 87.5,
      "probabilities": {"good": 87.5, "warning": 11.3, "critical": 1.2, "fouled": 0.0}
    }
  },
  "derived_features": {
    "TDS_Reduction": 91.5,
    "pH_Change": -0.32,
    ...
  }
}
```
