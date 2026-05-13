"""
==============================================================================
DITA Knowledge Base — Custom NLP Dataset
==============================================================================
Basis pengetahuan lokal yang digunakan oleh chatbot DITA untuk memberikan
respons akurat tanpa bergantung sepenuhnya pada LLM eksternal.

Data bersumber dari:
- Riset lapangan tim PJK-GM067 ke loket wisata Dieng
- Observasi langsung kondisi jalur dan medan
- Sumber resmi Dinas Pariwisata Wonosobo
- Wawancara warga lokal

Author: Ida Masruroh (AI Engineer) & Muhammad Sultan Baqa (Back-End)
==============================================================================
"""

# ─────────────────────────────────────────────
# 1. DATA RETRIBUSI RESMI (terverifikasi April 2026)
# ─────────────────────────────────────────────
RETRIBUSI_DATA = {
    "Kawah Sikidang": {"lokal": 20000, "asing": 50000, "parkir_motor": 5000, "parkir_mobil": 10000},
    "Kawah Candradimuka": {"lokal": 10000, "asing": 20000, "parkir_motor": 3000, "parkir_mobil": 5000},
    "Kawah Sileri": {"lokal": 15000, "asing": 30000, "parkir_motor": 5000, "parkir_mobil": 10000},
    "Kawah Nagasari": {"lokal": 10000, "asing": 20000, "parkir_motor": 3000, "parkir_mobil": 5000},
    "Candi Arjuna": {"lokal": 15000, "asing": 30000, "parkir_motor": 5000, "parkir_mobil": 10000},
    "Candi Gatotkaca": {"lokal": 10000, "asing": 20000, "parkir_motor": 3000, "parkir_mobil": 5000},
    "Candi Bima": {"lokal": 10000, "asing": 20000, "parkir_motor": 3000, "parkir_mobil": 5000},
    "Telaga Warna": {"lokal": 15000, "asing": 30000, "parkir_motor": 5000, "parkir_mobil": 10000},
    "Telaga Pengilon": {"lokal": 0, "asing": 0, "parkir_motor": 0, "parkir_mobil": 0},
    "Telaga Merdada": {"lokal": 5000, "asing": 10000, "parkir_motor": 2000, "parkir_mobil": 5000},
    "Telaga Dringo": {"lokal": 5000, "asing": 10000, "parkir_motor": 2000, "parkir_mobil": 5000},
    "Telaga Balekambang": {"lokal": 5000, "asing": 10000, "parkir_motor": 2000, "parkir_mobil": 5000},
    "Bukit Sikunir": {"lokal": 15000, "asing": 15000, "parkir_motor": 5000, "parkir_mobil": 10000},
    "Batu Ratapan Angin": {"lokal": 10000, "asing": 25000, "parkir_motor": 3000, "parkir_mobil": 5000},
    "Bukit Pangonan": {"lokal": 10000, "asing": 20000, "parkir_motor": 3000, "parkir_mobil": 5000},
    "Dieng Plateau Theater": {"lokal": 25000, "asing": 50000, "parkir_motor": 5000, "parkir_mobil": 10000},
    "Museum Kailasa": {"lokal": 10000, "asing": 20000, "parkir_motor": 3000, "parkir_mobil": 5000},
    "Tiket Terusan (Sikidang+Arjuna)": {"lokal": 30000, "asing": 75000, "parkir_motor": 5000, "parkir_mobil": 10000},
    "Sumur Jalatunda": {"lokal": 5000, "asing": 10000, "parkir_motor": 2000, "parkir_mobil": 5000},
    "Gua Semar": {"lokal": 5000, "asing": 10000, "parkir_motor": 2000, "parkir_mobil": 5000},
    "Goa Jaran": {"lokal": 5000, "asing": 10000, "parkir_motor": 2000, "parkir_mobil": 5000},
    "Air Terjun Sikarim": {"lokal": 5000, "asing": 10000, "parkir_motor": 2000, "parkir_mobil": 5000},
    "Camping Ground Sikunir": {"lokal": 25000, "asing": 40000, "parkir_motor": 5000, "parkir_mobil": 10000},
    "Padang Savana Dieng": {"lokal": 5000, "asing": 10000, "parkir_motor": 2000, "parkir_mobil": 5000},
    "Ladang Kentang Dieng": {"lokal": 5000, "asing": 10000, "parkir_motor": 2000, "parkir_mobil": 3000},
    "Gardu Pandang Tieng": {"lokal": 10000, "asing": 15000, "parkir_motor": 3000, "parkir_mobil": 5000},
}

