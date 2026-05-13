import os
import json
import httpx
import google.genai as genai
from google.genai import types as genai_types
from datetime import datetime
from fastapi import APIRouter
from pydantic import BaseModel

from ..models.predict import get_predictor

router = APIRouter()

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
        return ""
    risk = p.predict_risk_level(hour, month, doy, blend_temp, live_precip)
    rain = p.predict_rain(hour, month, doy, blend_temp, live_precip)
    return (
        f"\n[Konteks model ML DITA — pakai untuk weatherNote & gear]\n"
        f"- Risiko wisata (cuaca): {risk['risk_label']}. {risk['advisory']}\n"
        f"- Probabilitas hujan 1 jam ke depan: {rain['rain_probability']}%.\n"
        f"- Input model: suhu gabungan ~{blend_temp}°C, presipitasi {live_precip} mm.\n"
    )

class ItineraryRequest(BaseModel):
    duration: str
    travelStyle: str
    budget: int
    vehicle: str

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
_genai_client = None

def _get_client():
    global _genai_client
    if _genai_client is None and GEMINI_API_KEY and GEMINI_API_KEY != "MASUKKAN_API_KEY_ANDA_DI_SINI":
        _genai_client = genai.Client(api_key=GEMINI_API_KEY)
    return _genai_client

def get_mock_itinerary(duration, travelStyle, budget, vehicle, ml_note: str = ""):
    note = ml_note.strip() or "⚠️ Kabut tebal diprediksi sore hari. Hindari jalur curam."
    style_label = {"solo": "Solo", "couple": "Pasangan", "family": "Keluarga", "group": "Rombongan"}.get(travelStyle, travelStyle.capitalize())
    dur_label = {"1d": "1 Hari", "2d1n": "2 Hari 1 Malam", "3d2n": "3 Hari 2 Malam"}.get(duration, duration)

    day1 = {
        "day": "Hari 1", "date": "Hari Pertama",
        "items": [
            {"time": "07:00", "title": "Sarapan Mie Ongklok", "desc": "Kuliner khas Dieng yang wajib dicoba. Hangat dan mengenyangkan.", "cost": 15000, "type": "food"},
            {"time": "08:30", "title": "Candi Arjuna & Gatotkaca", "desc": "Kompleks candi Hindu tertua di Jawa. Durasi ~45 menit.", "cost": 15000, "type": "culture"},
            {"time": "10:00", "title": "Kawah Sikidang", "desc": "Kawah vulkanik aktif dengan fumarola. Jaga jarak aman.", "cost": 20000, "type": "attraction"},
            {"time": "12:00", "title": "Makan Siang", "desc": "Carica segar dan kentang goreng Dieng.", "cost": 20000, "type": "food"},
            {"time": "13:30", "title": "Telaga Warna & Pengilon", "desc": "Dua telaga bersebelahan dengan fenomena warna air. Trek ringan ~1 jam.", "cost": 15000, "type": "attraction"},
            {"time": "15:00", "title": "Dieng Plateau Theater", "desc": "Film 4D sejarah Dieng. Tempat berteduh saat kabut turun.", "cost": 25000, "type": "attraction"},
        ],
    }

    day2 = {
        "day": "Hari 2", "date": "Hari Kedua",
        "items": [
            {"time": "04:00", "title": "Sunrise Bukit Sikunir", "desc": "Golden sunrise terbaik Dieng! Bawa jaket tebal, suhu ~5°C. Trek 30 menit.", "cost": 15000, "type": "attraction"},
            {"time": "07:00", "title": "Sarapan Hangat", "desc": "Sarapan di warung dekat homestay.", "cost": 15000, "type": "food"},
            {"time": "08:30", "title": "Batu Ratapan Angin", "desc": "View point panorama 360° dataran Dieng.", "cost": 10000, "type": "attraction"},
            {"time": "10:00", "title": "Kawah Candradimuka", "desc": "Kawah legendaris Mahabharata. Trek ringan.", "cost": 10000, "type": "attraction"},
            {"time": "11:30", "title": "Beli Oleh-oleh", "desc": "Pasar Carica Dieng. Carica, keripik kentang, purwaceng.", "cost": 50000, "type": "shopping"},
            {"time": "12:30", "title": "Makan Siang & Pulang", "desc": "Hati-hati di turunan! Gunakan gear rendah.", "cost": 15000, "type": "food"},
        ],
    }

    day3 = {
        "day": "Hari 3", "date": "Hari Ketiga",
        "items": [
            {"time": "06:00", "title": "Sarapan Pagi", "desc": "Sarapan hangat terakhir di Dieng.", "cost": 0, "type": "food"},
            {"time": "07:30", "title": "Kawah Sileri", "desc": "Kawah terbesar Dieng. WAJIB ikuti jalur resmi!", "cost": 15000, "type": "attraction"},
            {"time": "09:30", "title": "Padang Savana & Desa Sembungan", "desc": "Desa tertinggi Pulau Jawa. Pemandangan menakjubkan.", "cost": 5000, "type": "attraction"},
            {"time": "11:00", "title": "Museum Kailasa", "desc": "Koleksi artefak dan geologi Dieng.", "cost": 10000, "type": "attraction"},
            {"time": "12:00", "title": "Beli Oleh-oleh & Pulang", "desc": "Perjalanan pulang. Hati-hati turunan!", "cost": 50000, "type": "shopping"},
        ],
    }

    if duration == "1d":
        day1["items"].append({"time": "16:30", "title": "Beli Oleh-oleh & Pulang", "desc": "Carica dan keripik kentang Dieng sebelum pulang.", "cost": 50000, "type": "shopping"})
        days = [day1]
        gear = ["Jaket tebal", "Jas hujan", "Sepatu hiking", "Air mineral"]
    elif duration == "3d2n":
        day1["items"].append({"time": "17:00", "title": "Check-in Homestay", "desc": "Istirahat di Dieng Kulon. Malam bisa turun ke 3°C!", "cost": 150000, "type": "stay"})
        day2_stay = dict(day2)
        day2_stay["items"] = day2["items"][:4] + [
            {"time": "12:00", "title": "Makan Siang", "desc": "Kentang goreng Dieng dan teh panas.", "cost": 20000, "type": "food"},
            {"time": "14:00", "title": "Candi Bima", "desc": "Candi unik dengan arsitektur berbeda.", "cost": 10000, "type": "attraction"},
            {"time": "16:00", "title": "Kembali ke Homestay", "desc": "Istirahat dan persiapan hari terakhir.", "cost": 0, "type": "stay"},
        ]
        days = [day1, day2_stay, day3]
        gear = ["Jaket tebal", "Senter/headlamp", "Jas hujan", "Sepatu hiking", "Syal/buff", "P3K dasar", "Air mineral", "Power bank"]
    else:  # 2d1n
        day1["items"].append({"time": "17:00", "title": "Check-in Homestay", "desc": "Istirahat di Dieng Kulon. Malam bisa turun ke 3°C!", "cost": 150000, "type": "stay"})
        days = [day1, day2]
        gear = ["Jaket tebal", "Senter/headlamp", "Jas hujan", "Sepatu hiking", "Syal/buff", "Air mineral"]

    return {
        "title": f"Itinerary {dur_label} — {style_label} Traveler",
        "budget": f"Rp {budget:,}",
        "weatherNote": note[:500],
        "gear": gear,
        "days": days,
    }

