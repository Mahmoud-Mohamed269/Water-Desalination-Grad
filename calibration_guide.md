# Analog Sensor Calibration Guide

This guide will walk you through calibrating the analog sensors across the new 3-Node Architecture to ensure accurate readings. Since we are using voltage dividers and analog-to-digital converters (ADC), software calibration is essential.

All calibration constants are stored in the respective node's `config.h` file (e.g., `firmware/Node1_WaterQuality/config.h` and `firmware/Node2_Environment/config.h`). 

---

## NODE 1 (Water Quality Sensors)

### 1. pH Sensor Calibration

The pH sensor requires a two-point calibration to find the midpoint voltage (at pH 7.0) and the slope.

#### Materials Needed:
- pH 7.0 buffer solution
- pH 4.0 buffer solution
- Distilled water (for rinsing)

#### Steps:
1. **Rinse** the pH probe in distilled water and dry it gently.
2. **Submerge** the probe in the **pH 7.0** buffer solution.
3. Wait 1 minute for the reading to stabilize.
4. Check the Serial Monitor. Look at the raw voltage reading (or write a quick `Serial.println(readADC_Voltage(PIN_PH))` in the `Node1_WaterQuality.ino` loop). Let's say the voltage reads `2.52V`.
5. Open `Node1_WaterQuality/config.h` and update:
   ```c
   #define PH_VOLTAGE_AT_PH7       2.52f
   ```
6. **Rinse** the probe again in distilled water.
7. **Submerge** the probe in the **pH 4.0** buffer solution.
8. Wait 1 minute. Note the new voltage (e.g., `3.05V`).
9. **Calculate the Slope:**
   ```
   Slope = (Voltage at pH 4.0 - Voltage at pH 7.0) / (4.0 - 7.0)
   Slope = (3.05 - 2.52) / -3.0
   Slope = -0.176
   ```
10. Open `config.h` and update:
    ```c
    #define PH_SLOPE                -0.176f
    ```

---

### 2. TDS Sensor Calibration

The TDS sensor formula relies on a temperature-compensated voltage. It usually doesn't need a complex slope adjustment if you are using standard 3.3V TDS modules, but you can calibrate it against a known standard.

#### Steps:
1. Ensure a temperature sensor is submerged in the same solution, as TDS relies heavily on accurate temperature compensation!
2. **Submerge** the TDS probe in a known calibration solution (e.g., 342 ppm).
3. Look at the Serial Monitor output for the calculated TDS value.
4. If the code outputs `300 ppm` but your solution is `342 ppm`, calculate the factor: `342 / 300 = 1.14`.
5. Change `TDS_CALIBRATION_FACTOR` in `config.h` from `1.0f` to `1.14f`.

---

### 3. Turbidity Sensor Calibration

The turbidity sensor outputs an inverse analog voltage: highest voltage when the water is clear (0 NTU), and lower voltage as it gets murkier.

#### Steps:
1. **Submerge** the turbidity sensor in pure distilled water (0 NTU).
2. Check the Serial Monitor for the raw ADC voltage (after the voltage divider multiplier is applied). Let's say it reads `4.15V`.
3. Open `config.h` and update the zero-point voltage:
   ```c
   #define TURBIDITY_VOLTAGE_CLEAR 4.15f
   ```

> [!WARNING]
> The Turbidity sensor is highly sensitive to ambient light. **Always calibrate under the same lighting conditions as the final installation.**

---

## NODE 2 (Environment Sensors)

### 4. MQ-Series Gas Sensor Calibration (Air Quality)

MQ sensors (like MQ-2, MQ-135) require a burn-in period and a baseline calibration in clean air. The sensor resistance changes based on target gas concentration.

#### Steps:
1. **Burn-in:** Leave the sensor powered on for **24 to 48 hours** before first use to burn off factory impurities.
2. **Clean Air Baseline (Ro calculation):**
   - Place the sensor in a known clean-air environment (e.g., outdoors in fresh air).
   - Read the analog voltage from the sensor.
   - Calculate the sensor resistance (Rs) using the voltage divider equation.
   - For clean air, the ratio `Rs/Ro` is a constant found in the datasheet (e.g., for MQ-135, `Rs/Ro ≈ 3.6` in clean air).
   - Divide your calculated Rs by this constant to find **Ro** (the base resistance).
3. Open `Node2_Environment/config.h` and update your `Ro` constant:
   ```c
   #define MQ_SENSOR_RO  15.5f  // Example base resistance in kilo-ohms
   ```
4. **Target Gas Calibration (Optional):** If you need absolute ppm for a specific gas (like CO2), you must expose it to a known concentration (e.g., 400ppm CO2) and adjust the scaling curve factor in your code.

---

### 5. Ultrasonic Sensor Calibration (Tank Levels)

Ultrasonic sensors (HC-SR04 or similar waterproof JSN-SR04T) measure time-of-flight. They don't need voltage calibration, but they do require geometric calibration for your specific tanks.

#### Steps:
1. Mount the ultrasonic sensor at the very top of the tank.
2. Measure the physical distance from the sensor to the bottom of the empty tank (e.g., `100 cm`). This is `TANK_DEPTH_CM`.
3. Measure the distance from the sensor to the water surface when the tank is at its absolute maximum safe capacity (e.g., `10 cm`). This is `TANK_EMPTY_GAP_CM`.
4. Update these constants in `Node2_Environment/config.h` so the code can map the distance reading (cm) to a percentage (0-100%).
