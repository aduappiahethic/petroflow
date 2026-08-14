# ============================================================
# PETROFLOW - PETROLEUM ENGINEERING FLUID FLOW ANALYZER
# PE 262 - Project 8: Vibe Coding Mini-App
#
# AI DOCUMENTATION
# ------------------------------------------------------------
# AI tool used:
# - ChatGPT (AI-assisted development)
#
# Key prompts used:
# 1. "Design a professional Streamlit fluid flow calculator
#    for a Petroleum Engineering programming project."
#
# 2. "Develop the engineering calculation model using
#    Darcy-Weisbach, Reynolds number, and the Haaland
#    friction-factor equation."
#
# 3. "Create a Streamlit application with interactive inputs,
#    error handling, a Pandas results table, and a dynamic
#    Plotly chart."
#
# Most important manual verification/fix:
# - The engineering equations, units, conversion from bbl/day
#   to m3/s, flow-regime limits, and calculated results must
#   be manually checked against engineering principles before
#   final submission.
# ============================================================

import math

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


# ------------------------------------------------------------
# PAGE CONFIGURATION
# ------------------------------------------------------------

st.set_page_config(
    page_title="PetroFlow",
    page_icon="⛽",
    layout="wide"
)


# ------------------------------------------------------------
# ENGINEERING CONSTANTS
# ------------------------------------------------------------

GRAVITY = 9.81
BBL_TO_M3 = 0.1589873
SECONDS_PER_DAY = 86400


# ------------------------------------------------------------
# ENGINEERING CALCULATION FUNCTIONS
# ------------------------------------------------------------

def calculate_area(diameter):
    """Calculate circular pipe cross-sectional area."""
    return math.pi * diameter**2 / 4


def convert_flow_rate(flow_bpd):
    """Convert flow rate from barrels/day to m3/s."""
    return flow_bpd * BBL_TO_M3 / SECONDS_PER_DAY


def calculate_velocity(flow_m3s, area):
    """Calculate average fluid velocity."""
    return flow_m3s / area


def calculate_reynolds(density, velocity, diameter, viscosity):
    """Calculate Reynolds number."""
    return density * velocity * diameter / viscosity


def determine_flow_regime(reynolds):
    """Classify flow based on Reynolds number."""

    if reynolds < 2300:
        return "Laminar"

    elif reynolds <= 4000:
        return "Transitional"

    else:
        return "Turbulent"


def calculate_friction_factor(reynolds, roughness, diameter):
    """
    Calculate Darcy friction factor.

    Laminar flow:
        f = 64 / Re

    Turbulent/non-laminar flow:
        Haaland equation
    """

    if reynolds <= 0:
        return np.nan

    if reynolds < 2300:
        return 64 / reynolds

    relative_roughness = roughness / diameter

    haaland_term = (
        (relative_roughness / 3.7) ** 1.11
        + 6.9 / reynolds
    )

    friction_factor = (
        -1.8 * math.log10(haaland_term)
    ) ** -2

    return friction_factor


def calculate_pressure_drop(
    friction_factor,
    length,
    diameter,
    density,
    velocity
):
    """Calculate Darcy-Weisbach pressure drop in Pa."""

    return (
        friction_factor
        * (length / diameter)
        * (density * velocity**2 / 2)
    )


def calculate_head_loss(
    friction_factor,
    length,
    diameter,
    velocity
):
    """Calculate Darcy-Weisbach head loss in metres."""

    return (
        friction_factor
        * (length / diameter)
        * (velocity**2 / (2 * GRAVITY))
    )


# ------------------------------------------------------------
# MAIN APPLICATION HEADER
# ------------------------------------------------------------

st.title("⛽ PetroFlow")

st.subheader("Petroleum Engineering Fluid Flow Analyzer")

st.write(
    "Enter the pipe and fluid properties in the sidebar to "
    "calculate flow velocity, Reynolds number, flow regime, "
    "friction factor, pressure drop, and head loss."
)


