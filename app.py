import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
import pickle
from src.database import query_db
from src.fetch_data import fetch_crisis_data
from src.process_data import process_data

# ── Page Config ────────────────────────────────────
st.set_page_config(
    page_title="🌍 Climate Crisis Intelligence Platform",
    page_icon="🌍",
    layout="wide"
)

# ── Title ──────────────────────────────────────────
st.title("🌍 Climate Crisis Intelligence Platform")
st.markdown("**Real-time global disaster monitoring powered by ML**")
st.divider()

# ── Load Data ──────────────────────────────────────
@st.cache_data
def load_data():
    return pd.read_csv("data/processed/crisis_processed.csv")

df = load_data()

# ── Sidebar Filters ────────────────────────────────
st.sidebar.title("🔍 Filters")
severity_filter = st.sidebar.multiselect(
    "Filter by Severity",
    options=df['severity'].unique(),
    default=df['severity'].unique()
)

country_search = st.sidebar.text_input("Search Country")

# Apply filters
filtered_df = df[df['severity'].isin(severity_filter)]
if country_search:
    filtered_df = filtered_df[
        filtered_df['country'].str.contains(country_search, case=False, na=False)
    ]

# ── KPI Cards ──────────────────────────────────────
st.subheader("📊 Overview")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Events", len(filtered_df))
with col2:
    red_count = len(filtered_df[filtered_df['severity'] == 'Red'])
    st.metric("🔴 Red Alerts", red_count)
with col3:
    orange_count = len(filtered_df[filtered_df['severity'] == 'Orange'])
    st.metric("🟠 Orange Alerts", orange_count)
with col4:
    recent = len(filtered_df[filtered_df['is_recent'] == 1])
    st.metric("📅 Recent (2024+)", recent)

st.divider()
# ── World Map ──────────────────────────────────────
st.subheader("🗺️ Global Disaster Map")



@st.cache_data
def get_coordinates():
    coords = {
        'Afghanistan': (33.93, 67.71),
        'Indonesia': (-0.79, 113.92),
        'Brazil': (-14.24, -51.93),
        'Kenya': (-0.02, 37.91),
        'Japan': (36.20, 138.25),
        'China': (35.86, 104.19),
        'Madagascar': (-18.77, 46.87),
        'Angola': (-11.20, 17.87),
        'Argentina': (-38.42, -63.62),
        'Mexico': (23.63, -102.55),
        'Russia': (61.52, 105.32),
        'Philippines': (12.88, 121.77),
        'India': (20.59, 78.96),
        'USA': (37.09, -95.71),
        'Australia': (-25.27, 133.77),
    }
    return coords

coords = get_coordinates()

map_df = filtered_df.copy()
map_df['lat'] = map_df['country'].map(lambda x: coords.get(x, (None, None))[0])
map_df['lon'] = map_df['country'].map(lambda x: coords.get(x, (None, None))[1])
map_df = map_df.dropna(subset=['lat', 'lon'])

color_map_severity = {'Red': 'red', 'Orange': 'orange', 'Green': 'green'}

fig_map = go.Figure(go.Scattergeo(
    lat=map_df['lat'],
    lon=map_df['lon'],
    text=map_df['title'] + '<br>' + map_df['country'] + '<br>Severity: ' + map_df['severity'],
    marker=dict(
        color=map_df['severity'].map(color_map_severity),
        size=12,
        opacity=0.8,
        line=dict(width=1, color='white')
    ),
    hoverinfo='text'
))

fig_map.update_layout(
    geo=dict(
        showframe=False,
        showcoastlines=True,
        projection_type='natural earth',
        bgcolor='rgba(0,0,0,0)'
    ),
    margin=dict(l=0, r=0, t=0, b=0),
    height=450,
    paper_bgcolor='rgba(0,0,0,0)'
)

