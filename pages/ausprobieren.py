import pandas as pd
import streamlit as st

# Load the Excel file
def get_last_values():
    try:
        df = pd.read_excel('E_H.xlsx', sheet_name='Fest', skiprows=2)
        
        # Get last non-NaN value specifically from Column D
        column_d = df.iloc[:, 3]  # Get Column D
        last_energy_value = column_d.dropna().iloc[-1]  # Get last non-NaN value
        last_energy_index = column_d.dropna().index[-1]  # Get its index
        
        st.write("### Column D Analysis:")
        st.write(f"Last non-NaN value in Column D: {last_energy_value}")
        st.write(f"Found in row: {last_energy_index + 3}")  # +3 because we skipped 2 rows
        
        # Show last 5 non-NaN values for context
        st.write("### Last 5 non-NaN values in Column D:")
        last_5_values = column_d.dropna().tail(5)
        for idx, value in last_5_values.items():
            st.write(f"Row {idx + 3}: {value}")
        
        return {
            'Column D (Energy)': last_energy_value,
            'Row number': last_energy_index + 3
        }
    except Exception as e:
        st.error(f"Error reading Excel: {str(e)}")
        return None

# Display the values
st.title("Excel Last Values Debug")
values = get_last_values()

if values:
    st.write("### Last Values from E_H.xlsx:")
    for key, value in values.items():
        st.write(f"**{key}:** {value}")
