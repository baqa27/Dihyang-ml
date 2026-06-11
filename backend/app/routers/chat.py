"""
DITA (Dieng Intelligence Tourism Assistant) — NLP Chatbot Router
Menggunakan Gemini API + Custom Knowledge Base untuk memberikan
respons akurat tentang wisata Dieng.
"""

import os
import re
import logging
import google.genai as genai
from google.genai import types as genai_types
from fastapi import APIRouter, Request, HTTPException, status
from pydantic import BaseModel, Field, field_validator
from slowapi import Limiter
from slowapi.util import get_remote_address

from ..config import settings
from ..models.knowledge_base import (
    build_knowledge_context, RETRIBUSI_DATA, DANGER_ZONES,
    SAFE_ROUTES, DESTINATIONS, ACCOMMODATIONS, TRANSPORTATION,
    SOLO_TRAVELER_TIPS, GEAR_RECOMMENDATIONS
)

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)
logger = logging.getLogger(__name__)

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    history: list = Field(default_factory=list, max_length=50)
    
    @field_validator('message')
    @classmethod
    def validate_message(cls, v: str) -> str:
        """Validate and sanitize message"""
        if not v or not v.strip():
            raise ValueError("Message tidak boleh kosong")
        
        # Strip whitespace
        v = v.strip()
        
        # Check for dangerous patterns (XSS prevention)
        dangerous_patterns = [
            r'<script[^>]*>.*?</script>',
            r'<iframe[^>]*>.*?</iframe>',
            r'javascript:',
            r'on\w+\s*=',  # onclick, onload, etc.
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, v, re.IGNORECASE):
                raise ValueError("Input mengandung karakter atau kode berbahaya")
        
        return v
    
    @field_validator('history')
    @classmethod
    def validate_history(cls, v: list) -> list:
        """Validate chat history"""
        if len(v) > 50:
            raise ValueError("History terlalu panjang (maksimal 50 pesan)")
        
        # Validate each message in history
        for msg in v:
            if not isinstance(msg, dict):
                raise ValueError("Format history tidak valid")
            if 'role' not in msg or 'content' not in msg:
                raise ValueError("Setiap pesan harus memiliki 'role' dan 'content'")
            if msg['role'] not in ['user', 'bot', 'model']:
                raise ValueError(f"Role tidak valid: {msg['role']}")
        
        return v

def _get_client():
    """Get Gemini client with validation"""
    if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY in [
        "MASUKKAN_API_KEY_ANDA_DI_SINI",
        "masukkan_api_key_anda_disini",
        ""
    ]:
        return None
    
    try:
        return genai.Client(api_key=settings.GEMINI_API_KEY)
    except Exception as e:
        print(f"Error initializing Gemini client: {e}")
        return None

# System instruction + Knowledge Base injection
# KNOWLEDGE_CONTEXT will be built dynamically per request

