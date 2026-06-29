# 🔐 Phase 9 — Security & API Key Protection

This phase adds an API key authentication layer to the FastAPI backend, tightens CORS policy, and moves all secrets to environment variables — making the system safe to deploy publicly.

---

## 📋 Table of Contents
1. [Objectives](#1-objectives)
2. [Threat Model](#2-threat-model)
3. [API Key Implementation](#3-api-key-implementation)
4. [CORS Hardening](#4-cors-hardening)
5. [Secret Management](#5-secret-management)
6. [Which Endpoints Are Protected](#6-which-endpoints-are-protected)
7. [Testing Security](#7-testing-security)
8. [Future Improvements](#8-future-improvements)

---

## 1. Objectives

| # | Objective | Priority |
|---|---|---|
| 1 | Prevent unauthorized writes to Firebase via `/ingest` | 🔴 Critical |
| 2 | Protect ML predictions from abuse | 🟠 High |
| 3 | Tighten CORS to known origins | 🟠 High |
| 4 | Remove hardcoded secrets from code | 🔴 Critical |
| 5 | Keep public read endpoints open (dashboard, mobile) | 🟠 High |

---

## 2. Threat Model

Without security, anyone who discovers your backend URL can:
- **Flood `/ingest`** with fake sensor data, corrupting your Firebase RTDB
- **Spam `/api/v1/chat`** consuming your Gemini API quota
- **Read live data** (acceptable — no PII, public monitoring data)

We do **not** need full user authentication (Firebase Auth) for this personal/lab project. An API key on write/mutating endpoints is sufficient.

---

## 3. API Key Implementation

### 3.1 How It Works

A new FastAPI dependency in `backend/app/core/security.py` checks the `X-API-Key` HTTP header on every protected request:

```python
async def verify_api_key(api_key: str = Security(API_KEY_HEADER)):
    if not settings.API_KEY:
        return  # Dev mode — no key configured, allow all

    if api_key != settings.API_KEY:
        raise HTTPException(
            status_code=403,
            detail="Invalid or missing API key."
        )
```

**Dev mode safety:** If `API_KEY` is empty in `.env` (local development), the check is bypassed entirely. This prevents you from locking yourself out during development.

### 3.2 Applying the Dependency

The dependency is added to a specific endpoint using FastAPI's `dependencies` parameter:

```python
@router.post("/ingest", dependencies=[Depends(verify_api_key)])
def ingest_sensor_data(payload: SensorPayload):
    ...
```

This is cleaner than adding the dependency to the router level (which would block public read endpoints).

### 3.3 Setting the API Key

**Local `.env` (never commit this file):**
```
API_KEY=aquamonitor-secret-key-2024
```

> [!WARNING]
> Change this value before deploying publicly. Use a random string of at least 32 characters. You can generate one with:
> ```python
> import secrets; print(secrets.token_urlsafe(32))
> ```

**Vercel Environment Variables (see Phase 10):**
Set `API_KEY` in your Vercel project → Settings → Environment Variables.

### 3.4 Sending the Key from Clients

Any client that calls a protected endpoint must include the header:

**From the Mobile App's sync worker (`db/sync.py`):**
```python
headers = {"X-API-Key": "aquamonitor-secret-key-2024"}
requests.post(f"{api_url}/api/v1/sensors/ingest", json=payload, headers=headers)
```

**From the ESP32 Main Hub (if posting directly):**
```cpp
http.addHeader("X-API-Key", "aquamonitor-secret-key-2024");
```

**From curl (testing):**
```bash
curl -X POST https://your-api.vercel.app/api/v1/sensors/ingest \
  -H "X-API-Key: aquamonitor-secret-key-2024" \
  -H "Content-Type: application/json" \
  -d '{"ph_feed": 7.2, "tds_feed": 300}'
```

---

## 4. CORS Hardening

### 4.1 What CORS Is

Cross-Origin Resource Sharing (CORS) controls which websites can call your API from a browser. Without CORS restrictions, any webpage in the world could silently call your backend from a visitor's browser.

### 4.2 Old Configuration (insecure)

```python
allow_origins=["*"]  # Any website can call your API
```

### 4.3 New Configuration

```python
ALLOWED_ORIGINS = [
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://127.0.0.1",
    # "https://your-project.vercel.app",  ← add after deploy
]
```

> [!IMPORTANT]
> After you deploy to Vercel, add your Vercel URL and your web dashboard's URL to `ALLOWED_ORIGINS` in `backend/main.py`. Then redeploy.

### 4.4 Note on CORS vs API Keys

CORS protections only apply to browser-based requests. Tools like `curl`, Postman, and the mobile app (Python `requests`) **ignore CORS** and send requests regardless. CORS protects against malicious web pages, not against scripts or servers. The API key protects against both.

---

## 5. Secret Management

### 5.1 What Must Never Be Committed to Git

| File | Contains | Gitignore Rule |
|---|---|---|
| `backend/.env` | API key, Gemini key | `backend/.env` |
| `backend/serviceAccountKey.json` | Firebase admin credentials | `backend/serviceAccountKey.json` |
| `serviceAccountKey.json` | (root copy) | `serviceAccountKey.json` |
| `mobile/src/sensor_data.sqlite` | User reading history | `*.sqlite` |

All of these are covered by `.gitignore` as of Phase 9.

### 5.2 Environment Variable Priority

```
Vercel Dashboard env vars
    ↓ (override)
backend/.env file
    ↓ (override)
Default values in config.py
```

### 5.3 The Gemini API Key

The Gemini API key was previously hardcoded in `config.py`:

```python
# ❌ Old — hardcoded in source code
GEMINI_API_KEY: str = "AQ.Ab8RN6LxZkUT-..."
```

It is now loaded exclusively from `.env`:

```python
# ✅ New — loaded from environment
GEMINI_API_KEY: str = ""  # Must be set in .env or Vercel env vars
```

Set it in `backend/.env`:
```
GEMINI_API_KEY=your-actual-key-here
```

---

## 6. Which Endpoints Are Protected

| Endpoint | Method | Protected | Reason |
|---|---|---|---|
| `/api/v1/sensors/live` | GET | ❌ Open | Read-only, public dashboard needs it |
| `/api/v1/sensors/history` | GET | ❌ Open | Read-only, charts need it |
| `/api/v1/sensors/ingest` | POST | ✅ **API Key** | Writes to Firebase |
| `/api/v1/predict/run` | GET | ❌ Open | Read-only, mobile dashboard |
| `/api/v1/predict/` | POST | ❌ Open | No state mutation |
| `/api/v1/alerts/history` | GET | ❌ Open | Read-only |
| `/api/v1/alerts/evaluate` | POST | ❌ Open | Writes to Firebase but ephemeral |
| `/api/v1/chat/` | POST | ❌ Open | Quota-limited by Gemini already |
| `/api/v1/status/` | GET | ❌ Open | Health check |

> [!TIP]
> If you want to protect the chat endpoint from quota abuse, add `dependencies=[Depends(verify_api_key)]` to the chat router as well.

---

## 7. Testing Security

### 7.1 Test that protected endpoint rejects unauthenticated requests

```bash
# Should return 403 Forbidden
curl -X POST http://127.0.0.1:8000/api/v1/sensors/ingest \
  -H "Content-Type: application/json" \
  -d '{"ph_feed": 7.2}'

# Expected response:
# {"detail":"Invalid or missing API key. Set X-API-Key header."}
```

### 7.2 Test that the correct key is accepted

```bash
# Should return 200 OK
curl -X POST http://127.0.0.1:8000/api/v1/sensors/ingest \
  -H "Content-Type: application/json" \
  -H "X-API-Key: aquamonitor-secret-key-2024" \
  -d '{"ph_feed": 7.2, "tds_feed": 300, "pressure_feed": 4.0}'

# Expected response:
# {"status":"ok","timestamp":"..."}
```

### 7.3 Test that public endpoints remain open

```bash
# Should return 200 OK (no API key needed)
curl http://127.0.0.1:8000/api/v1/sensors/live
```

---

## 8. Future Improvements

| Feature | Effort | Benefit |
|---|---|---|
| Firebase Authentication (JWT tokens per user) | High | Multi-user support, role-based access |
| API key rotation (multiple valid keys) | Medium | Zero-downtime key changes |
| Rate limiting (slowapi) | Low | Prevent DoS |
| HTTPS enforcement (redirect HTTP → HTTPS) | Low | Encrypted traffic |
| Audit log (log each /ingest call) | Medium | Traceability |

For a single-operator lab deployment, the current API key approach is sufficient and production-ready.