# ─────────────────────────────────────────────
# 2. DATA RUTE DAN TITIK BAHAYA
# ─────────────────────────────────────────────
DANGER_ZONES = [
    {
        "name": "Tanjakan Sikarim",
        "gradient_degree": 45,
        "risk": "TINGGI",
        "description": "Tanjakan paling berbahaya di jalur Dieng. Kemiringan 45 derajat menyebabkan rem blong pada kendaraan yang tidak siap.",
        "advice": "HINDARI jika naik motor standar. Gunakan gear rendah (1-2). Pastikan rem cakram berfungsi baik. Jangan pernah pakai rem mendadak saat turun.",
        "alternative": "Gunakan jalur utama via Kejajar - Dieng Kulon",
        "coordinates": {"lat": -7.2150, "lng": 109.8950}
    },
    {
        "name": "Tanjakan Watu Angkruk (15%)",
        "gradient_degree": 35,
        "risk": "TINGGI",
        "description": "Tanjakan dengan kemiringan 15% yang sering membuat mesin motor mati, terutama untuk motor matic/125cc.",
        "advice": "Motor matic sebaiknya tidak melewati jalur ini. Mobil wajib gunakan gear rendah. Pastikan mesin dalam kondisi prima.",
        "alternative": "Lewat jalur alternatif Kejajar",
        "coordinates": {"lat": -7.2200, "lng": 109.8870}
    },
    {
        "name": "Jalur Gardu Pandang",
        "gradient_degree": 18,
        "risk": "SEDANG",
        "description": "Kabut tebal sering turun secara tiba-tiba di area ini, terutama pukul 15:00-17:00.",
        "advice": "Hindari melewati jalur ini sore hari. Pastikan lampu kendaraan menyala. Kurangi kecepatan hingga 20 km/jam saat kabut.",
        "alternative": "Jika kabut tebal, tunda perjalanan atau bermalam di homestay terdekat",
        "coordinates": {"lat": -7.2100, "lng": 109.9050}
    },
]

SAFE_ROUTES = {
    "motorcycle": {
        "recommended": "Wonosobo → Kejajar → Dieng Kulon → Destinasi",
        "distance": "26 km",
        "duration": "50 menit",
        "description": "Jalur utama yang paling aman untuk motor. Tanjakan moderat dan jalan beraspal baik.",
        "tips": ["Gunakan gear rendah saat menanjak", "Pastikan rem cakram berfungsi", "Bawa jas hujan", "Isi bensin penuh di Wonosobo"]
    },
    "car": {
        "recommended": "Wonosobo → Kejajar → Dieng Kulon → Destinasi",
        "distance": "26 km",
        "duration": "45 menit",
        "description": "Jalur utama aman untuk mobil. Jalan cukup lebar untuk 2 jalur.",
        "tips": ["Gunakan gear rendah saat turun", "Nyalakan lampu kabut", "Hati-hati tikungan tajam di Kejajar"]
    }
}

