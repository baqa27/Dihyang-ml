"""
DITA ML Prediction API Router
Menyediakan endpoint untuk prediksi cuaca dan keamanan rute
menggunakan model ML yang sudah di-train.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from ..models.predict import get_predictor

router = APIRouter()


class WeatherPredictionRequest(BaseModel):
    hour: int
    month: int
    day_of_year: int
    current_temp: float
    current_precip: float = 0.0
    temp_3h_ago: Optional[float] = None
    temp_6h_ago: Optional[float] = None
    temp_24h_ago: Optional[float] = None


class RouteSafetyRequest(BaseModel):
    gradient: float
    width: float = 4.0
    visibility: float = 5.0
    guardrail: int = 0
    surface: str = "aspal"
    elevation: float = 2060.0
    curve_count: int = 5
    lighting: int = 0
    vehicle: str = "motorcycle"
    weather: str = "cerah"


@router.get("/model-info")
async def get_model_info():
    """Informasi tentang model ML yang digunakan."""
    predictor = get_predictor()
    info = predictor.get_model_info()
    info["models_loaded"] = predictor.models_loaded
    return info


@router.post("/predict/temperature")
async def predict_temperature(req: WeatherPredictionRequest):
    """Prediksi suhu 1 jam ke depan di Dieng."""
    predictor = get_predictor()
    kwargs = {}
    if req.temp_3h_ago is not None:
        kwargs["temp_3h_ago"] = req.temp_3h_ago
    if req.temp_6h_ago is not None:
        kwargs["temp_6h_ago"] = req.temp_6h_ago
    if req.temp_24h_ago is not None:
        kwargs["temp_24h_ago"] = req.temp_24h_ago
    return predictor.predict_temperature(
        hour=req.hour,
        month=req.month,
        day_of_year=req.day_of_year,
        current_temp=req.current_temp,
        current_precip=req.current_precip,
        **kwargs
    )


@router.post("/predict/rain")
async def predict_rain(req: WeatherPredictionRequest):
    """Prediksi apakah akan hujan dalam 1 jam ke depan."""
    predictor = get_predictor()
    kwargs = {}
    if req.temp_3h_ago is not None:
        kwargs["temp_3h_ago"] = req.temp_3h_ago
    if req.temp_6h_ago is not None:
        kwargs["temp_6h_ago"] = req.temp_6h_ago
    if req.temp_24h_ago is not None:
        kwargs["temp_24h_ago"] = req.temp_24h_ago
    return predictor.predict_rain(
        hour=req.hour,
        month=req.month,
        day_of_year=req.day_of_year,
        current_temp=req.current_temp,
        current_precip=req.current_precip,
        **kwargs
    )


@router.post("/predict/risk")
async def predict_risk(req: WeatherPredictionRequest):
    """Prediksi tingkat risiko wisata berdasarkan cuaca."""
    predictor = get_predictor()
    kwargs = {}
    if req.temp_3h_ago is not None:
        kwargs["temp_3h_ago"] = req.temp_3h_ago
    if req.temp_6h_ago is not None:
        kwargs["temp_6h_ago"] = req.temp_6h_ago
    if req.temp_24h_ago is not None:
        kwargs["temp_24h_ago"] = req.temp_24h_ago
    return predictor.predict_risk_level(
        hour=req.hour,
        month=req.month,
        day_of_year=req.day_of_year,
        current_temp=req.current_temp,
        current_precip=req.current_precip,
        **kwargs
    )


@router.post("/predict/route-safety")
async def predict_route_safety(req: RouteSafetyRequest):
    """Prediksi keamanan rute wisata tertentu."""
    predictor = get_predictor()
    return predictor.predict_route_safety(
        gradient=req.gradient,
        width=req.width,
        visibility=req.visibility,
        guardrail=req.guardrail,
        surface=req.surface,
        elevation=req.elevation,
        curve_count=req.curve_count,
        lighting=req.lighting,
        vehicle=req.vehicle,
        weather=req.weather
    )


@router.get("/predict/quick")
async def quick_prediction():
    """
    Prediksi cepat berdasarkan jam dan bulan saat ini.
    Endpoint ini dipanggil oleh Dashboard frontend untuk
    menampilkan status risiko real-time.
    """
    from datetime import datetime
    now = datetime.now()
    
    predictor = get_predictor()
    
    # Gunakan suhu estimasi berdasarkan jam (pattern Dieng)
    base_temps = {
        0: 9, 1: 8.5, 2: 8, 3: 7.5, 4: 7.5, 5: 8,
        6: 9, 7: 11, 8: 13, 9: 15, 10: 17, 11: 18,
        12: 19, 13: 19.5, 14: 19, 15: 17, 16: 15, 17: 13,
        18: 12, 19: 11, 20: 10.5, 21: 10, 22: 9.5, 23: 9
    }
    est_temp = base_temps.get(now.hour, 14)
    
    temp_pred = predictor.predict_temperature(
        hour=now.hour, month=now.month, day_of_year=now.timetuple().tm_yday,
        current_temp=est_temp, current_precip=0
    )
    
    rain_pred = predictor.predict_rain(
        hour=now.hour, month=now.month, day_of_year=now.timetuple().tm_yday,
        current_temp=est_temp, current_precip=0
    )
    
    risk_pred = predictor.predict_risk_level(
        hour=now.hour, month=now.month, day_of_year=now.timetuple().tm_yday,
        current_temp=est_temp, current_precip=0
    )
    
    return {
        "timestamp": now.isoformat(),
        "location": "Dieng Plateau (-7.2056, 109.8731)",
        "elevation": "2.060m",
        "temperature": temp_pred,
        "rain": rain_pred,
        "risk": risk_pred
    }