SYSTEM_INSTRUCTION_TEMPLATE = """
Kamu adalah DITA (Dieng Intelligence Tourism Assistant), asisten wisata cerdas dan pemandu wisata virtual untuk kawasan Dataran Tinggi Dieng, Wonosobo.

IDENTITAS & KARAKTER:
- Kamu dikembangkan oleh Tim PJK-GM067 (Capstone AI for Smart Tourism).
- Karaktermu: Hangat, profesional, antusias, dan sangat paham seluk-beluk Dieng.
- Gaya Bahasa: Santai tapi sopan (gunakan bahasa Indonesia yang natural, seperti "Halo!", "Tentu saja,", "Yuk,"). Gunakan emoji dengan tepat untuk membuat percakapan lebih hidup.

TUGAS & ATURAN KETAT (PENTING!):
1. ANTI-HALUSINASI: Seluruh informasi (terutama HARGA TIKET, NAMA DESTINASI, dan RUTE) WAJIB merujuk HANYA pada bagian KNOWLEDGE BASE di bawah ini. JANGAN PERNAH mengarang harga atau tempat wisata yang tidak terdaftar. Jika pengguna menanyakan tempat yang tidak ada di data, katakan dengan sopan bahwa kamu belum memiliki informasi resmi mengenai tempat tersebut.
2. HARGA TIKET & RETRIBUSI: Jika pengguna bertanya harga tiket masuk/retribusi, kamu WAJIB memformatnya dengan rapi sesuai instruksi di Knowledge Base (pisahkan harga Lokal, Asing, dan Parkir). Selalu ingatkan tentang bahaya pungli dan pentingnya meminta karcis resmi.
3. RUTE & KEAMANAN: Selalu prioritaskan keamanan. Ingatkan wisatawan soal tanjakan ekstrem (Sikarim) jika mereka membawa motor matic. Sebutkan bahwa rute Watu Angkruk cukup menanjak namun relatif paling aman untuk dilewati.
4. CUACA & PERLENGKAPAN: Berikan saran pakaian (jaket tebal, sarung tangan) jika menyinggung cuaca Dieng yang dingin ekstrem/embun upas.
5. PEMBUATAN ITINERARY: Jika pengguna meminta dibuatkan itinerary (rencana perjalanan) misalnya untuk 1 hari, 2 hari, dsb, susunlah jadwal yang realistis dan logis secara geografis. UNTUK SETIAP DESTINASI di itinerary, WAJIB CANTUMKAN HARGA TIKET (ambil dari data yang disediakan). Di bagian akhir itinerary, hitung dan berikan TOTAL ESTIMASI BIAYA TIKET untuk memudahkan pengguna.
6. FORMAT JAWABAN: Buat jawaban mudah dibaca. Gunakan bullet points, bold text untuk kata penting, dan paragraf pendek.

Berikut adalah seluruh data resmi yang harus kamu gunakan sebagai pedoman mutlak:

{STATIC_CONTEXT}

{DYNAMIC_CONTEXT}
"""


@router.post("")
@limiter.limit(f"{settings.RATE_LIMIT_CHAT_PER_MINUTE}/minute")
async def chat_with_dita(req: ChatRequest, request: Request):
    logger.info(f"💬 Chat request from {request.client.host if request.client else 'unknown'}: {req.message[:50]}...")
    
    client = _get_client()

    try:
        if not client:
            logger.warning("⚠️ Gemini client not available, using fallback")
            raise ValueError("Gemini client is not initialized")
        # RAG: Retrieve context from ChromaDB
        try:
            from ..models.rag_engine import retrieve_relevant_context
            # Karena jumlah destinasi wisata hanya 43 (sekitar 2000-3000 token), kita pass semua 
            # hasil (n_res=50) ke LLM untuk memastikan tidak ada destinasi yang terlewat oleh RAG embedding.
            n_res = 50
            dynamic_context = retrieve_relevant_context(req.message, n_results=n_res)
        except Exception as e:
            dynamic_context = f"DEBUG CHAT RAG ERROR: {str(e)}"
            
        # Fetch Real-time Weather
        weather_context = ""
        try:
            from .weather import get_current_weather
            weather_data = await get_current_weather()
            weather_context = f"\n\n--- REAL-TIME WEATHER DATA (GUNAKAN JIKA DITANYA CUACA SAAT INI) ---\n" \
                              f"Suhu Saat Ini: {weather_data['temperature']}°C (Terasa seperti {weather_data['feels_like']}°C)\n" \
                              f"Kondisi: {weather_data['condition_label']}\n" \
                              f"Kelembapan: {weather_data['humidity']}%\n" \
                              f"Angin: {weather_data['wind_speed']} km/h\n" \
                              f"Jarak Pandang: {weather_data['visibility']} km\n" \
                              f"Prakiraan Hari Ini: Min {weather_data['low']}°C, Max {weather_data['high']}°C\n"
        except Exception as e:
            logger.error(f"Failed to fetch weather for chat context: {e}")

        # Gabungkan context
        current_knowledge_context = build_knowledge_context()
        full_dynamic_context = dynamic_context + weather_context
        system_prompt = SYSTEM_INSTRUCTION_TEMPLATE.replace("{STATIC_CONTEXT}", current_knowledge_context).replace("{DYNAMIC_CONTEXT}", full_dynamic_context)

        # Bangun history dalam format google.genai
        history = []
        for msg in req.history:
            role = "user" if msg["role"] == "user" else "model"
            history.append(genai_types.Content(
                role=role,
                parts=[genai_types.Part(text=msg["content"])]
            ))

        import asyncio
        response = await asyncio.wait_for(
            client.aio.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=history + [genai_types.Content(
                    role="user",
                    parts=[genai_types.Part(text=req.message)]
                )],
                config=genai_types.GenerateContentConfig(
                    system_instruction=system_prompt,
                ),
            ),
            timeout=float(settings.GEMINI_TIMEOUT_SECONDS)
        )
        logger.info(f"✅ Gemini response generated successfully")
        return {"success": True, "reply": response.text}
    except Exception as e:
        logger.error(f"❌ Gemini API Error/Timeout: {type(e).__name__} - {str(e)}")
        
        # NVIDIA Fallback
        nvidia_key = os.getenv("NVIDIA_API_KEY")
        if nvidia_key and nvidia_key != "MASUKKAN_API_KEY_NVIDIA_ANDA_DI_SINI":
            try:
                from openai import AsyncOpenAI
                print("Mencoba fallback ke NVIDIA (meta/llama-3.1-70b-instruct)...")
                nvidia_client = AsyncOpenAI(
                    api_key=nvidia_key,
                    base_url="https://integrate.api.nvidia.com/v1"
                )
                
                messages = [{"role": "system", "content": system_prompt}]
                for msg in req.history:
                    # NVIDIA (OpenAI format) uses 'assistant', not 'model'
                    role = "assistant" if msg["role"] == "model" else msg["role"]
                    messages.append({"role": role, "content": msg["content"]})
                messages.append({"role": "user", "content": req.message})
                
                import asyncio
                response = await asyncio.wait_for(
                    nvidia_client.chat.completions.create(
                        model="meta/llama-3.1-70b-instruct",
                        messages=messages,
                        temperature=0.7
                    ),
                    timeout=45.0
                )
                return {"reply": response.choices[0].message.content}
            except Exception as ne:
                print(f"NVIDIA API Error details: {type(ne).__name__} - {str(ne)}")
        
        # Jika semua gagal, gunakan NLP fallback
        logger.info("🔄 Menggunakan NLP fallback (rule-based)")
        return {"success": True, "reply": handle_nlp_fallback(req.message, weather_data if 'weather_data' in locals() else None)["reply"], "source": "fallback"}

