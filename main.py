#!/usr/bin/env python3
"""Eletta S2 GL40 Calibration Tool - CLI Entry Point.

Command-line interface for calculating orifice diameters when using
the Eletta S2 GL40 differential pressure flow monitor with VG220/VG320 oils.
"""

import argparse
import sys
from typing import Optional

from src.calibrator import (
    OilType,
    calculate_orifice_diameter,
    get_beta_ratio,
    get_correction_factor,
    get_density,
    get_differential_pressure,
    get_dynamic_viscosity,
    get_reynolds_number,
    get_viscosity,
    validate_operating_conditions,
)


def print_header() -> None:
    """Print formatted header."""
    print("═" * 55)
    print("  ELETTA S2 GL40 CALIBRATION RESULTS")
    print("═" * 55)
    print()


def print_separator() -> None:
    """Print section separator."""
    print("─" * 55)


def print_footer() -> None:
    """Print formatted footer."""
    print("═" * 55)


def format_fluid_properties(oil: OilType, temp_c: float) -> None:
    """Print formatted fluid properties section.

    Args:
        oil: Oil type
        temp_c: Temperature in degrees Celsius
    """
    # Get fluid properties
    kinematic_visc = get_viscosity(oil, temp_c)
    dynamic_visc = get_dynamic_viscosity(oil, temp_c)
    density = get_density(oil, temp_c)

    print(f"Fluid Properties @ {temp_c}°C:")
    print(f"  Kinematic Viscosity:  {kinematic_visc:.1f} cSt")
    print(f"  Dynamic Viscosity:    {dynamic_visc * 1000:.1f} mPa·s")
    print(f"  Density:              {density:.0f} kg/m³")
    print()


def format_calculation_results(
    oil: OilType, temp_c: float, flow_lpm: float
) -> None:
    """Print formatted calculation results.

    Args:
        oil: Oil type
        temp_c: Temperature in degrees Celsius
        flow_lpm: Flow rate in liters per minute
    """
    # Calculate all parameters
    orifice_d = calculate_orifice_diameter(flow_lpm, oil, temp_c)
    beta = get_beta_ratio(orifice_d)
    lcf = get_correction_factor(oil, temp_c)
    reynolds = get_reynolds_number(flow_lpm, orifice_d, oil, temp_c)
    dp = get_differential_pressure(flow_lpm, orifice_d, oil, temp_c)

    print("Calculated Results:")
    print(f"  Orifice Diameter:     {orifice_d:.1f} mm")
    print(f"  Beta Ratio:           {beta:.3f}")
    print(f"  Correction Factor:    {lcf:.3f}")
    print(f"  Reynolds Number:      {reynolds:,.0f}")
    print(f"  Differential Pressure: {dp:.0f} mbar")
    print()

    # Validate operating conditions
    warnings = validate_operating_conditions(flow_lpm, orifice_d, oil, temp_c)

    if warnings:
        print("⚠ Warnings:")
        for warning in warnings:
            print(f"  - {warning}")
        print()
        print("Status: ⚠ Some parameters outside recommended range")
    else:
        print("Status: ✓ All parameters within valid range")


def single_point_calculation(
    oil: OilType, temp_c: float, flow_lpm: float
) -> None:
    """Perform single point calculation and display results.

    Args:
        oil: Oil type
        temp_c: Temperature in degrees Celsius
        flow_lpm: Flow rate in liters per minute
    """
    print_header()

    # Input parameters
    print("Input Parameters:")
    print(f"  Oil Type:        {oil.value}")
    print(f"  Temperature:     {temp_c} °C")
    print(f"  Target Flow:     {flow_lpm} L/min")
    print()

    # Fluid properties
    format_fluid_properties(oil, temp_c)

    # Calculation results
    format_calculation_results(oil, temp_c, flow_lpm)

    print_footer()


