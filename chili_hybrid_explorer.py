
import streamlit as st
import pandas as pd
import altair as alt

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

# File upload
uploaded_file = st.file_uploader("Upload your Hybrid Chili Combinations Excel file", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)

    # Display instructions
    st.info("Use the dropdowns and slider below to filter your hybrids by climate suitability and heat levels.")

    # Filter by climate suitability
    climate_filter = st.selectbox("Select Climate Suitability:", options=["All", "High", "Medium"])
    if climate_filter != "All":
        df = df[df['Climate Suitability (Cyprus)'] == climate_filter]

    # Filter by minimum expected heat
    min_heat = st.slider("Minimum Expected Heat (SHU)", min_value=0, max_value=int(df['Expected Heat (SHU)'].max()), step=50000, value=0)
    df = df[df['Expected Heat (SHU)'] >= min_heat]

    # Color-coding heat levels
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

    # Bar chart: Heat vs. Expected Yield
    st.write("## Heat vs. Expected Yield Chart")
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('Expected Heat (SHU):Q', bin=alt.Bin(maxbins=20), title='Expected Heat (SHU)'),
        y='count()',
        color=alt.Color('Expected Yield:N', scale=alt.Scale(scheme='redyellowgreen'))
    ).properties(width=800, height=400)

    st.altair_chart(chart, use_container_width=True)

    # Download button
    st.download_button("Download Filtered Data as CSV", df.to_csv(index=False), "filtered_hybrids.csv", "text/csv")

else:
    st.warning("Please upload your Excel file to explore the data.")
