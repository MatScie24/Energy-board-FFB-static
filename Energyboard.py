import time
from datetime import datetime, timedelta
import streamlit as st
import pydeck as pdk
import pandas as pd
import numpy as np
import plotly.express as px
from streamlit_extras.stylable_container import stylable_container
import random
import requests
import matplotlib.pyplot as plt

# Initialize session state variables
for i in range(4):
    if f'show_chart_{i}' not in st.session_state:
        st.session_state[f'show_chart_{i}'] = False

st.markdown(
    "<h1 style='text-align: center;'>Energy Board FFB</h1>",
    unsafe_allow_html=True
)

# Create an empty placeholder for live data
placeholder = st.empty()

@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_live_data():
    try:
        # SMARD API endpoints
        base_url = "https://smard.api.proxy.bund.dev/app/chart_data/1223/DE/1223_DE_hour_1.json"
        
        # Get timestamps for the last 24 hours
        end_time = int(datetime.now().replace(minute=0, second=0, microsecond=0).timestamp() * 1000)
        start_time = int((datetime.now().replace(minute=0, second=0, microsecond=0) - timedelta(hours=24)).timestamp() * 1000)
        
        # Filter IDs for different types of data:
        # 4359 = Solar (Actual Generation)
        # 4066 = Gas (Natural Gas Consumption)
        # 122 = Total Load (Consumption)
        
        # Debug print
        st.write(f"Fetching data from {start_time} to {end_time}")
        
        # Fetch solar generation
        solar_url = f"{base_url}/4359/DE/DE/{start_time}/{end_time}"
        solar_response = requests.get(solar_url)
        if solar_response.status_code != 200:
            st.error(f"Solar API Error: Status {solar_response.status_code}")
            st.write(f"Solar URL: {solar_url}")
            return None
        solar_data = solar_response.json()
        
        # Fetch gas consumption
        gas_url = f"{base_url}/4066/DE/DE/{start_time}/{end_time}"
        gas_response = requests.get(gas_url)
        if gas_response.status_code != 200:
            st.error(f"Gas API Error: Status {gas_response.status_code}")
            st.write(f"Gas URL: {gas_url}")
            return None
        gas_data = gas_response.json()
        
        # Fetch total load
        load_url = f"{base_url}/122/DE/DE/{start_time}/{end_time}"
        load_response = requests.get(load_url)
        if load_response.status_code != 200:
            st.error(f"Load API Error: Status {load_response.status_code}")
            st.write(f"Load URL: {load_url}")
            return None
        load_data = load_response.json()
        
        # Debug prints
        st.write("Solar Data:", solar_data)
        st.write("Gas Data:", gas_data)
        st.write("Load Data:", load_data)
        
        # Get the most recent values
        latest_solar = solar_data['series'][-1]['value'] if 'series' in solar_data else 0
        latest_gas = gas_data['series'][-1]['value'] if 'series' in gas_data else 0
        latest_load = load_data['series'][-1]['value'] if 'series' in load_data else 0
        
        # Convert to appropriate scale (values are in MW, convert to kW)
        return {
            'hiltrup_power': latest_load / 1000,
            'prefab_power': latest_load / 2000,
            'pv_roof_power': latest_solar / 1000,
            'hiltrup_gas': latest_gas / 1000,
            'prefab_gas': latest_gas / 2000,
            'pv_ppa_power': latest_solar / 1500
        }
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        st.write("Full error:", e)
        # Return default values
        return {
            'hiltrup_power': 0,
            'prefab_power': 0,
            'pv_roof_power': 0,
            'hiltrup_gas': 0,
            'prefab_gas': 0,
            'pv_ppa_power': 0
        }

