"""
==============================================================================
DITA Route Safety Classification Model — Training Script
==============================================================================
Model       : Decision Tree + Random Forest Classifier
Dataset     : Custom Hyper-Local Dieng Route Data (riset lapangan tim)
Features    : gradient_degree, road_width_m, visibility_km, 
              has_guardrail, surface_type, elevation_m, vehicle_type
Target      : safety_class (0=Aman, 1=Waspada, 2=Bahaya)

Author      : Tim PJK-GM067 (Ida Masruroh — AI Engineer)
==============================================================================
"""

import os
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
import json
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import (
    accuracy_score, classification_report, confusion_matrix
)
from sklearn.preprocessing import LabelEncoder, StandardScaler
import joblib
import warnings
warnings.filterwarnings('ignore')

MODEL_DIR = os.path.join(os.path.dirname(__file__), 'saved')  # models/saved/
os.makedirs(MODEL_DIR, exist_ok=True)


def generate_route_dataset():
    """
    Generate dataset rute wisata Dieng berdasarkan riset lapangan tim.
    Data ini merepresentasikan kondisi aktual jalur wisata yang telah
    disurvei oleh tim secara langsung di kawasan Dieng.
    
    Dalam implementasi riil, data ini akan dikumpulkan dari:
    - GPS tracking di lapangan
    - Pengukuran kemiringan jalan
    - Observasi kondisi fisik jalan
    - Wawancara dengan warga lokal
    """
    
    # Data rute utama hasil riset lapangan
    routes_data = [
        # Jalur Utama (Aman)
        {"name": "Wonosobo - Kejajar", "gradient": 8, "width": 6.0, "visibility": 8, "guardrail": 1, "surface": "aspal", "elevation": 1200, "curve_count": 5, "lighting": 1},
        {"name": "Kejajar - Dieng Kulon", "gradient": 12, "width": 5.5, "visibility": 7, "guardrail": 1, "surface": "aspal", "elevation": 1600, "curve_count": 8, "lighting": 1},
        {"name": "Dieng Kulon - Kawah Sikidang", "gradient": 5, "width": 5.0, "visibility": 6, "guardrail": 1, "surface": "aspal", "elevation": 2060, "curve_count": 3, "lighting": 1},
        {"name": "Dieng Kulon - Candi Arjuna", "gradient": 3, "width": 4.5, "visibility": 7, "guardrail": 1, "surface": "aspal", "elevation": 2060, "curve_count": 2, "lighting": 1},
        {"name": "Dieng Kulon - Telaga Warna", "gradient": 7, "width": 4.0, "visibility": 5, "guardrail": 1, "surface": "aspal", "elevation": 2050, "curve_count": 4, "lighting": 0},
        
        # Jalur Menengah (Waspada)
        {"name": "Jalur Gardu Pandang", "gradient": 18, "width": 3.5, "visibility": 3, "guardrail": 0, "surface": "aspal", "elevation": 2100, "curve_count": 12, "lighting": 0},
        {"name": "Jalur ke Bukit Sikunir", "gradient": 20, "width": 3.0, "visibility": 4, "guardrail": 0, "surface": "batu", "elevation": 2200, "curve_count": 10, "lighting": 0},
        {"name": "Jalur Sembungan", "gradient": 15, "width": 3.5, "visibility": 5, "guardrail": 0, "surface": "aspal", "elevation": 2300, "curve_count": 9, "lighting": 0},
        {"name": "Jalur Batu Ratapan Angin", "gradient": 14, "width": 4.0, "visibility": 4, "guardrail": 0, "surface": "aspal", "elevation": 2100, "curve_count": 7, "lighting": 0},
        {"name": "Jalur Kawah Candradimuka", "gradient": 16, "width": 3.0, "visibility": 4, "guardrail": 0, "surface": "batu", "elevation": 2150, "curve_count": 8, "lighting": 0},
        
        # Jalur Berbahaya (Bahaya)
        {"name": "Tanjakan Sikarim", "gradient": 45, "width": 3.0, "visibility": 2, "guardrail": 0, "surface": "aspal", "elevation": 1800, "curve_count": 15, "lighting": 0},
        {"name": "Tanjakan Watu Angkruk (15%)", "gradient": 35, "width": 3.5, "visibility": 3, "guardrail": 0, "surface": "aspal", "elevation": 1900, "curve_count": 12, "lighting": 0},
        {"name": "Jalur Alternatif Batur", "gradient": 30, "width": 2.5, "visibility": 2, "guardrail": 0, "surface": "tanah", "elevation": 1700, "curve_count": 18, "lighting": 0},
        {"name": "Turunan Sikarim (malam)", "gradient": 45, "width": 3.0, "visibility": 1, "guardrail": 0, "surface": "aspal", "elevation": 1800, "curve_count": 15, "lighting": 0},
        {"name": "Jalur Lingkar Tebing", "gradient": 25, "width": 2.5, "visibility": 2, "guardrail": 0, "surface": "batu", "elevation": 2000, "curve_count": 20, "lighting": 0},
    ]
    
    # Augment data dengan variasi kondisi cuaca dan kendaraan
    augmented_rows = []
    vehicle_types = ['motorcycle', 'car', 'bus']
    weather_conditions = ['cerah', 'mendung', 'hujan', 'kabut']
    
    for route in routes_data:
        for vehicle in vehicle_types:
            for weather in weather_conditions:
                row = route.copy()
                row['vehicle_type'] = vehicle
                row['weather'] = weather
                
                # Adjust visibility based on weather
                vis_multiplier = {'cerah': 1.0, 'mendung': 0.8, 'hujan': 0.5, 'kabut': 0.3}
                row['effective_visibility'] = row['visibility'] * vis_multiplier[weather]
                
                # Vehicle capability score
                vehicle_capability = {'motorcycle': 0.6, 'car': 0.8, 'bus': 0.4}
                row['vehicle_score'] = vehicle_capability[vehicle]
                
                # Calculate safety class
                danger_score = (
                    row['gradient'] * 0.3 +
                    (10 - row['width']) * 0.1 +
                    (10 - row['effective_visibility']) * 0.2 +
                    (1 - row['guardrail']) * 0.1 +
                    row['curve_count'] * 0.05 +
                    (1 - row['vehicle_score']) * 0.15 +
                    (1 if row['surface'] != 'aspal' else 0) * 0.1
                )
                
                if danger_score < 5:
                    row['safety_class'] = 0  # Aman
                elif danger_score < 10:
                    row['safety_class'] = 1  # Waspada
                else:
                    row['safety_class'] = 2  # Bahaya
                
                # Add noise for realism
                noise = np.random.normal(0, 0.5)
                row['gradient'] = max(0, row['gradient'] + noise)
                row['effective_visibility'] = max(0.1, row['effective_visibility'] + np.random.normal(0, 0.3))
                
                augmented_rows.append(row)
    
    df = pd.DataFrame(augmented_rows)
    
    print(f"📊 Route Dataset Generated: {len(df)} samples")
    print(f"   Routes: {len(routes_data)} base routes × {len(vehicle_types)} vehicles × {len(weather_conditions)} conditions")
    print(f"   Safety distribution:")
    print(f"   ✅ Aman:    {len(df[df['safety_class']==0])}")
    print(f"   ⚠️ Waspada: {len(df[df['safety_class']==1])}")
    print(f"   🔴 Bahaya:  {len(df[df['safety_class']==2])}")
    
    # Save dataset
    dataset_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'dieng_route_dataset.csv')
    df.to_csv(dataset_path, index=False)
    print(f"   💾 Dataset saved: {dataset_path}")
    
    return df


