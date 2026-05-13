"""
DITA ML Prediction API Router
"""

import httpx
from datetime import datetime
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from ..models.predict import get_predictor

router = APIRouter()

DIENG_LAT = -7.2125
DIENG_LON = 109.9100

BASE_TEMPS = {
    0: 9, 1: 8.5, 2: 8, 3: 7.5, 4: 7.5, 5: 8,
    6: 9, 7: 11, 8: 13, 9: 15, 10: 17, 11: 18,
    12: 19, 13: 19.5, 14: 19, 15: 17, 16: 15, 17: 13,
    18: 12, 19: 11, 20: 10.5, 21: 10, 22: 9.5, 23: 9,
}


async def _fetch_live_conditions() -> dict:
    """
    Ambil kondisi cuaca terkini dari Open-Meteo.
    v2: lebih banyak variabel untuk model yang sudah di-upgrade.
    """
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={DIENG_LAT}&longitude={DIENG_LON}"
        f"&current=temperature_2m,precipitation,relative_humidity_2m,"
        f"apparent_temperature,wind_speed_10m,cloud_cover,"
        f"dew_point_2m,visibility,weather_code"
    )
    defaults = {
        "temperature": 14.0, "precipitation": 0.0,
        "humidity": 80.0, "dewpoint": 10.0,
        "windspeed": 10.0, "cloudcover": 50.0,
        "visibility_km": 5.0, "apparent_temp": 11.0,
    }
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            cur = resp.json().get("current", {})
            vis_m = float(cur.get("visibility", 10000) or 10000)
            return {
                "temperature":    float(cur.get("temperature_2m", 14.0)),
                "precipitation":  float(cur.get("precipitation", 0.0) or 0.0),
                "humidity":       float(cur.get("relative_humidity_2m", 80.0)),
                "dewpoint":       float(cur.get("dew_point_2m", 10.0)),
                "windspeed":      float(cur.get("wind_speed_10m", 10.0)),
                "cloudcover":     float(cur.get("cloud_cover", 50.0)),
                "visibility_km":  vis_m / 1000.0,
                "apparent_temp":  float(cur.get("apparent_temperature", 11.0)),
            }
    except Exception:
        return defaults


async def _run_predictions():
    """Jalankan semua prediksi ML dengan data live. Dipakai oleh /quick dan /dashboard."""
    now = datetime.now()
    predictor = get_predictor()

    live = await _fetch_live_conditions()

    # Blend live temp dengan pola jam Dieng
    est_temp    = BASE_TEMPS.get(now.hour, 14)
    current_temp = round((live["temperature"] + est_temp) / 2, 1)

    kwargs = dict(
        hour=now.hour,
        month=now.month,
        day_of_year=now.timetuple().tm_yday,
        current_temp=current_temp,
        current_precip=live["precipitation"],
        # Variabel baru untuk model v2
        humidity=live["humidity"],
        dewpoint=live["dewpoint"],
        windspeed=live["windspeed"],
        cloudcover=live["cloudcover"],
        visibility_km=live["visibility_km"],
        apparent_temp=live["apparent_temp"],
    )

    return (
        now,
        current_temp,
        live,
        predictor,
        predictor.predict_temperature(**kwargs),
        predictor.predict_rain(**kwargs),
        predictor.predict_risk_level(**kwargs),
    )


# ── Request models ────────────────────────────────────────────────────────────

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


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/model-info")
async def get_model_info():
    """Info model ML dan metrik evaluasi."""
    predictor = get_predictor()
    info = predictor.get_model_info()
    info["models_loaded"] = predictor.models_loaded
    return info


@router.get("/predict/quick")
async def quick_prediction():
    """Prediksi lengkap real-time (dipakai Home & Chat)."""
    now, current_temp, live, predictor, temp_pred, rain_pred, risk_pred = await _run_predictions()
    return {
        "timestamp": now.isoformat(),
        "location": "Dieng Plateau (-7.2056, 109.8731)",
        "elevation": "2.060m",
        "input": {
            "current_temperature_c":    current_temp,
            "current_precipitation_mm": live["precipitation"],
            "humidity_pct":             live["humidity"],
            "visibility_km":            live["visibility_km"],
            "source": "Open-Meteo current + pola jam Dieng",
        },
        "temperature": temp_pred,
        "rain":        rain_pred,
        "risk":        risk_pred,
    }


