"""
==============================================================================
DITA Itinerary Recommendation Model Training
==============================================================================
Train ML model untuk rekomendasi itinerary berdasarkan:
1. User preferences (budget, interests, travel_style)
2. Historical data (simulasi user ratings)
3. Activity features (cost, duration, type, location)

Model: Hybrid Recommendation System
- Content-Based Filtering (activity features)
- Collaborative Filtering (user similarity)
- Matrix Factorization (latent features)

Author: Tim PJK-GM067 (Ida Masruroh — AI Engineer)
==============================================================================
"""

import os
import numpy as np
import pandas as pd
import joblib
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from datetime import datetime
import json

MODEL_DIR = os.path.join(os.path.dirname(__file__), 'saved')
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')


def generate_synthetic_training_data():
    """
    Generate synthetic training data dari aktivitas database.
    Simulasi user interactions dan ratings.
    """
    from app.models.itinerary_engine import DiengItineraryEngine
    
    engine = DiengItineraryEngine()
    activities = engine.activities_db
    
    # Simulate users dengan different preferences
    user_profiles = [
        # (user_id, budget_level, travel_style, interests, vehicle)
        (1, 'high', 'couple', ['alam', 'fotografi'], 'car'),
        (2, 'low', 'solo', ['petualangan', 'alam'], 'motorcycle'),
        (3, 'medium', 'family', ['keluarga', 'kuliner', 'edukasi'], 'car'),
        (4, 'high', 'group', ['budaya', 'sejarah'], 'bus'),
        (5, 'medium', 'couple', ['relaksasi', 'kuliner'], 'car'),
        (6, 'low', 'solo', ['fotografi', 'sunrise'], 'motorcycle'),
        (7, 'high', 'family', ['anak', 'keluarga', 'edukasi'], 'car'),
        (8, 'medium', 'group', ['petualangan', 'trekking'], 'motorcycle'),
        (9, 'low', 'couple', ['kuliner', 'santai'], 'motorcycle'),
        (10, 'high', 'solo', ['alam', 'sunrise', 'fotografi'], 'car'),
        (11, 'medium', 'family', ['keluarga', 'alam'], 'car'),
        (12, 'low', 'group', ['budaya', 'kuliner'], 'bus'),
        (13, 'high', 'couple', ['relaksasi', 'kuliner'], 'car'),
        (14, 'medium', 'solo', ['petualangan', 'fotografi'], 'motorcycle'),
        (15, 'low', 'family', ['anak', 'keluarga'], 'car'),
    ]
    
    budget_map = {'low': 250_000, 'medium': 750_000, 'high': 2_000_000}
    
    training_data = []
    
    for user_id, budget_level, travel_style, interests, vehicle in user_profiles:
        budget = budget_map[budget_level]
        
        for activity in activities:
            # Calculate rating based on user preferences
            rating = calculate_synthetic_rating(
                activity, budget, interests, travel_style, vehicle
            )
            
            # Add some noise to make it realistic
            rating += np.random.normal(0, 0.5)
            rating = max(1.0, min(5.0, rating))  # Clamp between 1-5
            
            # Extract features
            training_data.append({
                'user_id': user_id,
                'activity_id': activity['id'],
                'activity_name': activity['name'],
                'activity_type': activity['type'],
                'activity_location': activity['location'],
                'cost': activity['cost_per_person'],
                'duration': activity['duration_hours'],
                'priority_score': activity['priority_score'],
                'physical_level': activity['physical_level'],
                'weather_sensitive': int(activity['weather_sensitive']),
                'user_budget': budget,
                'budget_level': budget_level,
                'travel_style': travel_style,
                'vehicle': vehicle,
                'interest_match': len(set(interests) & set(activity['interests'])),
                'vehicle_compatible': int(vehicle in activity['vehicle_access']),
                'rating': round(rating, 2),
            })
    
    return pd.DataFrame(training_data)


def calculate_synthetic_rating(activity, budget, interests, travel_style, vehicle):
    """Calculate synthetic rating based on user preferences."""
    rating = 3.0  # Base rating
    
    # Interest matching (most important)
    interest_match = len(set(interests) & set(activity['interests']))
    rating += interest_match * 0.6
    
    # Budget consideration
    cost_ratio = activity['cost_per_person'] / (budget / 3)  # Assume 3 activities per day
    if cost_ratio <= 0.3:
        rating += 0.5  # Very affordable
    elif cost_ratio <= 0.6:
        rating += 0.3  # Affordable
    elif cost_ratio > 1.0:
        rating -= 0.5  # Too expensive
    
    # Travel style matching
    physical = activity['physical_level']
    if travel_style == 'family':
        if physical == 'easy':
            rating += 0.4
        elif physical == 'hard':
            rating -= 0.6
    elif travel_style == 'solo':
        if physical in ['medium', 'hard']:
            rating += 0.3
    
    # Vehicle compatibility
    if vehicle not in activity['vehicle_access']:
        rating -= 1.0
    
    # Priority score influence
    rating += (activity['priority_score'] - 70) / 50  # Normalize around 70
    
    return rating


