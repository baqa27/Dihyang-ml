"""
DITA (Dieng Intelligence Tourism Assistant) — NLP Chatbot Router
Menggunakan Gemini API + Custom Knowledge Base untuk memberikan
respons akurat tentang wisata Dieng.
"""

import os
import json
import google.genai as genai
from google.genai import types as genai_types
from fastapi import APIRouter
from pydantic import BaseModel
from ..models.knowledge_base import (
    build_knowledge_context, RETRIBUSI_DATA, DANGER_ZONES,
    SAFE_ROUTES, DESTINATIONS, ACCOMMODATIONS, TRANSPORTATION,
    SOLO_TRAVELER_TIPS, GEAR_RECOMMENDATIONS
)

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    history: list = []

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
_genai_client = None

def _get_client():
    global _genai_client
    if _genai_client is None and GEMINI_API_KEY and GEMINI_API_KEY != "MASUKKAN_API_KEY_ANDA_DI_SINI":
        _genai_client = genai.Client(api_key=GEMINI_API_KEY)
    return _genai_client

# System instruction + Knowledge Base injection
KNOWLEDGE_CONTEXT = build_knowledge_context()

SYSTEM_INSTRUCTION = f"""
Kamu adalah DITA (Dieng Intelligence Tourism Assistant), asisten wisata cerdas berbasis AI
untuk kawasan Dataran Tinggi Dieng, Wonosobo, Jawa Tengah.

IDENTITAS:
- Dikembangkan oleh Tim PJK-GM067 (Capstone AI for Smart Tourism — IBM SkillsBuild x Pijak)
- Menggunakan teknologi NLP (Natural Language Processing) dan Predictive Analytics
- Memiliki data terverifikasi dari riset lapangan langsung di kawasan Dieng

TUGAS UTAMA:
1. Memberikan info cuaca real-time dan peringatan proaktif (kabut, hujan, suhu ekstrem)
2. Merekomendasikan rute AMAN dan memperingatkan zona BAHAYA (Sikarim, Watu Angkruk)
3. Menyusun itinerary wisata adaptif terhadap cuaca dan preferensi pengguna
4. Memberikan informasi retribusi/biaya RESMI (anti-pungli)
5. Memberikan tips keamanan khusus solo traveler
6. Merekomendasikan perlengkapan berdasarkan kondisi cuaca

GAYA KOMUNIKASI:
- Bahasa Indonesia yang ramah, informatif, dan mudah dipahami
- Gunakan emoji secukupnya untuk kesan friendly
- Selalu sertakan disclaimer jika informasi bersifat estimasi
- Jika tidak yakin, akui dan sarankan cek ke Dinas Pariwisata Wonosobo

{KNOWLEDGE_CONTEXT}
"""


@router.post("")
async def chat_with_dita(req: ChatRequest):
    client = _get_client()
    if not client:
        return handle_nlp_fallback(req.message)

    try:
        # Bangun history dalam format google.genai
        history = []
        for msg in req.history:
            role = "user" if msg["role"] == "user" else "model"
            history.append(genai_types.Content(
                role=role,
                parts=[genai_types.Part(text=msg["content"])]
            ))

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=history + [genai_types.Content(
                role="user",
                parts=[genai_types.Part(text=req.message)]
            )],
            config=genai_types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
            ),
        )
        return {"reply": response.text}
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return handle_nlp_fallback(req.message)


