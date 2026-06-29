import pandas as pd
import numpy as np
import random

# عدد السجلات
N = 10000

data = []

for _ in range(N):

    # -------------------------
    # Raw Water (Before Treatment)
    # -------------------------
    ph_before = round(random.uniform(6.5, 8.8), 2)

    tds_before = round(random.uniform(500, 5000), 0)

    turb_before = round(random.uniform(1, 50), 2)

    temp_before = round(random.uniform(15, 40), 1)

    pressure = round(random.uniform(1, 6), 2)

    # -------------------------
    # Membrane Condition
    # -------------------------
    membrane_status = random.choice([
        "Healthy",
        "Needs Cleaning",
        "Replace"
    ])

    if membrane_status == "Healthy":
        removal_rate = random.uniform(0.85, 0.95)

    elif membrane_status == "Needs Cleaning":
        removal_rate = random.uniform(0.60, 0.85)

    else:
        removal_rate = random.uniform(0.30, 0.60)

    # -------------------------
    # After Treatment
    # -------------------------
    tds_after = round(tds_before * (1 - removal_rate), 0)

    turb_after = round(
        turb_before * random.uniform(0.05, 0.30),
        2
    )

    ph_after = round(
        7 + random.uniform(-0.5, 0.5),
        2
    )

    temp_after = round(
        temp_before + random.uniform(-1, 1),
        1
    )

    # -------------------------
    # Efficiency
    # -------------------------
    efficiency = round(
        ((tds_before - tds_after) / tds_before) * 100,
        2
    )

    # -------------------------
    # Water Quality Label
    # -------------------------
    if tds_after < 500 and turb_after < 1:
        water_status = "Excellent"

    elif tds_after < 1000 and turb_after < 3:
        water_status = "Acceptable"

    else:
        water_status = "Poor"

    # -------------------------
    # Feature Engineering
    # -------------------------
    tds_reduction = round(
        tds_before - tds_after,
        0
    )

    turb_reduction = round(
        turb_before - turb_after,
        2
    )

    ph_change = round(
        ph_after - ph_before,
        2
    )

    # -------------------------
    # Store Row
    # -------------------------
    data.append([
        ph_before,
        tds_before,
        turb_before,
        temp_before,
        pressure,

        ph_after,
        tds_after,
        turb_after,
        temp_after,

        efficiency,

        tds_reduction,
        turb_reduction,
        ph_change,

        water_status,
        membrane_status
    ])

# -------------------------
# Create DataFrame
# -------------------------
columns = [
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
    "pH_Change",

    "Water_Status",
    "Membrane_Status"
]

df = pd.DataFrame(data, columns=columns)

# -------------------------
# Save CSV
# -------------------------
df.to_csv(
    "desalination_dataset.csv",
    index=False
)

print("Dataset generated successfully!")
print(df.head())