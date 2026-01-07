# Eletta S2 GL40 Orifice Calibration Tool

A terminal-based Python tool for calculating corrected orifice diameters when using the Eletta S2 GL40 differential pressure flow monitor with VG220 and VG320 industrial gear oils.

## Purpose

The Eletta S2 GL40 is factory-calibrated for water. When measuring viscous oils like VG220 or VG320, correction factors must be applied to convert between scale readings and actual flow rates. This tool:

1. Calculates fluid properties (viscosity, density) at operating temperature
2. Determines the appropriate correction factor
3. Computes the required orifice diameter for a target flow rate
4. Validates that operating conditions are within sensor limits

## Installation

```bash
# Clone or download the files
cd eletta_calibration

# No dependencies required - uses Python standard library only
python main.py --help
```

**Requirements:** Python 3.8 or higher

## Usage

### Single Point Calculation

Calculate orifice diameter for a specific flow rate:

```bash
python main.py --oil VG220 --temp 50 --flow 150
```

Output:
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

### Flow Range Table

Generate a calibration table across a flow range:

```bash
python main.py --oil VG320 --temp 40 --flow-range 10 250
```

### Fluid Properties Only

Display oil properties at a specific temperature:

```bash
python main.py --oil VG220 --temp 60 --props-only
```

## Command Reference

| Argument | Description | Required |
|----------|-------------|----------|
| `--oil` | Oil type: `VG220` or `VG320` | Yes |
| `--temp` | Operating temperature in °C | Yes |
| `--flow` | Target flow rate in L/min | No* |
| `--flow-range` | Min and max flow for table (L/min) | No* |
| `--props-only` | Show fluid properties only | No |

*Either `--flow` or `--flow-range` required unless using `--props-only`

## Supported Oils

### ISO VG 220
- Kinematic viscosity @ 40°C: 220 cSt
- Kinematic viscosity @ 100°C: 19 cSt  
- Density @ 15°C: 895 kg/m³
- Typical applications: Heavy-duty gearboxes, industrial gear drives

### ISO VG 320
- Kinematic viscosity @ 40°C: 320 cSt
- Kinematic viscosity @ 100°C: 24.5 cSt
- Density @ 15°C: 900 kg/m³
- Typical applications: Heavily loaded gear systems, high-temperature environments

## GL40 Sensor Specifications

| Parameter | Value |
|-----------|-------|
| Pipe internal diameter | 41 mm |
| Connection | G 1½" BSP |
| Differential pressure range | 50-200 mbar |
| Valid beta ratio (d/D) | 0.25-0.75 |
| Minimum Reynolds number | 4000 |

## Physics Background

### Orifice Flow Equation

The sensor measures flow using the differential pressure across an orifice:

```
Q = Cd × A × √(2ΔP / ρ)
```

Where:
- Q = Volumetric flow rate
- Cd = Discharge coefficient (~0.61)
- A = Orifice cross-sectional area
- ΔP = Differential pressure
- ρ = Fluid density

### Correction Factor

Since the sensor is calibrated for water, a correction factor accounts for different fluid densities:

```
LCF = √[(ρ_float - ρ_oil) × ρ_water / ((ρ_float - ρ_water) × ρ_oil)]
```

The stainless steel float/reference has density ρ_float = 8020 kg/m³.

### Viscosity-Temperature Relationship

Oil viscosity varies significantly with temperature. The Walther-ASTM equation models this:

```
log(log(ν + 0.7)) = A - B × log(T)
```

Where T is absolute temperature (K) and A, B are oil-specific constants derived from the 40°C and 100°C reference viscosities.

## Warnings

The tool will warn you when:

- **Reynolds number < 4000**: Flow may be laminar, reducing measurement accuracy
- **Beta ratio outside 0.25-0.75**: Orifice size may cause measurement errors
- **ΔP outside 50-200 mbar**: Operating outside S2 sensor range

## Limitations

- Assumes sharp-edged orifice plate
- Does not account for pipe roughness or entrance effects
- Viscosity model valid for mineral-based gear oils
- Temperature range validated: 20-80°C

## File Structure

```
eletta_calibration/
├── main.py           # CLI entry point
├── calibrator.py     # Calculation functions
├── README.md         # This file
├── architecture.md   # Technical design
└── todo.md          # Development tasks
```

## References

- Eletta S2/S25 Installation and Operation Manual
- ISO 3448: Industrial liquid lubricants — ISO viscosity classification
- ASTM D341: Standard Practice for Viscosity-Temperature Charts
- ISO 5167: Measurement of fluid flow by means of pressure differential devices

## License

MIT License - Free to use and modify.
