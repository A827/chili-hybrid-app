
import streamlit as st
import pandas as pd

st.title("Chili Hybrid Combinations Explorer")

uploaded_file = st.file_uploader("Upload your Hybrid Chili Combinations Excel file", type=["xlsx"])
if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    st.write("## All Hybrid Combinations")
    st.dataframe(df)
    
    # Filter by climate suitability
    climate_filter = st.selectbox("Select Climate Suitability:", options=["All", "High", "Medium"])
    if climate_filter != "All":
        df = df[df['Climate Suitability (Cyprus)'] == climate_filter]
    
    # Filter by minimum expected heat
    min_heat = st.slider("Minimum Expected Heat (SHU)", min_value=0, max_value=3000000, step=50000, value=0)
    df = df[df['Expected Heat (SHU)'] >= min_heat]
    
    # Display filtered data
    st.write("## Filtered Hybrid Combinations")
    st.dataframe(df)
    
    # Download button
    st.download_button("Download Filtered Data as CSV", df.to_csv(index=False), "filtered_hybrids.csv", "text/csv")
