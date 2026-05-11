"""
==============================================================================
DITA Weather Prediction Model — Training Script
==============================================================================
Model       : Random Forest Regressor + Gradient Boosting Classifier
Dataset     : Dieng Historical Weather 2023 (Open-Meteo Archive API)
Features    : hour, day_of_year, month, temp_lag_1h, temp_lag_3h,
              precip_lag_1h, precip_lag_3h, rolling_mean_6h, rolling_std_6h
Targets     : (1) Temperature prediction   (Regression)
              (2) Rain probability          (Classification)
              (3) Fog/extreme risk alert    (Classification)

Author      : Tim PJK-GM067 (Ida Masruroh — AI Engineer)
==============================================================================
"""

import json
import os
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
from sklearn.metrics import (
    mean_absolute_error, mean_squared_error, r2_score,
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix
)
from sklearn.preprocessing import StandardScaler
import joblib
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────
# 1. LOAD & PREPROCESS DATA
# ─────────────────────────────────────────────
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
MODEL_DIR = os.path.join(os.path.dirname(__file__), 'saved')  # models/saved/
os.makedirs(MODEL_DIR, exist_ok=True)

def load_historical_data():
    """Load dan preprocess data cuaca historis Dieng 2023."""
    data_path = os.path.join(DATA_DIR, 'dieng_historical_2023.json')
    
    with open(data_path, 'r') as f:
        raw = json.load(f)
    
    df = pd.DataFrame({
        'datetime': pd.to_datetime(raw['hourly']['time']),
        'temperature': raw['hourly']['temperature_2m'],
        'precipitation': raw['hourly']['precipitation']
    })
    
    # Metadata
    print(f"📊 Dataset Loaded: {len(df)} records")
    print(f"📍 Lokasi: Lat {raw['latitude']}, Lon {raw['longitude']}")
    print(f"⛰️  Elevasi: {raw['elevation']}m (Dataran Tinggi Dieng)")
    print(f"📅 Periode: {df['datetime'].min()} — {df['datetime'].max()}")
    print(f"🌡️  Suhu: Min={df['temperature'].min():.1f}°C, "
          f"Max={df['temperature'].max():.1f}°C, "
          f"Mean={df['temperature'].mean():.1f}°C")
    print(f"🌧️  Presipitasi: Total={df['precipitation'].sum():.1f}mm, "
          f"Hari Hujan={len(df[df['precipitation'] > 0.1])} jam")
    
    return df


def engineer_features(df):
    """
    Feature Engineering — mengekstrak fitur temporal dan lag
    dari data time-series cuaca untuk meningkatkan akurasi prediksi.
    """
    df = df.copy()
    
    # Temporal features
    df['hour'] = df['datetime'].dt.hour
    df['day_of_year'] = df['datetime'].dt.dayofyear
    df['month'] = df['datetime'].dt.month
    df['day_of_week'] = df['datetime'].dt.dayofweek
    df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
    
    # Cyclical encoding (agar model mengerti jam 23 dekat jam 0)
    df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
    df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
    df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
    df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
    
    # Lag features (suhu & presipitasi sebelumnya)
    df['temp_lag_1h'] = df['temperature'].shift(1)
    df['temp_lag_3h'] = df['temperature'].shift(3)
    df['temp_lag_6h'] = df['temperature'].shift(6)
    df['temp_lag_24h'] = df['temperature'].shift(24)
    df['precip_lag_1h'] = df['precipitation'].shift(1)
    df['precip_lag_3h'] = df['precipitation'].shift(3)
    
    # Rolling statistics (tren jangka pendek)
    df['temp_rolling_mean_6h'] = df['temperature'].rolling(6).mean()
    df['temp_rolling_std_6h'] = df['temperature'].rolling(6).std()
    df['temp_rolling_mean_24h'] = df['temperature'].rolling(24).mean()
    df['precip_rolling_sum_6h'] = df['precipitation'].rolling(6).sum()
    df['precip_rolling_sum_24h'] = df['precipitation'].rolling(24).sum()
    
    # Rate of change (perubahan suhu per jam)
    df['temp_change_1h'] = df['temperature'].diff(1)
    df['temp_change_3h'] = df['temperature'].diff(3)
    
    # Target: Apakah akan hujan di jam berikutnya?
    df['will_rain_next'] = (df['precipitation'].shift(-1) > 0.1).astype(int)
    
    # Target: Risk level (untuk peringatan wisatawan)
    # Fog risk: suhu rendah (<10°C) + kelembaban tinggi (presipitasi rendah tapi udara dingin)
    # Rain risk: presipitasi > 0.5mm 
    df['risk_level'] = 0  # 0=Aman, 1=Waspada, 2=Bahaya
    df.loc[df['temperature'] < 10, 'risk_level'] = 1  # Suhu ekstrem
    df.loc[df['precipitation'] > 2.0, 'risk_level'] = 2  # Hujan lebat
    df.loc[(df['temperature'] < 8) & (df['precipitation'] > 0.5), 'risk_level'] = 2  # Kombinasi
    
    # Drop NaN (dari lag/rolling)
    df = df.dropna().reset_index(drop=True)
    
    print(f"\n🔧 Feature Engineering selesai: {len(df)} records, {len(df.columns)} features")
    print(f"   Risk distribution: Aman={len(df[df['risk_level']==0])}, "
          f"Waspada={len(df[df['risk_level']==1])}, "
          f"Bahaya={len(df[df['risk_level']==2])}")
    
    return df


