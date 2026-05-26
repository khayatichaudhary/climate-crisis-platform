import streamlit as st
import pandas as pd
import numpy as np
import requests
import os
from dotenv import load_dotenv
load_dotenv()
GDACS_NAME_MAP = {
    "Viet Nam": "Vietnam",
    "Korea, Republic of": "South Korea",
    "Korea, Dem. People's Rep.": "North Korea",
    "Congo, Dem. Rep.": "Democratic Republic of the Congo",
    "Congo, Rep.": "Republic of the Congo",
    "Tanzania, United Republic of": "Tanzania",
    "Iran, Islamic Republic of": "Iran",
    "Syrian Arab Republic": "Syria",
    "Lao PDR": "Laos",
    "Bolivia, Plurinational State of": "Bolivia",
    "Venezuela, Bolivarian Republic of": "Venezuela",
    "Moldova, Republic of": "Moldova",
    "Micronesia, Federated States of": "Micronesia",
    "Timor-Leste": "East Timor",
    "Cabo Verde": "Cape Verde",
    "Eswatini": "Swaziland",
    "Côte d'Ivoire": "Ivory Coast",
    "Türkiye": "Turkey",
    "Brunei Darussalam": "Brunei",
    "Myanmar": "Myanmar",
    "Russian Federation": "Russia",
    "United States of America": "United States",
    "United Kingdom of Great Britain and Northern Ireland": "United Kingdom",
    "Czechia": "Czech Republic",
    "North Macedonia": "Macedonia",
    "Palestine, State of": "Palestine",
    "Philippines": "Philippines",  # already correct but explicit
}
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
# ── Custom CSS Dark Theme ──────────────────────────
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }
    
    /* Metric cards */
    [data-testid="stMetric"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 15px;
    }

    /* Metric label and value white */
    [data-testid="stMetricLabel"] {
        color: #ffffff !important;
    }
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
    }
    
    /* Buttons */
    .stButton button {
        background-color: #ff4444;
        color: white;
        border-radius: 8px;
        border: none;
        font-weight: bold;
        width: 100%;
    }
    
    .stButton button:hover {
        background-color: #cc0000;
    }
    
    /* Subheaders white not orange */
    h2, h3 {
        color: #ffffff !important;
    }
    
    /* Divider */
    hr {
        border-color: #30363d;
    }

    /* Text area */
    .stTextArea textarea {
        background-color: #161b22;
        color: #ffffff;
        border: 1px solid #30363d;
        border-radius: 8px;
    }

    /* All text white */
    p, span, div, label {
        color: #ffffff;
    }

    /* Dataframe */
    .stDataFrame {
        border: 1px solid #30363d;
        border-radius: 8px;
    }
            /* Dropdown text white */
    .stSelectbox div[data-baseweb="select"] {
        background-color: #161b22 !important;
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
    }

    .stSelectbox div[data-baseweb="select"] span {
        color: #ffffff !important;
    }

    /* Force dropdown styling */
    div[data-baseweb="select"] > div {
        background-color: #161b22 !important;
        color: #ffffff !important;
        border-color: #30363d !important;
    }

    div[data-baseweb="select"] span {
        color: #ffffff !important;
    }

    div[data-baseweb="menu"] {
        background-color: #161b22 !important;
    }

    li[role="option"] {
        background-color: #161b22 !important;
        color: #ffffff !important;
    }

    /* Input text white */
    input {
        color: #ffffff !important;
        background-color: #161b22 !important;
    }
</style>
""", unsafe_allow_html=True)

# ── Title ──────────────────────────────────────────

st.markdown("""
<div style="text-align: center; padding: 20px 0px;">
    <h1 style="font-size: 2.5rem; background: linear-gradient(90deg, #ff4444, #ff8800); 
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
    font-weight: 900; margin-bottom: 5px;">
        🌍 Climate Crisis Intelligence Platform
    </h1>
    <p style="color: #8b949e; font-size: 1.1rem; margin-top: 0;">
        Real-time global disaster monitoring powered by Machine Learning & SQL
    </p>
    <div style="margin-top: 10px;">
        <span style="background:#ff4444; color:white; padding:4px 12px; border-radius:20px; font-size:0.8rem; margin:3px;">🔴 Live Data</span>
        <span style="background:#1f6feb; color:white; padding:4px 12px; border-radius:20px; font-size:0.8rem; margin:3px;">🤖 ML Powered</span>
        <span style="background:#238636; color:white; padding:4px 12px; border-radius:20px; font-size:0.8rem; margin:3px;">🗄️ SQL Backend</span>
    </div>
