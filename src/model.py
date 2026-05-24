import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import pickle
import os

def train_model():
    """
    Trains a Random Forest model to predict crisis severity
    """
    print("Loading processed data...")
    df = pd.read_csv("data/processed/crisis_processed.csv")
    
    # ── Select Features ────────────────────────────────
    feature_cols = [col for col in df.columns if col.startswith('type_')]
    feature_cols += ['month', 'weekday', 'is_weekend', 'is_recent']
    
    # Drop rows where severity_encoded is missing
    df = df.dropna(subset=['severity_encoded'])
    
    X = df[feature_cols]
    y = df['severity_encoded']
    
    print(f"Features used: {feature_cols}")
    print(f"Dataset size: {X.shape}")
    print(f"Target distribution:\n{y.value_counts()}")
    
    # ── Split Data ─────────────────────────────────────
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    print(f"\nTrain size: {len(X_train)}, Test size: {len(X_test)}")
    
    # ── Train Model ────────────────────────────────────
    print("\nTraining Random Forest model...")
    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        class_weight='balanced'
    )
    model.fit(X_train, y_train)
    
    # ── Evaluate Model ─────────────────────────────────
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\n✅ Model trained!")
    print(f"Accuracy: {accuracy:.2%}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    # ── Feature Importance ─────────────────────────────
    print("\n🔍 Top Feature Importances:")
    importance_df = pd.DataFrame({
        'feature': feature_cols,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    print(importance_df.to_string(index=False))
    
    # ── Save Model ─────────────────────────────────────
    os.makedirs("database", exist_ok=True)
    with open("database/model.pkl", "wb") as f:
        pickle.dump(model, f)
    print("\n✅ Model saved to database/model.pkl")
    
    return model, feature_cols

if __name__ == "__main__":
    train_model()