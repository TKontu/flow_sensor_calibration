# TODO: Eletta S2 GL40 Calibration Tool

## Project: Simple Terminal Tool for VG220/VG320 Oil Calibration

---

## Phase 1: Core Calculations ✱ START HERE

### 1.1 Create `calibrator.py`
- [ ] Oil property constants (VG220, VG320)
- [ ] Walther-ASTM viscosity calculation
  - [ ] Calculate A, B constants from reference data
  - [ ] `get_viscosity(oil, temp_c)` function
- [ ] Density calculation with temperature
  - [ ] `get_density(oil, temp_c)` function
- [ ] Correction factor calculation
  - [ ] `get_correction_factor(oil, temp_c)` function
- [ ] Orifice diameter calculation
  - [ ] `calculate_orifice(flow_lpm, oil, temp_c)` function
- [ ] Reynolds number check
  - [ ] `get_reynolds(flow, diameter, oil, temp)` function
- [ ] Differential pressure calculation
  - [ ] `get_dp(flow, orifice_d, oil, temp)` function

### 1.2 GL40 Constants
- [ ] Pipe diameter: 41 mm
- [ ] DP range: 50-200 mbar
- [ ] Float density: 8020 kg/m³
- [ ] Discharge coefficient: 0.61

---

## Phase 2: CLI Interface

### 2.1 Create `main.py`
- [ ] Argument parsing with argparse
  - [ ] `--oil` (VG220 or VG320, required)
  - [ ] `--temp` (temperature °C, required)
  - [ ] `--flow` (single flow rate L/min)
  - [ ] `--flow-range` (min max for table)
  - [ ] `--props-only` (show fluid properties only)
- [ ] Input validation
- [ ] Call calibrator functions
- [ ] Format and print results

### 2.2 Output Formatting
- [ ] Single calculation result display
- [ ] Flow range table output
- [ ] Warnings display (Re < 4000, β out of range)
- [ ] Clean terminal formatting with boxes/lines

---

## Phase 3: Testing & Validation

### 3.1 Manual Testing
- [ ] Test VG220 at 40°C (viscosity should be ~220 cSt)
- [ ] Test VG320 at 40°C (viscosity should be ~320 cSt)
- [ ] Test temperature range 20-80°C
- [ ] Test flow range 10-250 L/min
- [ ] Verify correction factors vs Eletta documentation

### 3.2 Edge Cases
- [ ] Very low flow (Re warning)
- [ ] Maximum flow (250 L/min)
- [ ] Temperature extremes

---

## Phase 4: Documentation

### 4.1 README.md
- [ ] Installation instructions
- [ ] Usage examples
- [ ] Oil properties reference
- [ ] Physics explanation (brief)

---

## Reference Data

### VG220 Oil
```
Kinematic viscosity @ 40°C:  220 cSt
Kinematic viscosity @ 100°C: 19 cSt
Density @ 15°C:              895 kg/m³
Viscosity Index:             95
```

### VG320 Oil
```
Kinematic viscosity @ 40°C:  320 cSt
Kinematic viscosity @ 100°C: 24.5 cSt
Density @ 15°C:              900 kg/m³
Viscosity Index:             95
```

### GL40 Sensor
```
Pipe internal diameter:      41 mm
Differential pressure range: 50-200 mbar (S2 model)
Valid beta ratio:            0.25-0.75
Minimum Reynolds number:     4000
```

---

## Quick Start Commands

```bash
# Single point calculation
python main.py --oil VG220 --temp 50 --flow 150

# Generate flow table
python main.py --oil VG320 --temp 40 --flow-range 10 250

# Show oil properties at temperature
python main.py --oil VG220 --temp 60 --props-only
```

---

## Notes

- All internal calculations in SI units
- Output in practical units (L/min, mm, mbar, cSt)
- No external dependencies beyond Python standard library
- Target Python 3.8+