# ─────────────────────────────────────────────
# 3. DATA DESTINASI WISATA
# ─────────────────────────────────────────────
DESTINATIONS = [
    {
        "name": "Kawah Sikidang",
        "type": "Alam",
        "description": "Kawah vulkanik aktif dengan fumarola belerang. Salah satu kawah paling aktif di Dieng.",
        "tips": "Jaga jarak minimal 2 meter dari lubang kawah. Jangan sentuh air kawah. Waktu kunjungan ideal: pagi hari.",
        "duration": "45-60 menit",
        "coordinates": {"lat": -7.2125, "lng": 109.9064}
    },
    {
        "name": "Kawah Candradimuka",
        "type": "Alam",
        "description": "Kawah legendaris dalam cerita Mahabharata. Trek ringan dengan pemandangan mistis.",
        "tips": "Kawah tidak selalu aktif. Cocok dikombinasikan dengan kunjungan ke Candi Arjuna.",
        "duration": "30-45 menit",
        "coordinates": {"lat": -7.2042, "lng": 109.9125}
    },
    {
        "name": "Kawah Sileri",
        "type": "Alam",
        "description": "Kawah terbesar dan paling aktif di Dieng. Luapan lumpur panas pernah terjadi.",
        "tips": "WAJIB ikuti jalur resmi! Jangan mendekati bibir kawah. Hati-hati gas beracun.",
        "duration": "30-45 menit",
        "coordinates": {"lat": -7.1986, "lng": 109.9278}
    },
    {
        "name": "Kawah Nagasari",
        "type": "Alam",
        "description": "Kawah kecil dengan aktivitas vulkanik. Akses mudah dari Kawah Sileri.",
        "tips": "Bisa dikunjungi bersamaan dengan Kawah Sileri. Jaga jarak dari lubang aktif.",
        "duration": "20-30 menit",
        "coordinates": {"lat": -7.2011, "lng": 109.9205}
    },
    {
        "name": "Telaga Warna",
        "type": "Alam",
        "description": "Telaga dengan fenomena warna air yang berubah-ubah karena kandungan belerang dan mineral.",
        "tips": "Bawa kamera! Warna terbaik saat pagi cerah. Trek ringan ~30 menit mengelilingi telaga.",
        "duration": "60-90 menit",
        "coordinates": {"lat": -7.2167, "lng": 109.9150}
    },
    {
        "name": "Telaga Pengilon",
        "type": "Alam",
        "description": "Telaga jernih seperti cermin. Gratis akses via Telaga Warna.",
        "tips": "Spot foto terbaik saat pagi cerah. Air jernih memantulkan langit.",
        "duration": "30-45 menit",
        "coordinates": {"lat": -7.2175, "lng": 109.9167}
    },
    {
        "name": "Telaga Merdada",
        "type": "Alam",
        "description": "Telaga tenang di tengah pegunungan. Cocok untuk relaksasi.",
        "tips": "Suasana lebih sepi dari Telaga Warna. Cocok untuk ketenangan.",
        "duration": "30-45 menit",
        "coordinates": {"lat": -7.2189, "lng": 109.9178}
    },
    {
        "name": "Candi Arjuna",
        "type": "Budaya",
        "description": "Kompleks candi Hindu tertua di Jawa (abad ke-7). Terdiri dari 5 candi utama.",
        "tips": "Sewa guide lokal Rp50.000 untuk penjelasan sejarah lengkap. Buka pagi-sore.",
        "duration": "30-45 menit",
        "coordinates": {"lat": -7.2069, "lng": 109.9103}
    },
    {
        "name": "Candi Gatotkaca",
        "type": "Budaya",
        "description": "Candi Hindu dengan relief Gatotkaca. Lokasi dekat Candi Arjuna.",
        "tips": "Kunjungi bersamaan dengan Candi Arjuna. Perhatikan detail relief.",
        "duration": "20-30 menit",
        "coordinates": {"lat": -7.2097, "lng": 109.9089}
    },
    {
        "name": "Candi Bima",
        "type": "Budaya",
        "description": "Candi dengan arsitektur unik berbeda dari candi lain di Dieng.",
        "tips": "Arsitektur mirip candi India Selatan. Lokasi agak terpisah dari kompleks utama.",
        "duration": "20-30 menit",
        "coordinates": {"lat": -7.2153, "lng": 109.9142}
    },
    {
        "name": "Bukit Sikunir",
        "type": "Alam",
        "description": "Golden Sunrise terbaik di Jawa. Trek 30 menit dari parkiran ke puncak.",
        "tips": "Berangkat jam 03:30-04:00 subuh. Bawa jaket SANGAT tebal (suhu bisa 3-5°C). Senter/headlamp wajib. Sepatu hiking anti-slip.",
        "duration": "2-3 jam (termasuk trek)",
        "coordinates": {"lat": -7.2250, "lng": 109.9000}
    },
    {
        "name": "Batu Ratapan Angin",
        "type": "Alam",
        "description": "View point dengan panorama lembah dan pegunungan Dieng 360 derajat.",
        "tips": "Angin sangat kencang! Pegang topi dan barang berharga. Cocok untuk foto landscape.",
        "duration": "30-45 menit",
        "coordinates": {"lat": -7.2108, "lng": 109.9167}
    },
    {
        "name": "Bukit Pangonan",
        "type": "Alam",
        "description": "Alternatif sunrise selain Sikunir. Lebih sepi dan tenang.",
        "tips": "Cocok untuk yang tidak suka keramaian. View sunset juga bagus.",
        "duration": "1-2 jam",
        "coordinates": {"lat": -7.2267, "lng": 109.9022}
    },
    {
        "name": "Dieng Plateau Theater",
        "type": "Edukasi",
        "description": "Teater 4D dengan film sejarah dan geologi Dieng. Edukatif dan menarik.",
        "tips": "Durasi ~30 menit. Tempat berteduh yang bagus saat kabut atau hujan.",
        "duration": "30-45 menit",
        "coordinates": {"lat": -7.2083, "lng": 109.9056}
    },
    {
        "name": "Museum Kailasa",
        "type": "Edukasi",
        "description": "Museum dengan koleksi artefak dari candi-candi Dieng dan informasi geologi.",
        "tips": "Kunjungi sebelum ke candi untuk pemahaman sejarah yang lebih baik.",
        "duration": "30-45 menit",
        "coordinates": {"lat": -7.2075, "lng": 109.9058}
    },
    {
        "name": "Sumur Jalatunda",
        "type": "Alam",
        "description": "Sumur bersejarah dengan air jernih. Dipercaya memiliki khasiat.",
        "tips": "Situs spiritual. Hormati adat setempat saat berkunjung.",
        "duration": "15-20 menit",
        "coordinates": {"lat": -7.2119, "lng": 109.9094}
    },
    {
        "name": "Gua Semar",
        "type": "Alam",
        "description": "Gua alami dengan legenda pewayangan. Tempat meditasi dan spiritual.",
        "tips": "Bawa senter. Gua tidak terlalu dalam. Sering digunakan untuk meditasi.",
        "duration": "20-30 menit",
        "coordinates": {"lat": -7.2131, "lng": 109.9111}
    },
    {
        "name": "Camping Ground Sikunir",
        "type": "Rekreasi",
        "description": "Area camping dekat Bukit Sikunir. Pengalaman bermalam di dataran tinggi.",
        "tips": "Bawa sleeping bag tebal! Suhu bisa turun hingga 3°C. Toilet tersedia.",
        "duration": "Overnight",
        "coordinates": {"lat": -7.2239, "lng": 109.8994}
    },
    {
        "name": "Padang Savana Dieng",
        "type": "Alam",
        "description": "Hamparan padang rumput dengan pemandangan Gunung Sindoro dan Sumbing.",
        "tips": "Spot foto landscape terbaik. Datang pagi atau sore untuk cahaya bagus.",
        "duration": "30-60 menit",
        "coordinates": {"lat": -7.2275, "lng": 109.9011}
    },
    {
        "name": "Desa Wisata Sembungan",
        "type": "Budaya",
        "description": "Desa tertinggi di Pulau Jawa (2.300 mdpl). Kehidupan petani dataran tinggi.",
        "tips": "Mampir ke kedai kopi lokal. Suasana desa yang asri dan masyarakat ramah.",
        "duration": "1-2 jam",
        "coordinates": {"lat": -7.2233, "lng": 109.8969}
    },
    {
        "name": "Pasar Carica Dieng",
        "type": "Kuliner",
        "description": "Pasar oleh-oleh khas Dieng. Wajib beli carica dan keripik kentang.",
        "tips": "Harga bisa ditawar. Beli carica dalam sirup dan keripik kentang Dieng.",
        "duration": "30-45 menit",
        "coordinates": {"lat": -7.2067, "lng": 109.9108}
    },
]

