"""
/api/v1/sensors — Ingest and retrieve live sensor data from Firebase
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Union
from datetime import datetime, timezone
from app.core.firebase import get_db_ref
from app.core.security import verify_api_key

router = APIRouter()

DEVICE_ID = "device_001"


class SensorPayload(BaseModel):
    # Node 1 — Water Quality (full schema matching Firebase)
    ph: Optional[float] = None
    ph_feed: Optional[float] = None
    ph_permeate: Optional[float] = 0.0
    tds: Optional[float] = None
    tds_feed: Optional[float] = None
    tds_permeate: Optional[float] = 0.0
    turbidity: Optional[float] = None
    turbidity_feed: Optional[float] = None
    temperature_feed: Optional[float] = 0.0
    temperature_permeate: Optional[float] = 0.0
    pressure: Optional[float] = None
    pressure_feed: Optional[float] = None
    flow_rate: Optional[float] = None
    flow_rate_feed: Optional[float] = None
    flow_rate_permeate: Optional[float] = 0.0
    recovery_rate: Optional[float] = 0.0
    rejection_rate: Optional[float] = 0.0
    level_feed_full: bool = False
    level_product_full: bool = False
    water_level_feed_tank: Optional[float] = None
    water_level_product_tank: Optional[float] = None
    pump_status: Union[bool, str] = False
    valve_status: Union[bool, str] = False
    uptime_seconds: int = 0

    # Node 2 — Environment
    tank1_level_cm: float = 0.0
    tank2_level_cm: float = 0.0
    ambient_temp: float = 0.0
    ambient_humidity: float = 0.0
    gas_1_ppm: float = 0.0
    gas_2_ppm: float = 0.0
    water_temp_1: float = 0.0
    water_temp_2: float = 0.0
    fan_1_status: bool = False
    fan_2_status: bool = False
    fan_3_status: bool = False

    def normalized(self) -> dict:
        """Return a normalized dict with consistent field names for Firebase/dashboard."""
        d = self.model_dump()
        # Normalize aliases: prefer _feed suffixed names, fall back to short names
        d["ph_feed"]        = self.ph_feed        if self.ph_feed        is not None else (self.ph or 0.0)
        d["tds_feed"]       = self.tds_feed       if self.tds_feed       is not None else (self.tds or 0.0)
        d["turbidity_feed"] = self.turbidity_feed  if self.turbidity_feed is not None else (self.turbidity or 0.0)
        d["pressure_feed"]  = self.pressure_feed  if self.pressure_feed  is not None else (self.pressure or 0.0)
        d["flow_rate_feed"] = self.flow_rate_feed if self.flow_rate_feed is not None else (self.flow_rate or 0.0)
        d["water_level_feed_tank"]    = self.water_level_feed_tank    if self.water_level_feed_tank    is not None else (100 if self.level_feed_full    else 0)
        d["water_level_product_tank"] = self.water_level_product_tank if self.water_level_product_tank is not None else (100 if self.level_product_full else 0)
        # Normalize pump/valve: accept bool (from ESP32) or string (from mobile/Firebase)
        if isinstance(self.pump_status, bool):
            d["pump_status"]  = "running" if self.pump_status  else "stopped"
        else:
            d["pump_status"]  = self.pump_status  # already a string like "running"
        if isinstance(self.valve_status, bool):
            d["valve_status"] = "open"    if self.valve_status else "closed"
        else:
            d["valve_status"] = self.valve_status  # already a string like "open"
        return d


@router.post("/ingest", dependencies=[Depends(verify_api_key)])
def ingest_sensor_data(payload: SensorPayload):
    """
    Receives aggregated sensor data from the Main Hub (or mobile BLE sync)
    and writes it to Firebase Realtime Database.
    """
    try:
        timestamp = datetime.now(timezone.utc).isoformat()
        data = payload.normalized()
        data["timestamp"] = timestamp

        # Write to live_data (overwritten every cycle)
        get_db_ref(f"/devices/{DEVICE_ID}/live_data").set(data)

        # Append to historical logs
        get_db_ref(f"/historical_logs/{DEVICE_ID}").push(data)

        return {"status": "ok", "timestamp": timestamp}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/live")
def get_live_data():
    """
    Returns the latest live sensor data snapshot from Firebase.
    """
    try:
        data = get_db_ref(f"/devices/{DEVICE_ID}/live_data").get()
        if data is None:
            return {"status": "no_data"}
        return {"status": "ok", "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
def get_history(limit: int = 50):
    """
    Returns the last N historical readings for charting.
    """
    try:
        data = get_db_ref(f"/historical_logs/{DEVICE_ID}").limit_to_last(limit).get()
        if data is None:
            return {"status": "no_data", "readings": []}
        readings = list(data.values()) if isinstance(data, dict) else []
        # Sort by timestamp
        readings.sort(key=lambda x: x.get("timestamp", ""), reverse=False)
        return {"status": "ok", "readings": readings}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
