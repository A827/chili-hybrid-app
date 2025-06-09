
import streamlit as st
import pandas as pd
import altair as alt
import numpy as np

st.set_page_config(page_title="Chili Hybrid Explorer", layout="wide")

# Custom header with branding
st.markdown(
    '''
    <style>
    .main-header {
        font-size:48px;
        font-weight:bold;
        color:#d7263d;
        text-align:center;
        margin-bottom:20px;
    }
    .sub-header {
        font-size:18px;
        text-align:center;
        color:#444444;
        margin-bottom:40px;
    }
    </style>
    ''',
    unsafe_allow_html=True
)

st.markdown('<div class="main-header">🌶️ Chili Hybrid Explorer 🌶️</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Explore, Analyze, and Visualize Your Hybrid Chili Combinations</div>', unsafe_allow_html=True)

# Sidebar for filters and search
st.sidebar.header("Filters & Options")

# File upload
uploaded_file = st.sidebar.file_uploader("Upload your Hybrid Chili Combinations Excel file", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)

    # Novelty checking (placeholder: mark all as "Likely Novel")
    df["Novelty Flag"] = "Likely Novel"

    # Data enrichment: add predicted flavor profile and days to harvest (placeholders)
    df["Predicted Flavor"] = df["Expected Flavor"].apply(lambda x: "Complex & Fruity")
    df["Estimated Days to Harvest"] = 90  # placeholder value

    # Search box
    search_term = st.sidebar.text_input("Search by Parent Name or Hybrid Trait:").lower()
    if search_term:
        df = df[df.apply(lambda row: search_term in row["Parent A"].lower() 
                                      or search_term in row["Parent B"].lower() 
                                      or search_term in row["Expected Flavor"].lower(), axis=1)]

    # Climate filter
    climate_filter = st.sidebar.selectbox("Select Climate Suitability:", options=["All", "High", "Medium"])
    if climate_filter != "All":
        df = df[df['Climate Suitability (Cyprus)'] == climate_filter]

    # Minimum expected heat
    min_heat = st.sidebar.slider("Minimum Expected Heat (SHU)", min_value=0, max_value=int(df['Expected Heat (SHU)'].max()), step=50000, value=0)
    df = df[df['Expected Heat (SHU)'] >= min_heat]

    # Sorting option
    sort_by = st.sidebar.selectbox("Sort By:", options=["Expected Heat (SHU)", "Expected Yield", "Novelty Flag"])
    df = df.sort_values(by=sort_by, ascending=False)

    # Display main dataframe with highlights
    def highlight_heat(val):
        if val >= 1000000:
            color = '#ff4c4c'  # Red
        elif val >= 500000:
            color = '#ff944c'  # Orange
        else:
            color = '#ffd24c'  # Yellow
        return f'background-color: {color}'

    st.write("## Filtered Hybrid Combinations")
    st.dataframe(df.style.applymap(highlight_heat, subset=['Expected Heat (SHU)']))

    # Scatter plot: Heat vs. Estimated Days to Harvest
    st.write("## Heat vs. Estimated Days to Harvest")
    scatter = alt.Chart(df).mark_circle(size=100).encode(
        x=alt.X('Expected Heat (SHU):Q', title='Expected Heat (SHU)'),
        y=alt.Y('Estimated Days to Harvest:Q', title='Estimated Days to Harvest'),
        color=alt.Color('Novelty Flag:N', legend=alt.Legend(title="Novelty")),
        tooltip=['Parent A', 'Parent B', 'Expected Heat (SHU)', 'Estimated Days to Harvest', 'Predicted Flavor']
    ).interactive().properties(width=800, height=400)

    st.altair_chart(scatter, use_container_width=True)

    # Download filtered data as Excel
    st.download_button(
        label="Download Filtered Data as Excel",
        data=df.to_excel(index=False, engine='openpyxl'),
        file_name="filtered_hybrids.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

else:
    st.warning("Please upload your Excel file to explore the data.")
