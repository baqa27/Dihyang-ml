from fastapi import APIRouter
import httpx
import os

router = APIRouter()

# Dieng coordinates
LAT = -7.2125
LON = 109.9100

@router.get("/current")
async def get_current_weather():
    url = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&current_weather=true&hourly=temperature_2m,relativehumidity_2m,windspeed_10m,visibility"
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()
            cw = data.get("current_weather", {})
            return {
                "temperature": cw.get("temperature", 14),
                "wind_speed": cw.get("windspeed", 12),
                "condition": "Berkabut" if cw.get("weathercode", 0) > 45 else "Cerah/Berawan",
                "humidity": 89, # Mocking some values for prototype
                "visibility": 3.2,
                "feels_like": cw.get("temperature", 14) - 3,
                "high": 19,
                "low": 7,
                "pressure": 1013,
            }
        except Exception as e:
            return {
                "temperature": 14,
                "feels_like": 11,
                "humidity": 89,
                "wind_speed": 12,
                "visibility": 3.2,
                "condition": "Berkabut",
                "pressure": 1013,
                "high": 19,
                "low": 7,
            }

@router.get("/forecast")
async def get_forecast():
    # Mocking for prototype
    return {"message": "Forecast endpoint coming soon"}

HISTORICAL_DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "dieng_historical_2023.json")

@router.get("/historical")
async def get_historical():
    import json
    if os.path.exists(HISTORICAL_DATA_FILE):
        with open(HISTORICAL_DATA_FILE, "r") as f:
            data = json.load(f)
            # Just returning summary to avoid massive payload
            return {
                "latitude": data.get("latitude"),
                "longitude": data.get("longitude"),
                "timezone": data.get("timezone"),
                "hourly_data_points": len(data.get("hourly", {}).get("time", [])),
                "message": "Historical data processed for Predictive Analytics prototype"
            }
    return {"message": "Historical data not found. Run scraper first."}