def flow_range_table(
    oil: OilType, temp_c: float, flow_min: float, flow_max: float, steps: int = 10
) -> None:
    """Generate calibration table across flow range.

    Args:
        oil: Oil type
        temp_c: Temperature in degrees Celsius
        flow_min: Minimum flow rate in liters per minute
        flow_max: Maximum flow rate in liters per minute
        steps: Number of steps in the table
    """
    print_header()

    # Input parameters
    print("Input Parameters:")
    print(f"  Oil Type:        {oil.value}")
    print(f"  Temperature:     {temp_c} °C")
    print(f"  Flow Range:      {flow_min}-{flow_max} L/min")
    print()

    # Fluid properties
    format_fluid_properties(oil, temp_c)

    # Table header
    print("Calibration Table:")
    print()
    print(f"{'Flow':>8}  {'Orifice':>8}  {'Beta':>6}  {'Reynolds':>10}  {'ΔP':>6}  {'Status':>6}")
    print(f"{'(L/min)':>8}  {'(mm)':>8}  {'(-)':>6}  {'(-)':>10}  {'(mbar)':>6}  {' ':>6}")
    print_separator()

    # Calculate for each flow point
    flow_step = (flow_max - flow_min) / (steps - 1)
    for i in range(steps):
        flow = flow_min + i * flow_step

        # Calculate parameters
        orifice_d = calculate_orifice_diameter(flow, oil, temp_c)
        beta = get_beta_ratio(orifice_d)
        reynolds = get_reynolds_number(flow, orifice_d, oil, temp_c)
        dp = get_differential_pressure(flow, orifice_d, oil, temp_c)

        # Check for warnings
        warnings = validate_operating_conditions(flow, orifice_d, oil, temp_c)
        status = "⚠" if warnings else "✓"

        print(
            f"{flow:8.1f}  {orifice_d:8.1f}  {beta:6.3f}  {reynolds:10,.0f}  {dp:6.0f}  {status:>6}"
        )

    print()
    print_footer()


def properties_only(oil: OilType, temp_c: float) -> None:
    """Display only fluid properties.

    Args:
        oil: Oil type
        temp_c: Temperature in degrees Celsius
    """
    print_header()

    print("Input Parameters:")
    print(f"  Oil Type:        {oil.value}")
    print(f"  Temperature:     {temp_c} °C")
    print()

    format_fluid_properties(oil, temp_c)

    lcf = get_correction_factor(oil, temp_c)
    print(f"Correction Factor:    {lcf:.3f}")
    print()

    print_footer()


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="Eletta S2 GL40 Calibration Tool for VG220/VG320 Oils",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single point calculation
  %(prog)s --oil VG220 --temp 50 --flow 150

  # Generate flow table
  %(prog)s --oil VG320 --temp 40 --flow-range 10 250

  # Show fluid properties only
  %(prog)s --oil VG220 --temp 60 --props-only
        """,
    )

    parser.add_argument(
        "--oil",
        type=str,
        choices=["VG220", "VG320"],
        required=True,
        help="Oil type: VG220 or VG320",
    )

    parser.add_argument(
        "--temp",
        type=float,
        required=True,
        help="Operating temperature in °C",
        metavar="TEMP",
    )

    parser.add_argument(
        "--flow", type=float, help="Target flow rate in L/min", metavar="FLOW"
    )

    parser.add_argument(
        "--flow-range",
        type=float,
        nargs=2,
        help="Min and max flow for table (L/min)",
        metavar=("MIN", "MAX"),
    )

    parser.add_argument(
        "--props-only",
        action="store_true",
        help="Show fluid properties only",
    )

    return parser.parse_args()


def validate_args(args: argparse.Namespace) -> Optional[str]:
    """Validate command-line arguments.

    Args:
        args: Parsed arguments

    Returns:
        Error message if validation fails, None otherwise
    """
    # Check that exactly one of flow, flow_range, or props_only is specified
    modes = sum([args.flow is not None, args.flow_range is not None, args.props_only])
    if modes == 0:
        return "Error: Must specify --flow, --flow-range, or --props-only"
    if modes > 1:
        return "Error: Can only specify one of --flow, --flow-range, or --props-only"

    # Validate temperature range
    if args.temp < 20 or args.temp > 80:
        return f"Warning: Temperature {args.temp}°C outside validated range (20-80°C)"

    # Validate flow rate
    if args.flow is not None:
        if args.flow <= 0 or args.flow > 250:
            return f"Error: Flow rate {args.flow} L/min outside valid range (0-250)"

    # Validate flow range
    if args.flow_range is not None:
        flow_min, flow_max = args.flow_range
        if flow_min <= 0 or flow_max > 250:
            return f"Error: Flow range outside valid range (0-250 L/min)"
        if flow_min >= flow_max:
            return "Error: Minimum flow must be less than maximum flow"

    return None


def main() -> int:
    """Main entry point.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    args = parse_args()

    # Validate arguments
    error = validate_args(args)
    if error:
        if error.startswith("Error"):
            print(error, file=sys.stderr)
            return 1
        else:
            # Warning - print but continue
            print(error, file=sys.stderr)

    # Parse oil type
    oil = OilType.VG220 if args.oil == "VG220" else OilType.VG320

    try:
        # Dispatch to appropriate function
        if args.props_only:
            properties_only(oil, args.temp)
        elif args.flow is not None:
            single_point_calculation(oil, args.temp, args.flow)
        elif args.flow_range is not None:
            flow_min, flow_max = args.flow_range
            flow_range_table(oil, args.temp, flow_min, flow_max)

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
