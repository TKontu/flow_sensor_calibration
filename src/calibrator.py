"""Eletta S2 GL40 orifice calibration calculations for VG220/VG320 oils."""

import math
from enum import Enum


class OilType(Enum):
    """Supported industrial gear oil types."""

    VG220 = "VG220"
    VG320 = "VG320"


# Oil property constants
OIL_PROPERTIES = {
    OilType.VG220: {
        "nu_40c": 220.0,  # Kinematic viscosity at 40°C (cSt)
        "nu_100c": 19.0,  # Kinematic viscosity at 100°C (cSt)
        "density_15c": 895.0,  # Density at 15°C (kg/m³)
    },
    OilType.VG320: {
        "nu_40c": 320.0,
        "nu_100c": 24.5,
        "density_15c": 900.0,
    },
}

# GL40 sensor constants
PIPE_DIAMETER_MM = 41.0  # Internal pipe diameter (mm)
FLOAT_DENSITY = 8020.0  # Stainless steel float density (kg/m³)
WATER_DENSITY = 1000.0  # Water density at reference conditions (kg/m³)
DISCHARGE_COEFFICIENT = 0.61  # Orifice discharge coefficient
THERMAL_EXPANSION_COEFF = 0.00065  # Oil thermal expansion coefficient (1/°C)

# Valid operating ranges
MIN_REYNOLDS = 4000  # Minimum Reynolds number for turbulent flow
MIN_BETA = 0.25  # Minimum beta ratio (d/D)
MAX_BETA = 0.75  # Maximum beta ratio
MIN_DP_MBAR = 50  # Minimum differential pressure (mbar)
MAX_DP_MBAR = 200  # Maximum differential pressure (mbar)


def _calculate_walther_constants(nu_40: float, nu_100: float) -> tuple[float, float]:
    """Calculate Walther-ASTM equation constants A and B from reference viscosities.

    Args:
        nu_40: Kinematic viscosity at 40°C (cSt)
        nu_100: Kinematic viscosity at 100°C (cSt)

    Returns:
        Tuple of (A, B) constants for Walther equation
    """
    # Convert temperatures to Kelvin
    t1 = 40.0 + 273.15  # 313.15 K
    t2 = 100.0 + 273.15  # 373.15 K

    # Walther equation: log(log(nu + 0.7)) = A - B * log(T)
    y1 = math.log10(math.log10(nu_40 + 0.7))
    y2 = math.log10(math.log10(nu_100 + 0.7))

    log_t1 = math.log10(t1)
    log_t2 = math.log10(t2)

    # Solve for B and A
    b = (y1 - y2) / (log_t2 - log_t1)
    a = y1 + b * log_t1

    return a, b


def get_viscosity(oil: OilType, temp_c: float) -> float:
    """Calculate kinematic viscosity at given temperature using Walther-ASTM equation.

    Args:
        oil: Oil type (VG220 or VG320)
        temp_c: Temperature in degrees Celsius

    Returns:
        Kinematic viscosity in cSt (mm²/s)
    """
    props = OIL_PROPERTIES[oil]
    nu_40 = props["nu_40c"]
    nu_100 = props["nu_100c"]

    # Calculate Walther constants
    a, b = _calculate_walther_constants(nu_40, nu_100)

    # Convert temperature to Kelvin
    temp_k = temp_c + 273.15

    # Apply Walther equation: log(log(nu + 0.7)) = A - B * log(T)
    log_log_nu = a - b * math.log10(temp_k)
    log_nu = 10**log_log_nu
    nu = 10**log_nu - 0.7

    return nu


def get_density(oil: OilType, temp_c: float) -> float:
    """Calculate oil density at given temperature.

    Args:
        oil: Oil type (VG220 or VG320)
        temp_c: Temperature in degrees Celsius

    Returns:
        Density in kg/m³
    """
    props = OIL_PROPERTIES[oil]
    density_15c = props["density_15c"]

    # Linear thermal expansion model: ρ(T) = ρ_15 * [1 - α * (T - 15)]
    density = density_15c * (1 - THERMAL_EXPANSION_COEFF * (temp_c - 15.0))

    return density


