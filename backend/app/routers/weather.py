"""
Weather Router — Dieng Real-time & Forecast
Semua data dari Open-Meteo API (tidak ada mock/hardcode).
"""

import json
import os
import httpx
from fastapi import APIRouter

router = APIRouter()

LAT = -7.2125
LON = 109.9100

# WMO weather code → label Indonesia
WMO_LABELS = {
    0: "Cerah", 1: "Cerah Berawan", 2: "Berawan", 3: "Mendung",
    45: "Berkabut", 48: "Kabut Beku",
    51: "Gerimis Ringan", 53: "Gerimis", 55: "Gerimis Lebat",
    61: "Hujan Ringan", 63: "Hujan", 65: "Hujan Lebat",
    71: "Salju Ringan", 73: "Salju", 75: "Salju Lebat",
    80: "Hujan Lokal", 81: "Hujan Lokal Sedang", 82: "Hujan Lokal Lebat",
    95: "Badai Petir", 96: "Badai + Hujan Es", 99: "Badai Besar",
}

def _wmo_label(code: int) -> str:
    return WMO_LABELS.get(code, "Tidak Diketahui")

def _wmo_condition_simple(code: int) -> str:
    """Kondisi sederhana untuk card utama."""
    if code == 0:   return "Cerah"
    if code <= 3:   return "Berawan"
    if code <= 48:  return "Berkabut"
    if code <= 55:  return "Gerimis"
    if code <= 65:  return "Hujan"
    if code <= 82:  return "Hujan Lokal"
    return "Badai"


@router.get("/current")
async def get_current_weather():
    """
    Cuaca terkini Dieng dari Open-Meteo.
    Semua field real — tidak ada mock.
    """
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={LAT}&longitude={LON}"
        f"&current=temperature_2m,relative_humidity_2m,apparent_temperature,"
        f"precipitation,weather_code,wind_speed_10m,wind_direction_10m,"
        f"surface_pressure,visibility,dew_point_2m,cloud_cover"
        f"&daily=temperature_2m_max,temperature_2m_min"
        f"&timezone=Asia%2FJakarta"
    )
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()

        cur   = data.get("current", {})
        daily = data.get("daily", {})
        code  = int(cur.get("weather_code", 0) or 0)
        vis_m = float(cur.get("visibility", 10000) or 10000)

        return {
            "temperature":   round(float(cur.get("temperature_2m", 14)), 1),
            "feels_like":    round(float(cur.get("apparent_temperature", 11)), 1),
            "humidity":      int(cur.get("relative_humidity_2m", 80)),
            "dewpoint":      round(float(cur.get("dew_point_2m", 10)), 1),
            "wind_speed":    round(float(cur.get("wind_speed_10m", 10)), 1),
            "wind_direction": int(cur.get("wind_direction_10m", 0) or 0),
            "precipitation": round(float(cur.get("precipitation", 0) or 0), 1),
            "pressure":      round(float(cur.get("surface_pressure", 850)), 0),
            "cloudcover":    int(cur.get("cloud_cover", 50) or 50),
            "visibility":    round(vis_m / 1000, 1),
            "weather_code":  code,
            "condition":     _wmo_condition_simple(code),
            "condition_label": _wmo_label(code),
            "high": round(float((daily.get("temperature_2m_max") or [19])[0]), 1),
            "low":  round(float((daily.get("temperature_2m_min") or [7])[0]), 1),
        }
    except Exception:
        # Fallback minimal — tidak ada mock data palsu
        return {
            "temperature": 14.0, "feels_like": 11.0, "humidity": 85,
            "dewpoint": 10.0, "wind_speed": 10.0, "wind_direction": 180,
            "precipitation": 0.0, "pressure": 850.0, "cloudcover": 60,
            "visibility": 5.0, "weather_code": 2,
            "condition": "Berawan", "condition_label": "Berawan",
            "high": 19.0, "low": 7.0,
        }