# ------------------------------------------------------------
# SIDEBAR INPUTS
# ------------------------------------------------------------

st.sidebar.header("⚙️ Fluid & Pipe Inputs")

diameter = st.sidebar.number_input(
    "Pipe Diameter (m)",
    min_value=0.001,
    value=0.10,
    step=0.01,
    format="%.3f"
)

length = st.sidebar.number_input(
    "Pipe Length (m)",
    min_value=0.1,
    value=1000.0,
    step=100.0,
    format="%.1f"
)

flow_rate_bpd = st.sidebar.number_input(
    "Flow Rate (bbl/day)",
    min_value=0.1,
    value=1000.0,
    step=100.0,
    format="%.1f"
)

density = st.sidebar.number_input(
    "Fluid Density (kg/m³)",
    min_value=0.1,
    value=850.0,
    step=10.0,
    format="%.1f"
)

viscosity = st.sidebar.number_input(
    "Dynamic Viscosity (Pa·s)",
    min_value=0.000001,
    value=0.005,
    step=0.001,
    format="%.6f"
)

roughness = st.sidebar.number_input(
    "Pipe Roughness (m)",
    min_value=0.0,
    value=0.000045,
    step=0.000005,
    format="%.6f"
)


# ------------------------------------------------------------
# INPUT VALIDATION
# ------------------------------------------------------------

valid_inputs = True

if diameter <= 0:
    st.warning("Pipe diameter must be greater than zero.")
    valid_inputs = False

if length <= 0:
    st.warning("Pipe length must be greater than zero.")
    valid_inputs = False

if flow_rate_bpd <= 0:
    st.warning("Flow rate must be greater than zero.")
    valid_inputs = False

if density <= 0:
    st.warning("Fluid density must be greater than zero.")
    valid_inputs = False

if viscosity <= 0:
    st.warning("Dynamic viscosity must be greater than zero.")
    valid_inputs = False

if roughness < 0:
    st.warning("Pipe roughness cannot be negative.")
    valid_inputs = False


# ============================================================
# VALID INPUT CALCULATIONS
# ============================================================