# ─────────────────────────────────────────────
# 4. DATA AKOMODASI DAN TRANSPORTASI
# ─────────────────────────────────────────────
ACCOMMODATIONS = [
    {"name": "Homestay Dieng Kulon", "type": "Homestay", "price_range": "Rp 100.000 - 200.000/malam", "rating": 4.2},
    {"name": "Hotel Gunung Mas", "type": "Hotel", "price_range": "Rp 300.000 - 500.000/malam", "rating": 4.5},
    {"name": "Dieng Plateau Inn", "type": "Hotel", "price_range": "Rp 250.000 - 400.000/malam", "rating": 4.3},
    {"name": "Homestay Bu Yanti", "type": "Homestay", "price_range": "Rp 80.000 - 150.000/malam", "rating": 4.0},
]

TRANSPORTATION = [
    {"type": "Bus Wonosobo-Dieng", "price": "Rp 20.000", "schedule": "06:00 - 17:00 (setiap 30 menit)"},
    {"type": "Ojek motor", "price": "Rp 50.000 - 100.000 (tergantung tujuan)", "schedule": "Tersedia sepanjang hari"},
    {"type": "Sewa motor", "price": "Rp 80.000 - 120.000/hari", "schedule": "Tersedia di Wonosobo"},
    {"type": "Travel Jakarta-Wonosobo", "price": "Rp 150.000 - 250.000", "schedule": "Malam hari (berangkat 20:00)"},
]

