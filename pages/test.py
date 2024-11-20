import time  # to simulate a real time data, time loop

import streamlit as st
import pydeck as pdk
import pandas as pd
import numpy as np
import plotly.express as px
from streamlit_extras.stylable_container import stylable_container


import requests

# Test the API endpoint
url = "https://smard.api.proxy.bund.dev/app/chart_data/1223/DE/1223_DE_hour_5.json"
response = requests.get(url)

print(f"Status Code: {response.status_code}")
if response.status_code == 200:
    print("API is working!")
    data = response.json()
    print("\nFirst few items of data:")
    print(data)
else:
    print(f"API error: {response.status_code}")