# Live data update loop
while True:
    live_data = fetch_live_data()
    
    if live_data is None:
        st.error("Failed to fetch data, retrying in 5 minutes...")
        time.sleep(300)
        continue
        
    with placeholder.container():
        # First row of KPIs
        kpi1, kpi2, kpi3 = st.columns(3)
        
        kpi1.metric(
            label="Stromverbrauch Hiltrup",
            value=f"{round(live_data['hiltrup_power'])}kWh",
            delta=round(live_data['hiltrup_power'] - 10),
        )

        kpi2.metric(
            label="Stromverbrauch Pre-Fab",
            value=f"{round(live_data['prefab_power'])}kWh",
            delta=round(live_data['prefab_power'] - 10),
        )

        kpi3.metric(
            label="PV Dach Strom",
            value=f"{round(live_data['pv_roof_power'])}kWh",
            delta=round(live_data['pv_roof_power'] - 10),
        )

        # Add a small space between rows
        st.markdown("<br>", unsafe_allow_html=True)

        # Second row of KPIs
        kpi4, kpi5, kpi6 = st.columns(3)
        
        kpi4.metric(
            label="Gasverbrauch Hiltrup",
            value=f"{round(live_data['hiltrup_gas'])}kWh",
            delta=round(live_data['hiltrup_gas'] - 5),
        )

        kpi5.metric(
            label="Gasverbrauch Pre-Fab",
            value=f"{round(live_data['prefab_gas'])}kWh",
            delta=round(live_data['prefab_gas'] - 5),
        )

        kpi6.metric(
            label="PV PPA Strom",
            value=f"{round(live_data['pv_ppa_power'])}kWh",
            delta=round(live_data['pv_ppa_power'] - 5),
        )

        time.sleep(300)  # Update every 5 minutes

st.markdown("---")  # Add a separator

# Create a layout with two columns: map on left (wider) and boxes on right
left_col, right_col = st.columns([2, 1])  # 2:1 ratio

with left_col:
    # Create markers data for different locations in Münster
    markers_data = pd.DataFrame({
        'lat': [51.9375, 51.9475, 51.9275, 51.9325],
        'lon': [7.6257, 7.6357, 7.6157, 7.6307],
        'name': ['Solar Plant', 'Hiltrup', 'Pre Fab', 'Fab'],
        'icon_type': ['circle', 'circle', 'circle', 'circle'],
        'color': [
            [0, 42, 59],     # Dark blue for Solar
            [57, 193, 205],  # Light blue for Wind
            [28, 149, 163],  # Medium-light blue for Biomass
            [13, 95, 111]    # Medium-dark blue for Hydro
        ]
    })

    view_state = pdk.ViewState(
        latitude=51.9375,
        longitude=7.6257,
        zoom=12
    )

    layer = pdk.Layer(
        'ScatterplotLayer',
        markers_data,
        get_position='[lon, lat]',
        get_radius=200,
        get_fill_color='color',
        pickable=True,
        auto_highlight=True
    )

    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={
            'html': '<b>{name}</b>',
            'style': {
                'color': 'white'
            }
        }
    )

    st.pydeck_chart(deck)

# Replace the button section in the right column with this:
with right_col:
    # Solar button
    with stylable_container(
        key="solar_container",
        css_styles="""
            button {
                background-color: #39c1cd;
                color: white;
                width: 100%;
                padding: 15px 30px;
                font-size: 16px;
                font-weight: bold;
                border: none;
                border-radius: 5px;
                margin: 10px 0;
            }
            button:hover {
                background-color: #001a25;
                color: white;
                transform: translateY(-2px);
                box-shadow: 0 6px 8px rgba(0, 0, 0, 0.2);
            }
        """,
    ):
        if st.button("Solar Energy", key="solar_button"):
            for i in range(4):
                st.session_state[f'show_chart_{i}'] = (i == 0)

    # Wind button
    with stylable_container(
        key="wind_container",
        css_styles="""
            button {
                background-color: #1c95a3;
                color: white;
                width: 100%;
                padding: 15px 30px;
                font-size: 16px;
                font-weight: bold;
                border: none;
                border-radius: 5px;
                margin: 10px 0;
            }
            button:hover {
                background-color: #2ea0aa;
                color: white;
                transform: translateY(-2px);
                box-shadow: 0 6px 8px rgba(0, 0, 0, 0.2);
            }
        """,
    ):
        if st.button("Hiltrup", key="wind_button"):
            for i in range(4):
                st.session_state[f'show_chart_{i}'] = (i == 1)

    # Biomass button
    with stylable_container(
        key="biomass_container",
        css_styles="""
            button {
                background-color: #0d5f6f;
                color: white;
                width: 100%;
                padding: 15px 30px;
                font-size: 16px;
                font-weight: bold;
                border: none;
                border-radius: 5px;
                margin: 10px 0;
            }
            button:hover {
                background-color: #0000cc;
                color: white;
                transform: translateY(-2px);
                box-shadow: 0 6px 8px rgba(0, 0, 0, 0.2);
            }
        """,
    ):
        if st.button("Pre Fab", key="biomass_button"):
            for i in range(4):
                st.session_state[f'show_chart_{i}'] = (i == 2)

    # Hydro button
    with stylable_container(
        key="hydro_container",
        css_styles="""
            button {
                background-color: #002a3b;
                color: white;
                width: 100%;
                padding: 15px 30px;
                font-size: 16px;
                font-weight: bold;
                border: none;
                border-radius: 5px;
                margin: 10px 0;
            }
            button:hover {
                background-color: #cccc00;
                color: white;
                transform: translateY(-2px);
                box-shadow: 0 6px 8px rgba(0, 0, 0, 0.2);
            }
        """,
    ):
        if st.button("Fab", key="hydro_button"):
            for i in range(4):
                st.session_state[f'show_chart_{i}'] = (i == 3)

