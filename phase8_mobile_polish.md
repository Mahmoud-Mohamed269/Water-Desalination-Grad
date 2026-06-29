# 📱 Phase 8 — Mobile App Polish & New Features

This phase covers all improvements made to the Flet mobile app after initial hardware validation in Phase 6. The app gains an Alerts page, in-dashboard ML predictions, and a fix for Flet API deprecations.

---

## 📋 Table of Contents
1. [Objectives](#1-objectives)
2. [What Was Fixed](#2-what-was-fixed)
3. [New: Alerts Page](#3-new-alerts-page)
4. [New: ML Predictions on Dashboard](#4-new-ml-predictions-on-dashboard)
5. [Navigation Bar Restructure](#5-navigation-bar-restructure)
6. [File Reference](#6-file-reference)
7. [Testing Checklist](#7-testing-checklist)
8. [Common Errors](#8-common-errors)

---

## 1. Objectives

| # | Objective | Priority |
|---|---|---|
| 1 | Fix deprecated Flet `NavigationDestination` API | 🔴 Critical |
| 2 | Add Alerts page pulling from FastAPI backend | 🔴 Critical |
| 3 | Add ML Analysis section to Dashboard | 🟠 High |
| 4 | Auto-refresh Alerts on tab switch | 🟡 Medium |
| 5 | Improve BLE error handling | 🟡 Medium |

---

## 2. What Was Fixed

### 2.1 Deprecated NavigationDestination

**Flet ≥ 0.23.0** deprecated `ft.NavigationDestination` in favour of `ft.NavigationBarDestination`. The old code produced this warning on every launch:

```
DeprecationWarning: NavigationDestination() is deprecated in version 0.23.0
and will be removed in version 0.26.0. Use NavigationBarDestination class instead.
```

**Fix in `mobile/src/main.py`:**

```python
# ❌ Old (deprecated)
ft.NavigationDestination(icon=ft.icons.DASHBOARD_OUTLINED, label="Live")

# ✅ New
ft.NavigationBarDestination(icon=ft.icons.DASHBOARD_OUTLINED,
                             selected_icon=ft.icons.DASHBOARD,
                             label="Live")
```

### 2.2 BLE Error Handling

The `RealBLEClient` threw `CancelledError` when Bluetooth was off or no device found. The existing `try/except` inside `connect()` already catches this via a broad `except Exception`, but the error still propagated because `page.run_task()` does not suppress exceptions from coroutines. This is an async cancellation from the OS Bluetooth stack — it is expected when no hardware is nearby and does **not** crash the app.

---

## 3. New: Alerts Page

**File:** `mobile/src/pages/alerts.py`

### 3.1 What It Shows

The Alerts page calls `GET /api/v1/alerts/history` on the FastAPI backend and displays the returned alert list sorted newest-first.

Each alert card shows:
- **Severity badge** — colour-coded pill (CRITICAL = red, WARNING = orange, INFO = blue)
- **Sensor name** — e.g. "TDS", "pH", "Pressure"
- **Message** — e.g. "TDS too high: 650 ppm"
- **Timestamp** — formatted as `YYYY-MM-DD  HH:MM:SS`

When the system is healthy and no alerts exist, a green ✓ icon with "No alerts — system is healthy!" is shown.

### 3.2 Severity Colour Reference

| Severity | Colour | Background | Icon |
|---|---|---|---|
| `critical` | `#ef4444` (red) | `#2d0a0a` | `ERROR` |
| `warning` | `#f97316` (orange) | `#2d1500` | `WARNING_AMBER` |
| `info` | `#3b82f6` (blue) | `#0a1a2d` | `INFO` |

### 3.3 How Refresh Works

`update_data()` is called automatically by `main.py` every time the user taps the **Alerts** tab (`index == 2` in `on_nav_change`). The user can also manually tap the ↻ refresh button.

The HTTP call is synchronous (`requests.get`) — this is acceptable because Flet runs UI updates on the main thread and HTTP calls on worker threads. For future improvement, consider wrapping in `page.run_thread()`.

### 3.4 Offline Behaviour

When the backend is unreachable, the status label turns red with the error message. Previously fetched alerts remain displayed from the `self._alerts` cache (in-memory for the session). Full offline persistence of alerts to SQLite is a future enhancement.

---

## 4. New: ML Predictions on Dashboard

**File:** `mobile/src/pages/dashboard.py`

### 4.1 ML Analysis Section

Added at the bottom of the scrollable dashboard column:

```
─────────────────────────────────
ML Analysis                    [↻]
┌─────────────────┐ ┌──────────────────┐
│ Water Quality   │ │ Membrane         │
│ Good            │ │ Warning          │
│ 94.2% confidence│ │ 68.1% confidence │
└─────────────────┘ └──────────────────┘
✓ Prediction complete
─────────────────────────────────
```

### 4.2 Endpoint Called

`GET /api/v1/predict/run` — this endpoint was added in Phase 10. It automatically:
1. Fetches the latest `live_data` snapshot from Firebase
2. Derives all 13 ML feature values (TDS Reduction, pH Change, etc.)
3. Runs both Random Forest models
4. Returns labels + confidence percentages

### 4.3 Label Colour Mapping

**Water Quality:**
| Label | Colour |
|---|---|
| good | `#22c55e` (green) |
| acceptable | `#84cc16` (lime) |
| poor | `#f97316` (orange) |
| bad | `#ef4444` (red) |

**Membrane Status:**
| Label | Colour |
|---|---|
| good | `#22c55e` (green) |
| warning | `#f97316` (orange) |
| critical / fouled | `#ef4444` (red) |

### 4.4 When to Run

The prediction is **not** run automatically on a timer (ML inference adds load to the backend). The user taps ↻ on demand. Typical use: tap once when you sit down to review the system status.

---

## 5. Navigation Bar Restructure

The nav bar was restructured from 4 to 5 destinations:

| Index | Old | New |
|---|---|---|
| 0 | Live | Live (unchanged) |
| 1 | History | History (unchanged) |
| 2 | WiFi | **Alerts** (new) |
| 3 | Settings | WiFi (shifted) |
| 4 | — | Settings (shifted) |

`on_nav_change` in `main.py` was updated to call `page_alerts.update_data()` when index 2 is selected.

---

## 6. File Reference

| File | Change Type | Description |
|---|---|---|
| `mobile/src/main.py` | Modified | Fixed deprecation, added Alerts tab, updated nav change handler |
| `mobile/src/pages/alerts.py` | **New** | Full alerts page with severity-coded cards |
| `mobile/src/pages/dashboard.py` | Modified | Added ML Analysis section with Water Quality + Membrane cards |
| `mobile/src/pages/history.py` | Modified (Phase earlier) | Fixed `update()` timing, added metric dropdown |

---

## 7. Testing Checklist

### Virtual BLE Mode (no hardware)
- [ ] Launch app → no deprecation warnings in terminal
- [ ] Live tab shows sensor data updating every second
- [ ] History tab shows pH chart and scrollable readings table
- [ ] Alerts tab loads, shows "No alerts" or pulls real alerts from backend
- [ ] Tapping ↻ on Alerts refreshes the list
- [ ] Dashboard ML section: tap ↻ → shows water quality + membrane status
- [ ] Settings save → status message appears green

### Real BLE Mode
- [ ] App connects to AquaMonitor ESP32 within 10 seconds
- [ ] Live data reflects actual sensor readings from Node 1
- [ ] History shows real readings accumulating in SQLite
- [ ] Alerts populate when TDS > 500 ppm or pH out of range

---

## 8. Common Errors

| Error | Cause | Fix |
|---|---|---|
| `DeprecationWarning: NavigationDestination` | Old Flet version | Upgrade: `pip install --upgrade flet` |
| `CancelledError` in terminal | Bluetooth off / no BLE device | Expected — enable virtual BLE in Settings |
| ML card shows "Offline" | Backend not running | Start backend: `uvicorn main:app --reload` in `backend/` |
| Alerts show "Server error 500" | Firebase not initialized | Check `serviceAccountKey.json` exists and `.env` is set |