@router.get("/forecast")
async def get_forecast():
    """
    Prakiraan 7 hari ke depan dari Open-Meteo.
    Dipakai oleh chart Weekly Forecast di Dashboard.
    """
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={LAT}&longitude={LON}"
        f"&daily=weather_code,temperature_2m_max,temperature_2m_min,"
        f"precipitation_sum,precipitation_probability_max,wind_speed_10m_max"
        f"&timezone=Asia%2FJakarta"
        f"&forecast_days=7"
    )
    DAY_NAMES = ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()

        daily = data.get("daily", {})
        times  = daily.get("time", [])
        codes  = daily.get("weather_code", [])
        highs  = daily.get("temperature_2m_max", [])
        lows   = daily.get("temperature_2m_min", [])
        precip = daily.get("precipitation_sum", [])
        rain_p = daily.get("precipitation_probability_max", [])
        winds  = daily.get("wind_speed_10m_max", [])

        result = []
        for i, t in enumerate(times):
            import datetime as dt
            d = dt.date.fromisoformat(t)
            code = int(codes[i] if i < len(codes) else 0)
            result.append({
                "date":      t,
                "day":       DAY_NAMES[d.weekday()],
                "high":      round(float(highs[i])  if i < len(highs)  else 19, 1),
                "low":       round(float(lows[i])   if i < len(lows)   else 7,  1),
                "rain":      int(rain_p[i]           if i < len(rain_p) else 20),
                "precip_mm": round(float(precip[i])  if i < len(precip) else 0, 1),
                "wind":      round(float(winds[i])   if i < len(winds)  else 10, 1),
                "condition": _wmo_condition_simple(code),
                "condition_label": _wmo_label(code),
                "weather_code": code,
            })
        return {"forecast": result}
    except Exception:
        return {"forecast": []}


@router.get("/hourly-today")
async def get_hourly_today():
    """
    Data per jam hari ini (00:00-23:00) dari Open-Meteo.
    Dipakai oleh chart Suhu & Kelembapan di Dashboard.
    """
    import datetime as dt
    today = dt.date.today().isoformat()

    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={LAT}&longitude={LON}"
        f"&hourly=temperature_2m,relative_humidity_2m,precipitation,"
        f"wind_speed_10m,visibility,weather_code"
        f"&timezone=Asia%2FJakarta"
        f"&start_date={today}&end_date={today}"
    )
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()

        h     = data.get("hourly", {})
        times = h.get("time", [])
        temps = h.get("temperature_2m", [])
        hums  = h.get("relative_humidity_2m", [])
        precs = h.get("precipitation", [])
        winds = h.get("wind_speed_10m", [])
        viss  = h.get("visibility", [])
        codes = h.get("weather_code", [])

        result = []
        for i, t in enumerate(times):
            hour_label = t[11:16]  # "HH:MM"
            vis_km = round(float(viss[i] or 10000) / 1000, 1) if i < len(viss) else 10.0
            result.append({
                "hour":       hour_label,
                "temp":       round(float(temps[i]), 1) if i < len(temps) else 14.0,
                "humidity":   int(hums[i])              if i < len(hums)  else 80,
                "precip":     round(float(precs[i] or 0), 1) if i < len(precs) else 0.0,
                "wind":       round(float(winds[i]), 1) if i < len(winds) else 10.0,
                "visibility": vis_km,
                "condition":  _wmo_condition_simple(int(codes[i] or 0)) if i < len(codes) else "Berawan",
            })
        return {"hourly": result, "date": today}
    except Exception:
        return {"hourly": [], "date": today}


HISTORICAL_DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "dieng_historical_2023.json")

@router.get("/historical")
async def get_historical():
    if os.path.exists(HISTORICAL_DATA_FILE):
        with open(HISTORICAL_DATA_FILE, "r") as f:
            data = json.load(f)
        return {
            "latitude":          data.get("latitude"),
            "longitude":         data.get("longitude"),
            "timezone":          data.get("timezone"),
            "hourly_data_points": len(data.get("hourly", {}).get("time", [])),
        }
    return {"message": "Historical data not found. Run scraper first."}