# ─────────────────────────────────────────────
# 5. TIPS KEAMANAN SOLO TRAVELER
# ─────────────────────────────────────────────
SOLO_TRAVELER_TIPS = [
    "Selalu beritahu seseorang (teman/keluarga) tentang rencana perjalanan dan destinasi Anda.",
    "Simpan nomor darurat: Polsek Kejajar (0286-3321110), SAR Wonosobo (0286-321100), RS Setjonegoro (0286-321006).",
    "Jangan mendaki Sikunir sendirian saat subuh. Gabung dengan grup wisatawan lain di homestay.",
    "Bawa power bank karena sinyal HP bisa hilang di beberapa titik.",
    "Selalu minta karcis resmi saat membayar retribusi. Jika tidak ada karcis = pungli!",
    "Suhu malam bisa turun hingga 3°C. Bawa jaket tebal, syal, dan sleeping bag jika camping.",
    "Hindari berkendara saat kabut tebal (jarak pandang < 5 meter). Lebih baik bermalam.",
    "Bawa obat-obatan pribadi dan P3K dasar. Apotek terdekat ada di Wonosobo (30 menit).",
    "Gunakan alas kaki anti-slip untuk trek ke kawah dan bukit. Tanah bisa sangat licin saat hujan.",
    "Jangan makan/minum di dekat kawah aktif. Uap belerang berbahaya bagi kesehatan.",
]

