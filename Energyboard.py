import time  # to simulate a real time data, time loop
from datetime import datetime
import streamlit as st
import pydeck as pdk
import pandas as pd
import numpy as np
import plotly.express as px
from streamlit_extras.stylable_container import stylable_container
import random

# Configuration for file paths
EXCEL_PATHS = {
    'energy': 'E_H.xlsx',  # Current path in repository
    'other': 'E_P.xlsx'  # Add your second Excel file name here
}

# Initialize session state variables
for i in range(4):
    if f'show_chart_{i}' not in st.session_state:
        st.session_state[f'show_chart_{i}'] = False

st.markdown(
    "<h1 style='text-align: center;'>Energy Board FFB</h1>",
    unsafe_allow_html=True
)

# Add this near the top of your app
if st.button('🔄 Refresh Data'):
    st.cache_data.clear()
    st.rerun()

# Modify the cache decorator to expire after a short time
@st.cache_data(ttl=5)  # Cache expires after 5 seconds
def load_excel_data():
    """Load and process data from Excel files"""
    try:
        # Load energy data from Hiltrup Excel file
        df_hiltrup = pd.read_excel(
            EXCEL_PATHS['energy'], 
            sheet_name='Fest', 
            skiprows=2
        )
        
        # Load energy data from Pre-Fab Excel file
        df_prefab = pd.read_excel(
            EXCEL_PATHS['other'], 
            sheet_name='Fest', 
            skiprows=2
        )
        
        # Get last non-NaN values for each column
        column_d = df_hiltrup.iloc[:, 3]  # Column D (Hiltrup Energy)
        column_l = df_hiltrup.iloc[:, 11]  # Column L (Hiltrup Gas)
        column_e = df_prefab.iloc[:, 4]  # Column E (Pre-Fab Energy)
        
        hiltrup_energy = column_d.dropna().iloc[-1]  # Last non-NaN value
        hiltrup_gas = column_l.dropna().iloc[-1]  # Last non-NaN value
        prefab_energy = column_e.dropna().iloc[-1]  # Last non-NaN value
        
        # Prepare for future Pre-Fab gas data (Column N will be index 13)
        try:
            column_n = df_prefab.iloc[:, 13]  # Column N (Pre-Fab Gas)
            prefab_gas = column_n.dropna().iloc[-1]  # Last non-NaN value
        except:
            prefab_gas = 0  # Default to 0 if data not yet available
        
        return {
            'hiltrup_energy': hiltrup_energy,
            'prefab_energy': prefab_energy,
            'hiltrup_gas': hiltrup_gas,
            'prefab_gas': prefab_gas
        }
    except Exception as e:
        st.error(f"Error loading Excel files: {str(e)}")
        return {
            'hiltrup_energy': 0,
            'prefab_energy': 0,
            'hiltrup_gas': 0,
            'prefab_gas': 0
        }

# Load the data
data = load_excel_data()

# Create an empty placeholder
placeholder = st.empty()

with placeholder.container():
    # Create KPI columns
    kpi1, kpi2, kpi3 = st.columns(3)
    
    # Update the Hiltrup metric with actual data from Excel
    kpi1.metric(
        label="Stromverbrauch Hiltrup",
        value=f"{round(data['hiltrup_energy'])}kWh",
        delta=None  # Remove delta for now, or calculate it based on historical data if needed
    )

    # Update the Pre-Fab metric with actual data from Excel
    kpi2.metric(
        label="Stromverbrauch Pre-Fab",
        value=f"{round(data['prefab_energy'])}kWh",
        delta=None  # Remove delta for now, or calculate it based on historical data if needed
    )

    # For now, keeping PV Dach Strom as placeholder
    kpi3.metric(
        label="PV Dach Strom",
        value="0 kWh",  # Replace with actual data when available
        delta=None
    )

    # Add a small space between rows
    st.markdown("<br>", unsafe_allow_html=True)

    # Second row of KPIs
    kpi4, kpi5, kpi6 = st.columns(3)
    
    # Update second row metrics with actual data
    kpi4.metric(
        label="Gasverbrauch Hiltrup",
        value=f"{round(data['hiltrup_gas'])}kWh",  # Now using actual gas consumption data
        delta=None
    )

    kpi5.metric(
        label="Gasverbrauch Pre-Fab",
        value=f"{round(data['prefab_gas'])}kWh",  # Will show 0 until data is available
        delta=None
    )

    kpi6.metric(
        label="PV PPA Strom",
        value="0 kWh",  # Replace with actual data when available
        delta=None
    )
    #time.sleep(5)

st.markdown("---")  # Add a separator

# Create a layout with two columns: map on left (wider) and boxes on right
left_col, right_col = st.columns([2, 1])  # 2:1 ratio

with left_col:
    # Create markers data for different locations in Münster
    markers_data = pd.DataFrame({
        'lat': [
            51.90420411948579,  # Hiltrup
            51.88415475117976,  # Pre Fab
            51.881361014123534,  # Fab
            51.87670010770188,   # Solar Plant (1st point)
            51.87183001556695,   # Solar Plant (2nd point)
            51.87157930783964    # Solar Plant (3rd point)
        ],
        'lon': [
            7.653420120874677,   # Hiltrup
            7.5811485841790285,  # Pre Fab
            7.577477778349916,   # Fab
            7.578040913354053,   # Solar Plant (1st point)
            7.577768505780002,   # Solar Plant (2nd point)
            7.580829529041081    # Solar Plant (3rd point)
        ],
        'name': [
            'Hiltrup', 
            'Pre Fab', 
            'Fab', 
            'Solar Plant 1', 
            'Solar Plant 2', 
            'Solar Plant 3'
        ],
        'icon_type': ['circle'] * 6,
        'color': [
            [57, 193, 205],  # #39c1cd (Light blue) for Hiltrup
            [28, 149, 163],  # #1c95a3 (Medium-light blue) for Pre Fab
            [13, 95, 111],    # #0d5f6f (Medium-dark blue) for Fab
            [0, 42, 59],     # #002a3b (Dark blue) for Solar Plant
            [0, 42, 59],     # #002a3b (Dark blue) for Solar Plant
            [0, 42, 59]      # #002a3b (Dark blue) for Solar Plant
        ]
    })

    view_state = pdk.ViewState(
    latitude=51.88916099819016,  # New starting latitude for Hiltrup
    longitude=7.6051777337444815,  # New starting longitude for Hiltrup
    zoom=12                       # Adjust zoom level as needed
)


    # Create a single ScatterplotLayer for all markers
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

