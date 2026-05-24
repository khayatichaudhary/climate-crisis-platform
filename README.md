# 🌍 Climate Crisis Intelligence Platform

An end-to-end ML platform that fetches real global crisis data, stores it in SQL, applies machine learning to predict crisis severity, and displays insights on an interactive dashboard.

## 🛠️ Tech Stack
- Python, Pandas, NumPy
- Scikit-learn, XGBoost
- SQLite, SQLAlchemy
- Plotly, Streamlit
- ReliefWeb API

## 📦 Project Structure
- `src/fetch_data.py` → fetches live crisis data
- `src/process_data.py` → cleaning & feature engineering
- `src/database.py` → SQL operations
- `src/model.py` → ML model
- `app.py` → Streamlit dashboard