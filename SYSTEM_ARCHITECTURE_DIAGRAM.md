# 🏗️ DITA SYSTEM ARCHITECTURE DIAGRAM

**Visual Guide untuk Presentasi**

---

## 📊 OVERALL SYSTEM ARCHITECTURE

```
┌────────────────────────────────────────────────────────────────────────┐
│                        DITA SYSTEM OVERVIEW                              │
│                  (Dieng Intelligent Tourism Assistant)                   │
└────────────────────────────────────────────────────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼
┌───────────────┐         ┌──────────────────┐       ┌──────────────────┐
│  WEATHER      │         │  ROUTE SAFETY    │       │   ITINERARY      │
│  PREDICTION   │         │  ASSESSMENT      │       │ RECOMMENDATION   │
│               │         │                  │       │                  │
│ • Temperature │         │ • Road condition │       │ • Personalized   │
│ • Rain        │         │ • Vehicle match  │       │ • Budget aware   │
│ • Risk Level  │         │ • Weather impact │       │ • Interest-based │
└───────────────┘         └──────────────────┘       └──────────────────┘
   3 ML Models                 1 ML Model                 1 ML Model
```

---

## 🔄 DATA FLOW DIAGRAM

### **1. Weather Prediction Flow**

```
┌─────────────────┐
│ Historical Data │  ← 38,880 samples (2022-2026)
│  (5 years)      │  ← Open-Meteo Historical API
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│         FEATURE ENGINEERING                             │
│  • Temporal: hour, day, month, cyclical encoding        │
│  • Lags: temp_lag_1h, 3h, 6h, 24h                      │
│  • Rolling: mean_6h, std_6h, sum_24h                   │
│  • Weather: humidity, dewpoint, windspeed, fog_risk    │
└────────┬────────────────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────────────────┐
│              ML MODEL TRAINING                         │
│                                                        │
│  Model 1: Random Forest (Temperature)  → R²: 99.58%   │
│  Model 2: GradientBoost (Rain)        → Acc: 95.85%  │
│  Model 3: GradientBoost (Risk)        → Acc: 98.03%  │
└────────┬───────────────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────────────────┐
│              SAVE MODELS                               │
│  • temperature_model.pkl + temp_scaler.pkl             │
│  • rain_classifier.pkl + rain_scaler.pkl               │
│  • risk_classifier.pkl + risk_scaler.pkl               │
└────────┬───────────────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────────────────┐
│           REAL-TIME PREDICTION                         │
│                                                        │
│  User Request → Load Models → Predict → Return JSON   │
│                                                        │
│  + Real-time API data (current conditions)             │
└────────────────────────────────────────────────────────┘
```

### **2. Route Safety Flow**

```
┌──────────────────┐
│  Route Dataset   │  ← 180 samples (30 routes × 6 conditions)
│  (Manual Survey) │  ← Expert labeling
└────────┬─────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│         FEATURE EXTRACTION                              │
│  • gradient, width, surface, visibility                 │
│  • guardrail, elevation, curves, lighting               │
│  • vehicle type, weather condition                      │
│  • effective_visibility (visibility × weather_factor)   │
│  • vehicle_score (engineered feature)                   │
└────────┬────────────────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────────────────┐
│          ENCODING & SCALING                            │
│  • LabelEncoder: surface, vehicle, weather             │
│  • StandardScaler: numerical features                  │
└────────┬───────────────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────────────────┐
│          RANDOM FOREST TRAINING                        │
│  • n_estimators=200, max_depth=15                      │
│  • Multi-class: Aman(0) / Waspada(1) / Bahaya(2)      │
│  • Result: 100% Accuracy                               │
└────────┬───────────────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────────────────┐
│          SAVE MODEL & ENCODERS                         │
│  • route_safety_model.pkl + route_scaler.pkl           │
│  • le_surface.pkl, le_vehicle.pkl, le_weather.pkl      │
└────────┬───────────────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────────────────┐
│          API PREDICTION                                │
│  Input: route params + vehicle + weather               │
│  Output: Safety class + confidence scores              │
└────────────────────────────────────────────────────────┘
```

### **3. Itinerary Recommendation Flow**

