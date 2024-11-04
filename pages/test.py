import time  # to simulate a real time data, time loop

import streamlit as st
import pydeck as pdk
import pandas as pd
import numpy as np
import plotly.express as px
from streamlit_extras.stylable_container import stylable_container


# Now you can use stylable_container like this:
with stylable_container(
    key="test_container",
    css_styles="""
        button {
            background-color: red;
            color: white;
            border-radius: 5px;
            padding: 10px 20px;
        }
        button:hover {
            background-color: darkred;
            color: white;
        }
    """,
):
    if st.button("Click me!", key="test_button"):
        st.write("Button clicked")

