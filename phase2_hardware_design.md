# 🔧 Phase 2 — Hardware Design and Connections

---

## 📋 Table of Contents

1. [Objectives](#1-objectives)
2. [Theory](#2-theory)
3. [Bill of Materials (BOM)](#3-bill-of-materials-bom)
4. [Power Supply Design](#4-power-supply-design)
5. [ESP32S 38-Pin Board Layout](#5-esp32s-38-pin-board-layout)
6. [Complete Pin Assignment Table](#6-complete-pin-assignment-table)
7. [Voltage Divider Design](#7-voltage-divider-design)
8. [Sensor Wiring Diagrams](#8-sensor-wiring-diagrams)
9. [Complete System Wiring Overview](#9-complete-system-wiring-overview)
10. [Source Code Files](#10-source-code-files)
11. [Testing Procedures](#11-testing-procedures)
12. [Validation Checklist](#12-validation-checklist)
13. [Common Errors & Troubleshooting](#13-common-errors--troubleshooting)
14. [Best Practices](#14-best-practices)

---

## 1. Objectives

| # | Objective |
|---|-----------|
| 1 | Connect all 7 sensors to the ESP32S safely |
| 2 | Design voltage dividers for 5V sensor outputs |
| 3 | Wire relay modules for pump and solenoid valve control |
| 4 | Design a clean power distribution system |
| 5 | Verify all connections with the hardware test sketch |
| 6 | Create the `config.h` master pin definition file |

---

## 2. Theory

### 2.1 ESP32 ADC Limitation — The Most Critical Rule

The ESP32 has **two ADC units**:

| ADC Unit | Pins | WiFi-Safe? |
|----------|------|------------|
| **ADC1** | GPIO32, 33, 34, 35, 36, 39 | ✅ YES |
| **ADC2** | GPIO0, 2, 4, 12, 13, 14, 15, 25, 26, 27 | ❌ NO |

> [!CAUTION]
> **ADC2 is internally used by the WiFi radio.** When WiFi is active, any `analogRead()` on ADC2 pins returns garbage values or causes crashes. ALL analog sensors in this project use ADC1 pins only.

### 2.2 Voltage Divider Principle

Several sensors are powered by 5V and output up to 4.5V. The ESP32 ADC maximum input is **3.3V**. Exceeding this **permanently damages** the ESP32.

**Solution: Resistor Voltage Divider**

```
  Sensor Output (5V max)
         │
        [R1 = 10kΩ]
         │
         ├──────────── To ESP32 GPIO (ADC)
         │
        [R2 = 20kΩ]
         │
        GND
```

```
Vout = Vin × R2 / (R1 + R2)
Vout = 5.0 × 20 / (10 + 20)
Vout = 5.0 × 0.667
Vout = 3.33V  ✅ (safe for ESP32)
```

**Affected sensors requiring dividers:**
- Turbidity Sensor (outputs 0–4.5V at 5V supply)
- Pressure Sensor G1/4 (outputs 0.5–4.5V at 5V supply)

### 2.3 OneWire Protocol (DS18B20)

The DS18B20 uses the Dallas OneWire protocol — a single-wire bidirectional communication. A **4.7kΩ pull-up resistor** between the DATA line and VCC is **mandatory**. Without it, the sensor will always return `-127°C` (error code).

### 2.4 Relay Module Logic

Most relay modules are **Active-LOW** (the relay energizes when the control pin is pulled LOW):
- `digitalWrite(PIN_RELAY, LOW)` → Relay **ON** → Pump/Valve ON
- `digitalWrite(PIN_RELAY, HIGH)` → Relay **OFF** → Pump/Valve OFF

The relay module uses an optocoupler for isolation, protecting the ESP32 from the high-current load circuit.

---

## 3. Bill of Materials (BOM)

### 3.1 Core Components

| # | Component | Quantity | Notes |
|---|-----------|----------|-------|
| 1 | ESP32 38-pin Development Board | 3 | Main Hub, Node 1, Node 2 |
| 2 | 5-inch SPI TFT LCD Module | 1 | ILI9488 or equivalent SPI display |
| 3 | pH Analog Sensor Kit | 1 | For Node 1 |
| 4 | TDS Meter Analog Sensor | 1 | For Node 1 |
| 5 | Water Turbidity Sensor | 1 | For Node 1 |
| 6 | Analog Water Pressure Sensor | 1 | For Node 1 |
| 7 | XKC-Y25 Level Sensor | 2 | For Node 1 |
| 8 | YF-S201 Water Flow Sensor | 1 | For Node 1 |
| 9 | Ultrasonic Distance Sensor | 2 | For Node 2 (Tank Levels) |
| 10 | DHT22 Temp/Humidity Sensor | 1 | For Node 2 |
| 11 | MQ-Series Gas Sensor | 2 | For Node 2 |
| 12 | DS18B20 Temp Sensor | 2 | For Node 2 |
| 13 | Relay Modules | 5 | 2 for Node 1 (Pump/Valve), 3 for Node 2 (Fans) |
| 14 | RO Pump & Solenoid Valve | 1 ea | Controlled by Node 1 |
| 15 | Cooling Fans (12V) | 3 | Controlled by Node 2 |

### 3.2 Passive Components

| # | Component | Quantity | Value | Purpose |
|---|-----------|----------|-------|---------|
| 1 | Resistor | 2 | 10kΩ (1%) | Voltage divider R1 |
| 2 | Resistor | 2 | 20kΩ (1%) | Voltage divider R2 |
| 3 | Resistor | 1 | 4.7kΩ | DS18B20 pull-up |
| 4 | Resistor | 1 | 10kΩ | Flow sensor pull-up |
| 5 | Capacitor | 4 | 100nF ceramic | ADC bypass caps |
| 6 | Capacitor | 1 | 10µF electrolytic | 3.3V power line filter |

### 3.3 Power & Wiring

| # | Component | Quantity | Notes |
|---|-----------|----------|-------|
| 1 | 5V 2A DC Power Supply | 1 | For ESP32 + all 5V sensors |
| 2 | 12V or 24V 5A DC Power Supply | 1 | For pump + solenoid valve |
| 3 | AMS1117-3.3 Regulator or equivalent | 1 | If needed for 3.3V rail |
| 4 | Terminal blocks (2-pin) | 10 | For sensor wire connections |
| 5 | Breadboard or PCB | 1 | For prototyping |
| 6 | Dupont jumper wires (M-M, M-F, F-F) | 40+ | Various |
| 7 | Shielded wire (for analog sensors) | 2m | Reduces noise |

### 3.4 Arduino Libraries Required

| Library | Author | Install via |
|---------|--------|-------------|
| `OneWire` | Paul Stoffregen | Arduino Library Manager |
| `DallasTemperature` | Miles Burton | Arduino Library Manager |
| `ArduinoJson` | Benoit Blanchon | Arduino Library Manager |
| `Firebase ESP Client` | Mobizt | Arduino Library Manager |
| `NTPClient` | Fabrice Weinberg | Arduino Library Manager |

---

## 4. Power Supply Design

### 4.1 Power Budget

| Component | Voltage | Current Draw | Source |
|-----------|---------|-------------|--------|
| ESP32S | 3.3V (via onboard LDO) | 80–250 mA | 5V supply via USB/VIN |
| pH Sensor board | 5V | ~5 mA | 5V rail |
| TDS Sensor board | 3.3–5V | ~3 mA | 3.3V or 5V rail |
| Turbidity Sensor | 5V | ~30 mA | 5V rail |
| DS18B20 | 3.3V | ~1.5 mA | 3.3V rail |
| Pressure Sensor | 5V | ~10 mA | 5V rail |
| XKC-Y25 × 2 | 5–12V | ~15 mA × 2 | 5V rail |
| YF-S201 Flow | 5–12V | ~15 mA | 5V rail |
| Relay Module | 5V (coil) | ~50 mA × 2 | 5V rail |
| **TOTAL 5V load** | **5V** | **~480 mA** | **5V 2A supply** |
| RO Pump | 12V | 3–5 A | 12V supply (separate) |
| Solenoid Valve | 12V | 0.5–1 A | 12V supply (separate) |

### 4.2 Power Distribution Diagram

```
  [5V 2A Power Supply]
         │
         ├─────────────────── ESP32S VIN pin
         │                    (onboard LDO → 3.3V)
         │
         ├─────────────────── pH Sensor VCC (5V)
         │
         ├─────────────────── Turbidity Sensor VCC (5V)
         │
         ├─────────────────── Pressure Sensor VCC (5V)
         │
         ├─────────────────── XKC-Y25 #1 VCC (5V)
         │
         ├─────────────────── XKC-Y25 #2 VCC (5V)
         │
         ├─────────────────── YF-S201 VCC (5V)
         │
         └─────────────────── Relay Module VCC (5V)

  [ESP32S 3.3V pin] ──────── TDS Sensor VCC (3.3V)
                   └──────── DS18B20 VCC (3.3V)

  [12V 5A Power Supply]
         ├─────────────────── Relay Common (COM)
         │                    → Relay NC → Pump
         └─────────────────── Relay Common (COM)
                              → Relay NC → Solenoid Valve

  GND ──────────────────────── ALL GND pins connected together
```

> [!IMPORTANT]
> The 12V pump/valve power supply **shares GND** with the 5V/3.3V circuit but the **12V line itself is isolated** — it only connects to the relay Common (COM) terminal. Never connect 12V directly to the ESP32 or sensors.

---

## 5. ESP32 Board Layouts (3 Nodes)

The system is distributed across three separate ESP32s to prevent GPIO exhaustion and ADC interference.

### 5.1 Node 1: Water Quality (Sensor Node)
```
                    ESP32S 38-PIN BOARD (Node 1)
                    ┌─────────────────┐
              EN ───┤ EN          D23 ├─── (free)
 pH(Perm) GPIO36 ─── ┤ VP(36)      D22 ├─── (free)
 TDS(Perm)GPIO39 ──┤ VN(39)      TX0 ├─── Serial TX
 pH(Feed) GPIO34 ───┤ D34         RX0 ├─── Serial RX
 TDS(Feed)GPIO35 ───┤ D35         D21 ├─── (free)
 TurbidityGPIO32 ───┤ D32         D19 ├────Level Product
 Pressure GPIO33 ───┤ D33         D18 ├────Flow (Feed)
 Valve    GPIO25 ───┤ D25    (TX2)D17 ├─── (free)
 Pump     GPIO26 ──┤ D26    (RX2)D16 ├─── (free)
 Flow(P)  GPIO27 ──┤ D27         D15 ├─── (free)
          GPIO14 ──┤ D14          D2 ├────Status LED
          GPIO12 ──┤ D12          D4 ├────DS18B20 Temp
              GND─ ┤ GND         GND ├─── GND
          GPIO13 ──┤ D13         D5  ├────Level Feed
              5V ─ ┤ 5V          3V3 ├─── 3.3V out
                    └─────────────────┘
```

### 5.2 Node 2: Environment
```
                    ESP32S 38-PIN BOARD (Node 2)
                    ┌─────────────────┐
              EN ───┤ EN          D23 ├─── (free)
 Gas1     GPIO36 ─── ┤ VP(36)      D22 ├─── (free)
 Gas2     GPIO39 ──┤ VN(39)      TX0 ├─── Serial TX
          GPIO34 ───┤ D34         RX0 ├─── Serial RX
          GPIO35 ───┤ D35         D21 ├─── (free)
 Fan3     GPIO32 ───┤ D32         D19 ├─── (free)
          GPIO33 ───┤ D33         D18 ├─── (free)
 Fan1     GPIO25 ───┤ D25    (TX2)D17 ├─── (free)
 Fan2     GPIO26 ──┤ D26    (RX2)D16 ├─── (free)
 US2 Echo GPIO27 ──┤ D27         D15 ├─── (free)
 US2 Trig GPIO14 ──┤ D14          D2 ├────Status LED
 US1 Echo GPIO12 ──┤ D12          D4 ├────DHT22
              GND─ ┤ GND         GND ├─── GND
 US1 Trig GPIO13 ──┤ D13         D5  ├────DS18B20 (Water Temps)
              5V ─ ┤ 5V          3V3 ├─── 3.3V out
                    └─────────────────┘
```

### 5.3 Main Hub (Comms & Display)
```
                    ESP32S 38-PIN BOARD (Main Hub)
                    ┌─────────────────┐
              EN ───┤ EN          D23 ├────TFT MOSI
          GPIO36 ─── ┤ VP(36)      D22 ├────TFT SCL (Touch)
          GPIO39 ──┤ VN(39)      TX0 ├─── Serial TX
          GPIO34 ───┤ D34         RX0 ├─── Serial RX
          GPIO35 ───┤ D35         D21 ├────TFT SDA (Touch)
          GPIO32 ───┤ D32         D19 ├────TFT MISO
          GPIO33 ───┤ D33         D18 ├────TFT SCK
          GPIO25 ───┤ D25    (TX2)D17 ├─── (free)
          GPIO26 ──┤ D26    (RX2)D16 ├─── (free)
          GPIO27 ──┤ D27         D15 ├─── (free)
          GPIO14 ──┤ D14          D2 ├────TFT DC
          GPIO12 ──┤ D12          D4 ├────TFT RST
              GND─ ┤ GND         GND ├─── GND
          GPIO13 ──┤ D13         D5  ├────TFT CS
              5V ─ ┤ 5V          3V3 ├─── 3.3V out
                    └─────────────────┘
```

---

## 6. Complete Pin Assignment Table

### 6.1 Node 1: Water Quality
| Sensor / Module | Pin Name | ESP32 GPIO | Role | Note |
|-----------------|----------|------------|------|------|
| pH Feed         | AOUT     | GPIO34     | ADC1 | Use shielded cable |
| pH Permeate     | AOUT     | GPIO36     | ADC1 | Use shielded cable |
| TDS Feed        | AOUT     | GPIO35     | ADC1 | |
| TDS Permeate    | AOUT     | GPIO39     | ADC1 | |
| Turbidity       | AOUT     | GPIO32     | ADC1 | Voltage divider required |
| Pressure G1/4   | OUT      | GPIO33     | ADC1 | Voltage divider required |
| DS18B20 Temps   | DATA     | GPIO4      | 1W   | 4.7kΩ pull-up to 3.3V |
| Flow Feed       | SIGNAL   | GPIO18     | INT  | 10kΩ pull-up |
| Flow Permeate   | SIGNAL   | GPIO27     | INT  | 10kΩ pull-up |
| Level Feed      | OUT      | GPIO5      | IN   | XKC-Y25, check for HIGH/LOW |
| Level Product   | OUT      | GPIO19     | IN   | XKC-Y25, check for HIGH/LOW |
| Relay (Pump)    | IN       | GPIO26     | OUT  | Active-LOW |
| Relay (Valve)   | IN       | GPIO25     | OUT  | Active-LOW |

### 6.2 Node 2: Environment
| Sensor / Module | Pin Name | ESP32 GPIO | Role | Note |
|-----------------|----------|------------|------|------|
| Gas 1           | AOUT     | GPIO36     | ADC1 | |
| Gas 2           | AOUT     | GPIO39     | ADC1 | |
| Ultrasonic 1    | TRIG     | GPIO13     | OUT  | Tank 1 |
| Ultrasonic 1    | ECHO     | GPIO12     | IN   | Tank 1 |
| Ultrasonic 2    | TRIG     | GPIO14     | OUT  | Tank 2 |
| Ultrasonic 2    | ECHO     | GPIO27     | IN   | Tank 2 |
| DHT22           | DATA     | GPIO4      | 1W   | Environment |
| DS18B20 Temps   | DATA     | GPIO5      | 1W   | Water Temps, shared bus |
| Relay (Fan 1)   | IN       | GPIO25     | OUT  | Active-LOW |
| Relay (Fan 2)   | IN       | GPIO26     | OUT  | Active-LOW |
| Relay (Fan 3)   | IN       | GPIO32     | OUT  | Active-LOW |

### 6.3 Main Hub (Comms & Display)
| Module          | Pin Name | ESP32 GPIO | Role | Note |
|-----------------|----------|------------|------|------|
| TFT SPI Display | CS       | GPIO5      | OUT  | Chip Select |
| TFT SPI Display | DC       | GPIO2      | OUT  | Data/Command |
| TFT SPI Display | RST      | GPIO4      | OUT  | Reset |
| TFT SPI Display | MOSI     | GPIO23     | OUT  | SPI Data Out |
| TFT SPI Display | MISO     | GPIO19     | IN   | SPI Data In |
| TFT SPI Display | SCK      | GPIO18     | OUT  | SPI Clock |
| TFT Touch I2C   | SDA      | GPIO21     | I2C  | Optional Touch |
| TFT Touch I2C   | SCL      | GPIO22     | I2C  | Optional Touch |

---

## 7. Voltage Divider Design

### 7.1 Turbidity Sensor Voltage Divider

```
  Turbidity Sensor AOUT (0–4.5V)
          │
         [R1 = 10kΩ]
          │
          ├──────── GPIO32 (ADC1_CH4)
          │         Max: 4.5 × 20/30 = 3.0V ✅
         [R2 = 20kΩ]
          │
         GND
```

**Inverse recovery in software:**
```cpp
// After reading ADC voltage (Vout):
float actualVoltage = Vout * VDIV_RATIO_TURBIDITY;  // × 1.5
// actualVoltage now represents the true 0–4.5V sensor output
```

### 7.2 Pressure Sensor Voltage Divider

```
  Pressure Sensor AOUT (0.5–4.5V)
          │
         [R1 = 10kΩ]
          │
          ├──────── GPIO33 (ADC1_CH5)
          │         Max: 4.5 × 20/30 = 3.0V ✅
         [R2 = 20kΩ]
          │
         GND
```

---

## 8. Sensor Wiring Diagrams

### 8.1 pH Sensor

```
  pH Sensor Board                    ESP32S
  ──────────────                     ──────
  VCC ─────────────────────────────── 5V (VIN)
  GND ─────────────────────────────── GND
  AOUT ──────────────[100nF]─── GND  GPIO34
         └───────────────────────────  (ADC1)

  * 100nF capacitor from AOUT to GND: noise bypass
  * Use shielded cable for AOUT line if > 20cm
  * pH Probe connects to BNC connector on sensor board
```

### 8.2 TDS Sensor V1.0

```
  TDS Sensor Board                   ESP32S
  ────────────────                   ──────
  VCC ─────────────────────────────── 3.3V
  GND ─────────────────────────────── GND
  AOUT ──────────────[100nF]─── GND  GPIO35
         └───────────────────────────  (ADC1)

  * TDS sensor outputs max 2.3V — safe for ESP32 directly
  * TDS probe (two stainless electrodes) connects to sensor board
```

### 8.3 Turbidity Sensor (with Voltage Divider)

```
  Turbidity Sensor                   Voltage Divider     ESP32S
  ────────────────                   ───────────────     ──────
  VCC ──────────────────────────────────────────────── 5V
  GND ──────────────────────────────────────────────── GND
  AOUT ─────────────────────── [10kΩ R1]
                                        │
                                        ├──── GPIO32 (ADC1)
                                        │
                               [20kΩ R2]
                                        │
                                       GND
  [100nF bypass cap from GPIO32 to GND]
```

### 8.4 DS18B20 Temperature Sensor

```
  DS18B20 (3-wire)                   ESP32S
  ────────────────                   ──────
  VDD (Red) ───────────────────────── 3.3V
  GND (Black) ─────────────────────── GND
  DATA (Yellow) ──────[4.7kΩ]──────── 3.3V (pull-up)
                  └──────────────────  GPIO4

  * 4.7kΩ pull-up BETWEEN Data and VCC is MANDATORY
  * Without pull-up: sensor always returns -127°C
  * Multiple DS18B20 can share the same GPIO4 (daisy chain)
  * Each sensor has unique 64-bit address for identification
```

### 8.5 Pressure Sensor G1/4 (with Voltage Divider)

```
  Pressure Sensor G1/4               Voltage Divider     ESP32S
  ────────────────────               ───────────────     ──────
  VCC (Red) ─────────────────────────────────────────── 5V
  GND (Black) ───────────────────────────────────────── GND
  AOUT (Yellow) ──────────────[10kΩ R1]
                                          │
                                          ├──── GPIO33 (ADC1)
                                          │
                                 [20kΩ R2]
                                          │
                                         GND
  [100nF bypass cap from GPIO33 to GND]

  Pressure Rating: Install G1/4 fitting on feed line (before membrane)
```

### 8.6 XKC-Y25 Non-Contact Water Level Sensor

```
  XKC-Y25 Sensor #1 (Feed Tank)      ESP32S
  ─────────────────────────────       ──────
  Brown  (VCC) ─────────────────────── 5V
  Blue   (GND) ─────────────────────── GND
  Black  (OUT) ─────────────────────── GPIO5 (INPUT_PULLUP)

  XKC-Y25 Sensor #2 (Product Tank)   ESP32S
  ─────────────────────────────────── ──────
  Brown  (VCC) ─────────────────────── 5V
  Blue   (GND) ─────────────────────── GND
  Black  (OUT) ─────────────────────── GPIO19 (INPUT_PULLUP)

  * Mount sensor on OUTSIDE of tank wall (non-contact)
  * Output: LOW = water at sensor level, HIGH = no water
  * ESP32 INPUT_PULLUP makes idle state HIGH (no water)
  * Use waterproof housing for sensor body if near splashes
```

### 8.7 YF-S201 Flow Sensor

```
  YF-S201 Flow Sensor                ESP32S
  ───────────────────                ──────
  Red   (VCC) ──────────────────────── 5V
  Black (GND) ──────────────────────── GND
  Yellow (Signal) ──[10kΩ]────────── 3.3V (pull-up)
                    └──────────────── GPIO18 (Interrupt)

  * 10kΩ pull-up from Signal to 3.3V (NOT 5V!)
  * Interrupt configured as FALLING edge
  * Flow rate: pulses/sec ÷ 7.5 = L/min
  * Install in-line with 1/2" thread fittings (G1/2)
  * Install on FEED water line after pre-filter
```

### 8.8 Relay Module (Pump + Valve)

```
  2-Channel Relay Module              ESP32S         Load Circuit
  ──────────────────────              ──────         ────────────
  VCC ────────────────────────────── 5V
  GND ────────────────────────────── GND ─────────── 12V Supply GND
  IN1 ────────────────────────────── GPIO26 (Pump)
  IN2 ────────────────────────────── GPIO25 (Valve)

  Relay Channel 1 (Pump):
    COM ──────── [+12V from power supply]
    NC  ──────── (normally connected — pump OFF by default)
    NO  ──────── [Pump positive terminal]

  Relay Channel 2 (Valve):
    COM ──────── [+12V from power supply]
    NC  ──────── (normally connected — valve OFF by default)
    NO  ──────── [Solenoid Valve positive terminal]

  * Active-LOW: GPIO LOW = Relay ON = Load ON
  * Use NC (Normally Closed) for fail-safe operation:
    If ESP32 loses power, pump/valve turns OFF automatically
```

---

## 9. Complete System Wiring Overview

```
                        ┌─────────────────────────────────────────┐
                        │           5V 2A Power Supply             │
                        └──────┬──────────────────────────────────┘
                               │ 5V                     GND
    ┌──────────────────────────┼────────────────────────┼──────────┐
    │                          │                         │          │
    │  ┌───────────────────────▼─────────────────────────▼───────┐  │
    │  │                    ESP32S 38-PIN                        │  │
    │  │                                                         │  │
    │  │  [VIN/5V]──────────────────────────────────────[GND]   │  │
    │  │  [3.3V out]                                            │  │
    │  │                                                         │  │
    │  │  GPIO34 ◄── pH Sensor Feed (5V, direct)                │  │
    │  │  GPIO35 ◄── TDS Sensor Feed (3.3V, direct)             │  │
    │  │  GPIO32 ◄── Turbidity Feed (5V, via 10k/20k divider)   │  │
    │  │  GPIO33 ◄── Pressure Feed (5V, via 10k/20k divider)    │  │
    │  │  GPIO36 ◄── pH Sensor Permeate (5V, direct)            │  │
    │  │  GPIO39 ◄── TDS Sensor Permeate (3.3V, direct)         │  │
    │  │  GPIO4  ◄── DS18B20 x2 (3.3V, 4.7k pull-up)            │  │
    │  │  GPIO5  ◄── XKC-Y25 Feed Tank (5V, INPUT_PULLUP)       │  │
    │  │  GPIO19 ◄── XKC-Y25 Product Tank (5V, INPUT_PULLUP)    │  │
    │  │  GPIO18 ◄── YF-S201 Flow Feed (5V, 10k pull-up, INT)   │  │
    │  │  GPIO27 ◄── YF-S201 Flow Permeate (5V, 10k pull-up, INT)│  │
    │  │  GPIO26 ──► Relay IN1 (Pump)                           │  │
    │  │  GPIO25 ──► Relay IN2 (Valve)                          │  │
    │  │  GPIO2  ──► Status LED (built-in)                      │  │
    │  └─────────────────────────────────────────────────────────┘  │
    │                                                                │
    │  ┌──────────────┐    ┌──────────────────────────────────────┐  │
    │  │ 2-CH Relay   │    │        12V 5A Power Supply           │  │
    │  │              │    └──────┬─────────────────────────┬────┘  │
    │  │ IN1 ◄─GPIO26 │           │ +12V                    │GND    │
    │  │ IN2 ◄─GPIO25 │           │                         │       │
    │  │              │    ┌──────┤                         │       │
    │  │ CH1 COM◄─12V─┘    │      │                         │       │
    │  │ CH1 NO──────────► │ RO PUMP (+) ──────────────────┘       │
    │  │                   └──────────────────────────────────────  │
    │  │ CH2 COM◄─12V───────────────────────────────────           │
    │  │ CH2 NO──────────── SOLENOID VALVE (+) ─────────────────   │
    └──┴──────────────────────────────────────────────────────────┘
```

---

## 10. Source Code Files

Three files have been created in your project:

### 10.1 [`config.h`](file:///d:/Projects/Arduino%20Projects/Water%20Desalination/Node1_WaterQuality/config.h) — Master Configuration

Contains ALL pin definitions, thresholds, ADC settings, calibration constants, sleep configuration, and debug macros. **Every number in the firmware comes from this file — never use magic numbers.**

Key sections:
- `PIN_*` — all GPIO assignments
- `ALERT_*_MIN/MAX` — alert thresholds per sensor
- `ADC_RESOLUTION`, `ADC_VREF`, `ADC_SAMPLES` — ADC settings
- `VDIV_RATIO_*` — voltage divider compensation factors
- `SLEEP_ENABLED`, `TIMER_WAKE_INTERVAL_SEC` — deep sleep config
- `RELAY_ON / RELAY_OFF` — relay logic level

### 10.2 [`secrets.h`](file:///d:/Projects/Arduino%20Projects/Water%20Desalination/Node1_WaterQuality/secrets.h) — Credentials

> [!CAUTION]
> This file contains WiFi password and Firebase secret. **Never commit to Git.** Add to `.gitignore`:
> ```
> Node1_WaterQuality/secrets.h
> ```

Contains:
- `WIFI_SSID` / `WIFI_PASSWORD`
- `FIREBASE_DATABASE_URL`
- `FIREBASE_AUTH_TOKEN`
- NTP server settings + timezone offset

### 10.3 [`Node1_WaterQuality.ino`](file:///d:/Projects/Arduino%20Projects/Water%20Desalination/Node1_WaterQuality/Node1_WaterQuality.ino) — Hardware Test Sketch

**Purpose (Phase 2 only):** Reads all sensors raw and prints to Serial Monitor. Verifies every hardware connection before writing calibration or Firebase code.

**What it does:**
- Reads ADC voltage from pH, TDS, Turbidity, Pressure sensors
- Reads DS18B20 temperature via OneWire
- Counts YF-S201 flow pulses via hardware interrupt
- Reads both XKC-Y25 level sensors (digital)
- Prints formatted table every 5 seconds at 115200 baud

---

## 11. Testing Procedures

### Test 1 — Power-On Test (Before connecting sensors)

1. Connect ESP32S to PC via USB
2. Open Arduino IDE → Tools → Port → select the ESP32 COM port
3. Open Serial Monitor (Ctrl+Shift+M) → set 115200 baud
4. Upload the current `Node1_WaterQuality.ino`
5. **Expected:** Welcome banner prints, "No DS18B20 found" (not connected yet)

### Test 2 — DS18B20 Temperature Sensor

1. Connect DS18B20 with 4.7kΩ pull-up resistor to GPIO4
2. Upload and run sketch
3. **Expected:**
   ```
   DS18B20 Sensors found on bus: 1
   Sensor 0 Address: 28:AA:BB:CC:DD:EE:FF:01
   Temperature DS18B20   24.500 °C   [OK]
   ```
4. **Fail:** `-127.000 °C [OK]` → Missing pull-up resistor

### Test 3 — Analog Sensors (Voltage Check)

Submerge each sensor probe in water and check expected voltage ranges:

| Sensor | Condition | Expected ADC Voltage |
|--------|-----------|---------------------|
| pH | In pH 7 buffer solution | ~2.5V |
| TDS | In 342 ppm water | ~0.7–1.0V |
| Turbidity | In clear water | ~3.8–4.2V (high V = clear) |
| Turbidity | In murky water | ~0.5–2.0V (lower V = murky) |
| Pressure | At atmospheric (no pressure) | ~0.33V (after divider) |
| Pressure | At 1 bar | ~0.63V (after divider) |

### Test 4 — Flow Sensor

1. Connect YF-S201 to GPIO18 with 10kΩ pull-up
2. Let water flow through the sensor
3. **Expected:** `Flow Rate: 2.xxx L/min [RAW]`
4. **Fail:** Always 0.000 → Check pull-up or interrupt pin

### Test 5 — Water Level Sensors

1. Connect XKC-Y25 to GPIO5
2. Place sensor on outside of container with water
3. **Expected:**
   ```
   Level Feed Tank      WATER         [OK]
   ```
4. Remove from water: `Level Feed Tank       EMPTY         [LOW]`

### Test 6 — Relay Module (Pump/Valve)

> [!WARNING]
> Do NOT have the pump/valve connected to 12V during this test. Test relay clicks only.

1. Short GPIO26 to GND manually (or run test code)
2. **Expected:** Audible **CLICK** from relay
3. LED on relay module illuminates

---

## 12. Validation Checklist

### Hardware
- [ ] ESP32S identified in Device Manager (COM port assigned)
- [ ] 5V supply measures 4.95–5.05V on multimeter
- [ ] 3.3V pin measures 3.28–3.32V
- [ ] All GNDs connected together (common ground)

### Sensor Connections
- [ ] pH sensor outputs ~2.5V at pH 7 buffer
- [ ] TDS sensor voltage changes when probe in vs out of water
- [ ] Turbidity voltage is HIGH (~4V) in clear water, LOWER in murky water
- [ ] DS18B20 detected on bus (not returning -127°C)
- [ ] Pressure sensor at atmospheric reads ~0.33V (after divider)
- [ ] XKC-Y25 Feed Tank: output changes when water present
- [ ] XKC-Y25 Product Tank: output changes when water present
- [ ] YF-S201: Flow rate > 0 when water flowing

### Voltage Safety
- [ ] Turbidity AOUT measured at GPIO32: < 3.3V ✅
- [ ] Pressure AOUT measured at GPIO33: < 3.3V ✅
- [ ] pH AOUT at GPIO34: < 3.3V ✅
- [ ] TDS AOUT at GPIO35: < 2.3V ✅

### Actuators
- [ ] Relay module relay clicks when GPIO26 driven LOW
- [ ] Relay module relay clicks when GPIO25 driven LOW
- [ ] Relay NC contact verified with multimeter (continuity when relay OFF)
- [ ] Relay NO contact verified (continuity when relay ON)

### Serial Monitor Output
- [ ] Welcome banner prints correctly
- [ ] All sensor rows print every 5 seconds
- [ ] No crash/reset observed
- [ ] DS18B20 address printed (8 bytes, not all zeros)

---

## 13. Common Errors & Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| DS18B20 always returns -127°C | Missing 4.7kΩ pull-up | Add pull-up between GPIO4 and 3.3V |
| DS18B20 shows 85°C on first read | Sensor just powered on, not yet read | Call `requestTemperatures()` before `getTempCByIndex()` and wait 750ms |
| ADC reads 0 or 4095 constantly | Sensor not powered or wrong pin | Verify sensor VCC and GND, check correct GPIO |
| ADC reads ~4095 even in air (pH) | Input voltage exceeds 3.3V | Measure actual sensor output with multimeter; add voltage divider if > 3.3V |
| Flow sensor always reads 0 | Missing 10kΩ pull-up | Add 10kΩ between GPIO18 and 3.3V |
| Flow sensor reads too high | Wrong calibration factor | YF-S201 factor is 7.5; check your specific sensor model |
| XKC-Y25 always shows WATER | Wiring issue or sensitivity too high | Adjust small potentiometer on back of XKC-Y25 sensor |
| XKC-Y25 never shows WATER | Sensor on wrong side of tank wall | Must be on DRY OUTSIDE surface pointing at water |
| Relay doesn't click | Power issue or wrong logic | Measure relay VCC = 5V; try `digitalWrite(PIN, LOW)` directly |
| ESP32 resets randomly | Power brownout from pump start | Add 1000µF capacitor on 5V rail; use separate 12V supply for pump |
| Garbage ADC when WiFi starts | Using ADC2 pin | Move sensor to GPIO32–39 (ADC1 only) |
| Serial garbled output | Wrong baud rate | Set Serial Monitor to exactly 115200 |

---

## 14. Best Practices

### 14.1 Wiring
1. **Use shielded cable** for analog sensor signal wires longer than 20cm
2. **Twist power and GND wires** together for sensors to cancel magnetic interference
3. **Keep analog signal wires away** from the relay coil and motor wires
4. **Add 100nF ceramic bypass caps** from each ADC pin to GND as close to the ESP32 as possible
5. **Use ferrule terminal crimps** on wire ends for reliable connections on terminal blocks

### 14.2 Power
1. **Never share the 12V pump line** with the ESP32 logic supply
2. **Add a 10A fuse** on the 12V line (before the relay)
3. **Use a TVS diode** across the pump terminals to clamp back-EMF spikes
4. **Add 1000µF capacitor** on the 5V rail near the ESP32 to handle current spikes

### 14.3 Code
1. **Always define `IRAM_ATTR`** on the flow sensor ISR function
2. **Use `noInterrupts()/interrupts()`** when reading `flowPulseCount` in loop
3. **Set `analogSetAttenuation(ADC_11db)`** for full 0–3.3V range (default is 0–1V)
4. **Oversample ADC** (average 10 readings) before applying any filters

---

## 📁 Phase 2 — Files Created

| File | Location | Purpose |
|------|----------|---------|
| [config.h](file:///d:/Projects/Arduino%20Projects/Water%20Desalination/Node1_WaterQuality/config.h) | `Node1_WaterQuality/` | Master configuration, all pins & constants |
| [secrets.h](file:///d:/Projects/Arduino%20Projects/Water%20Desalination/Node1_WaterQuality/secrets.h) | `Node1_WaterQuality/` | WiFi & Firebase credentials (gitignored) |
| [Node1_WaterQuality.ino](file:///d:/Projects/Arduino%20Projects/Water%20Desalination/Node1_WaterQuality/Node1_WaterQuality.ino) | `Node1_WaterQuality/` | Main sketch |

---

> [!IMPORTANT]
> **Before uploading to ESP32:**
> 1. Open `secrets.h` and fill in your real WiFi SSID, password, and Firebase URL
> 2. Install all required libraries via Arduino Library Manager
> 3. Tools → Board → ESP32 Arduino → **ESP32 Dev Module**
> 4. Tools → Partition Scheme → **Default 4MB with spiffs**
> 5. Tools → Upload Speed → **921600**
> 6. Tools → CPU Frequency → **240MHz (WiFi/BT)**

---

**Have you completed this phase?**

Reply with **"Phase Completed"** to proceed to **Phase 3: ESP32 Firmware Development** *(full sensor reading functions, deep sleep state machine, WiFi manager, Firebase client, and structured JSON payload builder)*.
