import os
import json
import re
import httpx
import logging
import google.genai as genai
from google.genai import types as genai_types
from datetime import datetime
from dotenv import load_dotenv
from fastapi import APIRouter, Query, Request
from pydantic import BaseModel, Field, field_validator
from slowapi import Limiter
from slowapi.util import get_remote_address

from ..config import settings
from ..models.predict import get_predictor
from ..models.itinerary_engine import get_itinerary_engine

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)
logger = logging.getLogger(__name__)
load_dotenv()

DIENG_LAT = -7.2125
DIENG_LON = 109.9100


async def _live_temp_precip_mm() -> tuple[float, float]:
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={DIENG_LAT}&longitude={DIENG_LON}"
        f"&current=temperature_2m,precipitation"
    )
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            cur = resp.json().get("current", {})
            return float(cur.get("temperature_2m", 14.0)), float(cur.get("precipitation", 0.0) or 0.0)
    except Exception:
        return 14.0, 0.0


def _ml_prompt_block(p, hour: int, month: int, doy: int, blend_temp: float, live_precip: float) -> str:
    """Ringkasan prediksi model DITA (suhu/presipitasi selaras endpoint /ml/predict/quick)."""
    if not p.models_loaded:
        # Gunakan rule-based prediction sebagai fallback tanpa warning
        return (
            f"\n[Konteks cuaca saat ini — gunakan untuk weatherNote & gear]\n"
            f"- Suhu saat ini: ~{blend_temp}°C, presipitasi: {live_precip} mm\n"
            f"- Jam: {hour}:00, kondisi Dieng Plateau\n"
        )
    risk = p.predict_risk_level(hour, month, doy, blend_temp, live_precip)
    rain = p.predict_rain(hour, month, doy, blend_temp, live_precip)
    return (
        f"\n[Konteks model ML DITA — pakai untuk weatherNote & gear]\n"
        f"- Risiko wisata (cuaca): {risk['risk_label']}. {risk['advisory']}\n"
        f"- Probabilitas hujan 1 jam ke depan: {rain['rain_probability']}%.\n"
        f"- Input model: suhu gabungan ~{blend_temp}°C, presipitasi {live_precip} mm.\n"
    )

