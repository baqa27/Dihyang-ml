from fastapi import APIRouter
from pydantic import BaseModel
import os
import google.generativeai as genai
import json

router = APIRouter()

class ItineraryRequest(BaseModel):
    duration: str
    travelStyle: str
    budget: int
    vehicle: str

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_mock_itinerary(duration, travelStyle, budget, vehicle):
    return {
        "title": f"Itinerary {duration} - {travelStyle.capitalize()} Traveler",
        "budget": f"Rp {budget:,}",
        "weatherNote": "⚠️ Kabut tebal diprediksi sore hari. Hindari jalur curam.",
        "gear": ["Jaket tebal", "Senter", "Obat pribadi"],
        "days": [
            {
                "day": "Hari 1",
                "date": "Hari Pertama",
                "items": [
                    { "time": "08:00", "title": "Kawah Sikidang", "desc": "Eksplorasi kawah vulkanik aktif.", "cost": 20000, "type": "attraction" },
                    { "time": "12:00", "title": "Makan Siang", "desc": "Mie Ongklok hangat.", "cost": 25000, "type": "food" },
                    { "time": "14:00", "title": "Candi Arjuna", "desc": "Kompleks candi bersejarah.", "cost": 15000, "type": "culture" }
                ]
            }
        ]
    }

@router.post("/generate")
async def generate_itinerary(req: ItineraryRequest):
    if not GEMINI_API_KEY or GEMINI_API_KEY == "MASUKKAN_API_KEY_ANDA_DI_SINI":
        return get_mock_itinerary(req.duration, req.travelStyle, req.budget, req.vehicle)
        
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        prompt = f"""
        Buatkan itinerary wisata Dieng dalam format JSON.
        Durasi: {req.duration} (contoh: 1d, 2d1n)
        Gaya: {req.travelStyle} (solo, family, couple, group)
        Budget: Rp {req.budget}
        Kendaraan: {req.vehicle}
        
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
        response = model.generate_content(prompt)
        # bersihkan json block
        text = response.text.replace("```json", "").replace("```", "").strip()
        data = json.loads(text)
        return data
    except Exception as e:
        # Biarkan frontend handle fallback demo
        raise e
