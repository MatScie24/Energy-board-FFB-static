import time  # to simulate a real time data, time loop
from datetime import datetime

import streamlit as st
import pydeck as pdk
import pandas as pd
import numpy as np
import random

st.title("Energieboard Zeitstrahl")

# Create two columns for the timeline selector
time_col1, time_col2 = st.columns([3, 1])

with time_col1:
    # Create a time range slider
    selected_range = st.slider(
        "Select Time Period",
        min_value=datetime(2023, 1, 1),
        max_value=datetime(2024, 12, 31),
        value=(datetime(2023, 1, 1), datetime(2023, 12, 31)),
        format="MM/DD/YY"
    )

with time_col2:
    # Add a radio button to switch between range and specific date
    time_type = st.radio(
        "Selection Type",
        ["Range", "Specific Date"]
    )
    
    if time_type == "Specific Date":
        selected_date = st.date_input(
            "Select Date",
            datetime(2023, 1, 1)
        )

# Function to get KPI values based on time selection
def get_kpi_values(time_selection):
    # Here you would normally query your database or data source
    # For this example, we'll generate random values
    if isinstance(time_selection, tuple):
        # For range selection
        start, end = time_selection
        days_diff = (end - start).days
        multiplier = days_diff / 365  # Scale based on selected period
    else:
        # For specific date
        multiplier = 1

    return {
        'energy': round(1000 * multiplier + random.uniform(-100, 100)),
        'co2': round(500 * multiplier + random.uniform(-50, 50)),
        'cost': round(2000 * multiplier + random.uniform(-200, 200))
    }

# Get KPI values based on selection
if time_type == "Range":
    kpi_values = get_kpi_values(selected_range)
else:
    kpi_values = get_kpi_values(selected_date)

# Display KPIs in large format
st.markdown("### Key Metrics for Selected Period")
kpi_cols = st.columns(3)

with kpi_cols[0]:
    st.metric(
        label="Energieverbrauch in",
        value=f"{kpi_values['energy']:,} kWh",
        delta=f"{round(kpi_values['energy'] * 0.1):,} kWh"
    )

with kpi_cols[1]:
    st.metric(
        label="CO2 equivalent",
        value=f"{kpi_values['co2']:,} kg",
        delta=f"{round(kpi_values['co2'] * 0.1):,} kg"
    )

with kpi_cols[2]:
    st.metric(
        label="Kosten",
        value=f"{kpi_values['cost']:,} €",
        delta=f"{round(kpi_values['cost'] * 0.1):,} €"
    )