class ItineraryRequest(BaseModel):
    destination: str = Field(default="Dieng Plateau", min_length=1, max_length=100)
    duration: int = Field(default=3, ge=1, le=30)
    budget: int = Field(default=750_000, ge=0, le=100_000_000)
    guests: int = Field(default=2, ge=1, le=50)
    interests: list[str] = Field(default_factory=list, max_length=20)
    travelStyle: str = Field(default="couple", min_length=1, max_length=30)
    vehicle: str = Field(default="Mobil", min_length=1, max_length=30)

    @field_validator("duration", mode="before")
    @classmethod
    def parse_duration(cls, value):
        if isinstance(value, int):
            if value < 1 or value > 30:
                raise ValueError("Durasi harus antara 1-30 hari")
            return value
        match = re.search(r"\d+", str(value))
        if not match:
            raise ValueError("Durasi harus berisi jumlah hari")
        days = int(match.group())
        if days < 1 or days > 30:
            raise ValueError("Durasi harus antara 1-30 hari")
        return days

    @field_validator("budget", mode="before")
    @classmethod
    def parse_budget(cls, value):
        if isinstance(value, (int, float)):
            budget_val = int(value)
            if budget_val < 0:
                raise ValueError("Budget tidak boleh negatif")
            if budget_val > 100_000_000:
                raise ValueError("Budget terlalu besar (max 100 juta)")
            return budget_val

        normalized = str(value).lower().replace(" ", "")
        if normalized.startswith("<") and "500" in normalized:
            return 300_000
        if "500" in normalized and ("1jt" in normalized or "1juta" in normalized):
            return 750_000
        if "1" in normalized and "2" in normalized and ("jt" in normalized or "juta" in normalized):
            return 1_500_000
        if normalized.startswith(">") and "2" in normalized:
            return 2_500_000

        digits = re.sub(r"[^\d]", "", normalized)
        if not digits:
            raise ValueError("Budget harus berupa angka rupiah")
        budget_val = int(digits)
        if budget_val > 100_000_000:
            raise ValueError("Budget terlalu besar (max 100 juta)")
        return budget_val
    
    @field_validator("guests")
    @classmethod
    def validate_guests(cls, v: int) -> int:
        if v < 1:
            raise ValueError("Jumlah tamu minimal 1 orang")
        if v > 50:
            raise ValueError("Jumlah tamu maksimal 50 orang")
        return v
    
    @field_validator("interests")
    @classmethod
    def validate_interests(cls, v: list) -> list:
        if len(v) > 20:
            raise ValueError("Terlalu banyak minat dipilih (maksimal 20)")
        
        # Sanitize each interest
        sanitized = []
        for interest in v:
            # Remove emojis and special characters, keep only alphanumeric and spaces
            clean = ''.join(c for c in interest if c.isalnum() or c.isspace()).strip()
            if clean:
                sanitized.append(interest)  # Keep original with emoji
        
        return sanitized
    
    @field_validator("destination")
    @classmethod
    def validate_destination(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Destinasi tidak boleh kosong")
        if len(v) > 100:
            raise ValueError("Nama destinasi terlalu panjang")
        return v

def _get_client():
    """Get Gemini client with validation"""
    api_key = settings.GEMINI_API_KEY
    invalid_keys = ["MASUKKAN_API_KEY_ANDA_DI_SINI", "masukkan_api_key_anda_disini", ""]
    
    if api_key in invalid_keys or len(api_key) < 20:
        logger.warning("⚠️ Gemini API key tidak valid untuk itinerary generation")
        return None
    
    try:
        return genai.Client(api_key=api_key)
    except Exception as e:
        logger.error(f"❌ Error creating Gemini client: {e}")
        return None

FALLBACK_DAY_PLANS = [
    [
        ("07:30", "Sarapan khas Dieng", "Pusat Dieng", "1 jam", "food", "Coba mie ongklok atau tempe kemul."),
        ("09:00", "Kompleks Candi Arjuna", "Dieng Kulon", "2 jam", "attraction", "Datang pagi agar area belum terlalu ramai."),
        ("11:30", "Museum Kailasa", "Dieng Kulon", "1 jam", "attraction", "Pilihan indoor saat kabut atau hujan."),
        ("14:00", "Kawah Sikidang", "Dieng Wetan", "1.5 jam", "attraction", "Gunakan masker dan tetap di jalur aman."),
        ("17:30", "Check-in dan istirahat", "Dieng Plateau", "-", "hotel", "Siapkan pakaian hangat untuk malam hari."),
    ],
    [
        ("03:30", "Perjalanan menuju Bukit Sikunir", "Desa Sembungan", "45 menit", "transport", "Bawa senter dan jaket tebal."),
        ("04:30", "Sunrise Bukit Sikunir", "Bukit Sikunir", "2 jam", "attraction", "Aktivitas bergantung pada kabut dan hujan."),
        ("07:30", "Sarapan dekat Telaga Cebong", "Desa Sembungan", "1 jam", "food", ""),
        ("10:00", "Telaga Warna dan Telaga Pengilon", "Dieng Wetan", "2 jam", "attraction", "Pilih jalur pandang sesuai kondisi cuaca."),
        ("15:00", "Batu Ratapan Angin", "Dieng Plateau", "1.5 jam", "attraction", "Waktu yang baik untuk fotografi."),
    ],
    [
        ("08:00", "Sumur Jalatunda", "Pekasiran", "1 jam", "attraction", "Gunakan alas kaki yang tidak licin."),
        ("10:00", "Kawah Sileri", "Kepakisan", "1.5 jam", "attraction", "Patuhi radius aman kawah."),
        ("12:00", "Makan siang kuliner lokal", "Dieng Plateau", "1 jam", "food", ""),
        ("14:00", "Dieng Plateau Theater", "Dieng Plateau", "1 jam", "attraction", "Alternatif aman saat cuaca memburuk."),
        ("16:00", "Berburu oleh-oleh carica", "Pusat Dieng", "1 jam", "food", ""),
    ],
    [
        ("05:30", "Persiapan trekking Gunung Prau", "Basecamp Patak Banteng", "1 jam", "transport", "Cek status jalur dan cuaca sebelum naik."),
        ("06:30", "Trekking Gunung Prau", "Gunung Prau", "5 jam", "attraction", "Gunakan pemandu bila belum mengenal jalur."),
        ("12:30", "Makan siang dan pemulihan", "Patak Banteng", "1.5 jam", "food", ""),
        ("15:00", "Waktu bebas di homestay", "Dieng Plateau", "2 jam", "hotel", "Hindari jadwal padat setelah trekking."),
    ],
    [
        ("08:00", "Perjalanan ke pusat Wonosobo", "Dieng - Wonosobo", "1 jam", "transport", ""),
        ("09:30", "Jelajah kota dan pasar lokal", "Wonosobo", "2 jam", "attraction", "Cari produk UMKM dan pangan lokal."),
        ("12:00", "Makan siang mie ongklok", "Wonosobo", "1 jam", "food", ""),
        ("14:00", "Pemandian air hangat Kalianget", "Wonosobo", "2 jam", "attraction", "Cocok untuk pemulihan setelah trekking."),
    ],
    [
        ("08:00", "Agrowisata Tambi", "Kejajar", "2.5 jam", "attraction", "Konfirmasi jadwal tur kebun terlebih dahulu."),
        ("11:30", "Makan siang di Kejajar", "Kejajar", "1 jam", "food", ""),
        ("13:30", "Jelajah desa dan fotografi", "Kejajar", "2 jam", "attraction", "Hormati aktivitas warga setempat."),
        ("16:00", "Kembali ke penginapan", "Dieng Plateau", "1 jam", "transport", ""),
    ],
    [
        ("07:30", "Perjalanan menuju Telaga Menjer", "Garung", "1.5 jam", "transport", ""),
        ("09:00", "Telaga Menjer", "Garung", "2 jam", "attraction", "Aktivitas perahu mengikuti kondisi angin."),
        ("12:00", "Makan siang", "Garung", "1 jam", "food", ""),
        ("14:00", "Kebun teh dan panorama pegunungan", "Wonosobo", "2 jam", "attraction", ""),
    ],
    [
        ("07:00", "Curug Sikarim", "Sembungan", "2.5 jam", "attraction", "Hindari jalur saat hujan deras."),
        ("10:30", "Desa Sembungan", "Sembungan", "1.5 jam", "attraction", "Wisata berbasis desa dan fotografi."),
        ("12:30", "Makan siang lokal", "Sembungan", "1 jam", "food", ""),
        ("14:30", "Waktu santai di Telaga Cebong", "Sembungan", "1.5 jam", "attraction", ""),
    ],
    [
        ("08:00", "Wisata budaya Dieng", "Dieng Kulon", "2 jam", "attraction", "Pelajari sejarah dan tradisi masyarakat Dieng."),
        ("10:30", "Belanja produk UMKM", "Pusat Dieng", "1.5 jam", "attraction", ""),
        ("12:30", "Tur kuliner Dieng", "Dieng Plateau", "2 jam", "food", "Sesuaikan pilihan dengan anggaran harian."),
        ("15:30", "Sesi fotografi sore", "Dieng Plateau", "1.5 jam", "attraction", ""),
    ],
    [
        ("08:00", "Sarapan dan check-out", "Dieng Plateau", "1.5 jam", "hotel", ""),
        ("10:00", "Kunjungan ulang destinasi favorit", "Dieng Plateau", "2 jam", "attraction", "Gunakan waktu cadangan untuk lokasi yang sempat tertunda."),
        ("12:30", "Makan siang terakhir", "Dieng Plateau", "1 jam", "food", ""),
        ("14:00", "Perjalanan pulang", "Dieng - Wonosobo", "1.5 jam", "transport", "Periksa kondisi kendaraan sebelum turun."),
    ],
]


def _weather_context(blend_temp: float, live_precip: float) -> dict:
    if live_precip >= 2:
        return {
            "icon": "🌧️",
            "condition": "Hujan",
            "temp": f"{round(blend_temp)}°C",
            "rain": 80,
            "warning": "Hujan terpantau di Dieng. Utamakan aktivitas indoor dan hindari jalur licin.",
        }
    if blend_temp <= 8:
        return {
            "icon": "🥶",
            "condition": "Sangat dingin",
            "temp": f"{round(blend_temp)}°C",
            "rain": 20,
            "warning": "Suhu sangat dingin. Siapkan pakaian berlapis dan perlengkapan hangat.",
        }
    return {
        "icon": "🌫️",
        "condition": "Sejuk, berpotensi kabut",
        "temp": f"{round(blend_temp)}°C",
        "rain": 25,
        "warning": "",
    }


def _build_fallback_itinerary(
    req: ItineraryRequest,
    blend_temp: float = 14.0,
    live_precip: float = 0.0,
) -> dict:
    weather = _weather_context(blend_temp, live_precip)
    days = []

    for index in range(req.duration):
        plan = FALLBACK_DAY_PLANS[index % len(FALLBACK_DAY_PLANS)]
        activities = [
            {
                "time": time,
                "name": name,
                "location": location,
                "duration": activity_duration,
                "type": activity_type,
                "note": note or None,
                "weatherOk": not (weather["rain"] >= 50 and activity_type == "attraction"),
            }
            for time, name, location, activity_duration, activity_type, note in plan
        ]
        if index == 0 and req.destination.lower() != "dieng plateau":
            for activity in activities:
                if activity["type"] == "attraction":
                    activity["name"] = f"Eksplorasi {req.destination}"
                    activity["location"] = req.destination
                    activity["note"] = "Tujuan utama disesuaikan dengan pilihan Anda."
                    break
        days.append(
            {
                "day": index + 1,
                "date": f"Hari ke-{index + 1}",
                "weather": {
                    "icon": weather["icon"],
                    "condition": weather["condition"],
                    "temp": weather["temp"],
                    "rain": weather["rain"],
                },
                "warning": weather["warning"] or None,
                "activities": activities,
            }
        )

    return {
        "days": days,
        "meta": {
            "source": "fallback",
            "requestedDays": req.duration,
            "message": "Rencana lokal digunakan karena layanan AI tidak tersedia atau respons AI tidak valid.",
        },
    }


def _parse_json_response(text: str) -> dict:
    cleaned = text.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start == -1 or end <= start:
            raise
        return json.loads(cleaned[start:end + 1])


def _normalize_activity(item: dict, fallback: dict) -> dict:
    allowed_types = {"attraction", "food", "transport", "hotel"}
    raw_type = str(item.get("type", fallback["type"])).lower()
    type_aliases = {
        "stay": "hotel",
        "accommodation": "hotel",
        "transportation": "transport",
    }
    activity_type = type_aliases.get(raw_type, raw_type)
    if activity_type not in allowed_types:
        activity_type = fallback["type"]

    return {
        "time": str(item.get("time") or fallback["time"]),
        "name": str(item.get("name") or item.get("title") or fallback["name"]),
        "location": str(item.get("location") or fallback["location"]),
        "duration": str(item.get("duration") or fallback["duration"]),
        "type": activity_type,
        "note": item.get("note") or item.get("desc") or fallback.get("note"),
        "weatherOk": bool(item.get("weatherOk", fallback.get("weatherOk", True))),
    }


def _normalize_generated_itinerary(data: dict, fallback: dict, source: str) -> dict:
    generated_days = data.get("days") if isinstance(data, dict) else None
    if not isinstance(generated_days, list):
        raise ValueError("Respons AI tidak memiliki daftar days")

    normalized_days = []
    for index, fallback_day in enumerate(fallback["days"]):
        generated_day = generated_days[index] if index < len(generated_days) else {}
        if not isinstance(generated_day, dict):
            generated_day = {}

        raw_activities = generated_day.get("activities") or generated_day.get("items") or []
        fallback_activities = fallback_day["activities"]
        normalized_activities = []
        if isinstance(raw_activities, list):
            for activity_index, item in enumerate(raw_activities):
                if not isinstance(item, dict):
                    continue
                activity_fallback = fallback_activities[
                    min(activity_index, len(fallback_activities) - 1)
                ]
                normalized_activities.append(_normalize_activity(item, activity_fallback))
        if not normalized_activities:
            normalized_activities = fallback_activities

        raw_weather = generated_day.get("weather")
        weather = fallback_day["weather"].copy()
        if isinstance(raw_weather, dict):
            weather.update(
                {
                    key: raw_weather[key]
                    for key in ("icon", "condition", "temp", "rain")
                    if raw_weather.get(key) is not None
                }
            )

        normalized_days.append(
            {
                "day": index + 1,
                "date": str(generated_day.get("date") or f"Hari ke-{index + 1}"),
                "weather": weather,
                "warning": generated_day.get("warning") or fallback_day.get("warning"),
                "activities": normalized_activities,
            }
        )

    return {
        "days": normalized_days,
        "meta": {
            "source": source,
            "requestedDays": len(fallback["days"]),
            "message": "",
        },
    }


@router.post("/generate-smart")
async def generate_smart_itinerary(req: ItineraryRequest):
    """
    Generate itinerary menggunakan Smart Template Engine (ML-based, no API).
    Lebih cepat, gratis, dan tidak tergantung API eksternal.
    """
    now = datetime.now()
    live_temp, live_precip = await _live_temp_precip_mm()
    
    # Determine weather condition
    if live_precip > 2:
        weather_cond = "hujan"
    elif live_temp < 10:
        weather_cond = "kabut"
    else:
        weather_cond = "cerah"
    
    engine = get_itinerary_engine()
    result = engine.generate_smart_itinerary(
        duration_days=req.duration,
        budget_per_day=req.budget,
        interests=req.interests or ["alam", "budaya"],
        travel_style=req.travelStyle,
        vehicle=req.vehicle.lower(),
        weather_condition=weather_cond,
        current_month=now.month,
    )
    
    return result


@router.get("/activities")
async def get_all_activities():
    """List semua aktivitas yang tersedia di database."""
    engine = get_itinerary_engine()
    return {
        "total": len(engine.activities_db),
        "activities": [
            {
                "id": act["id"],
                "name": act["name"],
                "location": act["location"],
                "type": act["type"],
                "interests": act["interests"],
                "cost": act["cost_per_person"],
                "duration": act["duration_hours"],
                "priority": act["priority_score"],
            }
            for act in engine.activities_db
        ]
    }

@router.post("/generate")
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
async def generate_itinerary(
    req: ItineraryRequest,
    request: Request,
    use_ai: bool = Query(default=True, description="Use AI (Gemini/NVIDIA) or Smart Engine")
):
    """
    Generate itinerary dengan strategi PRIORITAS AI:
    STRATEGI BARU (API First):
    1. Gemini AI (primary) - Kreatif, natural, data terkini
    2. NVIDIA API (fallback 1) - Backup saat Gemini limit/error
    3. Smart Engine (fallback 2) - Local, 35+ aktivitas, instant
    
    use_ai=False → Langsung pakai Smart Engine (skip API)
    """
    logger.info(f"📅 Itinerary request from {request.client.host if request.client else 'unknown'}: {req.destination} for {req.duration} days")
    
    try:
        live_temp, live_precip = await _live_temp_precip_mm()
        p = get_predictor()
        now = datetime.now()
        h, mo, doy = now.hour, now.month, now.timetuple().tm_yday
        base_temps = {
            0: 9, 1: 8.5, 2: 8, 3: 7.5, 4: 7.5, 5: 8,
            6: 9, 7: 11, 8: 13, 9: 15, 10: 17, 11: 18,
            12: 19, 13: 19.5, 14: 19, 15: 17, 16: 15, 17: 13,
            18: 12, 19: 11, 20: 10.5, 21: 10, 22: 9.5, 23: 9,
        }
        est = base_temps.get(h, 14)
        blend_temp = round((live_temp + est) / 2, 1)
        
        # Determine weather condition for smart engine
        if live_precip > 2:
            weather_cond = "hujan"
        elif blend_temp < 10:
            weather_cond = "kabut"
        else:
            weather_cond = "cerah"
        
        # Normalize vehicle untuk engine (siapkan sebagai fallback)
        vehicle_normalized = req.vehicle.lower()
        if "mobil" in vehicle_normalized or "car" in vehicle_normalized:
            vehicle_normalized = "car"
        elif "motor" in vehicle_normalized or "motorcycle" in vehicle_normalized:
            vehicle_normalized = "motorcycle"
        elif "bus" in vehicle_normalized:
            vehicle_normalized = "bus"
        else:
            vehicle_normalized = "car"
        
        # Jika user explicitly tidak mau AI, langsung pakai Smart Engine
        if not use_ai:
            engine = get_itinerary_engine()
            smart_template = engine.generate_smart_itinerary(
                duration_days=req.duration,
                budget_per_day=req.budget,
                interests=req.interests or ["alam", "budaya"],
                travel_style=req.travelStyle,
                vehicle=vehicle_normalized,
                weather_condition=weather_cond,
                current_month=mo,
            )
            smart_template["meta"]["message"] = "Itinerary berhasil dibuat oleh DITA berdasarkan database wisata Dieng."
            smart_template["meta"]["source"] = "dita_engine"
            return smart_template
        
        # STRATEGI PRIORITAS: API FIRST (Gemini → NVIDIA)
        ml_block = _ml_prompt_block(p, h, mo, doy, blend_temp, live_precip)
        client = _get_client()

        prompt = f"""
        Buatkan itinerary wisata cerdas (Smart Itinerary) ke Dieng.
        Tujuan Utama: {req.destination}
        Durasi: tepat {req.duration} hari
        Budget per hari: Rp {req.budget:,}
        Jumlah Tamu: {req.guests} orang
        Minat & Aktivitas: {', '.join(req.interests) if req.interests else 'wisata umum'}
        Gaya perjalanan: {req.travelStyle}
        Kendaraan: {req.vehicle}
        
        {ml_block}

        Format output WAJIB berupa JSON murni dengan struktur berikut:
        {{
          "days": [
            {{
              "day": 1,
              "date": "Hari ke-1",
              "weather": {{ "icon": "⛅", "condition": "Berawan", "temp": "15°C", "rain": 20 }},
              "warning": "Opsional: peringatan cuaca buruk jika hujan tinggi",
              "activities": [
                {{
                  "time": "08:00",
                  "name": "Nama Tempat / Kegiatan",
                  "location": "Lokasi spesifik",
                  "duration": "1.5 jam",
                  "type": "attraction",
                  "note": "Tips berguna singkat (opsional)",
                  "weatherOk": true
                }}
              ]
            }}
          ]
        }}
        Nilai type hanya boleh attraction, food, transport, atau hotel.
        Berikan HANYA JSON tanpa markdown atau teks lain.
        Array days WAJIB berisi tepat {req.duration} objek, dari day 1 sampai day {req.duration}.
        Setiap hari harus memiliki 3 sampai 6 aktivitas yang realistis dan tidak tumpang tindih.
        """
        
        # PRIORITAS 1: GEMINI AI (Primary)
        if client:
            try:
                print("🤖 Mencoba generate itinerary dengan Gemini AI...")
                import asyncio
                response = await asyncio.wait_for(
                    client.aio.models.generate_content(
                        model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
                        contents=prompt,
                        config=genai_types.GenerateContentConfig(
                            response_mime_type="application/json",
                            temperature=0.5,
                        ),
                    ),
                    timeout=float(os.getenv("GEMINI_TIMEOUT_SECONDS", "20"))
                )
                data = _parse_json_response(response.text)
                print("✅ Gemini AI berhasil generate itinerary!")
                
                # Buat fallback untuk normalisasi (bukan return langsung)
                engine = get_itinerary_engine()
                fallback_for_normalize = engine.generate_smart_itinerary(
                    duration_days=req.duration,
                    budget_per_day=req.budget,
                    interests=req.interests or ["alam", "budaya"],
                    travel_style=req.travelStyle,
                    vehicle=vehicle_normalized,
                    weather_condition=weather_cond,
                    current_month=mo,
                )
                return _normalize_generated_itinerary(data, fallback_for_normalize, "gemini")
            except Exception as gemini_error:
                print(f"⚠️ Gemini gagal: {str(gemini_error)[:50]}. Coba NVIDIA...")
                # Lanjut ke NVIDIA fallback
        else:
            print("⚠️ Gemini client tidak tersedia. Coba NVIDIA...")
        
        # PRIORITAS 2: NVIDIA API (Fallback dari Gemini)
        nvidia_key = os.getenv("NVIDIA_API_KEY")
        if nvidia_key and nvidia_key != "MASUKKAN_API_KEY_NVIDIA_ANDA_DI_SINI":
            try:
                from openai import AsyncOpenAI
                print("🤖 Mencoba generate itinerary dengan NVIDIA AI...")
                nvidia_client = AsyncOpenAI(
                    api_key=nvidia_key,
                    base_url="https://integrate.api.nvidia.com/v1"
                )
                
                import asyncio
                response = await asyncio.wait_for(
                    nvidia_client.chat.completions.create(
                        model=os.getenv("NVIDIA_MODEL", "meta/llama-3.1-70b-instruct"),
                        messages=[
                            {"role": "system", "content": "You are a helpful travel assistant. You must reply ONLY with valid JSON. Do not include markdown blocks or any other text."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.5
                    ),
                    timeout=float(os.getenv("NVIDIA_TIMEOUT_SECONDS", "15"))
                )
                
                text = response.choices[0].message.content.strip()
                data = _parse_json_response(text)
                print("✅ NVIDIA AI berhasil generate itinerary!")
                
                # Buat fallback untuk normalisasi
                engine = get_itinerary_engine()
                fallback_for_normalize = engine.generate_smart_itinerary(
                    duration_days=req.duration,
                    budget_per_day=req.budget,
                    interests=req.interests or ["alam", "budaya"],
                    travel_style=req.travelStyle,
                    vehicle=vehicle_normalized,
                    weather_condition=weather_cond,
                    current_month=mo,
                )
                return _normalize_generated_itinerary(data, fallback_for_normalize, "nvidia")
            except Exception as nvidia_error:
                print(f"⚠️ NVIDIA gagal: {str(nvidia_error)[:50]}. Pakai Smart Engine...")
        
    except Exception as e:
        print(f"❌ Error umum: {str(e)[:100]}")
    
    # PRIORITAS 3: SMART ENGINE (Ultimate Fallback - Always Works!)
    print("🔧 Menggunakan DITA Smart Engine (local, 35+ aktivitas)...")
    engine = get_itinerary_engine()
    smart_result = engine.generate_smart_itinerary(
        duration_days=req.duration,
        budget_per_day=req.budget,
        interests=req.interests or ["alam", "budaya"],
        travel_style=req.travelStyle,
        vehicle=vehicle_normalized,
        weather_condition=weather_cond,
        current_month=mo,
    )
    smart_result["meta"]["message"] = "Itinerary berhasil dibuat oleh DITA berdasarkan database wisata Dieng terkini."
    smart_result["meta"]["source"] = "dita_engine"
    print("✅ Smart Engine berhasil generate itinerary!")
    return smart_result
