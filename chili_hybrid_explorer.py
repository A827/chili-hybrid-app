import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
import sqlite3
import io
import pickle

st.set_page_config(page_title="Chili Hybrid Explorer", layout="wide")

# Load AI model
model = None
model_file = "success_score_model.pkl"
try:
    with open(model_file, "rb") as f:
        model = pickle.load(f)
    st.sidebar.success("✅ AI model loaded successfully!")
except Exception as e:
    st.sidebar.error(f"❌ AI model failed to load: {e}")
    model = None

# Connect to SQLite database
conn = sqlite3.connect("hybrids.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS hybrids (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        parent_a TEXT,
        parent_b TEXT,
        expected_heat INTEGER,
        expected_yield TEXT,
        climate_suitability TEXT,
        expected_flavor TEXT,
        ai_success_score TEXT
    )
""")
conn.commit()

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
st.markdown('<div class="sub-header">Now Database-Driven! Add and View Hybrid Combinations Over Time</div>', unsafe_allow_html=True)

# Data entry form
st.sidebar.header("Add New Hybrid Combination")
with st.sidebar.form("add_hybrid"):
    parent_a = st.text_input("Parent A")
    parent_b = st.text_input("Parent B")
    expected_heat = st.number_input("Expected Heat (SHU)", min_value=0, step=5000)
    expected_yield = st.selectbox("Expected Yield", ["Low", "Medium", "High", "Very High"])
    climate_suitability = st.selectbox("Climate Suitability (Cyprus)", ["Low", "Medium", "High"])
    expected_flavor = st.text_input("Expected Flavor")
    submitted = st.form_submit_button("Add Hybrid")

    if submitted:
        ai_success_score = "Unknown"
        if model:
            # Prepare feature set
            input_df = pd.DataFrame({
                "Expected Heat (SHU)": [expected_heat],
                "Expected Yield": [expected_yield],
                "Climate Suitability (Cyprus)": [climate_suitability]
            })
            input_encoded = pd.get_dummies(input_df, columns=['Expected Yield', 'Climate Suitability (Cyprus)'])
            missing_cols = set(model.feature_names_in_) - set(input_encoded.columns)
            for col in missing_cols:
                input_encoded[col] = 0
            input_encoded = input_encoded[model.feature_names_in_]
            ai_success_score = model.predict(input_encoded)[0]

        cursor.execute("""
            INSERT INTO hybrids (parent_a, parent_b, expected_heat, expected_yield, climate_suitability, expected_flavor, ai_success_score)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (parent_a, parent_b, expected_heat, expected_yield, climate_suitability, expected_flavor, ai_success_score))
        conn.commit()
        st.sidebar.success(f"✅ Hybrid added with AI Success Score: {ai_success_score}")

# Load and display hybrids from database
df = pd.read_sql_query("SELECT * FROM hybrids", conn)

sort_by = st.sidebar.selectbox("Sort By:", options=["expected_heat", "expected_yield", "ai_success_score"], index=0)
df = df.sort_values(by=sort_by, ascending=False)

def highlight_heat(val):
    if val >= 1000000:
        color = '#ff4c4c'
    elif val >= 500000:
        color = '#ff944c'
    else:
        color = '#ffd24c'
    return f'background-color: {color}'

st.write("## All Hybrid Combinations (Database)")
st.dataframe(df.style.applymap(highlight_heat, subset=['expected_heat']))

# Scatter plot
st.write("## Heat vs. AI Success Score")
scatter = alt.Chart(df).mark_circle(size=100).encode(
    x=alt.X('expected_heat:Q', title='Expected Heat (SHU)'),
    y=alt.Y('ai_success_score:N', title='AI Success Score'),
    color=alt.Color('ai_success_score:N', legend=alt.Legend(title="AI Success Score")),
    tooltip=['parent_a', 'parent_b', 'expected_heat', 'expected_yield', 'climate_suitability', 'expected_flavor', 'ai_success_score']
).interactive().properties(width=800, height=400)

st.altair_chart(scatter, use_container_width=True)

# Download all data
output = io.BytesIO()
with pd.ExcelWriter(output, engine='openpyxl') as writer:
    df.to_excel(writer, index=False)
processed_data = output.getvalue()

st.download_button(
    label="Download All Hybrids as Excel",
    data=processed_data,
    file_name="all_hybrids.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

conn.close()