```
┌───────────────────┐         ┌──────────────────────┐
│ Activities DB     │         │  Synthetic Users     │
│ (105 activities)  │    ×    │  (15 profiles)       │
│ • 76 attractions  │         │  • Budget levels     │
│ • 28 culinary     │         │  • Travel styles     │
│ • 1 hotel         │         │  • Interests         │
└─────────┬─────────┘         └──────────┬───────────┘
          │                              │
          └──────────┬───────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────┐
│         SYNTHETIC RATING GENERATION                      │
│                                                          │
│  For each (user, activity) pair:                         │
│    base_rating = 3.0                                     │
│    + interest_match × 0.6                                │
│    + budget_fit (affordable: +0.5, expensive: -0.5)      │
│    + style_match (family+easy: +0.4, family+hard: -0.6)  │
│    + vehicle_compatible (match: 0, no_match: -1.0)       │
│    + random_noise ~ N(0, 0.5)                            │
│    = final_rating (1.0 - 5.0 stars)                      │
│                                                          │
│  Total: 15 users × 105 activities = 1,575 samples        │
└─────────┬────────────────────────────────────────────────┘
          │
          ▼
┌──────────────────────────────────────────────────────────┐
│         FEATURE ENGINEERING (12 features)                │
│                                                          │
│  Activity Features:                                      │
│    • cost, duration, priority_score                      │
│    • weather_sensitive (binary)                          │
│    • type_encoded (attraction/food/hotel)                │
│    • physical_encoded (easy/medium/hard)                 │
│                                                          │
│  User Features:                                          │
│    • user_budget, budget_encoded (low/med/high)          │
│    • style_encoded (solo/couple/family/group)            │
│    • vehicle_encoded (motorcycle/car/bus)                │
│                                                          │
│  Interaction Features:                                   │
│    • interest_match (0-5)                                │
│    • vehicle_compatible (binary)                         │
└─────────┬────────────────────────────────────────────────┘
          │
          ▼
┌──────────────────────────────────────────────────────────┐
│         RANDOM FOREST TRAINING                           │
│  • Task: Regression (predict rating 1-5)                 │
│  • Algorithm: Random Forest Regressor                    │
│  • Parameters: n_estimators=200, max_depth=15            │
│  • Train/Test: 1,260 / 315 (80/20 split)                │
│                                                          │
│  Results:                                                │
│    • Train R²: 79.49%, MAE: 0.2554                       │
│    • Test R²: 38.38%, MAE: 0.4318                        │
│                                                          │
│  Feature Importance:                                     │
│    1. interest_match: 43.4% ← MOST IMPORTANT!            │
│    2. priority_score: 13.3%                              │
│    3. vehicle_compatible: 12.6%                          │
└─────────┬────────────────────────────────────────────────┘
          │
          ▼
┌──────────────────────────────────────────────────────────┐
│         SAVE MODEL & ENCODERS                            │
│  • itinerary_recommender.pkl + itinerary_scaler.pkl      │
│  • le_budget, le_style, le_vehicle, le_type, le_physical│
│  • itinerary_model_report.json                           │
│  • itinerary_training_sample.csv                         │
└─────────┬────────────────────────────────────────────────┘
          │
          ▼
┌──────────────────────────────────────────────────────────┐
│      INFERENCE (Generate Personalized Itinerary)         │
│                                                          │
│  1. User submits preferences:                            │
│     • budget, interests, travel_style, vehicle, days     │
│                                                          │
│  2. For each of 105 activities:                          │
│     • Extract features                                   │
│     • Encode categorical variables                       │
│     • Scale numerical features                           │
│     • ML model predicts rating (1-5 stars)               │
│                                                          │
│  3. Rank activities by predicted rating (high → low)     │
│                                                          │
│  4. Select top activities considering:                   │
│     • Budget constraint (total cost ≤ budget × days)     │
│     • Time constraint (fit activities in N days)         │
│     • Variety (mix attraction, food, accommodation)      │
│                                                          │
│  5. Build daily schedule with optimal timing             │
│                                                          │
│  6. Return JSON response with ranked itinerary           │
└──────────────────────────────────────────────────────────┘
```

---

## 🎯 MULTI-LAYER FALLBACK STRATEGY

### **Itinerary Generation Hierarchy**

