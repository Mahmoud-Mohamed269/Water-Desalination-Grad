import pandas as pd
import joblib

# Load Models
water_model = joblib.load("water_quality_rf.pkl")
water_encoder = joblib.load("water_quality_encoder.pkl")

membrane_model = joblib.load("membrane_status_rf.pkl")
membrane_encoder = joblib.load("membrane_encoder.pkl")

# Example Sensor Reading
sample = pd.DataFrame([{
    "pH_before": 8.0,
    "TDS_before": 2500,
    "Turbidity_before": 8,
    "Temperature_before": 25,
    "Pressure_before": 3,

    "pH_after": 7.2,
    "TDS_after": 300,
    "Turbidity_after": 0.5,
    "Temperature_after": 24.5,

    "Efficiency": 88,

    "TDS_Reduction": 2200,
    "Turbidity_Reduction": 7.5,
    "pH_Change": -0.8
}])

# Predict Water Quality
water_pred = water_model.predict(sample)

water_result = water_encoder.inverse_transform(
    water_pred
)

# Predict Membrane Status
membrane_pred = membrane_model.predict(sample)

membrane_result = membrane_encoder.inverse_transform(
    membrane_pred
)

print("Water Quality:", water_result[0])
print("Membrane Status:", membrane_result[0])