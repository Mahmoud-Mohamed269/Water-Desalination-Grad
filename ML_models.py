import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

# ==========================================
# Load Dataset
# ==========================================
df = pd.read_csv("desalination_dataset.csv")

print("Dataset Shape:")
print(df.shape)

# ==========================================
# Features & Targets
# ==========================================

FEATURES = [
    "pH_before",
    "TDS_before",
    "Turbidity_before",
    "Temperature_before",
    "Pressure_before",

    "pH_after",
    "TDS_after",
    "Turbidity_after",
    "Temperature_after",

    "Efficiency",

    "TDS_Reduction",
    "Turbidity_Reduction",
    "pH_Change"
]

X = df[FEATURES]

# ==================================================
# MODEL 1 : Water Quality Prediction
# ==================================================

y_water = df["Water_Status"]

water_encoder = LabelEncoder()

y_water_encoded = water_encoder.fit_transform(y_water)

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y_water_encoded,
    test_size=0.20,
    random_state=42,
    stratify=y_water_encoded
)

water_model = RandomForestClassifier(
    n_estimators=200,
    max_depth=None,
    random_state=42,
    n_jobs=-1
)

water_model.fit(X_train, y_train)

water_predictions = water_model.predict(X_test)

water_accuracy = accuracy_score(
    y_test,
    water_predictions
)

print("\nWater Quality Model Accuracy:")
print(water_accuracy)

print("\nClassification Report:")
print(
    classification_report(
        y_test,
        water_predictions,
        target_names=water_encoder.classes_
    )
)

# Save model
joblib.dump(
    water_model,
    "water_quality_rf.pkl"
)

joblib.dump(
    water_encoder,
    "water_quality_encoder.pkl"
)

# ==================================================
# MODEL 2 : Membrane Health Prediction
# ==================================================

y_membrane = df["Membrane_Status"]

membrane_encoder = LabelEncoder()

y_membrane_encoded = membrane_encoder.fit_transform(
    y_membrane
)

X_train2, X_test2, y_train2, y_test2 = train_test_split(
    X,
    y_membrane_encoded,
    test_size=0.20,
    random_state=42,
    stratify=y_membrane_encoded
)

membrane_model = RandomForestClassifier(
    n_estimators=200,
    max_depth=None,
    random_state=42,
    n_jobs=-1
)

membrane_model.fit(
    X_train2,
    y_train2
)

membrane_predictions = membrane_model.predict(
    X_test2
)

membrane_accuracy = accuracy_score(
    y_test2,
    membrane_predictions
)

print("\nMembrane Status Model Accuracy:")
print(membrane_accuracy)

print("\nClassification Report:")
print(
    classification_report(
        y_test2,
        membrane_predictions,
        target_names=membrane_encoder.classes_
    )
)

# Save model
joblib.dump(
    membrane_model,
    "membrane_status_rf.pkl"
)

joblib.dump(
    membrane_encoder,
    "membrane_encoder.pkl"
)

print("\nModels Saved Successfully")