st.plotly_chart(fig_map, use_container_width=True)
# ── Charts Row 1 ───────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("🌪️ Events by Disaster Type")
    type_cols = [col for col in filtered_df.columns if col.startswith('type_')]
    type_counts = filtered_df[type_cols].sum().reset_index()
    type_counts.columns = ['Type', 'Count']
    type_counts['Type'] = type_counts['Type'].str.replace('type_', '')
    fig1 = px.bar(type_counts, x='Type', y='Count',
                  color='Count', color_continuous_scale='Reds')
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("🚨 Severity Distribution")
    severity_counts = filtered_df['severity'].value_counts().reset_index()
    severity_counts.columns = ['Severity', 'Count']
    color_map = {'Red': '#ff4444', 'Orange': '#ff8800', 'Green': '#00cc44'}
    fig2 = px.pie(severity_counts, values='Count', names='Severity',
                  color='Severity', color_discrete_map=color_map)
    st.plotly_chart(fig2, use_container_width=True)

# ── Charts Row 2 ───────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("📅 Events by Month")
    monthly = filtered_df.groupby('month').size().reset_index(name='count')
    fig3 = px.line(monthly, x='month', y='count', markers=True,
                   color_discrete_sequence=['#ff4444'])
    st.plotly_chart(fig3, use_container_width=True)

with col2:
    st.subheader("🔴 Top Countries by High Alert")
    high_alert = filtered_df[filtered_df['is_high_alert'] == 1]
    country_counts = high_alert['country'].value_counts().head(10).reset_index()
    country_counts.columns = ['Country', 'Count']
    fig4 = px.bar(country_counts, x='Count', y='Country',
                  orientation='h', color='Count',
                  color_continuous_scale='Reds')
    st.plotly_chart(fig4, use_container_width=True)

st.divider()

# ── SQL Query Section ──────────────────────────────
st.subheader("🗄️ Live SQL Query Explorer")
st.markdown("Write your own SQL query on the crisis database!")

default_query = "SELECT country, severity, title FROM crisis_events WHERE is_high_alert = 1 ORDER BY severity DESC LIMIT 10"
user_query = st.text_area("SQL Query", value=default_query, height=100)

if st.button("▶️ Run Query"):
    try:
        result = query_db(user_query)
        st.dataframe(result, use_container_width=True)
        st.success(f"✅ {len(result)} rows returned")
    except Exception as e:
        st.error(f"❌ Query error: {e}")

st.divider()
# ── ML Prediction Section ──────────────────────────
st.subheader("🤖 ML Severity Predictor")
st.markdown("Predict the severity of a new crisis event using our trained model!")

col1, col2, col3 = st.columns(3)

with col1:
    month_input = st.slider("Month of Year", 1, 12, 6)

with col2:
    type_input = st.selectbox("Disaster Type", ["EQ", "FL", "DR", "TC", "VO", "WF"])
    is_recent = st.selectbox("Is Recent (2024+)?", [1, 0])

with col3:
    st.markdown("###")
    predict_btn = st.button("🔮 Predict Severity", use_container_width=True)

if predict_btn:
    import pickle
    import numpy as np

    with open("database/model.pkl", "rb") as f:
        model = pickle.load(f)

    type_cols = ["type_DR", "type_EQ", "type_FL", "type_TC", "type_VO", "type_WF"]
    type_values = [1 if f"type_{type_input}" == col else 0 for col in type_cols]
    
    # weekday and is_weekend set to average/neutral values
    features = type_values + [month_input, 2, 0, is_recent]
    input_array = np.array(features).reshape(1, -1)

    prediction = model.predict(input_array)[0]
    severity_map = {
        0: ("🟢 Green", "Low risk — situation is manageable"),
        1: ("🟠 Orange", "Medium risk — monitor closely"),
        2: ("🔴 Red", "High risk — immediate action needed!")
    }

    label, message = severity_map.get(prediction, ("Unknown", ""))
    st.success(f"**Predicted Severity: {label}**")
    st.info(f"💡 {message}")