@router.get("/predict/dashboard")
async def dashboard_prediction():
    """Prediksi real-time dengan format ringkas untuk Dashboard."""
    now, current_temp, live, predictor, temp_pred, rain_pred, risk_pred = await _run_predictions()
    return {
        "success": True,
        "timestamp": now.isoformat(),
        "current": {
            "temperature":   current_temp,
            "precipitation": live["precipitation"],
            "humidity":      live["humidity"],
            "visibility_km": live["visibility_km"],
            "windspeed":     live["windspeed"],
            "hour":          now.hour,
            "date":          now.strftime("%Y-%m-%d"),
        },
        "predictions": {
            "temperature": {
                "current":  current_temp,
                "predicted": temp_pred["predicted_temperature"],
                "change":    temp_pred["change"],
                "advisory":  temp_pred["advisory"],
            },
            "rain": {
                "will_rain":   rain_pred["will_rain"],
                "probability": rain_pred["rain_probability"],
                "advisory":    rain_pred["advisory"],
            },
            "risk": {
                "level":      risk_pred["risk_level"],
                "label":      risk_pred["risk_label"],
                "icon":       risk_pred["risk_icon"],
                "color":      risk_pred["risk_color"],
                "advisory":   risk_pred["advisory"],
                "confidence": risk_pred["confidence"],
            },
        },
        "models": {
            "temperature": temp_pred["model"],
            "rain":        rain_pred["model"],
            "risk":        risk_pred["model"],
            "loaded":      predictor.models_loaded,
        },
    }


@router.post("/predict/temperature")
async def predict_temperature(req: WeatherPredictionRequest):
    """Prediksi suhu 1 jam ke depan."""
    predictor = get_predictor()
    kwargs = {k: v for k, v in {
        "temp_3h_ago": req.temp_3h_ago,
        "temp_6h_ago": req.temp_6h_ago,
        "temp_24h_ago": req.temp_24h_ago,
    }.items() if v is not None}
    return predictor.predict_temperature(
        hour=req.hour, month=req.month, day_of_year=req.day_of_year,
        current_temp=req.current_temp, current_precip=req.current_precip, **kwargs
    )


@router.post("/predict/rain")
async def predict_rain(req: WeatherPredictionRequest):
    """Prediksi hujan 1 jam ke depan."""
    predictor = get_predictor()
    kwargs = {k: v for k, v in {
        "temp_3h_ago": req.temp_3h_ago,
        "temp_6h_ago": req.temp_6h_ago,
        "temp_24h_ago": req.temp_24h_ago,
    }.items() if v is not None}
    return predictor.predict_rain(
        hour=req.hour, month=req.month, day_of_year=req.day_of_year,
        current_temp=req.current_temp, current_precip=req.current_precip, **kwargs
    )


@router.post("/predict/risk")
async def predict_risk(req: WeatherPredictionRequest):
    """Prediksi tingkat risiko wisata."""
    predictor = get_predictor()
    kwargs = {k: v for k, v in {
        "temp_3h_ago": req.temp_3h_ago,
        "temp_6h_ago": req.temp_6h_ago,
        "temp_24h_ago": req.temp_24h_ago,
    }.items() if v is not None}
    return predictor.predict_risk_level(
        hour=req.hour, month=req.month, day_of_year=req.day_of_year,
        current_temp=req.current_temp, current_precip=req.current_precip, **kwargs
    )


@router.post("/predict/route-safety")
async def predict_route_safety(req: RouteSafetyRequest):
    """Prediksi keamanan rute wisata."""
    predictor = get_predictor()
    return predictor.predict_route_safety(
        gradient=req.gradient, width=req.width, visibility=req.visibility,
        guardrail=req.guardrail, surface=req.surface, elevation=req.elevation,
        curve_count=req.curve_count, lighting=req.lighting,
        vehicle=req.vehicle, weather=req.weather,
    )
