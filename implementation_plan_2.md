# Node 1 & Phase 1–4 Updates — Adding Pressure Sensor + All Missing Sensor Support

## Summary

The project has a **pressure sensor (G1/4 analog)** wired to **GPIO33** and documented throughout Phases 1–4,
but it is completely absent from the Node 1 firmware (`sensors.h`, `sensors.cpp`, `alert_engine.cpp`, `firebase_client.cpp`).
Additionally, the phase documentation files reference the pressure sensor in sensor tables, wiring diagrams, BOM,
and API schemas — all of which need to be verified as consistent.

There is also a critical **pin conflict** to fix: `PIN_FLOW_PERMEATE` is currently set to GPIO27, which is an **ADC2 pin**
and can interfere with WiFi. Since it's used as a digital interrupt (not ADC), it can work — but the comment and phase docs
should document this explicitly.

---

## Open Questions

> [!IMPORTANT]
> **GPIO27 for PIN_FLOW_PERMEATE** — GPIO27 is listed in ADC2, which *cannot be used for analogRead() while WiFi is active*.
> However it IS being used here as a **digital interrupt** (not analogRead), which IS safe. The existing code is fine,
> but the warning in config.h says "ADC2 pins CANNOT be used while WiFi is active" — this could be confusing.
> The plan will add a clarifying comment.

> [!IMPORTANT]
> **DS18B20 Sensor Count** — The firmware uses `readTemperature(0)` for feed and `readTemperature(1)` for permeate,
> implying 2x DS18B20 sensors on the same OneWire bus. The BOM (Phase 2) lists DS18B20 under Node 2, not Node 1.
> Node 1's firmware already has this. No change needed — just documenting the discrepancy.

---

## Proposed Changes

### Node 1 Firmware

#### [MODIFY] [config.h](file:///d:/Projects/Arduino%20Projects/Water%20Desalination/Node1_WaterQuality/config.h)
- Add `PIN_PRESSURE_FEED` definition (GPIO33, already wired correctly)
- Add pressure sensor calibration constants (`PRESSURE_OFFSET_V`, `PRESSURE_SCALE_V`, `PRESSURE_MAX_BAR`)
- Add pressure alert thresholds (`ALERT_PRESSURE_MAX`, `ALERT_PRESSURE_CRITICAL`)
- Fix the ADC2 note to clarify GPIO27 is safe as a digital-only interrupt
- Add `VDIV_RATIO_PRESSURE` (same as turbidity: 1.5f)

#### [MODIFY] [sensors.h](file:///d:/Projects/Arduino%20Projects/Water%20Desalination/Node1_WaterQuality/sensors.h)
- Add `pressure_feed` field to `SensorReading` struct
- Add `pressure` field to `SensorHealth` struct
- Add `readPressure()` function declaration

#### [MODIFY] [sensors.cpp](file:///d:/Projects/Arduino%20Projects/Water%20Desalination/Node1_WaterQuality/sensors.cpp)
- Implement `readPressure(uint8_t pin)` function using voltage-to-bar conversion
- Add `PIN_PRESSURE_FEED` to `readAllSensors()` — set `reading.pressure_feed`
- Add pressure health check in `checkSensorHealth()`

#### [MODIFY] [alert_engine.h](file:///d:/Projects/Arduino%20Projects/Water%20Desalination/Node1_WaterQuality/alert_engine.h)
- Already has correct struct — no change needed (Alert struct is fine)

#### [MODIFY] [alert_engine.cpp](file:///d:/Projects/Arduino%20Projects/Water%20Desalination/Node1_WaterQuality/alert_engine.cpp)
- Add `lastAlertTime_Pressure` cooldown tracker
- Add pressure alert check: warn if > ALERT_PRESSURE_MAX, critical if > ALERT_PRESSURE_CRITICAL
- Initialize pressure cooldown in `alertEngineInit()`

#### [MODIFY] [firebase_client.cpp](file:///d:/Projects/Arduino%20Projects/Water%20Desalination/Node1_WaterQuality/firebase_client.cpp)
- Add `pressure_feed` to `pushLiveData()` JSON
- Add `pressure_feed` to `pushHistoricalLog()` JSON
- Add `pressure` health to `pushSystemStatus()` health JSON

#### [MODIFY] [Node1_WaterQuality.ino](file:///d:/Projects/Arduino%20Projects/Water%20Desalination/Node1_WaterQuality/Node1_WaterQuality.ino)
- Update header comment to include "Pressure" in the sensor list
- Update firmware version to 1.1.0

---

### Phase Documentation Files

#### [MODIFY] [phase1_requirements_and_architecture.md](file:///d:/Projects/Arduino%20Projects/Water%20Desalination/phase1_requirements_and_architecture.md)
- Update Node 1 pin assignment section to include GPIO33 → Pressure Sensor explicitly
- Update Firebase schema `live_data` to include `pressure_feed` field (it already shows `pressure_feed` — verify it matches firmware)
- Update Sensor Specifications table to confirm all 7 sensors are listed
- Mark Phase 1 checklist items as done (they were all ✅ already, just update sensor list)

#### [MODIFY] [phase2_hardware_design.md](file:///d:/Projects/Arduino%20Projects/Water%20Desalination/phase2_hardware_design.md)
- Pin assignment table already shows GPIO33 → Pressure; confirm it says "GPIO33 — ADC1_CH5"  
- Wiring diagram section 8.5 already shows pressure sensor wiring — verify it references correct GPIO33
- Update Source Code Files section to reference the correct Node1_WaterQuality folder (currently shows old `ESP_Sensors/` paths)

#### [MODIFY] [phase3_firmware_development.md](file:///d:/Projects/Arduino%20Projects/Water%20Desalination/phase3_firmware_development.md)
- Update Node 1 sensor list to explicitly include "Pressure" (currently says "pH, TDS, Turbidity, Pressure, Level, Flow" — ✅ already there)
- Add note about all 7 sensors now being implemented in firmware
- Update validation checklist to include pressure sensor test item

#### [MODIFY] [phase4_backend_development.md](file:///d:/Projects/Arduino%20Projects/Water%20Desalination/phase4_backend_development.md)
- Update `POST /api/v1/sensors/ingest` request body to include `pressure_feed` field
- The ML features table already has `Pressure_before` — confirm it matches `pressure_feed` from Node 1

---

## Verification Plan

### Firmware
- Confirm `config.h` compiles (no duplicate defines)
- Confirm `sensors.cpp` compiles (readPressure uses readADC_Voltage)
- Confirm all Firebase JSON keys match Phase 1 schema (`pressure_feed`)
- Confirm alert engine has no missing initializations

### Phase Docs
- Confirm consistent sensor count: 7 sensors on Node 1 (pH×2, TDS×2, Turbidity×2, DS18B20×2, Pressure×1, Flow×2, Level×2)
- Confirm GPIO33 is used for pressure throughout
- Confirm Firebase schema in Phase 1 matches what firmware actually sends