def train_itinerary_recommendation_model():
    """
    Train ML model untuk recommendation system.
    """
    print("=" * 70)
    print("TRAINING ITINERARY RECOMMENDATION MODEL")
    print("=" * 70)
    
    # 1. Generate training data
    print("\n[1/6] Generating synthetic training data...")
    df = generate_synthetic_training_data()
    print(f"✅ Generated {len(df)} training samples")
    print(f"   - Unique users: {df['user_id'].nunique()}")
    print(f"   - Unique activities: {df['activity_id'].nunique()}")
    print(f"   - Rating distribution: {df['rating'].describe()}")
    
    # 2. Feature engineering
    print("\n[2/6] Feature engineering...")
    
    # Encode categorical features
    le_budget = LabelEncoder()
    le_style = LabelEncoder()
    le_vehicle = LabelEncoder()
    le_type = LabelEncoder()
    le_physical = LabelEncoder()
    
    df['budget_encoded'] = le_budget.fit_transform(df['budget_level'])
    df['style_encoded'] = le_style.fit_transform(df['travel_style'])
    df['vehicle_encoded'] = le_vehicle.fit_transform(df['vehicle'])
    df['type_encoded'] = le_type.fit_transform(df['activity_type'])
    df['physical_encoded'] = le_physical.fit_transform(df['physical_level'])
    
    # Feature columns for model
    feature_cols = [
        'cost', 'duration', 'priority_score', 'weather_sensitive',
        'user_budget', 'interest_match', 'vehicle_compatible',
        'budget_encoded', 'style_encoded', 'vehicle_encoded',
        'type_encoded', 'physical_encoded',
    ]
    
    X = df[feature_cols]
    y = df['rating']
    
    print(f"✅ Features shape: {X.shape}")
    print(f"   Features: {feature_cols}")
    
    # 3. Split data
    print("\n[3/6] Splitting train/test data...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    print(f"✅ Train: {len(X_train)} samples, Test: {len(X_test)} samples")
    
    # 4. Scale features
    print("\n[4/6] Scaling features...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    print("✅ Features scaled")
    
    # 5. Train model
    print("\n[5/6] Training Random Forest Regressor...")
    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=15,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
        verbose=0
    )
    
    model.fit(X_train_scaled, y_train)
    print("✅ Model trained")
    
    # 6. Evaluate
    print("\n[6/6] Evaluating model...")
    y_pred_train = model.predict(X_train_scaled)
    y_pred_test = model.predict(X_test_scaled)
    
    train_rmse = np.sqrt(mean_squared_error(y_train, y_pred_train))
    test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
    train_mae = mean_absolute_error(y_train, y_pred_train)
    test_mae = mean_absolute_error(y_test, y_pred_test)
    train_r2 = r2_score(y_train, y_pred_train)
    test_r2 = r2_score(y_test, y_pred_test)
    
    print(f"\n{'='*70}")
    print("MODEL EVALUATION RESULTS")
    print(f"{'='*70}")
    print(f"Train RMSE: {train_rmse:.4f}")
    print(f"Test RMSE:  {test_rmse:.4f}")
    print(f"Train MAE:  {train_mae:.4f}")
    print(f"Test MAE:   {test_mae:.4f}")
    print(f"Train R²:   {train_r2:.4f}")
    print(f"Test R²:    {test_r2:.4f}")
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': feature_cols,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print(f"\n{'='*70}")
    print("FEATURE IMPORTANCE")
    print(f"{'='*70}")
    for idx, row in feature_importance.head(10).iterrows():
        print(f"{row['feature']:30s} {row['importance']:.4f}")
    
    # 7. Save models
    print(f"\n{'='*70}")
    print("SAVING MODELS")
    print(f"{'='*70}")
    
    os.makedirs(MODEL_DIR, exist_ok=True)
    
    joblib.dump(model, os.path.join(MODEL_DIR, 'itinerary_recommender.pkl'))
    joblib.dump(scaler, os.path.join(MODEL_DIR, 'itinerary_scaler.pkl'))
    joblib.dump(le_budget, os.path.join(MODEL_DIR, 'le_budget_itinerary.pkl'))
    joblib.dump(le_style, os.path.join(MODEL_DIR, 'le_style_itinerary.pkl'))
    joblib.dump(le_vehicle, os.path.join(MODEL_DIR, 'le_vehicle_itinerary.pkl'))
    joblib.dump(le_type, os.path.join(MODEL_DIR, 'le_type_itinerary.pkl'))
    joblib.dump(le_physical, os.path.join(MODEL_DIR, 'le_physical_itinerary.pkl'))
    
    print("✅ Saved: itinerary_recommender.pkl")
    print("✅ Saved: itinerary_scaler.pkl")
    print("✅ Saved: 5 label encoders")
    
    # Save training data sample for reference
    df.head(100).to_csv(
        os.path.join(MODEL_DIR, 'itinerary_training_sample.csv'),
        index=False
    )
    print("✅ Saved: itinerary_training_sample.csv")
    
    # Save evaluation report
    report = {
        'model_type': 'Random Forest Regressor',
        'training_date': datetime.now().isoformat(),
        'n_samples': len(df),
        'n_features': len(feature_cols),
        'n_users': df['user_id'].nunique(),
        'n_activities': df['activity_id'].nunique(),
        'metrics': {
            'train_rmse': float(train_rmse),
            'test_rmse': float(test_rmse),
            'train_mae': float(train_mae),
            'test_mae': float(test_mae),
            'train_r2': float(train_r2),
            'test_r2': float(test_r2),
        },
        'feature_importance': feature_importance.to_dict('records'),
        'feature_columns': feature_cols,
    }
    
    with open(os.path.join(MODEL_DIR, 'itinerary_model_report.json'), 'w') as f:
        json.dump(report, f, indent=2)
    print("✅ Saved: itinerary_model_report.json")
    
    print(f"\n{'='*70}")
    print("✅ TRAINING COMPLETED SUCCESSFULLY!")
    print(f"{'='*70}")
    
    return model, scaler, report


if __name__ == '__main__':
    train_itinerary_recommendation_model()
