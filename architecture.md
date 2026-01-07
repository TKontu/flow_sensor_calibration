# Architecture: Eletta S2 GL40 Orifice Calibration Tool

## Overview

A simple terminal-based Python tool for calculating corrected orifice diameters for the Eletta S2 GL40 flow monitor when used with VG220/VG320 gear oils (0-250 L/min).

## System Design

```
┌────────────────────────────────────────────────────────┐
│                    main.py (CLI)                       │
│    4 modes: flow calc, table, props, correction       │
└────────────────────────────────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────┐
│              src/calibrator.py (Core)                  │
│  ┌──────────────┐  ┌─────────────┐  ┌──────────────┐  │
│  │ Oil Props    │  │  Orifice    │  │  Correction  │  │
│  │ (viscosity,  │  │  Equations  │  │  Factors     │  │
│  │  density)    │  │  (ΔP, flow) │  │  & Sizing    │  │
│  └──────────────┘  └─────────────┘  └──────────────┘  │
└────────────────────────────────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────┐
│           tests/test_calibrator.py                     │
│              32 unit tests (TDD)                       │
└────────────────────────────────────────────────────────┘
```

## Core Physics

### Orifice Flow Equation
```
Q = Cd × A × √(2ΔP / ρ)

Where:
  Q  = Flow rate (m³/s)
  Cd = Discharge coefficient (~0.61)
  A  = Orifice area (m²)
  ΔP = Differential pressure (Pa)
  ρ  = Fluid density (kg/m³)
```

### Correction Factor for Non-Water Fluids
```
LCF = √[(ρ_float - ρ_oil) × ρ_water / ((ρ_float - ρ_water) × ρ_oil)]

actual_flow = scale_reading × LCF
```

Where ρ_float = 8020 kg/m³ (stainless steel reference)

### Viscosity-Temperature (Walther-ASTM)
```
log(log(ν + 0.7)) = A - B × log(T)

Where:
  ν = kinematic viscosity (cSt)
  T = temperature (K)
  A, B = constants from 40°C and 100°C reference data
```

### Density-Temperature
```
ρ(T) = ρ_15 × [1 - α × (T - 15)]

Where:
  α = thermal expansion coefficient (~0.00065 /°C)
```

## Oil Reference Data

| Property | VG220 | VG320 | Unit |
|----------|-------|-------|------|
| ν @ 40°C | 220 | 320 | cSt |
| ν @ 100°C | 19 | 24.5 | cSt |
| ρ @ 15°C | 895 | 900 | kg/m³ |
| Viscosity Index | 95 | 95 | - |

## GL40 Sensor Specs

| Parameter | Value |
|-----------|-------|
| Pipe ID | 41 mm |
| ΔP range (S2) | 50-200 mbar |
| Valid β ratio | 0.25-0.75 |
| Min Reynolds | 4000 |

## File Structure

```
flow_sensor_calibration/
├── main.py                    # CLI entry point (4 modes)
├── src/
│   ├── __init__.py
│   └── calibrator.py          # All calculation logic
├── tests/
│   ├── __init__.py
│   └── test_calibrator.py     # 32 unit tests
├── README.md
├── architecture.md
├── todo.md
├── pyproject.toml             # Ruff, pytest, mypy config
├── requirements.txt           # Production (empty)
├── requirements-dev.txt       # Development (pytest)
└── CLAUDE.md                  # Python guidelines
```

## CLI Modes

### 1. Single Point Calculation
```bash
python3 main.py --oil VG220 --temp 50 --flow 150
```

### 2. Flow Range Table
```bash
python3 main.py --oil VG320 --temp 40 --flow-range 10 250
```

### 3. Fluid Properties Only
```bash
python3 main.py --oil VG220 --temp 60 --props-only
```

### 4. Orifice Correction (NEW)
```bash
python3 main.py --oil VG220 --temp 50 --correct \
  --true-flow 150 \
  --sensor-reading 120 \
  --current-orifice 20
```

**Use case:** When you have a reference flow meter showing true flow, but the sensor reads incorrectly due to wrong orifice size. Calculates the corrected orifice diameter needed.

## Output Format

```
═══════════════════════════════════════════════════════
  ELETTA S2 GL40 CALIBRATION RESULTS
═══════════════════════════════════════════════════════

Input Parameters:
  Oil Type:        VG220
  Temperature:     50 °C
  Target Flow:     150 L/min

Fluid Properties @ 50°C:
  Kinematic Viscosity:  98.5 cSt
  Dynamic Viscosity:    86.2 mPa·s
  Density:              872 kg/m³

Calculated Results:
  Orifice Diameter:     18.5 mm
  Beta Ratio:           0.45
  Correction Factor:    1.073
  Reynolds Number:      12,450
  Differential Pressure: 125 mbar

Status: ✓ All parameters within valid range
═══════════════════════════════════════════════════════
```
