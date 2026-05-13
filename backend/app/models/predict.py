"""
==============================================================================
DITA ML Prediction Engine — Inference Module
==============================================================================
Modul ini memuat model ML yang sudah di-train dan menyediakan
fungsi prediksi yang dapat dipanggil oleh FastAPI endpoint.

Usage:
    from app.ml.predict import DiengPredictor
    predictor = DiengPredictor()
    result = predictor.predict_weather(hour=15, month=6, ...)
    safety = predictor.predict_route_safety("Tanjakan Sikarim", "motorcycle", "kabut")

Author      : Tim PJK-GM067 (Ida Masruroh — AI Engineer)
==============================================================================
"""

import os
import json
import numpy as np
import pandas as pd
import joblib
from datetime import datetime

MODEL_DIR = os.path.join(os.path.dirname(__file__), 'saved')  # models/saved/
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')


class DiengPredictor:
    """
    Kelas utama untuk melakukan prediksi menggunakan model ML
    yang telah di-train pada data historis Dieng.
    """
    
    def __init__(self):
        self.models_loaded = False
        self.temp_model = None
        self.temp_scaler = None
        self.rain_model = None
        self.rain_scaler = None
        self.risk_model = None
        self.risk_scaler = None
        self.route_model = None
        self.route_scaler = None
        self.le_surface = None
        self.le_vehicle = None
        self.le_weather = None
        
        self._load_models()
    
    def _load_models(self):
        """Load semua model dari disk."""
        try:
            self.temp_model = joblib.load(os.path.join(MODEL_DIR, 'temperature_model.pkl'))
            self.temp_scaler = joblib.load(os.path.join(MODEL_DIR, 'temp_scaler.pkl'))
            self.rain_model = joblib.load(os.path.join(MODEL_DIR, 'rain_classifier.pkl'))
            self.rain_scaler = joblib.load(os.path.join(MODEL_DIR, 'rain_scaler.pkl'))
            self.risk_model = joblib.load(os.path.join(MODEL_DIR, 'risk_classifier.pkl'))
            self.risk_scaler = joblib.load(os.path.join(MODEL_DIR, 'risk_scaler.pkl'))
            self.route_model = joblib.load(os.path.join(MODEL_DIR, 'route_safety_model.pkl'))
            self.route_scaler = joblib.load(os.path.join(MODEL_DIR, 'route_scaler.pkl'))
            self.le_surface = joblib.load(os.path.join(MODEL_DIR, 'le_surface.pkl'))
            self.le_vehicle = joblib.load(os.path.join(MODEL_DIR, 'le_vehicle.pkl'))
            self.le_weather = joblib.load(os.path.join(MODEL_DIR, 'le_weather.pkl'))
            self.models_loaded = True
            print("[OK] Semua model ML berhasil dimuat!")
        except Exception as e:
            print(f"[WARN] Model belum di-train. Jalankan training dulu: {e}")
            self.models_loaded = False
    
    def _build_weather_features(self, hour, month, day_of_year, current_temp,
                                current_precip, temp_3h_ago, temp_6h_ago, temp_24h_ago,
                                humidity=80.0, dewpoint=None, windspeed=10.0,
                                cloudcover=50.0, visibility_km=5.0, apparent_temp=None):
        """Build feature DataFrame dengan nama kolom yang sesuai training v2."""
        if dewpoint is None:
            # Estimasi dewpoint dari suhu dan humidity (Magnus formula approx)
            dewpoint = current_temp - ((100 - humidity) / 5.0)
        if apparent_temp is None:
            apparent_temp = current_temp - 3.0

        temp_dewpoint_spread = current_temp - dewpoint
        # Fog risk score
        spread_norm   = min(max(temp_dewpoint_spread, 0), 10) / 10.0
        humidity_norm = (min(max(humidity, 50), 100) - 50) / 50.0
        vis_norm      = 1.0 - (min(max(visibility_km, 0), 10) / 10.0)
        fog_risk_score = (
            (1 - spread_norm) * 0.4 +
            humidity_norm     * 0.35 +
            vis_norm          * 0.25
        )

        return pd.DataFrame([{
            # Temporal
            "hour":        hour,
            "day_of_year": day_of_year,
            "month":       month,
            "is_weekend":  1 if datetime.now().weekday() >= 5 else 0,
            "hour_sin":    np.sin(2 * np.pi * hour / 24),
            "hour_cos":    np.cos(2 * np.pi * hour / 24),
            "month_sin":   np.sin(2 * np.pi * month / 12),
            "month_cos":   np.cos(2 * np.pi * month / 12),
            # Temperature lags
            "temp_lag_1h":  current_temp,
            "temp_lag_3h":  temp_3h_ago,
            "temp_lag_6h":  temp_6h_ago,
            "temp_lag_24h": temp_24h_ago,
            # Precipitation lags
            "precip_lag_1h": current_precip,
            "precip_lag_3h": current_precip * 0.8,
            # Rolling stats
            "temp_rolling_mean_6h":   (current_temp + temp_3h_ago + temp_6h_ago) / 3,
            "temp_rolling_std_6h":    float(np.std([current_temp, temp_3h_ago, temp_6h_ago])),
            "temp_rolling_mean_24h":  (current_temp + temp_24h_ago) / 2,
            "precip_rolling_sum_6h":  current_precip * 3,
            "precip_rolling_sum_24h": current_precip * 12,
            # Rate of change
            "temp_change_1h": current_temp - temp_3h_ago,
            "temp_change_3h": current_temp - temp_6h_ago,
            # NEW: Humidity & dewpoint
            "humidity":                  humidity,
            "dewpoint":                  dewpoint,
            "temp_dewpoint_spread":      temp_dewpoint_spread,
            "humidity_lag_1h":           humidity,
            "humidity_rolling_mean_6h":  humidity,
            # NEW: Wind
            "windspeed":      windspeed,
            "windspeed_lag_1h": windspeed,
            # NEW: Cloud & visibility
            "cloudcover":    cloudcover,
            "visibility_km": visibility_km,
            # NEW: Apparent temp
            "apparent_temp": apparent_temp,
            # NEW: Fog risk
            "fog_risk_score": fog_risk_score,
        }])

    def predict_temperature(self, hour: int, month: int, day_of_year: int,
                            current_temp: float, current_precip: float,
                            temp_3h_ago: float = None, temp_6h_ago: float = None,
                            temp_24h_ago: float = None, **kwargs):
        """Prediksi suhu 1 jam ke depan di Dieng."""
        if not self.models_loaded:
            return self._fallback_temp_prediction(hour, month, current_temp)

        if temp_3h_ago is None: temp_3h_ago = current_temp
        if temp_6h_ago is None: temp_6h_ago = current_temp
        if temp_24h_ago is None: temp_24h_ago = current_temp

        features = self._build_weather_features(
            hour, month, day_of_year, current_temp, current_precip,
            temp_3h_ago, temp_6h_ago, temp_24h_ago,
            humidity=kwargs.get("humidity", 80.0),
            dewpoint=kwargs.get("dewpoint", None),
            windspeed=kwargs.get("windspeed", 10.0),
            cloudcover=kwargs.get("cloudcover", 50.0),
            visibility_km=kwargs.get("visibility_km", 5.0),
            apparent_temp=kwargs.get("apparent_temp", None),
        )

        # Handle model trained with old features (v1) vs new features (v2)
        try:
            features_scaled = self.temp_scaler.transform(features)
        except ValueError:
            # Fallback: model lama hanya punya 21 kolom, pakai subset
            features_scaled = self.temp_scaler.transform(features[self._v1_cols()])

        predicted_temp = float(self.temp_model.predict(features_scaled)[0])
        advisory = self._generate_temp_advisory(predicted_temp, hour)

        return {
            "predicted_temperature": round(predicted_temp, 1),
            "current_temperature": current_temp,
            "change": round(predicted_temp - current_temp, 1),
            "model": "Random Forest Regressor",
            "advisory": advisory,
        }
    
    def predict_rain(self, hour: int, month: int, day_of_year: int,
                     current_temp: float, current_precip: float, **kwargs):
        """Prediksi apakah akan hujan dalam 1 jam ke depan."""
        if not self.models_loaded:
            return self._fallback_rain_prediction(hour, current_precip)

        temp_3h_ago  = kwargs.get('temp_3h_ago', current_temp)
        temp_6h_ago  = kwargs.get('temp_6h_ago', current_temp)
        temp_24h_ago = kwargs.get('temp_24h_ago', current_temp)

        features = self._build_weather_features(
            hour, month, day_of_year, current_temp, current_precip,
            temp_3h_ago, temp_6h_ago, temp_24h_ago,
            humidity=kwargs.get("humidity", 80.0),
            dewpoint=kwargs.get("dewpoint", None),
            windspeed=kwargs.get("windspeed", 10.0),
            cloudcover=kwargs.get("cloudcover", 50.0),
            visibility_km=kwargs.get("visibility_km", 5.0),
            apparent_temp=kwargs.get("apparent_temp", None),
        )

        try:
            features_scaled = self.rain_scaler.transform(features)
        except ValueError:
            features_scaled = self.rain_scaler.transform(features[self._v1_cols()])

        prediction  = int(self.rain_model.predict(features_scaled)[0])
        probability = float(self.rain_model.predict_proba(features_scaled)[0][1])

        return {
            "will_rain": bool(prediction),
            "rain_probability": round(probability * 100, 1),
            "model": "Gradient Boosting Classifier",
            "advisory": "🌧️ Siapkan jas hujan dan peralatan anti-air!" if prediction else "☀️ Tidak ada prediksi hujan dalam 1 jam ke depan.",
        }
    
    def predict_risk_level(self, hour: int, month: int, day_of_year: int,
                          current_temp: float, current_precip: float, **kwargs):
        """Prediksi tingkat risiko wisata berdasarkan kondisi cuaca."""
        if not self.models_loaded:
            return self._fallback_risk_prediction(current_temp, current_precip)

        temp_3h_ago  = kwargs.get('temp_3h_ago', current_temp)
        temp_6h_ago  = kwargs.get('temp_6h_ago', current_temp)
        temp_24h_ago = kwargs.get('temp_24h_ago', current_temp)

        features = self._build_weather_features(
            hour, month, day_of_year, current_temp, current_precip,
            temp_3h_ago, temp_6h_ago, temp_24h_ago,
            humidity=kwargs.get("humidity", 80.0),
            dewpoint=kwargs.get("dewpoint", None),
            windspeed=kwargs.get("windspeed", 10.0),
            cloudcover=kwargs.get("cloudcover", 50.0),
            visibility_km=kwargs.get("visibility_km", 5.0),
            apparent_temp=kwargs.get("apparent_temp", None),
        )

        try:
            features_scaled = self.risk_scaler.transform(features)
        except ValueError:
            features_scaled = self.risk_scaler.transform(features[self._v1_cols()])

        prediction    = int(self.risk_model.predict(features_scaled)[0])
        probabilities = self.risk_model.predict_proba(features_scaled)[0]
        
        risk_labels = {0: "Aman", 1: "Waspada", 2: "Bahaya"}
        risk_icons = {0: "✅", 1: "⚠️", 2: "🔴"}
        risk_colors = {0: "#22c55e", 1: "#f59e0b", 2: "#ef4444"}
        
        advisories = {
            0: "Kondisi cuaca aman untuk berwisata. Tetap patuhi rambu dan bawa perlengkapan dasar.",
            1: "Harap berhati-hati! Suhu cukup rendah atau cuaca berpotensi berubah. Bawa jaket tebal dan senter.",
            2: "BAHAYA! Kondisi cuaca ekstrem. Hindari jalur terbuka dan tanjakan curam. Utamakan keselamatan!"
        }
        
        return {
            "risk_level": prediction,
            "risk_label": risk_labels[prediction],
            "risk_icon": risk_icons[prediction],
            "risk_color": risk_colors[prediction],
            "confidence": {
                "aman": round(float(probabilities[0]) * 100, 1),
                "waspada": round(float(probabilities[1]) * 100, 1),
                "bahaya": round(float(probabilities[2]) * 100, 1),
            },
            "model": "Gradient Boosting Classifier",
            "advisory": advisories[prediction]
        }
    
    def predict_route_safety(self, gradient: float, width: float,
                             visibility: float, guardrail: int,
                             surface: str, elevation: float,
                             curve_count: int, lighting: int,
                             vehicle: str, weather: str):
        """Prediksi keamanan rute wisata spesifik berdasarkan kondisi."""
        if not self.models_loaded:
            return self._fallback_route_safety(gradient, vehicle)

        vehicle_scores = {'motorcycle': 0.6, 'car': 0.8, 'bus': 0.4}
        vis_multiplier = {'cerah': 1.0, 'mendung': 0.8, 'hujan': 0.5, 'kabut': 0.3}

        effective_vis = visibility * vis_multiplier.get(weather, 0.5)
        vehicle_score = vehicle_scores.get(vehicle, 0.6)

        try:
            surface_enc = int(self.le_surface.transform([surface])[0])
        except ValueError:
            surface_enc = 0
        try:
            vehicle_enc = int(self.le_vehicle.transform([vehicle])[0])
        except ValueError:
            vehicle_enc = 0
        try:
            weather_enc = int(self.le_weather.transform([weather])[0])
        except ValueError:
            weather_enc = 0

        features = pd.DataFrame([{
            'gradient': gradient,
            'width': width,
            'effective_visibility': effective_vis,
            'guardrail': guardrail,
            'surface_encoded': surface_enc,
            'elevation': elevation,
            'curve_count': curve_count,
            'lighting': lighting,
            'vehicle_encoded': vehicle_enc,
            'weather_encoded': weather_enc,
            'vehicle_score': vehicle_score,
        }])

        features_scaled = self.route_scaler.transform(features)
        prediction = int(self.route_model.predict(features_scaled)[0])
        probabilities = self.route_model.predict_proba(features_scaled)[0]
        
        safety_labels = {0: "Aman", 1: "Waspada", 2: "Bahaya"}
        safety_icons = {0: "✅", 1: "⚠️", 2: "🔴"}
        
        return {
            "safety_class": prediction,
            "safety_label": safety_labels[prediction],
            "safety_icon": safety_icons[prediction],
            "confidence": {
                "aman": round(float(probabilities[0]) * 100, 1),
                "waspada": round(float(probabilities[1]) * 100, 1),
                "bahaya": round(float(probabilities[2]) * 100, 1),
            },
            "vehicle": vehicle,
            "weather": weather,
            "model": "Random Forest Classifier"
        }
    
    def _v1_cols(self):
        """Kolom model v1 (21 features) untuk backward compatibility."""
        return [
            'hour', 'day_of_year', 'month',
            'hour_sin', 'hour_cos', 'month_sin', 'month_cos', 'is_weekend',
            'temp_lag_1h', 'temp_lag_3h', 'temp_lag_6h', 'temp_lag_24h',
            'precip_lag_1h', 'precip_lag_3h',
            'temp_rolling_mean_6h', 'temp_rolling_std_6h', 'temp_rolling_mean_24h',
            'precip_rolling_sum_6h', 'precip_rolling_sum_24h',
            'temp_change_1h', 'temp_change_3h',
        ]

    # ─── FALLBACK METHODS (bila model belum di-train) ───
    
    def _fallback_temp_prediction(self, hour, month, current_temp):
        # Pola suhu harian Dieng: dingin malam, hangat siang
        hour_effect = -3 * np.cos(2 * np.pi * (hour - 14) / 24)
        predicted = current_temp + hour_effect * 0.3
        return {
            "predicted_temperature": round(predicted, 1),
            "current_temperature": current_temp,
            "change": round(predicted - current_temp, 1),
            "model": "Rule-based Fallback",
            "advisory": self._generate_temp_advisory(predicted, hour)
        }
    
    def _fallback_rain_prediction(self, hour, current_precip):
        # Afternoon rain pattern di dataran tinggi
        prob = 30 if 13 <= hour <= 18 else 15
        if current_precip > 0: prob = min(prob + 40, 95)
        return {
            "will_rain": prob > 50,
            "rain_probability": prob,
            "model": "Rule-based Fallback",
            "advisory": "🌧️ Siapkan jas hujan!" if prob > 50 else "☀️ Tidak ada prediksi hujan."
        }
    
    def _fallback_risk_prediction(self, temp, precip):
        if temp < 8 and precip > 0.5:
            level, label = 2, "Bahaya"
        elif temp < 10 or precip > 2:
            level, label = 1, "Waspada"
        else:
            level, label = 0, "Aman"
        return {
            "risk_level": level, "risk_label": label,
            "risk_icon": ["✅", "⚠️", "🔴"][level],
            "risk_color": ["#22c55e", "#f59e0b", "#ef4444"][level],
            "confidence": {"aman": 0, "waspada": 0, "bahaya": 0},
            "model": "Rule-based Fallback",
            "advisory": "Gunakan rule-based karena model belum di-train."
        }
    
    def _fallback_route_safety(self, gradient, vehicle):
        if gradient > 25:
            level = 2
        elif gradient > 15:
            level = 1
        else:
            level = 0
        labels = {0: "Aman", 1: "Waspada", 2: "Bahaya"}
        return {
            "safety_class": level, "safety_label": labels[level],
            "safety_icon": ["✅", "⚠️", "🔴"][level],
            "confidence": {"aman": 0, "waspada": 0, "bahaya": 0},
            "vehicle": vehicle, "weather": "unknown",
            "model": "Rule-based Fallback"
        }
    
    def _generate_temp_advisory(self, temp, hour):
        advisories = []
        if temp < 5:
            advisories.append("🥶 PERINGATAN SUHU EKSTREM! Suhu diprediksi di bawah 5°C. Wajib bawa jaket tebal, syal, dan sarung tangan.")
        elif temp < 10:
            advisories.append("🧥 Suhu cukup dingin. Pastikan membawa jaket tebal dan pakaian berlapis.")
        
        if 3 <= hour <= 5:
            advisories.append("🌅 Waktu ideal menuju Bukit Sikunir untuk sunrise! Bersiap dari jam 3-4 subuh.")
        
        if 15 <= hour <= 17:
            advisories.append("🌫️ Kabut tebal sering terjadi pukul 15:00-17:00. Hindari jalur Sikarim pada jam ini.")
        
        return " ".join(advisories) if advisories else "Kondisi cuaca normal untuk berwisata."
    
    def get_model_info(self):
        """Return info tentang model yang dimuat."""
        report_path = os.path.join(MODEL_DIR, 'evaluation_report.json')
        if os.path.exists(report_path):
            with open(report_path, 'r') as f:
                return json.load(f)
        return {"status": "Models not trained yet"}


# Singleton instance
_predictor = None

def get_predictor():
    global _predictor
    if _predictor is None:
        _predictor = DiengPredictor()
    return _predictor
