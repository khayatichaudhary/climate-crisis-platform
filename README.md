# 🌍 Climate Crisis Intelligence Platform

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Streamlit-red?style=for-the-badge&logo=streamlit)](https://climate-crisis-platform.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.13-blue?style=for-the-badge&logo=python)](https://python.org)
[![ML](https://img.shields.io/badge/ML-Random%20Forest-green?style=for-the-badge&logo=scikit-learn)](https://scikit-learn.org)

> **A real-time global disaster monitoring platform powered by Machine Learning, SQL, and live API data.**

🔗 **Live App:** https://climate-crisis-platform.streamlit.app/

---

## 🎯 What It Does

This platform fetches **live global disaster data**, stores it in a **SQL database**, applies **Machine Learning** to predict crisis severity, and displays everything on an **interactive dashboard** with a world map.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Data Source** | GDACS API (live disaster data) |
| **Data Processing** | Python, Pandas |
| **Database** | SQLite + SQLAlchemy |
| **Machine Learning** | Scikit-learn (Random Forest) |
| **Visualization** | Plotly (interactive charts + world map) |
| **Dashboard** | Streamlit |
| **Deployment** | Streamlit Cloud |

---

## 🔥 Key Features

- 🌐 **Live Data Pipeline** — fetches real disaster data from GDACS API
- 🗄️ **SQL Backend** — stores and queries data using SQLite
- 🤖 **ML Severity Predictor** — predicts crisis severity using Random Forest
- 🗺️ **Interactive World Map** — visualizes disasters globally with severity colors
- 📊 **Dynamic Charts** — disaster types, monthly trends, country analysis
- 🔍 **SQL Query Explorer** — write live SQL queries on the crisis database
- 🎛️ **Filters** — filter by severity and country in real time

---
## 🧠 ML Pipeline

Live API Data → Feature Engineering → SQLite Database → Random Forest → Dashboard

---
## 🤖 Model Performance

| Metric | Score |
|--------|-------|
| Accuracy | 84.2% |
| F1 Score (weighted) | 81.8% |
| Model | Random Forest Classifier |
| Features Used | disaster type, month, weekday, is_weekend, is_recent |
| Training Data | 95 disaster events |
| Test Split | 80/20 |
## 🚀 Run Locally

```bash
git clone https://github.com/khayatichaudhary/climate-crisis-platform.git
cd climate-crisis-platform
pip install -r requirements.txt
streamlit run app.py
```

---

## 👩‍💻 Author

**Khayati Chaudhary** — Chemical Engineering student at MNNIT.

🔗 [GitHub](https://github.com/khayatichaudhary)