def handle_nlp_fallback(message: str):
    """
    NLP Fallback berbasis keyword matching + knowledge base lokal.
    Digunakan saat Gemini API tidak tersedia.
    Menggunakan teknik Intent Classification sederhana.
    """
    msg = message.lower()
    
    # ─── Intent: Cuaca ───
    if any(k in msg for k in ["cuaca", "weather", "suhu", "temperatur", "hujan", "kabut", "dingin", "panas"]):
        reply = """🌤️ **Informasi Cuaca Dieng Terkini**

🌡️ Suhu rata-rata Dieng: 12-20°C (siang) dan 5-10°C (malam)
💧 Kelembapan: 80-95%
🌬️ Angin: 10-15 km/h
👁️ Jarak pandang: 3-8 km (tergantung kabut)

⚠️ **Peringatan Khusus:**
- Kabut tebal sering turun pukul **15:00-17:00**
- Hujan deras biasanya pukul **13:00-16:00**
- Suhu bisa turun hingga **3°C** di dini hari (terutama Juni-Agustus)

🧥 **Saran Perlengkapan:** Jaket tebal, syal, sepatu anti-slip, jas hujan.

_Data cuaca real-time tersedia di menu Dashboard Cuaca._"""
        return {"reply": reply}
    
    # ─── Intent: Rute/Jalan ───
    if any(k in msg for k in ["rute", "jalan", "arah", "sikarim", "watu angkruk", "navigasi", "jalur"]):
        motor_route = SAFE_ROUTES["motorcycle"]
        reply = f"""🗺️ **Rekomendasi Rute Aman ke Dieng**

✅ **Rute Direkomendasikan:**
{motor_route['recommended']}
📏 Jarak: {motor_route['distance']} | ⏱️ Waktu: {motor_route['duration']}
{motor_route['description']}

❌ **WAJIB DIHINDARI:**
"""
        for zone in DANGER_ZONES:
            reply += f"- 🔴 **{zone['name']}** (kemiringan {zone['gradient_degree']}°): {zone['description']}\n  💡 {zone['advice']}\n\n"
        
        reply += "💡 **Tips:** Gunakan gear rendah saat menanjak. Pastikan rem prima sebelum berangkat."
        return {"reply": reply}
    
    # ─── Intent: Retribusi/Biaya ───
    if any(k in msg for k in ["biaya", "retribusi", "tiket", "harga", "tarif", "bayar", "pungli", "karcis"]):
        reply = "💰 **Biaya Retribusi Resmi Wisata Dieng** _(terverifikasi April 2026)_\n\n"
        reply += "| Destinasi | Wisatawan Lokal | Wisatawan Asing |\n|-----------|:-:|:-:|\n"
        for dest, prices in RETRIBUSI_DATA.items():
            reply += f"| {dest} | Rp {prices['lokal']:,} | Rp {prices['asing']:,} |\n"
        reply += "\n⚠️ **PENTING:** Selalu minta **karcis resmi** setelah membayar! Jika tidak ada karcis, kemungkinan besar itu pungli. Laporkan ke Dinas Pariwisata Wonosobo."
        return {"reply": reply}
    
    # ─── Intent: Itinerary ───
    if any(k in msg for k in ["itinerary", "jadwal", "rencana", "hari", "malam", "trip"]):
        reply = """📅 **Rekomendasi Itinerary 2 Hari 1 Malam**

**Hari 1 (Sabtu):**
- 🌅 04:00 — Sunrise di **Bukit Sikunir** (Rp 15.000)
- ☕ 07:00 — Sarapan **Mie Ongklok** (~Rp 15.000)
- 🏛️ 08:30 — **Candi Arjuna** (Rp 15.000)
- 🌋 10:00 — **Kawah Sikidang** (Rp 20.000)
- 🍽️ 12:00 — Makan siang + Carica (~Rp 20.000)
- 🏞️ 13:30 — **Telaga Warna & Pengilon** (Rp 15.000)
- 🎬 15:00 — **Dieng Plateau Theater** (Rp 25.000)
- 🏠 17:00 — Check-in homestay (~Rp 150.000)

**Hari 2 (Minggu):**
- 🌄 06:00 — Sarapan pagi
- 🪨 07:30 — **Batu Ratapan Angin** (Rp 10.000)
- 🌋 09:00 — **Kawah Candradimuka** (Rp 10.000)
- 🛍️ 11:00 — Beli oleh-oleh (~Rp 50.000)
- 🍜 12:30 — Makan siang & pulang

💰 **Estimasi total:** ~Rp 360.000 (belum termasuk transport)

_Untuk itinerary yang lebih personal dan adaptif cuaca, gunakan menu **Smart Itinerary**!_"""
        return {"reply": reply}
    
    # ─── Intent: Solo Traveler / Keamanan ───
    if any(k in msg for k in ["solo", "sendiri", "aman", "keamanan", "safety", "bahaya", "darurat", "tips"]):
        reply = "🛡️ **Tips Keamanan Solo Traveler di Dieng**\n\n"
        for i, tip in enumerate(SOLO_TRAVELER_TIPS, 1):
            reply += f"{i}. {tip}\n"
        reply += "\n📞 **Nomor Darurat:**\n- Polsek Kejajar: 0286-3321110\n- SAR Wonosobo: 0286-321100\n- RS Setjonegoro: 0286-321006"
        return {"reply": reply}
    
    # ─── Intent: Destinasi ───
    if any(k in msg for k in ["destinasi", "wisata", "tempat", "kawah", "candi", "telaga", "bukit", "sikunir", "sikidang"]):
        reply = "🏔️ **Destinasi Wisata Dieng**\n\n"
        for dest in DESTINATIONS:
            reply += f"**{dest['name']}** ({dest['type']})\n{dest['description']}\n💡 {dest['tips']}\n⏱️ Durasi: {dest['duration']}\n\n"
        return {"reply": reply}
    
    # ─── Intent: Penginapan ───
    if any(k in msg for k in ["hotel", "penginapan", "homestay", "menginap", "tidur"]):
        reply = "🏠 **Penginapan di Dieng**\n\n"
        for acc in ACCOMMODATIONS:
            reply += f"- **{acc['name']}** ({acc['type']}): {acc['price_range']} — ⭐ {acc['rating']}/5\n"
        reply += "\n💡 _Saran: Pesan 1-2 hari sebelumnya, terutama saat weekend dan libur nasional._"
        return {"reply": reply}
    
    # ─── Intent: Transportasi ───
    if any(k in msg for k in ["transport", "bus", "ojek", "sewa", "kendaraan", "motor"]):
        reply = "🚗 **Transportasi ke/di Dieng**\n\n"
        for t in TRANSPORTATION:
            reply += f"- **{t['type']}**: {t['price']} — {t['schedule']}\n"
        reply += "\n💡 _Saran: Isi bensin penuh di Wonosobo karena SPBU di Dieng terbatas._"
        return {"reply": reply}
    
    # ─── Intent: Perlengkapan ───
    if any(k in msg for k in ["perlengkapan", "bawa", "persiapan", "siapkan", "jaket", "sepatu"]):
        gear = GEAR_RECOMMENDATIONS["umum"]
        reply = "🎒 **Perlengkapan Wajib Wisata Dieng**\n\n"
        reply += "**Wajib bawa:**\n"
        for item in gear["wajib"]:
            reply += f"✅ {item}\n"
        reply += "\n**Saran tambahan:**\n"
        for item in gear["saran"]:
            reply += f"💡 {item}\n"
        reply += "\n🥶 _Jika suhu < 8°C, tambahkan: syal, sarung tangan, topi kupluk, sleeping bag._"
        return {"reply": reply}
    
    # ─── Intent: Sapaan ───
    if any(k in msg for k in ["halo", "hai", "hi", "hey", "selamat", "assalamualaikum", "pagi", "siang", "sore", "malam"]):
        reply = """👋 Halo! Saya **DITA** (Dieng Intelligence Tourism Assistant) 🏔️

Saya asisten wisata cerdas yang siap membantu Anda menjelajahi Dataran Tinggi Dieng dengan aman dan nyaman!

Saya bisa membantu Anda dengan:
- 🌤️ **Informasi cuaca** real-time dan peringatan
- 🛡️ **Rute aman** dan peringatan jalur berbahaya
- 💰 **Biaya retribusi resmi** (anti-pungli!)
- 📅 **Smart itinerary** adaptif cuaca
- 🏔️ **Info destinasi** dan tips solo traveler
- 🎒 **Rekomendasi perlengkapan**

Silakan tanya apa saja tentang wisata Dieng! 😊"""
        return {"reply": reply}
    
    # ─── Default ───
    reply = """Terima kasih atas pertanyaannya! 😊

Saya DITA, asisten wisata cerdas untuk Dieng. Berikut yang bisa saya bantu:

- 🌤️ Ketik **"cuaca"** untuk info cuaca terkini
- 🗺️ Ketik **"rute aman"** untuk rekomendasi jalur
- 💰 Ketik **"retribusi"** untuk biaya tiket resmi
- 📅 Ketik **"itinerary"** untuk rencana perjalanan
- 🛡️ Ketik **"tips keamanan"** untuk tips solo traveler
- 🏔️ Ketik **"destinasi"** untuk daftar tempat wisata
- 🏠 Ketik **"penginapan"** untuk info hotel/homestay

Silakan coba salah satu! 🙌"""
    return {"reply": reply}