</div>
""", unsafe_allow_html=True)
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
# ── Top 5 Most Dangerous RIGHT NOW ─────────────────
st.subheader("🚨 Top 5 Most Dangerous Disasters Right Now")

if 'risk_score' not in filtered_df.columns:
    filtered_df['risk_score'] = 0.0

top5 = filtered_df.nlargest(5, 'risk_score')[['title', 'country', 'severity', 'risk_score']]

for i, row in top5.iterrows():
    color = '#ff4444' if row['severity'] == 'Red' else '#ff8800'
    st.markdown(f"""
    <div style="background-color:#161b22; border-left: 4px solid {color}; 
    padding: 12px 20px; border-radius: 8px; margin-bottom: 10px;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <span style="color:{color}; font-weight:bold; font-size:1rem;">
                    {'🔴' if row['severity'] == 'Red' else '🟠'} {row['title']}
                </span><br>
                <span style="color:#8b949e; font-size:0.85rem;">📍 {row['country']}</span>
            </div>
            <div style="text-align:right;">
                <span style="color:{color}; font-size:1.5rem; font-weight:900;">
                    {row['risk_score']}
                </span><br>
                <span style="color:#8b949e; font-size:0.75rem;">Risk Score</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True) 

st.divider()
# ── World Map ──────────────────────────────────────
st.subheader("🗺️ Global Disaster Map")



@st.cache_data
def get_coordinates():
    coords_df = pd.read_csv("data/country_coordinates.csv")
    coords = dict(zip(coords_df["country"], zip(coords_df["lat"], coords_df["lon"])))
    return coords

coords = get_coordinates()




map_df = filtered_df.copy()
# Normalize GDACS country names before coordinate lookup
map_df['country_normalized'] = map_df['country'].replace(GDACS_NAME_MAP)
map_df['lat'] = map_df['country_normalized'].map(lambda x: coords.get(x, (None, None))[0])
map_df['lon'] = map_df['country_normalized'].map(lambda x: coords.get(x, (None, None))[1])

# Silent drop — no warning shown to users
map_df = map_df.dropna(subset=['lat', 'lon'])


color_map_severity = {'Red': 'red', 'Orange': 'orange', 'Green': 'green'}

fig_map = go.Figure(go.Scattergeo(
    lat=map_df['lat'],
    lon=map_df['lon'],
    text=map_df['title'] + '<br>' + map_df['country'] + '<br>Severity: ' + map_df['severity'],
   marker=dict(
        color=map_df['severity'].map(color_map_severity),
        size=map_df['risk_score'] / 5 + 8,
        opacity=0.8,
        line=dict(width=1, color='white')
    ),
    hoverinfo='text'
))

