import time  # to simulate a real time data, time loop
import streamlit as st
import numpy as np
import pandas as pd

st.markdown(
    "<h1 style='text-align: center;'>Energy Board FFB</h1>",
    unsafe_allow_html=True
)


# read csv from a github repo
url = 'https://raw.githubusercontent.com/MatScie24/blank-app/refs/heads/main/Book1.csv'

# read csv from a URL
@st.cache_data
def get_data() -> pd.DataFrame:
    return pd.read_csv(url)

df = get_data()

avg_halloeins = np.mean(df["Halloeins"])
avg_hallozwei = np.mean(df["Hallozwei"])
avg_hallodrei = np.mean(df["Hallodrei"])

row1 = st.columns(3)

for col in row1:
    tile = col.container(height=150)
    tile.subheader("Hallo")
    tile.button(f"Energieverbrauch in:{avg_halloeins}")



# Generate random data around Münster
map_data = pd.DataFrame(
    np.random.randn(1000, 2) / [50, 50] + [51.9375, 7.6257],  # Coordinates for Münster
    columns=['lat', 'lon'],
)

# Display the map
st.map(map_data)
