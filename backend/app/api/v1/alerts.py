"""
/api/v1/alerts — Retrieve and write system alerts in Firebase
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime, timezone
from app.core.firebase import get_db_ref

router = APIRouter()
DEVICE_ID = "device_001"

# Sensor safety thresholds
THRESHOLDS = {
    "ph_min": 6.5,
    "ph_max": 8.5,
    "tds_max": 500,      # ppm — WHO drinking water limit
    "turbidity_max": 4,  # NTU — WHO limit
    "pressure_max": 5.5, # bar — operational max
    "gas_1_max": 1000,   # ppm — example limit
    "gas_2_max": 1000,
    "ambient_temp_max": 45.0,  # °C
}


class SensorSnapshot(BaseModel):
    ph: float
    tds: float
    turbidity: float
    pressure: float
    gas_1_ppm: float = 0.0
    gas_2_ppm: float = 0.0
    ambient_temp: float = 0.0


@router.post("/evaluate")
def evaluate_alerts(snapshot: SensorSnapshot):
    """
    Evaluates sensor readings against thresholds and writes alerts to Firebase.
    Returns a list of active alerts.
    """
    active_alerts = []
    timestamp = datetime.now(timezone.utc).isoformat()

    checks = [
        ("pH", snapshot.ph < THRESHOLDS["ph_min"] or snapshot.ph > THRESHOLDS["ph_max"],
         f"pH out of range: {snapshot.ph:.2f}", "warning"),
        ("TDS", snapshot.tds > THRESHOLDS["tds_max"],
         f"TDS too high: {snapshot.tds:.0f} ppm", "critical"),
        ("Turbidity", snapshot.turbidity > THRESHOLDS["turbidity_max"],
         f"Turbidity too high: {snapshot.turbidity:.1f} NTU", "warning"),
        ("Pressure", snapshot.pressure > THRESHOLDS["pressure_max"],
         f"Pressure critical: {snapshot.pressure:.2f} bar", "critical"),
        ("Gas1", snapshot.gas_1_ppm > THRESHOLDS["gas_1_max"],
         f"Gas sensor 1 alert: {snapshot.gas_1_ppm:.0f} ppm", "critical"),
        ("Gas2", snapshot.gas_2_ppm > THRESHOLDS["gas_2_max"],
         f"Gas sensor 2 alert: {snapshot.gas_2_ppm:.0f} ppm", "critical"),
        ("Temperature", snapshot.ambient_temp > THRESHOLDS["ambient_temp_max"],
         f"Ambient temperature critical: {snapshot.ambient_temp:.1f}°C", "warning"),
    ]

    for sensor, triggered, message, severity in checks:
        if triggered:
            alert = {
                "sensor": sensor,
                "message": message,
                "severity": severity,
                "timestamp": timestamp
            }
            active_alerts.append(alert)
            # Write to Firebase
            try:
                get_db_ref(f"/alerts/{DEVICE_ID}").push(alert)
            except Exception:
                pass  # Non-blocking; local evaluation still continues

    return {
        "status": "ok",
        "alert_count": len(active_alerts),
        "alerts": active_alerts
    }


@router.get("/history")
def get_alert_history(limit: int = 20):
    """
    Returns recent alerts from Firebase.
    """
    try:
        data = get_db_ref(f"/alerts/{DEVICE_ID}").order_by_key().limit_to_last(limit).get()
        alerts = list(data.values()) if data else []
        return {"status": "ok", "alerts": alerts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
