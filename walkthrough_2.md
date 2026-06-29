# Walkthrough: Adding Pressure Sensor and Fixing Pin Assignments

I have fully implemented the missing pressure sensor logic into Node 1 and fixed several pin mapping inconsistencies across the project. 

## 1. Firmware Updates (`Node1_WaterQuality`)

### Pin Assignments Fixed (`config.h`)
The pressure sensor is wired to an analog port, but it was originally omitted from the pin mapping. It was added to `GPIO33`, but doing so correctly meant shifting other pins so that they all remained on the WiFi-safe **ADC1** group and matched the hardware diagram in Phase 2.

- **`PIN_PRESSURE_FEED`** was added to `GPIO33` (ADC1_CH5).
- **`PIN_PH_PERMEATE`** was moved to `GPIO36` (VP/ADC1_CH0).
- **`PIN_TDS_PERMEATE`** was moved to `GPIO39` (VN/ADC1_CH3).
- Added a note clarifying that while `GPIO27` (Flow Permeate) is an ADC2 pin, it is perfectly safe because we are using it purely as a digital hardware interrupt, not for `analogRead()`.

### Pressure Sensor Implementation
The pressure sensor (G1/4 analog, 0–12 bar) is now fully integrated:
1. **Calibration (`config.h`):** Added `PRESSURE_OFFSET_V` (0.5V), `PRESSURE_SCALE_V` (4.5V), and a voltage divider ratio `VDIV_RATIO_PRESSURE` (1.5x) to recover the 5V signal from the 10k/20k voltage divider.
2. **Reading (`sensors.cpp`):** Implemented `readPressure()`, which scales the ADC voltage back to 0-12 bar linearly. It is now called on every cycle inside `readAllSensors()`.
3. **Data Structures (`sensors.h`):** The `SensorReading` struct now has a `pressure_feed` float. The `SensorHealth` struct tracks the `pressure` string state.

### Alert Engine (`alert_engine.cpp`)
Pressure is now a critical safety metric:
- Created a cooldown timer `lastAlertTime_Pressure`.
- Evaluates `pressure_feed` against `ALERT_PRESSURE_MAX` (8 bar, Warning) and `ALERT_PRESSURE_CRITICAL` (10 bar, Critical).

### Firebase Integration (`firebase_client.cpp`)
- `pressure_feed` is now included in the `live_data` snapshot pushed every 5 seconds.
- `pressure_feed` is now saved in the `historical_logs` array.
- The `sensor_health` object pushed to `system_status` now includes the `pressure` health status.

*(Firmware version bumped to **1.1.0** in `Node1_WaterQuality.ino` to reflect the complete 8-sensor support).*

---

## 2. Documentation Sync

All four phase documents were updated to ensure they perfectly match the firmware:

- **[Phase 1](file:///d:/Projects/Arduino%20Projects/Water%20Desalination/phase1_requirements_and_architecture.md):** Fixed the pin table, explicitly listing Feed/Permeate splits. Updated the Firebase `live_data` JSON schema to include `pressure_feed` and properly format the arrays (and removed a stray double-comma syntax error).
- **[Phase 2](file:///d:/Projects/Arduino%20Projects/Water%20Desalination/phase2_hardware_design.md):** Corrected the hardware wiring diagram (section 9) and pin table to match the new GPIO32/33/34/35/36/39 mappings. Fixed the file reference paths (which were incorrectly pointing to `ESP_Sensors/` instead of `Node1_WaterQuality/`).
- **[Phase 3](file:///d:/Projects/Arduino%20Projects/Water%20Desalination/phase3_firmware_development.md):** Added pressure sensor testing to the validation checklist and explicitly listed pressure in the Node 1 logic section.
- **[Phase 4](file:///d:/Projects/Arduino%20Projects/Water%20Desalination/phase4_backend_development.md):** Added `pressure_feed` to the `POST /api/v1/sensors/ingest` FastAPI payload example to ensure the backend expects the new data.