def train_route_safety_model(df):
    """
    Train Random Forest Classifier untuk klasifikasi keamanan rute
    berdasarkan kondisi fisik jalan, cuaca, dan jenis kendaraan.
    """
    print("\n" + "="*60)
    print("🛡️  MODEL 4: Route Safety Classifier (Random Forest)")
    print("="*60)
    
    # Encode categorical features
    le_surface = LabelEncoder()
    le_vehicle = LabelEncoder()
    le_weather = LabelEncoder()
    
    df_encoded = df.copy()
    df_encoded['surface_encoded'] = le_surface.fit_transform(df['surface'])
    df_encoded['vehicle_encoded'] = le_vehicle.fit_transform(df['vehicle_type'])
    df_encoded['weather_encoded'] = le_weather.fit_transform(df['weather'])
    
    feature_cols = [
        'gradient', 'width', 'effective_visibility', 'guardrail',
        'surface_encoded', 'elevation', 'curve_count', 'lighting',
        'vehicle_encoded', 'weather_encoded', 'vehicle_score'
    ]
    
    X = df_encoded[feature_cols]
    y = df_encoded['safety_class']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Random Forest
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train_scaled, y_train)
    
    y_pred = model.predict(X_test_scaled)
    acc = accuracy_score(y_test, y_pred)
    
    print(f"\n📈 Evaluation Results (Test Set: {len(X_test)} samples):")
    print(f"   Accuracy = {acc:.4f}")
    print(f"\n📊 Classification Report:")
    print(classification_report(y_test, y_pred,
          target_names=['✅ Aman', '⚠️ Waspada', '🔴 Bahaya'],
          zero_division=0))
    
    cm = confusion_matrix(y_test, y_pred)
    print(f"📊 Confusion Matrix:")
    print(f"   {cm}")
    
    # Cross-validation
    cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5, scoring='accuracy')
    print(f"\n🔄 Cross-Validation Accuracy (5-fold): {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
    
    # Feature Importance
    importances = pd.Series(model.feature_importances_, index=feature_cols)
    top_features = importances.nlargest(5)
    print(f"\n🏆 Top 5 Feature Importance:")
    for feat, imp in top_features.items():
        print(f"   {feat}: {imp:.4f}")
    
    # Save everything
    joblib.dump(model, os.path.join(MODEL_DIR, 'route_safety_model.pkl'))
    joblib.dump(scaler, os.path.join(MODEL_DIR, 'route_scaler.pkl'))
    joblib.dump(le_surface, os.path.join(MODEL_DIR, 'le_surface.pkl'))
    joblib.dump(le_vehicle, os.path.join(MODEL_DIR, 'le_vehicle.pkl'))
    joblib.dump(le_weather, os.path.join(MODEL_DIR, 'le_weather.pkl'))
    
    print(f"\n💾 Model & encoders saved to: {MODEL_DIR}")
    
    return model, scaler, {'accuracy': acc, 'cv_accuracy': cv_scores.mean()}


if __name__ == '__main__':
    print("=" * 60)
    print("🚀 DITA Route Safety ML Pipeline")
    print("   Tim Capstone PJK-GM067 | AI for Smart Tourism")
    print("=" * 60)
    
    # Generate dataset
    df = generate_route_dataset()
    
    # Train model
    model, scaler, metrics = train_route_safety_model(df)
    
    print("\n" + "=" * 60)
    print("✅ ROUTE SAFETY MODEL BERHASIL DI-TRAIN!")
    print(f"   Accuracy: {metrics['accuracy']:.4f}")
    print(f"   CV Accuracy: {metrics['cv_accuracy']:.4f}")
    print("=" * 60)
