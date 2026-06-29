"""
/api/v1/predict — ML Prediction endpoints
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.ml_service import predict_water_quality
from app.core.firebase import get_db_ref

router = APIRouter()

DEVICE_ID = "device_001"


class PredictionRequest(BaseModel):
    pH_before: float
    TDS_before: float
    Turbidity_before: float
    Temperature_before: float
    Pressure_before: float
    pH_after: float
    TDS_after: float
    Turbidity_after: float
    Temperature_after: float
    Efficiency: float
    TDS_Reduction: float
    Turbidity_Reduction: float
    pH_Change: float


@router.post("/")
def predict(request: PredictionRequest):
    """
    Accepts raw sensor features and returns water quality + membrane status predictions.
    """
    try:
        features = [
            request.pH_before,
            request.TDS_before,
            request.Turbidity_before,
            request.Temperature_before,
            request.Pressure_before,
            request.pH_after,
            request.TDS_after,
            request.Turbidity_after,
            request.Temperature_after,
            request.Efficiency,
            request.TDS_Reduction,
            request.Turbidity_Reduction,
            request.pH_Change,
        ]
        result = predict_water_quality(features)
        return {"status": "ok", "predictions": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/run")
def run_prediction_from_live():
    """
    Fetches the latest live sensor snapshot from Firebase and automatically
    derives all 13 ML features, then returns predictions.
    No manual input required — call this from the mobile app / dashboard.
    """
    try:
        data = get_db_ref(f"/devices/{DEVICE_ID}/live_data").get()
        if not data:
            raise HTTPException(status_code=404,
                                detail="No live data in Firebase yet.")

        # ── Extract raw readings ────────────────────────────────
        ph_feed         = float(data.get("ph_feed",          7.0))
        ph_permeate     = float(data.get("ph_permeate",      7.0))
        tds_feed        = float(data.get("tds_feed",       300.0))
        tds_permeate    = float(data.get("tds_permeate",    30.0))
        turb_feed       = float(data.get("turbidity_feed",   1.0))
        temp_feed       = float(data.get("temperature_feed", 25.0))
        temp_permeate   = float(data.get("temperature_permeate", temp_feed))
        pressure_feed   = float(data.get("pressure_feed",    4.0))
        recovery_rate   = float(data.get("recovery_rate",   50.0))

        # ── Derive computed features ────────────────────────────
        tds_reduction = (
            (tds_feed - tds_permeate) / tds_feed * 100
            if tds_feed > 0 else 0.0
        )
        # Approximate permeate turbidity from TDS rejection ratio
        rejection_fraction = tds_reduction / 100.0
        turb_permeate = turb_feed * max(0.0, 1.0 - rejection_fraction)
        turbidity_reduction = (
            (turb_feed - turb_permeate) / turb_feed * 100
            if turb_feed > 0 else 0.0
        )
        ph_change = ph_permeate - ph_feed

        features = [
            ph_feed, tds_feed, turb_feed, temp_feed, pressure_feed,
            ph_permeate, tds_permeate, turb_permeate, temp_permeate,
            recovery_rate, tds_reduction, turbidity_reduction, ph_change,
        ]

        result = predict_water_quality(features)

        return {
            "status": "ok",
            "predictions": result,
            "derived_features": {
                "pH_before":           ph_feed,
                "TDS_before":          tds_feed,
                "Turbidity_before":    turb_feed,
                "Temperature_before":  temp_feed,
                "Pressure_before":     pressure_feed,
                "pH_after":            ph_permeate,
                "TDS_after":           tds_permeate,
                "Turbidity_after":     round(turb_permeate, 3),
                "Temperature_after":   temp_permeate,
                "Efficiency":          recovery_rate,
                "TDS_Reduction":       round(tds_reduction, 2),
                "Turbidity_Reduction": round(turbidity_reduction, 2),
                "pH_Change":           round(ph_change, 3),
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