```
┌────────────────────────────────────────────────────────────────┐
│                   USER REQUEST                                 │
│  POST /api/itinerary/generate                                  │
│  {duration: 3, budget: 1.5M, interests: ["alam","fotografi"]}  │
└──────────────────────────┬─────────────────────────────────────┘
                           │
                    ┌──────┴───────┐
                    │  use_ai ?    │
                    └──────┬───────┘
                           │
              ┌────────────┴────────────┐
              │                         │
             YES                       NO
              │                         │
              ▼                         ▼
    ┌──────────────────┐      ┌─────────────────┐
    │   LAYER 1: AI    │      │  SKIP TO LAYER 2│
    │                  │      └─────────────────┘
    │ ┌──────────────┐ │               │
    │ │ Gemini AI    │ │               │
    │ │ (Primary)    │ │               │
    │ └──────┬───────┘ │               │
    │        │Success  │               │
    │        ├────────►├───────────────┤
    │        │Fail     │               │
    │        ▼         │               │
    │ ┌──────────────┐ │               │
    │ │ NVIDIA API   │ │               │
    │ │ (Fallback 1) │ │               │
    │ └──────┬───────┘ │               │
    │        │Success  │               │
    │        ├────────►├───────────────┤
    │        │Fail     │               │
    └────────┼─────────┘               │
             │                         │
             ▼                         ▼
    ┌──────────────────────────────────────┐
    │   LAYER 2: ML MODEL (Smart Engine)   │
    │                                      │
    │  ┌────────────────────────────────┐  │
    │  │ Check: ML model loaded?        │  │
    │  └────────────┬───────────────────┘  │
    │               │                      │
    │      ┌────────┴────────┐             │
    │      │                 │             │
    │     YES               NO             │
    │      │                 │             │
    │      ▼                 ▼             │
    │  ┌────────────┐  ┌────────────┐     │
    │  │ ML-based   │  │ Rule-based │     │
    │  │ Scoring    │  │ Scoring    │     │
    │  │            │  │            │     │
    │  │ • Load     │  │ • Priority │     │
    │  │   model    │  │   score    │     │
    │  │ • Predict  │  │ • Interest │     │
    │  │   ratings  │  │   match    │     │
    │  │ • Rank by  │  │ • Budget   │     │
    │  │   ML score │  │   filter   │     │
    │  └────────────┘  └────────────┘     │
    │      │                 │             │
    │      └────────┬─────────┘            │
    │               │                      │
    └───────────────┼──────────────────────┘
                    │
                    ▼
    ┌──────────────────────────────────────┐
    │   BUILD DAILY ITINERARY              │
    │   • Distribute activities across days│
    │   • Optimize timing                  │
    │   • Check budget & time constraints  │
    │   • Add variety (mix types)          │
    └──────────────────┬───────────────────┘
                       │
                       ▼
    ┌──────────────────────────────────────┐
    │   RETURN JSON RESPONSE               │
    │   {                                  │
    │     "days": [...],                   │
    │     "meta": {                        │
    │       "source": "ml_model",          │
    │       "model_type": "Random Forest", │
    │       "total_cost": 450000           │
    │     }                                │
    │   }                                  │
    └──────────────────────────────────────┘

Legend:
✅ Success path
❌ Fail → fallback
🔄 Alternative path
```

---

## 📦 MODEL FILES STRUCTURE

```
backend/app/models/saved/
│
├── WEATHER MODELS (Models 1-3)
│   ├── temperature_model.pkl         ← Random Forest Regressor
│   ├── temp_scaler.pkl                ← StandardScaler
│   ├── rain_classifier.pkl            ← Gradient Boosting Classifier
│   ├── rain_scaler.pkl                ← StandardScaler
│   ├── risk_classifier.pkl            ← Gradient Boosting Classifier
│   └── risk_scaler.pkl                ← StandardScaler
│
├── ROUTE SAFETY MODEL (Model 4)
│   ├── route_safety_model.pkl         ← Random Forest Classifier
│   ├── route_scaler.pkl               ← StandardScaler
│   ├── le_surface.pkl                 ← LabelEncoder (aspal/beton/tanah)
│   ├── le_vehicle.pkl                 ← LabelEncoder (motor/car/bus)
│   └── le_weather.pkl                 ← LabelEncoder (cerah/hujan/kabut)
│
├── ITINERARY MODEL (Model 5)
│   ├── itinerary_recommender.pkl      ← Random Forest Regressor
│   ├── itinerary_scaler.pkl           ← StandardScaler
│   ├── le_budget_itinerary.pkl        ← LabelEncoder (low/med/high)
│   ├── le_style_itinerary.pkl         ← LabelEncoder (solo/couple/family/group)
│   ├── le_vehicle_itinerary.pkl       ← LabelEncoder (motor/car/bus)
│   ├── le_type_itinerary.pkl          ← LabelEncoder (attraction/food/hotel)
│   ├── le_physical_itinerary.pkl      ← LabelEncoder (easy/medium/hard)
│   ├── itinerary_model_report.json    ← Evaluation metrics
│   └── itinerary_training_sample.csv  ← Training data sample (100 rows)
│
└── VERSIONING (Optional)
    └── archive/
        ├── version_history.json
        └── [timestamped model backups]

TOTAL FILES: 19 .pkl files + 2 reports
```