if valid_inputs:

    # --------------------------------------------------------
    # BASIC CALCULATIONS
    # --------------------------------------------------------

    area = calculate_area(diameter)

    flow_m3s = convert_flow_rate(flow_rate_bpd)

    velocity = calculate_velocity(
        flow_m3s,
        area
    )

    reynolds = calculate_reynolds(
        density,
        velocity,
        diameter,
        viscosity
    )

    flow_regime = determine_flow_regime(
        reynolds
    )

    relative_roughness = roughness / diameter

    friction_factor = calculate_friction_factor(
        reynolds,
        roughness,
        diameter
    )

    pressure_drop_pa = calculate_pressure_drop(
        friction_factor,
        length,
        diameter,
        density,
        velocity
    )

    pressure_drop_kpa = pressure_drop_pa / 1000

    head_loss = calculate_head_loss(
        friction_factor,
        length,
        diameter,
        velocity
    )


    # --------------------------------------------------------
    # TRANSITIONAL FLOW WARNING
    # --------------------------------------------------------

    if 2300 <= reynolds <= 4000:

        st.warning(
            "The calculated Reynolds number is in the "
            "transitional region (2300–4000). The Haaland "
            "equation is primarily intended for turbulent "
            "flow, so the friction-factor result should be "
            "treated with caution."
        )


    # --------------------------------------------------------
    # KEY RESULTS
    # --------------------------------------------------------

    st.header("📊 Calculation Results")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Flow Velocity",
            f"{velocity:.3f} m/s"
        )

    with col2:

        st.metric(
            "Reynolds Number",
            f"{reynolds:,.0f}"
        )

    with col3:

        st.metric(
            "Flow Regime",
            flow_regime
        )


    col4, col5, col6 = st.columns(3)

    with col4:

        st.metric(
            "Friction Factor",
            f"{friction_factor:.5f}"
        )

    with col5:

        st.metric(
            "Pressure Drop",
            f"{pressure_drop_kpa:.3f} kPa"
        )

    with col6:

        st.metric(
            "Head Loss",
            f"{head_loss:.3f} m"
        )


    # --------------------------------------------------------
    # PANDAS RESULTS TABLE
    # --------------------------------------------------------

    st.header("📋 Detailed Results")

    results_data = {
        "Parameter": [
            "Pipe Cross-Sectional Area",
            "Flow Rate",
            "Flow Velocity",
            "Reynolds Number",
            "Flow Regime",
            "Relative Roughness",
            "Darcy Friction Factor",
            "Pressure Drop",
            "Head Loss"
        ],

        "Value": [
            f"{area:.4f}",
            f"{flow_rate_bpd:.2f}",
            f"{velocity:.4f}",
            f"{reynolds:.0f}",
            flow_regime,
            f"{relative_roughness:.6f}",
            f"{friction_factor:.5f}",
            f"{pressure_drop_kpa:.3f}",
            f"{head_loss:.3f}"
        ],

        "Unit": [
            "m²",
            "bbl/day",
            "m/s",
            "dimensionless",
            "-",
            "dimensionless",
            "dimensionless",
            "kPa",
            "m"
        ]
    }

    results_df = pd.DataFrame(
        results_data
    )

    st.dataframe(
        results_df,
        width="stretch",
        hide_index=True
    )


    # --------------------------------------------------------
    # DYNAMIC PRESSURE-DROP CHART
    # --------------------------------------------------------

    st.header("📈 Pressure Drop vs. Flow Rate")

    chart_flow_bpd = np.linspace(
        max(flow_rate_bpd * 0.1, 0.1),
        flow_rate_bpd * 2.0,
        40
    )

    chart_pressure_drop_kpa = []


    for q_bpd in chart_flow_bpd:

        q_m3s = convert_flow_rate(
            q_bpd
        )

        chart_velocity = calculate_velocity(
            q_m3s,
            area
        )

        chart_reynolds = calculate_reynolds(
            density,
            chart_velocity,
            diameter,
            viscosity
        )

        chart_friction_factor = calculate_friction_factor(
            chart_reynolds,
            roughness,
            diameter
        )

        chart_dp_pa = calculate_pressure_drop(
            chart_friction_factor,
            length,
            diameter,
            density,
            chart_velocity
        )

        chart_pressure_drop_kpa.append(
            chart_dp_pa / 1000
        )


    # --------------------------------------------------------
    # CREATE PLOTLY FIGURE
    # --------------------------------------------------------

    fig = go.Figure()


    fig.add_trace(
        go.Scatter(
            x=chart_flow_bpd,
            y=chart_pressure_drop_kpa,
            mode="lines",
            name="Pressure Drop"
        )
    )


    fig.add_trace(
        go.Scatter(
            x=[flow_rate_bpd],
            y=[pressure_drop_kpa],
            mode="markers",
            name="Selected Flow Rate",
            marker=dict(
                size=10
            )
        )
    )


    fig.update_layout(
        xaxis_title="Flow Rate (bbl/day)",
        yaxis_title="Pressure Drop (kPa)",
        title="Effect of Flow Rate on Pipe Pressure Drop",
        hovermode="x unified"
    )


    st.plotly_chart(
        fig,
        width="stretch"
    )


    # --------------------------------------------------------
    # ENGINEERING NOTES
    # --------------------------------------------------------

    st.header("ℹ️ Engineering Notes")

    st.write(
        "Reynolds number is used to identify the flow regime. "
        "The Darcy friction factor is calculated using 64/Re "
        "for laminar flow and the Haaland equation for "
        "non-laminar flow. Pressure drop and head loss are "
        "calculated using the Darcy-Weisbach equation."
    )


# ============================================================
# INVALID INPUT MESSAGE
# ============================================================

else:

    st.info(
        "Please correct the invalid input values above to "
        "perform the fluid-flow calculations."
    )