def get_dynamic_viscosity(oil: OilType, temp_c: float) -> float:
    """Calculate dynamic viscosity from kinematic viscosity and density.

    Args:
        oil: Oil type
        temp_c: Temperature in degrees Celsius

    Returns:
        Dynamic viscosity in Pa·s
    """
    nu = get_viscosity(oil, temp_c)  # cSt
    rho = get_density(oil, temp_c)  # kg/m³

    # Convert kinematic to dynamic: μ = ν * ρ
    # Note: 1 cSt = 1 mm²/s = 1e-6 m²/s
    mu = nu * 1e-6 * rho

    return mu


def get_correction_factor(oil: OilType, temp_c: float) -> float:
    """Calculate liquid correction factor (LCF) for non-water fluids.

    The S2 GL40 is factory-calibrated for water. The LCF converts
    scale readings to actual flow rates for oils.

    Args:
        oil: Oil type
        temp_c: Temperature in degrees Celsius

    Returns:
        Liquid correction factor (dimensionless)
    """
    rho_oil = get_density(oil, temp_c)

    # LCF = sqrt[(ρ_float - ρ_oil) * ρ_water / ((ρ_float - ρ_water) * ρ_oil)]
    numerator = (FLOAT_DENSITY - rho_oil) * WATER_DENSITY
    denominator = (FLOAT_DENSITY - WATER_DENSITY) * rho_oil

    lcf = math.sqrt(numerator / denominator)

    return lcf


def calculate_orifice_diameter(
    flow_lpm: float, oil: OilType, temp_c: float, target_dp_mbar: float = 125.0
) -> float:
    """Calculate required orifice diameter for target flow rate.

    The Eletta S2 GL40 is calibrated for water. When used with oil, we must
    account for the correction factor in our sizing. The sensor will "see"
    a different flow rate than actual due to density differences.

    Args:
        flow_lpm: Target flow rate in liters per minute
        oil: Oil type
        temp_c: Temperature in degrees Celsius
        target_dp_mbar: Target differential pressure in mbar (default 125)

    Returns:
        Orifice diameter in mm
    """
    # Get correction factor - actual_flow = scale_reading × LCF
    lcf = get_correction_factor(oil, temp_c)

    # The sensor scale reading for water-equivalent flow
    scale_flow_lpm = flow_lpm / lcf
    flow_m3s = scale_flow_lpm / 60000.0

    # Use water density since sensor is calibrated for water
    rho = WATER_DENSITY

    # Convert target DP to Pa
    dp_pa = target_dp_mbar * 100.0

    # Iterative solution to account for velocity of approach factor
    # Start with initial guess assuming beta = 0.5
    diameter_mm = PIPE_DIAMETER_MM * 0.5

    for _ in range(10):  # Usually converges in 3-4 iterations
        beta = diameter_mm / PIPE_DIAMETER_MM

        # Velocity of approach factor
        epsilon = math.sqrt(1 - beta**4)

        # Orifice equation with velocity correction
        # Q = (Cd / epsilon) * A * sqrt(2*ΔP/ρ)
        # A = Q * epsilon / (Cd * sqrt(2*ΔP/ρ))
        area_m2 = (flow_m3s * epsilon) / (DISCHARGE_COEFFICIENT * math.sqrt(2 * dp_pa / rho))

        # Calculate diameter from area
        new_diameter_mm = math.sqrt(4 * area_m2 / math.pi) * 1000.0

        # Check convergence
        if abs(new_diameter_mm - diameter_mm) < 0.01:
            break

        diameter_mm = new_diameter_mm

    return diameter_mm