---

## 🔬 FEATURE ENGINEERING SUMMARY

### **Weather Models (42 features)**

```
┌─────────────────────────────────────────────┐
│         FEATURE CATEGORIES                  │
├─────────────────────────────────────────────┤
│ 1. Temporal (8 features)                    │
│    • hour, day_of_year, month, is_weekend   │
│    • hour_sin, hour_cos (cyclical)          │
│    • month_sin, month_cos (cyclical)        │
│                                             │
│ 2. Temperature (4 features)                 │
│    • temp_lag_1h, 3h, 6h, 24h               │
│                                             │
│ 3. Precipitation (2 features)               │
│    • precip_lag_1h, 3h                      │
│                                             │
│ 4. Rolling Stats (5 features)               │
│    • temp: mean_6h, std_6h, mean_24h        │
│    • precip: sum_6h, sum_24h                │
│                                             │
│ 5. Rate of Change (2 features)              │
│    • temp_change_1h, temp_change_3h         │
│                                             │
│ 6. Humidity & Dewpoint (4 features)         │
│    • humidity, dewpoint                     │
│    • temp_dewpoint_spread                   │
│    • humidity_rolling_mean_6h               │
│                                             │
│ 7. Wind (2 features)                        │
│    • windspeed, windspeed_lag_1h            │
│                                             │
│ 8. Visibility & Cloud (2 features)          │
│    • cloudcover, visibility_km              │
│                                             │
│ 9. Derived (2 features)                     │
│    • apparent_temp                          │
│    • fog_risk_score (engineered)            │
└─────────────────────────────────────────────┘
```

### **Route Safety Model (11 features)**

```
┌─────────────────────────────────────────────┐
│    FEATURE CATEGORIES                       │
├─────────────────────────────────────────────┤
│ 1. Road Geometry (4 features)               │
│    • gradient (degrees)                     │
│    • width (meters)                         │
│    • curve_count (integer)                  │
│    • elevation (mdpl)                       │
│                                             │
│ 2. Infrastructure (3 features)              │
│    • surface_encoded (aspal/beton/tanah)    │
│    • guardrail (binary)                     │
│    • lighting (binary)                      │
│                                             │
│ 3. Visibility (1 feature)                   │
│    • effective_visibility                   │
│      = visibility × weather_multiplier      │
│      (cerah: 1.0, hujan: 0.5, kabut: 0.3)   │
│                                             │
│ 4. Vehicle & Weather (3 features)           │
│    • vehicle_encoded (motor/car/bus)        │
│    • weather_encoded (cerah/hujan/kabut)    │
│    • vehicle_score (engineered:             │
│      motor=0.6, car=0.8, bus=0.4)           │
└─────────────────────────────────────────────┘
```

### **Itinerary Model (12 features)**

```
┌─────────────────────────────────────────────┐
│    FEATURE CATEGORIES                       │
├─────────────────────────────────────────────┤
│ 1. Activity Attributes (4 features)         │
│    • cost (Rupiah)                          │
│    • duration (hours)                       │
│    • priority_score (0-100)                 │
│    • weather_sensitive (binary)             │
│                                             │
│ 2. User Preferences (3 features)            │
│    • user_budget (Rupiah)                   │
│    • budget_encoded (low/med/high)          │
│    • style_encoded (solo/couple/family)     │
│                                             │
│ 3. Matching Features (2 features)           │
│    • interest_match (0-5) ← KEY!            │
│    • vehicle_compatible (binary)            │
│                                             │
│ 4. Encoded Categories (3 features)          │
│    • vehicle_encoded (motor/car/bus)        │
│    • type_encoded (attraction/food/hotel)   │
│    • physical_encoded (easy/medium/hard)    │
└─────────────────────────────────────────────┘
```

