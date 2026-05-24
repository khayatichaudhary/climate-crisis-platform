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

# ── Raw Data Table ─────────────────────────────────
st.subheader("📋 Crisis Events Data")
st.dataframe(
    filtered_df[['title', 'country', 'severity', 'year', 'month', 'is_high_alert']],
    use_container_width=True
)