fig_map.update_layout(
    geo=dict(
    showframe=False,
    showcoastlines=True,
    coastlinecolor='#00ff88',
    coastlinewidth=1,
    showland=True,
    landcolor='#1a3a2a',
    showocean=True,
    oceancolor='#0a1628',
    showlakes=True,
    lakecolor='#0a1628',
    showcountries=True,
    countrycolor='#2a5a3a',
    countrywidth=0.5,
    projection=dict(
    type='orthographic',
    rotation=dict(lon=30, lat=20, roll=0)
),
    bgcolor='#0e1117',
    lataxis_range=[-60, 90],
    lonaxis_range=[-180, 180],
),
paper_bgcolor='#0e1117',
plot_bgcolor='#0e1117',
margin=dict(l=0, r=0, t=10, b=0),
height=550,
width=None,)


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
              color='Count', color_continuous_scale='Reds',
              template="plotly_dark")
    fig1.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color='#ffffff'), xaxis=dict(color='#ffffff'), yaxis=dict(color='#ffffff'), coloraxis_colorbar=dict(tickfont=dict(color='#ffffff'), title=dict(font=dict(color='#ffffff'))))
    st.plotly_chart(fig1, use_container_width=True)
    # Citation box explaining disaster type codes
    st.markdown("""
    <div style="background:#161b22; border:1px solid #30363d; border-radius:10px; padding:16px; margin-top:10px;">
      <p style="color:#ff8800; font-weight:bold; margin-bottom:8px;">📖 What do these codes mean?</p>
      <p style="color:#c9d1d9; font-size:0.85rem; margin:3px 0;"><span style="background:#ff4444; color:white; padding:1px 7px; border-radius:5px; font-size:0.8rem;">EQ</span> &nbsp;<b>Earthquake</b> — Sudden shaking of the ground due to tectonic plate movement.</p>
      <p style="color:#c9d1d9; font-size:0.85rem; margin:3px 0;"><span style="background:#ff4444; color:white; padding:1px 7px; border-radius:5px; font-size:0.8rem;">FL</span> &nbsp;<b>Flood</b> — Overflow of water onto normally dry land from heavy rain or rivers.</p>
      <p style="color:#c9d1d9; font-size:0.85rem; margin:3px 0;"><span style="background:#ff4444; color:white; padding:1px 7px; border-radius:5px; font-size:0.8rem;">DR</span> &nbsp;<b>Drought</b> — Long period of low rainfall causing water and food scarcity.</p>
      <p style="color:#c9d1d9; font-size:0.85rem; margin:3px 0;"><span style="background:#ff4444; color:white; padding:1px 7px; border-radius:5px; font-size:0.8rem;">TC</span> &nbsp;<b>Tropical Cyclone</b> — Rotating storm with strong winds. Called Hurricane or Typhoon in other regions.</p>
      <p style="color:#c9d1d9; font-size:0.85rem; margin:3px 0;"><span style="background:#ff4444; color:white; padding:1px 7px; border-radius:5px; font-size:0.8rem;">VO</span> &nbsp;<b>Volcano</b> — Eruption of magma and ash from Earth's crust.</p>
      <p style="color:#c9d1d9; font-size:0.85rem; margin:3px 0;"><span style="background:#ff4444; color:white; padding:1px 7px; border-radius:5px; font-size:0.8rem;">WF</span> &nbsp;<b>Wildfire</b> — Uncontrolled fire spreading through forests or grasslands.</p>
      <p style="color:#8b949e; font-size:0.75rem; margin-top:10px; margin-bottom:0;">Source: <a href="https://www.gdacs.org" target="_blank" style="color:#1f6feb;">GDACS — Global Disaster Alert and Coordination System</a></p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.subheader("🚨 Severity Distribution")
    severity_counts = filtered_df['severity'].value_counts().reset_index()
    severity_counts.columns = ['Severity', 'Count']
    color_map = {'Red': '#ff4444', 'Orange': '#ff8800', 'Green': '#00cc44'}
    fig2 = px.pie(severity_counts, values='Count', names='Severity',
              color='Severity', color_discrete_map=color_map,
              template="plotly_dark")
    fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color='#ffffff'), legend=dict(font=dict(color='#ffffff')))
    st.plotly_chart(fig2, use_container_width=True)
# ── Charts Row 2 ───────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("📅 Events by Month")
    monthly = filtered_df.groupby('month').size().reset_index(name='count')
    fig3 = px.line(monthly, x='month', y='count', markers=True,
               color_discrete_sequence=['#ff4444'],
               template="plotly_dark")
    fig3.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color='#ffffff'), xaxis=dict(color='#ffffff'), yaxis=dict(color='#ffffff'))
    st.plotly_chart(fig3, use_container_width=True)


with col2:
    st.subheader("🔴 Top Countries by High Alert")
    high_alert = filtered_df[filtered_df['is_high_alert'] == 1]
    
    # Split "Viet Nam, Philippines, Laos" → individual countries, then count
    country_counts = (
        high_alert['country']
        .dropna()
        .str.split(',')          # split on comma
        .explode()               # one row per country
        .str.strip()             # remove spaces
        .replace(GDACS_NAME_MAP) # normalize names (same map from Fix 1)
        .value_counts()
        .head(10)
        .reset_index()
    )
    country_counts.columns = ['Country', 'Count']
    fig4 = px.bar(country_counts, x='Count', y='Country',
              orientation='h', color='Count',
              color_continuous_scale='Reds',
              template="plotly_dark")
    fig4.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color='#ffffff'), xaxis=dict(color='#ffffff'), yaxis=dict(color='#ffffff'), coloraxis_colorbar=dict(tickfont=dict(color='#ffffff'), title=dict(font=dict(color='#ffffff'))))
    st.plotly_chart(fig4, use_container_width=True)

st.divider()

# ── SQL Query Section ──────────────────────────────
st.subheader("🗄️ Live SQL Query Explorer")

# --- NL to SQL helper function ---
def nl_to_sql(natural_language_query):
    TABLE_SCHEMA = """
    Table: crisis_events
    Columns: id, title, country, severity (Red/Orange/Green), risk_score (float),
             month (int 1-12), is_recent (0 or 1), is_high_alert (0 or 1),
             type_EQ, type_FL, type_DR, type_TC, type_VO, type_WF (all 0 or 1, 1 means that type)
    """
    try:
        from config import GROQ_API_KEY
        api_key = GROQ_API_KEY
    except ImportError:
        import os
        api_key = os.environ.get("GROQ_API_KEY", "")
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{
            "role": "user",
            "content": f"""You are a SQL expert. Convert this to a valid SQLite SQL query.
Schema: {TABLE_SCHEMA}
Query: {natural_language_query}
Rules: Return ONLY the SQL, no explanation, no backticks. Always use LIMIT 50."""
        }]
    }
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        },
        json=payload,
        timeout=15
    )
    data = response.json()
    if "error" in data:
        raise Exception(f"API Error: {data['error']['message']}")

    sql = data["choices"][0]["message"]["content"].strip()
    return sql.replace("```sql", "").replace("```", "").strip()

# --- Natural language input ---
st.markdown("#### 💬 Don't know SQL? Just describe what you want!")
nl_input = st.text_input("Plain English Query", placeholder='e.g. "Show all red alert floods" or "Which country has the most disasters?"')

generated_sql = None
if nl_input:
    with st.spinner("🤖 Converting to SQL..."):
        try:
            generated_sql = nl_to_sql(nl_input)
            st.success("✅ SQL generated — you can edit it below before running!")
        except Exception as e:
            st.error(f"❌ {e}")
            generated_sql = None

default_query = generated_sql if generated_sql else \
    "SELECT country, severity, title FROM crisis_events WHERE is_high_alert = 1 ORDER BY severity DESC LIMIT 10"

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
    is_recent_toggle = st.toggle("Is Recent (2024+)?", value=True)
    is_recent = 1 if is_recent_toggle else 0

with col3:
    st.markdown("###")
    predict_btn = st.button("🔮 Predict Severity", use_container_width=True)

if predict_btn:
    
    with open("database/model.pkl", "rb") as f:
        model = pickle.load(f)

    type_cols = ["type_DR", "type_EQ", "type_FL", "type_TC", "type_VO", "type_WF"]
    type_values = [1 if f"type_{type_input}" == col else 0 for col in type_cols]
    
    # weekday and is_weekend set to average/neutral values
    features = type_values + [month_input, 2, 0, is_recent]
    input_array = np.array(features).reshape(1, -1)

    prediction = model.predict(input_array)[0]

    severity_map = {
        0: ("🟢 Green", "Low risk — situation is manageable", "#00cc44"),
        1: ("🟠 Orange", "Medium risk — monitor closely", "#ff8800"),
        2: ("🔴 Red", "High risk — immediate action needed!", "#ff4444"),
    }

    label, message, color = severity_map.get(prediction, ("Unknown", "", "#ffffff"))
    st.success(f"**Predicted Severity: {label}**")
    st.info(f"💡 {message}")

    # --- Confidence Score ---
    st.markdown("#### 📊 Model Confidence")
    proba = model.predict_proba(input_array)[0]   # gives [prob_green, prob_orange, prob_red]
    classes = model.classes_                       # gives [0, 1, 2]

    severity_colors = {0: "#00cc44", 1: "#ff8800", 2: "#ff4444"}
    severity_names  = {0: "🟢 Green", 1: "🟠 Orange", 2: "🔴 Red"}

    for i, cls in enumerate(classes):
        pct = round(proba[i] * 100, 1)
        clr = severity_colors[cls]
        name = severity_names[cls]
        st.markdown(f"""
        <div style="margin-bottom:12px;">
          <div style="display:flex; justify-content:space-between;">
            <span style="color:{clr}; font-weight:bold;">{name}</span>
            <span style="color:{clr}; font-weight:bold;">{pct}%</span>
          </div>
          <div style="background:#0e1117; border-radius:6px; height:12px; margin-top:4px;">
            <div style="width:{int(pct)}%; background:{clr}; height:12px; border-radius:6px;"></div>
          </div>
        </div>
        """, unsafe_allow_html=True)