# After your map and buttons, add this code:
st.markdown("---")  # Add a separator

# Create two columns for the charts
if any(st.session_state[f'show_chart_{i}'] for i in range(4)):
    chart_cols = st.columns(2)
    
    # Dictionary mapping energy types to their data and titles
    energy_types = {
        0: {"name": "Solar", "color": "#002a3b"},
        1: {"name": "Wind", "color": "#39c1cd"},
        2: {"name": "Pre Fab", "color": "#0000ff"},
        3: {"name": "Fab", "color": "#ffff00"}
    }

    # Show charts for the selected energy type
    for i in range(4):
        if st.session_state[f'show_chart_{i}']:
            # Left column: Line chart
            with chart_cols[0]:
                st.subheader(f"{energy_types[i]['name']} Energy Production")
                # Generate sample data - replace with your actual data
                chart_data = pd.DataFrame(
                    np.random.randn(20, 1) * 20 + 100,  # Random data between ~60 and ~140
                    columns=['Production (kWh)'],
                    index=pd.date_range(start='2024-01-01', periods=20)
                )
                st.line_chart(
                    chart_data,
                    use_container_width=True
                )

            # Right column: Bar chart
            with chart_cols[1]:
                st.subheader(f"{energy_types[i]['name']} Energy Consumption")
                # Generate sample data - replace with your actual data
                chart_data = pd.DataFrame(
                    np.random.randn(20, 1) * 15 + 80,  # Random data between ~50 and ~110
                    columns=['Consumption (kWh)'],
                    index=pd.date_range(start='2024-01-01', periods=20)
                )
                st.bar_chart(
                    chart_data,
                    use_container_width=True
                )
            

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



# Add this after your map section but before the colored boxes
st.markdown("---")  # Add a separator line

# Import matplotlib
import matplotlib.pyplot as plt

# Create pie chart data
labels = ['Solar Energy', 'Hiltrup', 'Pre Fab', 'Fab']
sizes = [30, 25, 25, 20]  # Example values, adjust as needed
colors = ['#002a3b',    # Dark blue for Solar
          '#39c1cd',    # Light blue for Wind
          '#1c95a3',    # Medium-light blue for Biomass
          '#0d5f6f']    # Medium-dark blue for Hydro

# Create centered heading for the pie chart
st.markdown("<h3 style='text-align: center;'>Energy Distribution</h3>", unsafe_allow_html=True)

# Create the pie chart with dark background
fig, ax = plt.subplots(figsize=(10, 6), facecolor='#0E1117')  # Streamlit's dark background color
ax.set_facecolor('#0E1117')  # Set axis background color

wedges, texts, autotexts = ax.pie(sizes, 
                                 labels=labels, 
                                 colors=colors, 
                                 autopct='%1.1f%%', 
                                 startangle=90,
                                 wedgeprops={"linewidth": 1, "edgecolor": "white"})

# Make percentage labels white for better visibility on colored backgrounds
for autotext in autotexts:
    autotext.set_color('white')

# Make labels white
for text in texts:
    text.set_color('white')

# Equal aspect ratio ensures that pie is drawn as a circle
ax.axis('equal')  


# Set the figure background to match Streamlit's dark theme
plt.rcParams['figure.facecolor'] = '#0E1117'

# Display the pie chart
st.pyplot(fig)