# ─────────────────────────────────────────────
# 2. MODEL TRAINING
# ─────────────────────────────────────────────
FEATURE_COLS = [
    'hour', 'day_of_year', 'month',
    'hour_sin', 'hour_cos', 'month_sin', 'month_cos',
    'is_weekend',
    'temp_lag_1h', 'temp_lag_3h', 'temp_lag_6h', 'temp_lag_24h',
    'precip_lag_1h', 'precip_lag_3h',
    'temp_rolling_mean_6h', 'temp_rolling_std_6h', 'temp_rolling_mean_24h',
    'precip_rolling_sum_6h', 'precip_rolling_sum_24h',
    'temp_change_1h', 'temp_change_3h'
]


def train_temperature_model(df):
    """
    Model 1: Random Forest Regressor — Prediksi Suhu
    Memprediksi suhu 1 jam ke depan berdasarkan pola historis.
    """
    print("\n" + "="*60)
    print("🌡️  MODEL 1: Temperature Prediction (Random Forest Regressor)")
    print("="*60)
    
    X = df[FEATURE_COLS]
    y = df['temperature']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, shuffle=False  # Time-series split
    )
    
    # Standardize features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train Random Forest
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=15,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train_scaled, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test_scaled)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    
    print(f"\n📈 Evaluation Results (Test Set: {len(X_test)} samples):")
    print(f"   MAE  = {mae:.3f}°C")
    print(f"   RMSE = {rmse:.3f}°C")
    print(f"   R²   = {r2:.4f}")
    
    # Cross-validation
    cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5, scoring='r2')
    print(f"\n🔄 Cross-Validation R² (5-fold): {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
    
    # Feature Importance
    importances = pd.Series(model.feature_importances_, index=FEATURE_COLS)
    top_features = importances.nlargest(5)
    print(f"\n🏆 Top 5 Feature Importance:")
    for feat, imp in top_features.items():
        print(f"   {feat}: {imp:.4f}")
    
    # Save model
    model_path = os.path.join(MODEL_DIR, 'temperature_model.pkl')
    scaler_path = os.path.join(MODEL_DIR, 'temp_scaler.pkl')
    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)
    print(f"\n💾 Model saved: {model_path}")
    
    return model, scaler, {'mae': mae, 'rmse': rmse, 'r2': r2, 'cv_r2': cv_scores.mean()}


def train_rain_classifier(df):
    """
    Model 2: Gradient Boosting Classifier — Prediksi Hujan
    Memprediksi apakah akan terjadi hujan di jam berikutnya.
    """
    print("\n" + "="*60)
    print("🌧️  MODEL 2: Rain Prediction (Gradient Boosting Classifier)")
    print("="*60)
    
    X = df[FEATURE_COLS]
    y = df['will_rain_next']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, shuffle=False
    )
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    model = GradientBoostingClassifier(
        n_estimators=100,
        max_depth=5,
        learning_rate=0.1,
        subsample=0.8,
        random_state=42
    )
    model.fit(X_train_scaled, y_train)
    
    y_pred = model.predict(X_test_scaled)
    
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    
    print(f"\n📈 Evaluation Results (Test Set: {len(X_test)} samples):")
    print(f"   Accuracy  = {acc:.4f}")
    print(f"   Precision = {prec:.4f}")
    print(f"   Recall    = {rec:.4f}")
    print(f"   F1 Score  = {f1:.4f}")
    
    print(f"\n📊 Classification Report:")
    print(classification_report(y_test, y_pred, target_names=['Tidak Hujan', 'Hujan']))
    
    cm = confusion_matrix(y_test, y_pred)
    print(f"📊 Confusion Matrix:")
    print(f"   {cm}")
    
    # Feature Importance
    importances = pd.Series(model.feature_importances_, index=FEATURE_COLS)
    top_features = importances.nlargest(5)
    print(f"\n🏆 Top 5 Feature Importance:")
    for feat, imp in top_features.items():
        print(f"   {feat}: {imp:.4f}")
    
    model_path = os.path.join(MODEL_DIR, 'rain_classifier.pkl')
    scaler_path = os.path.join(MODEL_DIR, 'rain_scaler.pkl')
    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)
    print(f"\n💾 Model saved: {model_path}")
    
    return model, scaler, {'accuracy': acc, 'precision': prec, 'recall': rec, 'f1': f1}