@router.post("/generate")
async def generate_itinerary(req: ItineraryRequest):
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
    ml_block = _ml_prompt_block(p, h, mo, doy, blend_temp, live_precip)

    client = _get_client()
    if not client:
        mock_note = ml_block.replace("\n", " ").strip() if ml_block else ""
        if not mock_note:
            mock_note = "⚠️ Kabut tebal diprediksi sore hari. Hindari jalur curam."
        return get_mock_itinerary(req.duration, req.travelStyle, req.budget, req.vehicle, mock_note)

    try:
        prompt = f"""
        Buatkan itinerary wisata Dieng dalam format JSON.
        Durasi: {req.duration} (contoh: 1d, 2d1n)
        Gaya: {req.travelStyle} (solo, family, couple, group)
        Budget: Rp {req.budget}
        Kendaraan: {req.vehicle}
        {ml_block}

        Format JSON harus mengikuti struktur ini persis:
        {{
            "title": "Judul Itinerary",
            "budget": "Rp XX.XXX",
            "weatherNote": "Catatan cuaca/peringatan jalur aman sesuai kendaraan",
            "gear": ["Item 1", "Item 2"],
            "days": [
                {{
                    "day": "Hari X",
                    "date": "Hari",
                    "items": [
                        {{
                            "time": "HH:MM",
                            "title": "Nama Aktivitas",
                            "desc": "Deskripsi singkat",
                            "cost": 15000,
                            "type": "attraction/food/stay/shopping"
                        }}
                    ]
                }}
            ]
        }}
        Berikan HANYA JSON. Jangan tambahkan markdown atau teks lain.
        """
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
        text = response.text.replace("```json", "").replace("```", "").strip()
        data = json.loads(text)
        return data
    except Exception:
        # Fallback ke mock jika Gemini gagal (quota, network, dll)
        mock_note = ml_block.replace("\n", " ").strip() if ml_block else ""
        if not mock_note:
            mock_note = "⚠️ Kabut tebal diprediksi sore hari. Hindari jalur curam."
        return get_mock_itinerary(req.duration, req.travelStyle, req.budget, req.vehicle, mock_note)
