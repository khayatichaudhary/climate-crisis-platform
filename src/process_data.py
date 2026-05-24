import pandas as pd
import os

def process_data():
    """
    Cleans and engineers features from raw crisis data
    """
    print("Loading raw data...")
    df = pd.read_csv("data/raw/crisis_data.csv")
    print(f"Raw data shape: {df.shape}")
    
    # ── Step 1: Handle Missing Values ──────────────────
    print("\n Step 1: Handling missing values...")
    df['country'] = df['country'].fillna('Unknown')
    df['severity'] = df['severity'].fillna('Green')
    df['type'] = df['type'].fillna('Unknown')
    print(df.isnull().sum())

    # ── Step 2: Encode Severity (Label Encoding) ───────
    print("\n Step 2: Encoding severity...")
    severity_map = {'Green': 0, 'Orange': 1, 'Red': 2}
    df['severity_encoded'] = df['severity'].map(severity_map).fillna(0).astype(int)

    # ── Step 3: Encode Disaster Type (One Hot) ─────────
    print("\n Step 3: One-hot encoding disaster type...")
    df = pd.get_dummies(df, columns=['type'], prefix='type', drop_first=False)

    # ── Step 4: Extract Date Features ──────────────────
    print("\n Step 4: Extracting date features...")
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['year']       = df['date'].dt.year
    df['month']      = df['date'].dt.month
    df['day']        = df['date'].dt.day
    df['weekday']    = df['date'].dt.dayofweek
    df['is_weekend'] = df['weekday'].isin([5, 6]).astype(int)

    # ── Step 5: Create New Features ────────────────────
    print("\n Step 5: Creating new features...")
    df['is_high_alert'] = (df['severity_encoded'] >= 2).astype(int)
    df['is_recent']     = (df['year'] >= 2024).astype(int)

    # ── Save Processed Data ────────────────────────────
    os.makedirs("data/processed", exist_ok=True)
    df.to_csv("data/processed/crisis_processed.csv", index=False)
    print(f"\n✅ Processed data saved! Shape: {df.shape}")
    print(df[['title', 'country', 'severity', 'severity_encoded', 
              'is_high_alert', 'year', 'month', 'is_weekend']].head(10))
    
    return df

if __name__ == "__main__":
    process_data()