# 🌊 AquaMonitor — Phases 8–11 Implementation Plan

## Overview

Hardware + Firebase + Dashboard are confirmed working. We now focus on:
**Mobile polish → Security → Cloud deployment → Final documentation**

---

## Phase 8 — Mobile App Polish & Packaging

### 8.1 Bug Fixes (Quick wins)
#### [MODIFY] [main.py](file:///d:/Projects/Arduino%20Projects/Water%20Desalination/mobile/src/main.py)
- Replace deprecated `NavigationDestination` → `NavigationBarDestination`
- Add **Alerts tab** (new 5th nav item) and **Predictions tab** (new 6th nav item)
- Make `update_ui_loop` also refresh the active Alerts/Predictions page when shown
- Fix BLE retry logic: currently crashes with `CancelledError` when no hardware found — add graceful retry with a user-visible status

### 8.2 New: Alerts Page
#### [NEW] [alerts.py](file:///d:/Projects/Arduino%20Projects/Water%20Desalination/mobile/src/pages/alerts.py)
- Fetches `/api/v1/alerts/history` from the FastAPI backend
- Displays a scrollable list of alert cards: severity badge (red/orange/yellow), parameter name, value vs threshold, timestamp
- Falls back gracefully when offline (shows last known alerts from SQLite)

### 8.3 New: Predictions Page
#### [NEW] [predictions.py](file:///d:/Projects/Arduino%20Projects/Water%20Desalination/mobile/src/pages/predictions.py)
- Fetches `/api/v1/predict/run` from the FastAPI backend
- Shows:
  - Water Quality Score gauge (0–100)
  - Membrane Status card (Good / Warning / Critical)
  - Days until membrane replacement estimate
  - Feature importance bar chart (top 5 factors)

### 8.4 Android APK Build Preparation
#### [NEW] [requirements-mobile.txt](file:///d:/Projects/Arduino%20Projects/Water%20Desalination/mobile/requirements-mobile.txt)
- Pin exact dependency versions for reproducible APK builds (`flet==0.24.x`, `bleak`, etc.)

> [!IMPORTANT]
> `flet build apk` requires Flutter SDK and Android SDK installed. We will prepare the build config, and you run the build command manually. I will guide you through the one-time SDK setup.

---

## Phase 9 — Security & Authentication

### 9.1 Firebase Authentication on the Mobile App
#### [NEW] [auth.py](file:///d:/Projects/Arduino%20Projects/Water%20Desalination/mobile/src/pages/auth.py)
- A login screen shown before the main app
- Email + password login via Firebase REST Auth API (`/v1/accounts:signInWithPassword`)
- Token stored in SQLite `settings` table (key: `auth_token`, `auth_email`)
- Subsequent app launches auto-login if token is valid

#### [MODIFY] [main.py](file:///d:/Projects/Arduino%20Projects/Water%20Desalination/mobile/src/main.py)
- Check if `auth_token` exists on startup; if not, show `AuthPage` instead of the main nav

### 9.2 API Key Protection on the Backend
#### [MODIFY] [config.py](file:///d:/Projects/Arduino%20Projects/Water%20Desalination/backend/app/core/config.py)
- Add `API_KEY: str` field (loaded from `.env`)

#### [NEW] [security.py](file:///d:/Projects/Arduino%20Projects/Water%20Desalination/backend/app/core/security.py)
- FastAPI dependency `verify_api_key(x_api_key: str = Header(...))` 
- Applied to all non-public endpoints (`/ingest`, `/predict`, `/chat`)

#### [MODIFY] [main.py](file:///d:/Projects/Arduino%20Projects/Water%20Desalination/backend/main.py)
- Tighten CORS: replace `allow_origins=["*"]` with specific allowed origins

> [!WARNING]
> The Gemini API key is currently hardcoded in `config.py` in plaintext. This will be moved to `.env` only.

---

## Phase 10 — Cloud Deployment

> [!IMPORTANT]
> **Vercel does NOT support long-running Python processes well** (10s max execution time, no persistent connections). Since your backend uses Firebase Admin SDK with persistent connections, we will deploy to **Railway** instead — which is free, fully supports Python/FastAPI, and has no execution timeout.

### 10.1 Railway Deployment Config
#### [NEW] [Procfile](file:///d:/Projects/Arduino%20Projects/Water%20Desalination/backend/Procfile)
- `web: uvicorn main:app --host 0.0.0.0 --port $PORT`

#### [MODIFY] [requirements.txt](file:///d:/Projects/Arduino%20Projects/Water%20Desalination/backend/requirements.txt)
- Add `pydantic-settings` (currently missing but used in config.py)
- Pin versions for deterministic Railway builds

#### [NEW] [railway.json](file:///d:/Projects/Arduino%20Projects/Water%20Desalination/backend/railway.json)
- Railway deployment configuration (build command, start command, env vars)

### 10.2 Update All Clients to Use Cloud URL
#### [MODIFY] [settings.py](file:///d:/Projects/Arduino%20Projects/Water%20Desalination/mobile/src/pages/settings.py)
- Change default `api_url` to the Railway deployment URL once deployed

---

## Phase 11 — Documentation & Final Demo

### 11.1 README.md
#### [NEW] [README.md](file:///d:/Projects/Arduino%20Projects/Water%20Desalination/README.md)
- Project overview with system architecture diagram
- Hardware BOM with links and prices
- Setup instructions for all 4 components (firmware, backend, dashboard, mobile)
- Screenshots of live dashboard and mobile app
- Deployment instructions

### 11.2 Demo Video Preparation
- Script a short walkthrough: Node → Firebase → Dashboard → Mobile History → Alerts → Predictions

---

## Open Questions

> [!IMPORTANT]
> **Do you want user login (Phase 9)?** Firebase Auth adds a login screen before the app. If this is a personal/local tool only used by you, we can skip auth and just add the API key protection on the backend.

> [!IMPORTANT]
> **Railway vs Vercel?** I recommend Railway (free tier, no timeout limits). Do you agree, or do you have a preference?

> [!IMPORTANT]
> **Android APK?** Do you have Flutter SDK installed? If not, do you want to install it and build the APK, or skip for now and just ensure the desktop app is polished?

---

## Execution Order

```
Phase 8 (mobile fixes + alerts + predictions pages)
    ↓
Phase 9 (API key security → optional auth)
    ↓
Phase 10 (Railway deploy → update mobile API URL)
    ↓
Phase 11 (README + screenshots + demo)
```

**Total estimated work: ~3–4 sessions**
