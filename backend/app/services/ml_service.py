"""
ML Service — loads pkl models once at startup and serves predictions.
Uses the same features as ML_models.py:
  pH_before, TDS_before, Turbidity_before, Temperature_before, Pressure_before,
  pH_after, TDS_after, Turbidity_after, Temperature_after,
  Efficiency, TDS_Reduction, Turbidity_Reduction, pH_Change
"""
import joblib
import pandas as pd
from functools import lru_cache
from app.core.config import settings

FEATURE_NAMES = [
    "pH_before", "TDS_before", "Turbidity_before", "Temperature_before",
    "Pressure_before", "pH_after", "TDS_after", "Turbidity_after",
    "Temperature_after", "Efficiency", "TDS_Reduction",
    "Turbidity_Reduction", "pH_Change"
]


@lru_cache(maxsize=1)
def _load_models():
    water_model = joblib.load(settings.WATER_QUALITY_MODEL_PATH)
    water_encoder = joblib.load(settings.WATER_QUALITY_ENCODER_PATH)
    membrane_model = joblib.load(settings.MEMBRANE_MODEL_PATH)
    membrane_encoder = joblib.load(settings.MEMBRANE_ENCODER_PATH)
    return water_model, water_encoder, membrane_model, membrane_encoder


def predict_water_quality(features: list[float]) -> dict:
    """
    features order: pH_before, TDS_before, Turbidity_before, Temperature_before,
                    Pressure_before, pH_after, TDS_after, Turbidity_after,
                    Temperature_after, Efficiency, TDS_Reduction,
                    Turbidity_Reduction, pH_Change
    """
    water_model, water_encoder, membrane_model, membrane_encoder = _load_models()

    # Use a named DataFrame to match training column names — no sklearn warnings
    df = pd.DataFrame([features], columns=FEATURE_NAMES)

    water_pred_encoded = water_model.predict(df)[0]
    water_proba = water_model.predict_proba(df)[0]
    water_label = water_encoder.inverse_transform([water_pred_encoded])[0]

    membrane_pred_encoded = membrane_model.predict(df)[0]
    membrane_proba = membrane_model.predict_proba(df)[0]
    membrane_label = membrane_encoder.inverse_transform([membrane_pred_encoded])[0]

    return {
        "water_quality": {
            "label": water_label,
            "confidence": round(float(max(water_proba)) * 100, 1),
            "probabilities": {
                cls: round(float(p) * 100, 1)
                for cls, p in zip(water_encoder.classes_, water_proba)
            }
        },
        "membrane_status": {
            "label": membrane_label,
            "confidence": round(float(max(membrane_proba)) * 100, 1),
            "probabilities": {
                cls: round(float(p) * 100, 1)
                for cls, p in zip(membrane_encoder.classes_, membrane_proba)
            }
        }
    }

