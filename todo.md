# TODO: Eletta S2 GL40 Calibration Tool

## Project: Simple Terminal Tool for VG220/VG320 Oil Calibration

**Status:** ✅ **COMPLETED** - All phases finished using TDD approach

---

## Phase 1: Core Calculations ✅ DONE

### 1.1 Create `calibrator.py` ✅
- [x] Oil property constants (VG220, VG320)
- [x] Walther-ASTM viscosity calculation
  - [x] Calculate A, B constants from reference data
  - [x] `get_viscosity(oil, temp_c)` function
- [x] Density calculation with temperature
  - [x] `get_density(oil, temp_c)` function
- [x] Correction factor calculation
  - [x] `get_correction_factor(oil, temp_c)` function
- [x] Orifice diameter calculation
  - [x] `calculate_orifice_diameter(flow_lpm, oil, temp_c)` function
- [x] Reynolds number check
  - [x] `get_reynolds_number(flow, diameter, oil, temp)` function
- [x] Differential pressure calculation
  - [x] `get_differential_pressure(flow, orifice_d, oil, temp)` function
- [x] **NEW:** Orifice correction calculation
  - [x] `calculate_corrected_orifice()` function for incorrect sensor readings

### 1.2 GL40 Constants ✅
- [x] Pipe diameter: 41 mm
- [x] DP range: 50-200 mbar
- [x] Float density: 8020 kg/m³
- [x] Discharge coefficient: 0.61

---

## Phase 2: CLI Interface ✅ DONE

### 2.1 Create `main.py` ✅
- [x] Argument parsing with argparse
  - [x] `--oil` (VG220 or VG320, required)
  - [x] `--temp` (temperature °C, required)
  - [x] `--flow` (single flow rate L/min)
  - [x] `--flow-range` (min max for table)
  - [x] `--props-only` (show fluid properties only)
  - [x] **NEW:** `--correct` (orifice correction mode)
  - [x] **NEW:** `--true-flow`, `--sensor-reading`, `--current-orifice`
- [x] Input validation
- [x] Call calibrator functions
- [x] Format and print results

### 2.2 Output Formatting ✅
- [x] Single calculation result display
- [x] Flow range table output
- [x] Warnings display (Re < 4000, β out of range)
- [x] Clean terminal formatting with boxes/lines
- [x] **NEW:** Correction mode output with comparison

---

## Phase 3: Testing & Validation ✅ DONE

### 3.1 Unit Tests (TDD) ✅
- [x] 32 comprehensive unit tests (all passing)
- [x] Test VG220 viscosity at 40°C and 100°C
- [x] Test VG320 viscosity at 40°C and 100°C
- [x] Test temperature-dependent calculations (20-80°C)
- [x] Test flow range 10-250 L/min
- [x] Test correction factor calculations
- [x] Test orifice diameter sizing
- [x] Test Reynolds number calculations
- [x] Test differential pressure calculations
- [x] **NEW:** Test orifice correction function (6 tests)

### 3.2 Manual Testing ✅
- [x] Tested VG220 at various temperatures
- [x] Tested VG320 at various temperatures
- [x] Tested temperature range 20-80°C
- [x] Tested flow range 10-250 L/min
- [x] Validated correction mode with real scenarios

### 3.3 Edge Cases ✅
- [x] Very low flow (Re warning triggered correctly)
- [x] Maximum flow (250 L/min)
- [x] Temperature extremes
- [x] Beta ratio validation

---

## Phase 4: Documentation ✅ DONE

### 4.1 README.md ✅
- [x] Installation instructions with git clone
- [x] Usage examples for all 4 modes
- [x] Oil properties reference
- [x] Physics explanation (brief)
- [x] Command reference tables
- [x] **NEW:** Orifice correction mode documentation
- [x] **NEW:** Updated file structure

### 4.2 architecture.md ✅
- [x] System design diagram
- [x] Core physics equations
- [x] File structure
- [x] Usage examples
- [x] **NEW:** Correction mode documentation
- [x] **NEW:** Updated architecture

---

## Development Approach

✅ **Test-Driven Development (TDD)**
- Wrote tests first (Red phase)
- Implemented code to pass tests (Green phase)
- Iteratively refined for edge cases
- 32/32 tests passing

---

## Current File Structure

```
flow_sensor_calibration/
├── main.py                    # CLI with 4 modes
├── src/
│   ├── __init__.py
│   └── calibrator.py          # Core calculations
├── tests/
│   ├── __init__.py
│   └── test_calibrator.py     # 32 unit tests
├── README.md                  # User documentation
├── architecture.md            # Technical design
├── todo.md                    # This file
├── pyproject.toml             # Project config
└── CLAUDE.md                  # Python guidelines
```

---

## CLI Usage Summary

```bash
# 1. Single point calculation
python3 main.py --oil VG220 --temp 50 --flow 150

# 2. Flow range table
python3 main.py --oil VG320 --temp 40 --flow-range 10 250

# 3. Fluid properties only
python3 main.py --oil VG220 --temp 60 --props-only

# 4. Orifice correction (NEW)
python3 main.py --oil VG220 --temp 50 --correct \
  --true-flow 150 --sensor-reading 120 --current-orifice 20
```

---

## Key Features Implemented

- ✅ Walther-ASTM viscosity calculations
- ✅ Temperature-dependent density calculations
- ✅ Liquid correction factor for non-water fluids
- ✅ Iterative orifice sizing with velocity of approach factor
- ✅ Reynolds number validation
- ✅ Differential pressure calculations
- ✅ Operating condition validation with warnings
- ✅ **Orifice correction mode** for field calibration
- ✅ Comprehensive error handling
- ✅ Clean formatted output

---

## Future Enhancements (Optional)

- [ ] Add support for more oil types (VG100, VG460, etc.)
- [ ] Export results to CSV/JSON
- [ ] Interactive mode with prompts
- [ ] Plot generation (requires matplotlib)
- [ ] Web interface (requires FastAPI/Flask)
- [ ] Configuration file support

---

## Notes

- No external dependencies for core functionality
- Uses Python 3.12+ standard library only
- Developed and tested using TDD methodology
- All code formatted with Ruff
- Type hints throughout for mypy validation
- Git repository: https://github.com/TKontu/flow_sensor_calibration.git