def get_reynolds_number(
    flow_lpm: float, orifice_diameter_mm: float, oil: OilType, temp_c: float
) -> float:
    """Calculate Reynolds number for flow through orifice.

    Args:
        flow_lpm: Flow rate in liters per minute
        orifice_diameter_mm: Orifice diameter in mm
        oil: Oil type
        temp_c: Temperature in degrees Celsius

    Returns:
        Reynolds number (dimensionless)
    """
    # Convert to SI units
    flow_m3s = flow_lpm / 60000.0
    diameter_m = orifice_diameter_mm / 1000.0

    # Calculate velocity through orifice
    area_m2 = math.pi * diameter_m**2 / 4
    velocity_ms = flow_m3s / area_m2

    # Get fluid properties
    rho = get_density(oil, temp_c)
    mu = get_dynamic_viscosity(oil, temp_c)

    # Reynolds number: Re = ρ*v*d/μ
    reynolds = rho * velocity_ms * diameter_m / mu

    return reynolds


def get_differential_pressure(
    flow_lpm: float, orifice_diameter_mm: float, oil: OilType, temp_c: float
) -> float:
    """Calculate differential pressure across orifice for given flow.

    Args:
        flow_lpm: Flow rate in liters per minute
        orifice_diameter_mm: Orifice diameter in mm
        oil: Oil type
        temp_c: Temperature in degrees Celsius

    Returns:
        Differential pressure in mbar
    """
    # Convert to SI units
    flow_m3s = flow_lpm / 60000.0
    diameter_m = orifice_diameter_mm / 1000.0
    area_m2 = math.pi * diameter_m**2 / 4

    # Get fluid density
    rho = get_density(oil, temp_c)

    # Orifice flow equation: Q = Cd * A * sqrt(2*ΔP/ρ)
    # Solve for ΔP: ΔP = (Q / (Cd * A))² * ρ / 2
    velocity_term = flow_m3s / (DISCHARGE_COEFFICIENT * area_m2)
    dp_pa = velocity_term**2 * rho / 2

    # Convert to mbar (1 mbar = 100 Pa)
    dp_mbar = dp_pa / 100.0

    return dp_mbar


def get_beta_ratio(orifice_diameter_mm: float) -> float:
    """Calculate beta ratio (orifice/pipe diameter ratio).

    Args:
        orifice_diameter_mm: Orifice diameter in mm

    Returns:
        Beta ratio (dimensionless)
    """
    return orifice_diameter_mm / PIPE_DIAMETER_MM


def validate_operating_conditions(
    flow_lpm: float, orifice_diameter_mm: float, oil: OilType, temp_c: float
) -> list[str]:
    """Validate that operating conditions are within sensor limits.

    Args:
        flow_lpm: Flow rate in liters per minute
        orifice_diameter_mm: Orifice diameter in mm
        oil: Oil type
        temp_c: Temperature in degrees Celsius

    Returns:
        List of warning messages (empty if all conditions valid)
    """
    warnings = []

    # Check Reynolds number
    reynolds = get_reynolds_number(flow_lpm, orifice_diameter_mm, oil, temp_c)
    if reynolds < MIN_REYNOLDS:
        warnings.append(
            f"Reynolds number {reynolds:.0f} < {MIN_REYNOLDS} - "
            "Flow may be laminar, reducing measurement accuracy"
        )

    # Check beta ratio
    beta = get_beta_ratio(orifice_diameter_mm)
    if beta < MIN_BETA or beta > MAX_BETA:
        warnings.append(
            f"Beta ratio {beta:.3f} outside valid range "
            f"[{MIN_BETA}-{MAX_BETA}] - May cause measurement errors"
        )

    # Check differential pressure
    dp = get_differential_pressure(flow_lpm, orifice_diameter_mm, oil, temp_c)
    if dp < MIN_DP_MBAR or dp > MAX_DP_MBAR:
        warnings.append(
            f"Differential pressure {dp:.1f} mbar outside S2 range "
            f"[{MIN_DP_MBAR}-{MAX_DP_MBAR} mbar]"
        )

    return warnings