def _fuzzy_match(msg: str, keywords: list, threshold=75) -> bool:
    try:
        from thefuzz import fuzz
        # Check against each keyword
        for k in keywords:
            # Menggunakan token_set_ratio untuk akurasi yang jauh lebih baik dan mencegah false positive
            if fuzz.token_set_ratio(k, msg) >= threshold:
                return True
        return False
    except ImportError:
        # Fallback to exact match if thefuzz is not installed yet
        return any(k in msg for k in keywords)


def handle_nlp_fallback(message: str, weather_data: dict = None):
    """
    NLP Fallback berbasis keyword matching + knowledge base lokal.
    Digunakan saat Gemini API tidak tersedia.
    Sekarang dengan Fuzzy Matching untuk toleransi typo.
    """
    msg = message.lower()
    
    # ─── Intent: Cuaca ───
    if _fuzzy_match(msg, ["cuaca", "weather", "suhu", "temperatur", "hujan", "kabut", "dingin", "panas"]):
        if weather_data:
            reply = f"""🌤️ Informasi Cuaca Dieng Terkini (Real-time)

🌡️ Suhu Saat Ini: {weather_data['temperature']}°C (Terasa seperti {weather_data['feels_like']}°C)
☁️ Kondisi: {weather_data['condition_label']}
💧 Kelembapan: {weather_data['humidity']}%
🌬️ Angin: {weather_data['wind_speed']} km/h
👁️ Jarak Pandang: {weather_data['visibility']} km

⚠️ Prakiraan Hari Ini: Suhu terendah {weather_data['low']}°C, tertinggi {weather_data['high']}°C.

🧥 Saran Perlengkapan: {"Gunakan jaket tebal dan syal!" if weather_data['temperature'] < 15 else "Bawa jaket dan jas hujan untuk berjaga-jaga."}
"""
        else:
            reply = """🌤️ Informasi Cuaca Dieng Terkini

🌡️ Suhu rata-rata Dieng: 12-20°C (siang) dan 5-10°C (malam)
💧 Kelembapan: 80-95%
🌬️ Angin: 10-15 km/h
👁️ Jarak pandang: 3-8 km (tergantung kabut)

⚠️ Peringatan Khusus:
• Kabut tebal sering turun pukul 15:00-17:00
• Hujan deras biasanya pukul 13:00-16:00
• Suhu bisa turun hingga 3°C di dini hari (terutama Juni-Agustus)

🧥 Saran Perlengkapan: Jaket tebal, syal, sepatu anti-slip, jas hujan.

Data cuaca real-time tersedia di menu Dashboard Cuaca."""
        return {"reply": reply}
    
    # ─── Intent: Rute/Jalan ───
    if _fuzzy_match(msg, ["rute", "jalan", "arah", "sikarim", "watu angkruk", "navigasi", "jalur"]):
        motor_route = SAFE_ROUTES["motorcycle"]
        reply = f"""🗺️ Rekomendasi Rute Aman ke Dieng

✅ Rute Direkomendasikan:
{motor_route['recommended']}
📏 Jarak: {motor_route['distance']} | ⏱️ Waktu: {motor_route['duration']}
{motor_route['description']}

"""
        # Separate by risk
        danger_zones = [z for z in DANGER_ZONES if z['risk'] == 'TINGGI' or z['risk'] == 'SEDANG']
        safe_zones = [z for z in DANGER_ZONES if z['risk'] == 'AMAN']
        
        if safe_zones:
            reply += "✅ Jalur Menanjak Namun Aman:\n"
            for zone in safe_zones:
                reply += f"🟢 {zone['name']} (kemiringan {zone['gradient_degree']}°)\n"
                reply += f"   {zone['description']}\n"
                reply += f"   💡 {zone['advice']}\n\n"
        
        if danger_zones:
            reply += "❌ Wajib Dihindari / Sangat Hati-hati:\n"
            for zone in danger_zones:
                reply += f"🔴 {zone['name']} (kemiringan {zone['gradient_degree']}°)\n"
                reply += f"   {zone['description']}\n"
                reply += f"   💡 {zone['advice']}\n\n"
        
        reply += "💡 Tips: Gunakan gear rendah saat menanjak. Pastikan rem prima sebelum berangkat."
        return {"reply": reply}
    
    # ─── Intent: Retribusi/Biaya ───
    if _fuzzy_match(msg, ["biaya", "retribusi", "tiket", "tuket", "harga", "tarif", "bayar", "pungli", "karcis"]):
        mentioned_destinations = []
        for dest, prices in RETRIBUSI_DATA.items():
            dest_lower = dest.lower()
            generic_words = ["candi", "kawah", "telaga", "bukit", "goa", "gua", "batu", "air", "terjun", "padang", "gunung", "museum", "dieng", "tiket", "terusan"]
            specific_words = [w for w in dest_lower.replace("(", "").replace(")", "").replace("+", " ").split() if w not in generic_words]
            
            if dest_lower in msg:
                mentioned_destinations.append((dest, prices))
            else:
                for word in specific_words:
                    if len(word) >= 3 and word in msg:
                        if (dest, prices) not in mentioned_destinations:
                            mentioned_destinations.append((dest, prices))

        reply = "Berikut rincian biaya retribusi dan parkir resmi di kawasan wisata Dieng:\n\n"
        
        # Tambahkan penjelasan khusus jika menyebut arjuna atau sikidang
        if "arjuna" in msg or "sikidang" in msg:
            reply += "💡 Info Penting: Tiket masuk Candi Arjuna sudah bundling (terusan) dengan Kawah Sikidang, sehingga Anda cukup membayar satu kali untuk mengunjungi kedua tempat tersebut. Anda bisa memilih lewat Pintu A atau Pintu B.\n\n"
            
        target_list = mentioned_destinations if mentioned_destinations else RETRIBUSI_DATA.items()
        
        for dest, prices in target_list:
            reply += f"🎫 {dest}\n"
            desc = prices.get('description', '')
            if desc and desc != 'Deskripsi belum tersedia.':
                reply += f"{desc}\n\n"
            reply += f"  • Wisatawan Lokal : Rp {prices['lokal']:,}\n"
            reply += f"  • Wisatawan Asing : Rp {prices['asing']:,}\n\n"
            
            if prices['parkir_motor'] > 0 or prices['parkir_mobil'] > 0:
                reply += f"🅿️ Tarif Parkir\n"
                reply += f"  • Roda 2 (Motor)  : Rp {prices['parkir_motor']:,}\n"
                reply += f"  • Roda 4 (Mobil)  : Rp {prices['parkir_mobil']:,}\n\n"
            
        import random
        all_dests = list(RETRIBUSI_DATA.keys())
        random_dests = random.sample(all_dests, min(3, len(all_dests)))
        opsi_str = ", ".join([f"Harga tiket {d}" for d in random_dests])
        
        reply += "⚠️ PENTING: Pastikan Anda selalu meminta karcis resmi saat membayar tiket masuk dan tarif parkir! Jika oknum/petugas tidak memberikan karcis, kemungkinan besar itu adalah pungli. Silakan laporkan kejadian tersebut ke Dinas Pariwisata Wonosobo."
        reply += f"\n\n[OPSI: {opsi_str}]"
        return {"reply": reply}
    
    # ─── Intent: Itinerary ───
    if _fuzzy_match(msg, ["itinerary", "jadwal", "rencana", "hari", "malam", "trip", "liburan", "perjalanan"]):
        # Parse durasi dari pesan
        import re
        duration = 3  # default
        
        # Cari angka yang diikuti "hari" atau "day"
        day_match = re.search(r'(\d+)\s*(?:hari|day|d)', msg)
        if day_match:
            duration = int(day_match.group(1))
        # Atau cari format "2D1N", "3D2N" dll
        elif re.search(r'(\d+)d\d*n', msg, re.IGNORECASE):
            match = re.search(r'(\d+)d\d*n', msg, re.IGNORECASE)
            duration = int(match.group(1))
        
        # Batasi durasi maksimal untuk fallback
        duration = min(duration, 10)
        
        try:
            # Gunakan Smart Itinerary Engine
            from ..models.itinerary_engine import get_itinerary_engine
            engine = get_itinerary_engine()
            
            # Generate itinerary menggunakan engine
            itinerary_data = engine.generate_smart_itinerary(
                duration_days=duration,
                budget_per_day=750000,
                interests=["alam", "budaya", "kuliner"],
                travel_style="balanced",
                vehicle="motorcycle",
                weather_condition="normal"
            )
            
            # Format response
            reply = f"📅 Rekomendasi Itinerary {duration} Hari di Dieng\n\n"
            reply += "Dibuat oleh Smart Itinerary Engine (Mode Offline)\n\n"
            
            total_cost = 0
            
            for day_idx, day_data in enumerate(itinerary_data['days'], 1):
                day_name = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"][(day_idx - 1) % 7]
                reply += f"Hari {day_idx} ({day_name}):\n"
                
                for activity in day_data['activities']:
                    time = activity.get('time', '08:00')
                    name = activity.get('name', 'Aktivitas')
                    location = activity.get('location', 'Dieng')
                    duration_text = activity.get('duration', '1-2 jam')
                    note = activity.get('note', '')
                    
                    # Icon berdasarkan tipe
                    icon = "🏔️"
                    if activity.get('type') == 'food':
                        icon = "🍽️"
                    elif activity.get('type') == 'hotel':
                        icon = "🏠"
                    elif activity.get('type') == 'transport':
                        icon = "🚗"
                    elif 'sunrise' in name.lower() or 'sikunir' in name.lower():
                        icon = "🌅"
                    elif 'candi' in name.lower():
                        icon = "🏛️"
                    elif 'kawah' in name.lower():
                        icon = "🌋"
                    elif 'telaga' in name.lower():
                        icon = "🏞️"
                    
                    # Extract price from note or name
                    price_match = re.search(r'Rp\s*([\d.,]+)', note + ' ' + name)
                    if price_match:
                        price_str = price_match.group(0)
                        price_value = int(re.sub(r'[^\d]', '', price_match.group(1)))
                        total_cost += price_value
                        reply += f"  {icon} {time} — {name} ({price_str})\n"
                    else:
                        reply += f"  {icon} {time} — {name}\n"
                    
                    if note and 'Rp' not in note:
                        reply += f"    💡 {note}\n"
                
                reply += "\n"
            
            if total_cost > 0:
                reply += f"💰 Estimasi Total Biaya Tiket: ~Rp {total_cost:,}\n"
                reply += "Belum termasuk transport, makan, dan penginapan\n\n"
            
            reply += "✨ Tips:\n"
            reply += "  • Datang pagi untuk menghindari kabut sore\n"
            reply += "  • Bawa jaket tebal (suhu bisa 5-10°C)\n"
            reply += "  • Siapkan uang cash (banyak tempat belum terima e-wallet)\n\n"
            reply += "💡 Untuk itinerary yang lebih personal dan adaptif cuaca, gunakan fitur Smart Itinerary di halaman utama!"
            
            return {"reply": reply}
            
        except Exception as e:
            logger.error(f"Error generating itinerary from engine: {e}")
            # Fallback ke response sederhana
            reply = f"""⚠️ Maaf, AI kami (Gemini) sedang sibuk dan sistem itinerary otomatis mengalami gangguan.

📅 Untuk itinerary {duration} hari yang detail dan adaptif cuaca, silakan:

1. 🎯 Gunakan fitur Smart Itinerary di halaman utama website
2. 🤖 Atau coba tanya lagi dalam beberapa saat agar AI Gemini bisa membantu

Referensi Singkat Destinasi Populer:
  • 🌅 Bukit Sikunir (Rp 15.000) - Sunrise terbaik
  • 🏛️ Candi Arjuna (Rp 15.000) - Heritage
  • 🌋 Kawah Sikidang (Rp 20.000) - Kawah aktif
  • 🏞️ Telaga Warna (Rp 15.000) - Danau eksotis
  • 🪨 Batu Ratapan Angin (Rp 10.000) - View point

Silakan gunakan fitur Smart Itinerary untuk rencana perjalanan lengkap! ✨"""
            return {"reply": reply}
    
    # ─── Intent: Solo Traveler / Keamanan ───
    if _fuzzy_match(msg, ["solo", "sendiri", "aman", "keamanan", "safety", "bahaya", "darurat", "tips"]):
        reply = "🛡️ Tips Keamanan Solo Traveler di Dieng\n\n"
        for i, tip in enumerate(SOLO_TRAVELER_TIPS, 1):
            reply += f"{i}. {tip}\n"
        reply += "\n📞 Nomor Darurat:\n  • Polsek Kejajar: 0286-3321110\n  • SAR Wonosobo: 0286-321100\n  • RS Setjonegoro: 0286-321006"
        return {"reply": reply}
    
    # ─── Intent: Destinasi ───
    if _fuzzy_match(msg, ["destinasi", "wisata", "tempat", "kawah", "candi", "telaga", "bukit", "sikunir", "sikidang"]):
        reply = "🏔️ Destinasi Wisata Dieng\n\n"
        for dest in DESTINATIONS:
            reply += f"{dest['name']} ({dest['type']})\n{dest['description']}\n💡 {dest['tips']}\n⏱️ Durasi: {dest['duration']}\n\n"
        return {"reply": reply}
    
    # ─── Intent: Penginapan ───
    if _fuzzy_match(msg, ["hotel", "penginapan", "homestay", "menginap", "tidur"]):
        reply = "🏠 Penginapan di Dieng\n\n"
        for acc in ACCOMMODATIONS:
            reply += f"  • {acc['name']} ({acc['type']}): {acc['price_range']} — ⭐ {acc['rating']}/5\n"
        reply += "\n💡 Saran: Pesan 1-2 hari sebelumnya, terutama saat weekend dan libur nasional."
        return {"reply": reply}
    
    # ─── Intent: Transportasi ───
    if _fuzzy_match(msg, ["transport", "bus", "ojek", "sewa", "kendaraan", "motor"]):
        reply = "🚗 Transportasi ke/di Dieng\n\n"
        for t in TRANSPORTATION:
            reply += f"  • {t['type']}: {t['price']} — {t['schedule']}\n"
        reply += "\n💡 Saran: Isi bensin penuh di Wonosobo karena SPBU di Dieng terbatas."
        return {"reply": reply}
    
    # ─── Intent: Perlengkapan ───
    if _fuzzy_match(msg, ["perlengkapan", "bawa", "persiapan", "siapkan", "jaket", "sepatu"]):
        gear = GEAR_RECOMMENDATIONS["umum"]
        reply = "🎒 Perlengkapan Wajib Wisata Dieng\n\n"
        reply += "Wajib bawa:\n"
        for item in gear["wajib"]:
            reply += f"  ✅ {item}\n"
        reply += "\nSaran tambahan:\n"
        for item in gear["saran"]:
            reply += f"  💡 {item}\n"
        reply += "\n🥶 Jika suhu < 8°C, tambahkan: syal, sarung tangan, topi kupluk, sleeping bag."
        return {"reply": reply}

    # ─── Intent: Sunrise ───
    if _fuzzy_match(msg, ["sunrise", "matahari terbit", "pagi", "sikunir", "angkruk"]):
        reply = "🌅 Rekomendasi Spot Sunrise Terbaik di Dieng:\n\n"
        reply += "1. Bukit Sikunir\n"
        reply += "   Pilihan terbaik jika Anda ingin/suka mendaki. Menawarkan Golden Sunrise yang luar biasa memukau dengan latar belakang gunung kembar.\n\n"
        reply += "2. Batu Angkruk\n"
        reply += "   Sangat cocok untuk yang tidak ingin mendaki karena bisa diakses langsung dari pinggir jalan. ⚠️ Catatan: parkiran di Batu Angkruk agak sempit."
        return {"reply": reply}
        
    # ─── Intent: Rute Yogyakarta ───
    if _fuzzy_match(msg, ["yogyakarta", "jogja", "jogjakarta"]):
        reply = "🚌 Panduan Perjalanan dari Yogyakarta ke Dieng:\n\n"
        reply += "• Travel Yogyakarta - Wonosobo: Mulai dari Rp 80.000\n"
        reply += "  (Biasanya melayani perjalanan sampai Wonosobo, kemudian Anda bisa menyambung bus ke Dieng)\n\n"
        reply += "• Opsi lainnya: Anda bisa menyewa mobil dari Jogja atau naik bus umum tujuan Magelang - Wonosobo.\n\n"
        reply += "Jarak tempuh dari Jogja ke Dieng adalah sekitar 3.5 - 4 jam perjalanan darat."
        return {"reply": reply}
    
    # ─── Intent: Sapaan ───
    if _fuzzy_match(msg, ["halo", "hai", "hi", "hey", "selamat", "assalamualaikum", "pagi", "siang", "sore", "malam"]):
        reply = """👋 Halo! Saya DITA (Dieng Intelligence Tourism Assistant) 🏔️

Saya asisten wisata cerdas yang siap membantu Anda menjelajahi Dataran Tinggi Dieng dengan aman dan nyaman!

Saya bisa membantu Anda dengan:
  • 🌤️ Informasi cuaca real-time dan peringatan
  • 🛡️ Rute aman dan peringatan jalur berbahaya
  • 💰 Biaya retribusi resmi (anti-pungli!)
  • 📅 Smart itinerary adaptif cuaca
  • 🏔️ Info destinasi dan tips solo traveler
  • 🎒 Rekomendasi perlengkapan

Silakan tanya apa saja tentang wisata Dieng! 😊"""
        return {"reply": reply}
    
    # ─── Default ───
    reply = """Terima kasih atas pertanyaannya! 😊

Saya DITA, asisten wisata cerdas untuk Dieng. Berikut yang bisa saya bantu:

  • 🌤️ Ketik "cuaca" untuk info cuaca terkini
  • 🗺️ Ketik "rute aman" untuk rekomendasi jalur
  • 💰 Ketik "retribusi" untuk biaya tiket resmi
  • 📅 Ketik "itinerary" untuk rencana perjalanan
  • 🛡️ Ketik "tips keamanan" untuk tips solo traveler
  • 🏔️ Ketik "destinasi" untuk daftar tempat wisata
  • 🏠 Ketik "penginapan" untuk info hotel/homestay

Silakan coba salah satu! 🙌"""
    return {"reply": reply}