# ─────────────────────────────────────────────
# 6. PERLENGKAPAN WAJIB PER KONDISI
# ─────────────────────────────────────────────
GEAR_RECOMMENDATIONS = {
    "dingin_ekstrem": {  # suhu < 8°C
        "wajib": ["Jaket tebal/windbreaker", "Syal/buff", "Sarung tangan", "Topi kupluk", "Kaos kaki tebal"],
        "saran": ["Sleeping bag (jika camping)", "Hand warmer", "Termos air panas"]
    },
    "hujan": {
        "wajib": ["Jas hujan", "Sepatu anti-slip", "Kantong plastik (untuk gadget)", "Payung lipat"],
        "saran": ["Baju ganti", "Handuk kecil", "Sandal cadangan"]
    },
    "sunrise_sikunir": {
        "wajib": ["Jaket SANGAT tebal", "Senter/headlamp", "Sepatu hiking", "Air mineral"],
        "saran": ["Tripod kamera", "Makanan ringan energi", "Kopi/teh hangat dalam termos"]
    },
    "umum": {
        "wajib": ["Jaket ringan", "Sepatu nyaman", "Air mineral 1.5L", "Sunscreen", "Obat pribadi"],
        "saran": ["Kamera", "Power bank", "Topi", "Snack"]
    }
}


def build_knowledge_context():
    """
    Membangun konteks pengetahuan lengkap yang akan disisipkan ke
    system prompt Gemini API agar DITA memiliki Custom Knowledge Base.
    """
    context = """
=== KNOWLEDGE BASE DITA (Data Terverifikasi Tim PJK-GM067) ===

## RETRIBUSI RESMI WISATA DIENG (April 2026):
"""
    for dest, prices in RETRIBUSI_DATA.items():
        context += f"- {dest}: Lokal Rp{prices['lokal']:,} | Asing Rp{prices['asing']:,}"
        if prices['parkir_motor'] > 0:
            context += f" | Parkir Motor Rp{prices['parkir_motor']:,} | Parkir Mobil Rp{prices['parkir_mobil']:,}"
        context += "\n"
    
    context += "\n## ZONA BAHAYA & RUTE AMAN:\n"
    for zone in DANGER_ZONES:
        context += f"- {zone['name']} (Kemiringan {zone['gradient_degree']}°, Risiko {zone['risk']}): {zone['description']} Saran: {zone['advice']}\n"
    
    context += "\n## RUTE AMAN:\n"
    for vehicle, route in SAFE_ROUTES.items():
        context += f"- {vehicle.upper()}: {route['recommended']} ({route['distance']}, {route['duration']}). {route['description']}\n"
    
    context += "\n## DESTINASI:\n"
    for dest in DESTINATIONS:
        context += f"- {dest['name']} ({dest['type']}): {dest['description']} Tips: {dest['tips']} Durasi: {dest['duration']}\n"
    
    context += "\n## AKOMODASI:\n"
    for acc in ACCOMMODATIONS:
        context += f"- {acc['name']} ({acc['type']}): {acc['price_range']}, Rating {acc['rating']}/5\n"
    
    context += "\n## TRANSPORTASI:\n"
    for t in TRANSPORTATION:
        context += f"- {t['type']}: {t['price']}, Jadwal: {t['schedule']}\n"
    
    context += "\n## TIPS KEAMANAN SOLO TRAVELER:\n"
    for i, tip in enumerate(SOLO_TRAVELER_TIPS, 1):
        context += f"{i}. {tip}\n"
    
    context += """
## ATURAN PENTING DITA:
- Selalu PERINGATKAN wisatawan tentang Tanjakan Sikarim dan Watu Angkruk jika mereka bertanya soal rute.
- Selalu sertakan harga RESMI dari knowledge base. Ingatkan untuk minta karcis resmi.
- Jika cuaca buruk, PRIORITASKAN keselamatan di atas itinerary.
- Gunakan emoji untuk membuat respons lebih friendly dan informatif.
- Jika tidak tahu jawaban pasti, akui dan sarankan untuk cek informasi ke Dinas Pariwisata Wonosobo.
"""
    return context