---

## 🎯 PERFORMANCE SUMMARY TABLE

| Model | Algorithm | Samples | Features | Train Metric | Test Metric | Status |
|-------|-----------|---------|----------|--------------|-------------|--------|
| **Temperature** | Random Forest Reg | 38,880 | 42 | R²: 99.58% | MAE: 0.088°C | ⭐⭐⭐⭐⭐ |
| **Rain** | Gradient Boost CL | 38,880 | 42 | Acc: 96.2% | Acc: 95.85% | ⭐⭐⭐⭐⭐ |
| **Risk** | Gradient Boost CL | 38,880 | 42 | Acc: 98.5% | Acc: 98.03% | ⭐⭐⭐⭐⭐ |
| **Route Safety** | Random Forest CL | 180 | 11 | Acc: 100% | Acc: 100% | ⭐⭐⭐⭐⭐ |
| **Itinerary** | Random Forest Reg | 1,575 | 12 | R²: 79.49% | R²: 38.38% | ⭐⭐⭐ |

**Legend:**
- ⭐⭐⭐⭐⭐ = Excellent (production-ready)
- ⭐⭐⭐ = Good (acceptable for recommendation)
- Reg = Regressor, CL = Classifier

---

## 📱 API INTEGRATION FLOW

```
┌──────────────┐
│   Frontend   │  (React/Vite)
│   (User UI)  │
└──────┬───────┘
       │ HTTP Request
       │ (JSON)
       ▼
┌──────────────────────┐
│   FastAPI Backend    │  (Python)
│   Port: 8000         │
└──────┬───────────────┘
       │
       ├──► POST /api/ml/predict/quick
       │    ├─► Load weather models (1-3)
       │    ├─► Get real-time data (Open-Meteo API)
       │    ├─► Predict: temp, rain, risk
       │    └─► Return: predictions + advisory
       │
       ├──► POST /api/ml/predict/route
       │    ├─► Load route model (4)
       │    ├─► Encode: surface, vehicle, weather
       │    ├─► Predict: safety class
       │    └─► Return: safety level + confidence
       │
       └──► POST /api/itinerary/generate
            ├─► Try: Gemini AI (if use_ai=true)
            ├─► Try: NVIDIA API (fallback)
            └─► Use: ML Model (5) or Rules
                ├─► Load 105 activities from DB
                ├─► Predict ratings for all activities
                ├─► Rank by ML score
                ├─► Build N-day itinerary
                └─► Return: JSON with daily schedule
```

---

## 💾 DATA PERSISTENCE

```
┌────────────────────────────────────────────┐
│         DATA STORAGE LAYERS                │
├────────────────────────────────────────────┤
│                                            │
│  ┌──────────────────────────────────────┐  │
│  │  HISTORICAL DATA (Static)            │  │
│  │  • dieng_historical_combined.json    │  │
│  │  • dieng_route_dataset.csv           │  │
│  │  • 105 activities (hard-coded in .py)│  │
│  └──────────────────────────────────────┘  │
│                                            │
│  ┌──────────────────────────────────────┐  │
│  │  ML MODELS (Persistent)              │  │
│  │  • 19 .pkl files in saved/           │  │
│  │  • Version history (JSON)            │  │
│  │  • Evaluation reports (JSON)         │  │
│  └──────────────────────────────────────┘  │
│                                            │
│  ┌──────────────────────────────────────┐  │
│  │  REAL-TIME DATA (Dynamic)            │  │
│  │  • Open-Meteo API (weather)          │  │
│  │  • User requests (session)           │  │
│  │  • API responses (temporary)         │  │
│  └──────────────────────────────────────┘  │
│                                            │
│  ┌──────────────────────────────────────┐  │
│  │  FUTURE: User Database               │  │
│  │  • User profiles                     │  │
│  │  • Trip history                      │  │
│  │  • Ratings & feedback                │  │
│  │  • Collaborative filtering data      │  │
│  └──────────────────────────────────────┘  │
│                                            │
└────────────────────────────────────────────┘
```

---

**Use these diagrams during presentation untuk explain system architecture!**