def train_risk_classifier(df):
    """
    Model 3: Gradient Boosting Classifier — Tourism Risk Level
    Mengklasifikasikan tingkat risiko wisata (Aman/Waspada/Bahaya)
    berdasarkan kondisi cuaca untuk keamanan wisatawan di Dieng.
    """
    print("\n" + "="*60)
    print("⚠️  MODEL 3: Tourism Risk Classification (Gradient Boosting)")
    print("="*60)
    
    X = df[FEATURE_COLS]
    y = df['risk_level']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, shuffle=False
    )
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    model = GradientBoostingClassifier(
        n_estimators=150,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        random_state=42
    )
    model.fit(X_train_scaled, y_train)
    
    y_pred = model.predict(X_test_scaled)
    
    acc = accuracy_score(y_test, y_pred)
    
    print(f"\n📈 Evaluation Results (Test Set: {len(X_test)} samples):")
    print(f"   Accuracy = {acc:.4f}")
    # Use dynamic labels based on what appears in the data
    unique_labels = sorted(set(y_test) | set(y_pred))
    label_map = {0: 'Aman', 1: 'Waspada', 2: 'Bahaya'}
    target_names = [label_map[l] for l in unique_labels]
    print(classification_report(y_test, y_pred, 
          labels=unique_labels,
          target_names=target_names,
          zero_division=0))
    
    cm = confusion_matrix(y_test, y_pred)
    print(f"📊 Confusion Matrix:")
    print(f"   {cm}")
    
    model_path = os.path.join(MODEL_DIR, 'risk_classifier.pkl')
    scaler_path = os.path.join(MODEL_DIR, 'risk_scaler.pkl')
    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)
    print(f"\n💾 Model saved: {model_path}")
    
    return model, scaler, {'accuracy': acc}


# ─────────────────────────────────────────────
# 3. SAVE EVALUATION REPORT
# ─────────────────────────────────────────────
def save_evaluation_report(temp_metrics, rain_metrics, risk_metrics):
    """Simpan laporan evaluasi model ke JSON untuk dokumentasi."""
    report = {
        "project": "DITA - Dieng Intelligence Tourism Assistant",
        "team": "PJK-GM067",
        "ai_engineer": "Ida Masruroh (APC466D6X0040)",
        "dataset": {
            "source": "Open-Meteo Historical Weather API",
            "location": "Dieng Plateau (-7.2056, 109.8731)",
            "elevation": "2.060m",
            "period": "2023-01-01 to 2023-12-31",
            "total_records": 8760,
            "features_engineered": len(FEATURE_COLS)
        },
        "models": {
            "temperature_prediction": {
                "type": "Random Forest Regressor",
                "n_estimators": 100,
                "test_split": "20%",
                "metrics": temp_metrics
            },
            "rain_prediction": {
                "type": "Gradient Boosting Classifier",
                "n_estimators": 100,
                "test_split": "20%",
                "metrics": rain_metrics
            },
            "risk_classification": {
                "type": "Gradient Boosting Classifier",
                "n_estimators": 150,
                "classes": ["Aman", "Waspada", "Bahaya"],
                "test_split": "20%",
                "metrics": risk_metrics
            }
        }
    }
    
    report_path = os.path.join(MODEL_DIR, 'evaluation_report.json')
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Evaluation report saved: {report_path}")
    return report


# ─────────────────────────────────────────────
# 4. MAIN EXECUTION
# ─────────────────────────────────────────────
if __name__ == '__main__':
    print("=" * 60)
    print("🚀 DITA ML Pipeline — Training All Models")
    print("   Tim Capstone PJK-GM067 | AI for Smart Tourism")
    print("=" * 60)
    
    # Step 1: Load data
    df = load_historical_data()
    
    # Step 2: Feature engineering
    df = engineer_features(df)
    
    # Step 3: Train models
    temp_model, temp_scaler, temp_metrics = train_temperature_model(df)
    rain_model, rain_scaler, rain_metrics = train_rain_classifier(df)
    risk_model, risk_scaler, risk_metrics = train_risk_classifier(df)
    
    # Step 4: Save report
    report = save_evaluation_report(temp_metrics, rain_metrics, risk_metrics)
    
    print("\n" + "=" * 60)
    print("✅ SEMUA MODEL BERHASIL DI-TRAIN DAN DISIMPAN!")
    print("=" * 60)
    print(f"   📁 Model files: {MODEL_DIR}")
    print(f"   📊 Temperature R²: {temp_metrics['r2']:.4f}")
    print(f"   🌧️  Rain F1 Score:  {rain_metrics['f1']:.4f}")
    print(f"   ⚠️  Risk Accuracy:  {risk_metrics['accuracy']:.4f}")
    print("=" * 60)
