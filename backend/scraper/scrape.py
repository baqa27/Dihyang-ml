"""
DITA Data Scraper - Dieng Historical Weather + Retribusi + Realtime
Mengambil data cuaca historis multi-tahun dari Open-Meteo Archive API
dengan variabel yang lebih lengkap untuk meningkatkan akurasi model ML.

Jalankan dari folder backend:
    python scraper/scrape.py
    python scraper/scrape.py --realtime  # untuk update data terbaru saja

Output:
    app/data/dieng_historical_2022.json
    app/data/dieng_historical_2023.json
    app/data/dieng_historical_2024.json
    app/data/dieng_historical_2025.json
    app/data/dieng_historical_2026.json
    app/data/dieng_historical_combined.json
    app/data/dieng_retribusi.json
    app/data/dieng_realtime.json (data 7 hari terakhir + forecast 7 hari)
"""

import requests
import json
import time
import os
import sys
from datetime import datetime, timedelta

# ── Konfigurasi ───────────────────────────────────────────────────────────────
LAT = -7.2056236
LON = 109.8731
ELEVATION = 2060.0
TIMEZONE = "Asia/Jakarta"

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'app', 'data')
os.makedirs(DATA_DIR, exist_ok=True)

# Variabel cuaca yang diambil - lebih lengkap dari sebelumnya (hanya temp+precip)
HOURLY_VARS = ",".join([
    "temperature_2m",           # Suhu udara 2m
    "precipitation",            # Presipitasi total
    "rain",                     # Hujan (tanpa salju)
    "snowfall",                 # Salju (jarang di Dieng tapi penting untuk embun upas)
    "windspeed_10m",            # Kecepatan angin
    "winddirection_10m",        # Arah angin
    "relativehumidity_2m",      # Kelembapan relatif
    "dewpoint_2m",              # Titik embun (penting untuk prediksi kabut)
    "apparent_temperature",     # Suhu terasa
    "cloudcover",               # Tutupan awan (%)
    "visibility",               # Jarak pandang (m)
    "weathercode",              # Kode cuaca WMO
    "surface_pressure",         # Tekanan permukaan
    "et0_fao_evapotranspiration", # Evapotranspirasi (indikator kekeringan)
])

YEARS = ["2022", "2023", "2024", "2025", "2026"]  # 2026 = data tahun berjalan (sampai kemarin)


# ── Fungsi Scraping ───────────────────────────────────────────────────────────

def scrape_year(year: str) -> dict | None:
    """Ambil data cuaca historis satu tahun dari Open-Meteo Archive API."""
    start = f"{year}-01-01"
    current_year = datetime.now().year
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    # Untuk tahun berjalan, ambil sampai kemarin (archive API tidak punya data hari ini)
    if int(year) == current_year:
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        end = yesterday
    # Untuk tahun masa depan, gunakan forecast API
    elif int(year) > current_year:
        print(f"  Fetching {year} (future year - using forecast)...", end=" ", flush=True)
        return scrape_forecast_year(year)
    else:
        end = f"{year}-12-31"

    url = (
        f"https://archive-api.open-meteo.com/v1/archive"
        f"?latitude={LAT}&longitude={LON}"
        f"&start_date={start}&end_date={end}"
        f"&hourly={HOURLY_VARS}"
        f"&timezone={TIMEZONE}"
    )

    print(f"  Fetching {year} ({start} to {end})...", end=" ", flush=True)
    try:
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        n = len(data.get("hourly", {}).get("time", []))
        print(f"OK - {n:,} records, {len(data['hourly'])-1} variables")
        return data
    except requests.exceptions.HTTPError as e:
        print(f"HTTP {e.response.status_code} - {e}")
        return None
    except Exception as e:
        print(f"ERROR - {e}")
        return None


def scrape_forecast_year(year: str) -> dict | None:
    """
    Untuk tahun masa depan, gunakan forecast API (max 16 hari).
    Ini hanya untuk demo/testing, data forecast tidak akurat untuk training model.
    """
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={LAT}&longitude={LON}"
        f"&hourly={HOURLY_VARS}"
        f"&forecast_days=16"
        f"&timezone={TIMEZONE}"
    )
    
    try:
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        n = len(data.get("hourly", {}).get("time", []))
        print(f"OK - {n:,} forecast records (16 days max)")
        return data
    except Exception as e:
        print(f"ERROR - {e}")
        return None


def combine_years(datasets: list[dict]) -> dict:
    """
    Gabungkan data dari beberapa tahun menjadi satu dataset.
    Semua key di 'hourly' di-concat.
    """
    if not datasets:
        return {}

    combined = {
        "latitude": datasets[0]["latitude"],
        "longitude": datasets[0]["longitude"],
        "elevation": datasets[0]["elevation"],
        "timezone": datasets[0]["timezone"],
        "timezone_abbreviation": datasets[0]["timezone_abbreviation"],
        "utc_offset_seconds": datasets[0]["utc_offset_seconds"],
        "hourly_units": datasets[0]["hourly_units"],
        "hourly": {},
        "years_included": [],
    }

    # Kumpulkan semua key dari hourly
    all_keys = set()
    for d in datasets:
        all_keys.update(d.get("hourly", {}).keys())

    for key in all_keys:
        combined["hourly"][key] = []
        for d in datasets:
            combined["hourly"][key].extend(d.get("hourly", {}).get(key, []))

    combined["years_included"] = [str(d.get("hourly", {}).get("time", ["?"])[0][:4]) for d in datasets]
    combined["total_records"] = len(combined["hourly"].get("time", []))

    return combined


def scrape_weather():
    """Scrape data cuaca historis 2022-2024 dan simpan per tahun + combined."""
    print("=" * 60)
    print("DITA Weather Scraper - Open-Meteo Archive API")
    print(f"Lokasi: Dieng Plateau ({LAT}, {LON}), {ELEVATION}m")
    print(f"Variabel: {len(HOURLY_VARS.split(','))} hourly variables")
    print(f"Tahun: {', '.join(YEARS)}")
    print("=" * 60)

    datasets = []
    for year in YEARS:
        data = scrape_year(year)
        if data:
            # Simpan per tahun
            path = os.path.join(DATA_DIR, f"dieng_historical_{year}.json")
            with open(path, "w") as f:
                json.dump(data, f, separators=(",", ":"))  # compact, hemat disk
            print(f"  Saved: {path}")
            datasets.append(data)
        else:
            print(f"  Skipping {year} (failed)")
        time.sleep(1)  # rate limit

    if len(datasets) > 1:
        print("\nCombining all years...", end=" ")
        combined = combine_years(datasets)
        path = os.path.join(DATA_DIR, "dieng_historical_combined.json")
        with open(path, "w") as f:
            json.dump(combined, f, separators=(",", ":"))
        print(f"OK - {combined['total_records']:,} total records")
        print(f"  Saved: {path}")
    elif datasets:
        # Hanya 1 tahun berhasil, pakai itu sebagai combined
        combined = datasets[0]
        path = os.path.join(DATA_DIR, "dieng_historical_combined.json")
        with open(path, "w") as f:
            json.dump(combined, f, separators=(",", ":"))
        print(f"  Saved combined (single year): {path}")

    return datasets


def scrape_realtime():
    """
    Ambil data realtime: 7 hari terakhir (historical) + 7 hari forecast.
    Untuk update model dan prediksi realtime.
    """
    print("\n" + "=" * 60)
    print("DITA Realtime Scraper - Recent + Forecast")
    print("=" * 60)
    
    # 7 hari terakhir
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    # Historical recent
    url_hist = (
        f"https://archive-api.open-meteo.com/v1/archive"
        f"?latitude={LAT}&longitude={LON}"
        f"&start_date={start_date.strftime('%Y-%m-%d')}"
        f"&end_date={end_date.strftime('%Y-%m-%d')}"
        f"&hourly={HOURLY_VARS}"
        f"&timezone={TIMEZONE}"
    )
    
    print(f"  Fetching recent 7 days...", end=" ", flush=True)
    try:
        resp = requests.get(url_hist, timeout=60)
        resp.raise_for_status()
        hist_data = resp.json()
        n_hist = len(hist_data.get("hourly", {}).get("time", []))
        print(f"OK - {n_hist} records")
    except Exception as e:
        print(f"ERROR - {e}")
        hist_data = None
    
    # Forecast 7 hari
    url_forecast = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={LAT}&longitude={LON}"
        f"&hourly={HOURLY_VARS}"
        f"&forecast_days=7"
        f"&timezone={TIMEZONE}"
    )
    
    print(f"  Fetching 7-day forecast...", end=" ", flush=True)
    try:
        resp = requests.get(url_forecast, timeout=60)
        resp.raise_for_status()
        forecast_data = resp.json()
        n_forecast = len(forecast_data.get("hourly", {}).get("time", []))
        print(f"OK - {n_forecast} records")
    except Exception as e:
        print(f"ERROR - {e}")
        forecast_data = None
    
    # Combine
    realtime = {
        "updated_at": datetime.now().isoformat(),
        "location": {"lat": LAT, "lon": LON, "elevation": ELEVATION},
        "recent_7days": hist_data,
        "forecast_7days": forecast_data,
    }
    
    path = os.path.join(DATA_DIR, "dieng_realtime.json")
    with open(path, "w") as f:
        json.dump(realtime, f, separators=(",", ":"))
    print(f"  Saved: {path}")
    return realtime


def scrape_retribusi():
    """
    Data retribusi resmi Dieng - hasil riset lapangan tim PJK-GM067.
    Divalidasi langsung ke loket wisata April 2026.
    UPDATE: Ditambahkan lebih banyak destinasi wisata Dieng.
    """
    print("\n" + "=" * 60)
    print("DITA Retribusi Scraper - Data Lapangan Tim")
    print("=" * 60)

    retribusi = [
        # Kawah & Fenomena Alam
        {
            "id": 1,
            "name": "Kawah Sikidang",
            "category": "Alam",
            "retribusi_lokal": 20000,
            "retribusi_asing": 50000,
            "parking_motor": 5000,
            "parking_mobil": 10000,
            "open_hour": "07:00",
            "close_hour": "17:00",
            "coordinates": {"lat": -7.2125, "lon": 109.9064},
            "notes": "Kawah aktif dengan fumarola. Tiket terusan tersedia bersama Candi Arjuna",
            "description": "Kawah vulkanik aktif dengan aktivitas fumarola dan belerang. Salah satu ikon wisata Dieng.",
        },
        {
            "id": 2,
            "name": "Kawah Candradimuka",
            "category": "Alam",
            "retribusi_lokal": 10000,
            "retribusi_asing": 20000,
            "parking_motor": 3000,
            "parking_mobil": 5000,
            "open_hour": "07:00",
            "close_hour": "17:00",
            "coordinates": {"lat": -7.2042, "lon": 109.9125},
            "notes": "Kawah legendaris dalam cerita Mahabharata",
            "description": "Kawah dengan legenda Mahabharata. Trek ringan dengan pemandangan mistis.",
        },
        {
            "id": 3,
            "name": "Kawah Sileri",
            "category": "Alam",
            "retribusi_lokal": 15000,
            "retribusi_asing": 30000,
            "parking_motor": 5000,
            "parking_mobil": 10000,
            "open_hour": "07:00",
            "close_hour": "17:00",
            "coordinates": {"lat": -7.1986, "lon": 109.9278},
            "notes": "Kawah terbesar di Dieng. Hati-hati gas beracun!",
            "description": "Kawah terbesar dan paling aktif di Dieng. Wajib ikuti jalur aman.",
        },
        
        # Candi & Budaya
        {
            "id": 4,
            "name": "Candi Arjuna",
            "category": "Budaya",
            "retribusi_lokal": 15000,
            "retribusi_asing": 30000,
            "parking_motor": 5000,
            "parking_mobil": 10000,
            "open_hour": "07:00",
            "close_hour": "17:00",
            "coordinates": {"lat": -7.2069, "lon": 109.9103},
            "notes": "Kompleks candi Hindu tertua di Jawa. Tiket terusan Sikidang+Arjuna Rp 30.000",
            "description": "Kompleks 5 candi Hindu dari abad ke-7. Arsitektur klasik Jawa Tengah.",
        },
        {
            "id": 5,
            "name": "Candi Gatotkaca",
            "category": "Budaya",
            "retribusi_lokal": 10000,
            "retribusi_asing": 20000,
            "parking_motor": 3000,
            "parking_mobil": 5000,
            "open_hour": "07:00",
            "close_hour": "17:00",
            "coordinates": {"lat": -7.2097, "lon": 109.9089},
            "notes": "Candi tunggal dengan relief indah",
            "description": "Candi Hindu dengan relief Gatotkaca. Lokasi dekat Candi Arjuna.",
        },
        {
            "id": 6,
            "name": "Candi Bima",
            "category": "Budaya",
            "retribusi_lokal": 10000,
            "retribusi_asing": 20000,
            "parking_motor": 3000,
            "parking_mobil": 5000,
            "open_hour": "07:00",
            "close_hour": "17:00",
            "coordinates": {"lat": -7.2153, "lon": 109.9142},
            "notes": "Candi unik dengan arsitektur berbeda",
            "description": "Candi dengan arsitektur unik berbeda dari candi lain di Dieng.",
        },
        
        # Telaga
        {
            "id": 7,
            "name": "Telaga Warna",
            "category": "Alam",
            "retribusi_lokal": 15000,
            "retribusi_asing": 30000,
            "parking_motor": 5000,
            "parking_mobil": 10000,
            "open_hour": "07:00",
            "close_hour": "17:00",
            "coordinates": {"lat": -7.2167, "lon": 109.9150},
            "notes": "Telaga dengan fenomena perubahan warna. Termasuk akses ke Telaga Pengilon",
            "description": "Telaga dengan fenomena warna air yang berubah-ubah. View point indah.",
        },
        {
            "id": 8,
            "name": "Telaga Pengilon",
            "category": "Alam",
            "retribusi_lokal": 0,
            "retribusi_asing": 0,
            "parking_motor": 0,
            "parking_mobil": 0,
            "open_hour": "07:00",
            "close_hour": "17:00",
            "coordinates": {"lat": -7.2175, "lon": 109.9167},
            "notes": "Gratis, akses via Telaga Warna. Air jernih seperti cermin",
            "description": "Telaga dengan air jernih seperti cermin. Spot foto favorit.",
        },
        {
            "id": 9,
            "name": "Telaga Merdada",
            "category": "Alam",
            "retribusi_lokal": 5000,
            "retribusi_asing": 10000,
            "parking_motor": 2000,
            "parking_mobil": 5000,
            "open_hour": "07:00",
            "close_hour": "17:00",
            "coordinates": {"lat": -7.2189, "lon": 109.9178},
            "notes": "Telaga tenang dengan pemandangan pegunungan",
            "description": "Telaga tenang di tengah pegunungan. Cocok untuk relaksasi.",
        },
        {
            "id": 10,
            "name": "Telaga Dringo",
            "category": "Alam",
            "retribusi_lokal": 5000,
            "retribusi_asing": 10000,
            "parking_motor": 2000,
            "parking_mobil": 5000,
            "open_hour": "07:00",
            "close_hour": "17:00",
            "coordinates": {"lat": -7.2203, "lon": 109.9156},
            "notes": "Telaga dengan legenda lokal",
            "description": "Telaga dengan cerita legenda masyarakat setempat.",
        },
        
        # View Point & Sunrise
        {
            "id": 11,
            "name": "Bukit Sikunir",
            "category": "Alam",
            "retribusi_lokal": 15000,
            "retribusi_asing": 15000,
            "parking_motor": 5000,
            "parking_mobil": 10000,
            "open_hour": "03:00",
            "close_hour": "12:00",
            "coordinates": {"lat": -7.2250, "lon": 109.9000},
            "notes": "Sunrise terbaik di Dieng. Buka dini hari. Harga sama lokal/asing. Trek 30 menit",
            "description": "Spot sunrise terbaik di Dieng. Golden sunrise di atas awan. Wajib datang subuh!",
        },
        {
            "id": 12,
            "name": "Batu Ratapan Angin",
            "category": "Alam",
            "retribusi_lokal": 10000,
            "retribusi_asing": 25000,
            "parking_motor": 3000,
            "parking_mobil": 5000,
            "open_hour": "07:00",
            "close_hour": "17:00",
            "coordinates": {"lat": -7.2108, "lon": 109.9167},
            "notes": "View point terbaik untuk foto panorama dataran Dieng",
            "description": "View point dengan panorama 360° dataran Dieng. Spot foto Instagram!",
        },
        {
            "id": 13,
            "name": "Bukit Pangonan",
            "category": "Alam",
            "retribusi_lokal": 10000,
            "retribusi_asing": 20000,
            "parking_motor": 3000,
            "parking_mobil": 5000,
            "open_hour": "06:00",
            "close_hour": "18:00",
            "coordinates": {"lat": -7.2267, "lon": 109.9022},
            "notes": "Alternatif sunrise selain Sikunir. Lebih sepi",
            "description": "Bukit dengan view sunrise dan sunset. Lebih tenang dari Sikunir.",
        },
        
        # Edukasi & Museum
        {
            "id": 14,
            "name": "Dieng Plateau Theater",
            "category": "Edukasi",
            "retribusi_lokal": 25000,
            "retribusi_asing": 50000,
            "parking_motor": 5000,
            "parking_mobil": 10000,
            "open_hour": "08:00",
            "close_hour": "16:00",
            "coordinates": {"lat": -7.2083, "lon": 109.9056},
            "notes": "Film 4D sejarah Dieng, durasi ~30 menit. Tempat berteduh saat kabut",
            "description": "Teater 4D dengan film sejarah dan geologi Dieng. Edukatif dan menarik.",
        },
        {
            "id": 15,
            "name": "Museum Kailasa",
            "category": "Edukasi",
            "retribusi_lokal": 10000,
            "retribusi_asing": 20000,
            "parking_motor": 3000,
            "parking_mobil": 5000,
            "open_hour": "08:00",
            "close_hour": "16:00",
            "coordinates": {"lat": -7.2075, "lon": 109.9058},
            "notes": "Museum arkeologi dan geologi Dieng. Koleksi artefak candi",
            "description": "Museum dengan koleksi artefak dari candi-candi Dieng dan informasi geologi.",
        },
        
        # Paket Wisata
        {
            "id": 16,
            "name": "Tiket Terusan (Sikidang + Arjuna)",
            "category": "Paket",
            "retribusi_lokal": 30000,
            "retribusi_asing": 75000,
            "parking_motor": 5000,
            "parking_mobil": 10000,
            "open_hour": "07:00",
            "close_hour": "17:00",
            "coordinates": {"lat": -7.2069, "lon": 109.9103},
            "notes": "Lebih hemat Rp 5.000 dibanding beli terpisah",
            "description": "Paket hemat untuk mengunjungi 2 destinasi utama Dieng.",
        },
        
        # Wisata Alam Lainnya
        {
            "id": 17,
            "name": "Sumur Jalatunda",
            "category": "Alam",
            "retribusi_lokal": 5000,
            "retribusi_asing": 10000,
            "parking_motor": 2000,
            "parking_mobil": 5000,
            "open_hour": "07:00",
            "close_hour": "17:00",
            "coordinates": {"lat": -7.2119, "lon": 109.9094},
            "notes": "Sumur kuno dengan air jernih",
            "description": "Sumur bersejarah dengan air jernih. Dipercaya memiliki khasiat.",
        },
        {
            "id": 18,
            "name": "Gua Semar",
            "category": "Alam",
            "retribusi_lokal": 5000,
            "retribusi_asing": 10000,
            "parking_motor": 2000,
            "parking_mobil": 5000,
            "open_hour": "07:00",
            "close_hour": "17:00",
            "coordinates": {"lat": -7.2131, "lon": 109.9111},
            "notes": "Gua dengan legenda Semar. Spot meditasi",
            "description": "Gua alami dengan legenda pewayangan. Tempat meditasi dan spiritual.",
        },
        {
            "id": 19,
            "name": "Bukit Sidengkeng",
            "category": "Alam",
            "retribusi_lokal": 10000,
            "retribusi_asing": 20000,
            "parking_motor": 3000,
            "parking_mobil": 5000,
            "open_hour": "06:00",
            "close_hour": "18:00",
            "coordinates": {"lat": -7.2289, "lon": 109.8978},
            "notes": "Bukit dengan view telaga dan pegunungan",
            "description": "Bukit dengan pemandangan telaga-telaga Dieng dari ketinggian.",
        },
        {
            "id": 20,
            "name": "Air Terjun Sikarim",
            "category": "Alam",
            "retribusi_lokal": 5000,
            "retribusi_asing": 10000,
            "parking_motor": 2000,
            "parking_mobil": 5000,
            "open_hour": "07:00",
            "close_hour": "17:00",
            "coordinates": {"lat": -7.2342, "lon": 109.8956},
            "notes": "Air terjun kecil di jalur Sikarim. Akses via trek",
            "description": "Air terjun kecil dengan trek menantang. Cocok untuk petualangan.",
        },
        
        # Destinasi Tambahan — diperluas Mei 2026
        {
            "id": 21,
            "name": "Kawah Nagasari",
            "category": "Alam",
            "retribusi_lokal": 10000,
            "retribusi_asing": 20000,
            "parking_motor": 3000,
            "parking_mobil": 5000,
            "open_hour": "07:00",
            "close_hour": "17:00",
            "coordinates": {"lat": -7.2011, "lon": 109.9205},
            "notes": "Kawah kecil yang masih aktif, dekat Kawah Sileri",
            "description": "Kawah kecil dengan aktivitas vulkanik. Akses mudah dari Kawah Sileri.",
        },
        {
            "id": 22,
            "name": "Gardu Pandang Tieng",
            "category": "Alam",
            "retribusi_lokal": 10000,
            "retribusi_asing": 15000,
            "parking_motor": 3000,
            "parking_mobil": 5000,
            "open_hour": "06:00",
            "close_hour": "18:00",
            "coordinates": {"lat": -7.2100, "lon": 109.9050},
            "notes": "Gardu pandang dengan pemandangan lembah Tieng. Sering berkabut sore hari",
            "description": "View point dengan panorama lembah Tieng dan pegunungan sekitar Dieng.",
        },
        {
            "id": 23,
            "name": "Goa Jaran",
            "category": "Alam",
            "retribusi_lokal": 5000,
            "retribusi_asing": 10000,
            "parking_motor": 2000,
            "parking_mobil": 5000,
            "open_hour": "07:00",
            "close_hour": "16:00",
            "coordinates": {"lat": -7.2145, "lon": 109.9081},
            "notes": "Gua kecil bersejarah. Akses dari kawasan Candi Arjuna",
            "description": "Gua alami di kawasan candi. Situs arkeologi dengan legenda kuda mistis.",
        },
        {
            "id": 24,
            "name": "Embung Kali Semar",
            "category": "Alam",
            "retribusi_lokal": 5000,
            "retribusi_asing": 10000,
            "parking_motor": 2000,
            "parking_mobil": 3000,
            "open_hour": "06:00",
            "close_hour": "17:00",
            "coordinates": {"lat": -7.2156, "lon": 109.9044},
            "notes": "Danau buatan kecil dengan pemandangan tenang",
            "description": "Danau kecil buatan yang tenang. Spot foto dengan latar pegunungan.",
        },
        {
            "id": 25,
            "name": "Ladang Kentang Dieng",
            "category": "Agrowisata",
            "retribusi_lokal": 5000,
            "retribusi_asing": 10000,
            "parking_motor": 2000,
            "parking_mobil": 3000,
            "open_hour": "06:00",
            "close_hour": "17:00",
            "coordinates": {"lat": -7.2194, "lon": 109.9033},
            "notes": "Wisata edukasi agrikultur. Bisa petik kentang langsung",
            "description": "Ladang kentang khas Dieng. Wisata edukasi pertanian dataran tinggi.",
        },
        {
            "id": 26,
            "name": "Telaga Balekambang",
            "category": "Alam",
            "retribusi_lokal": 5000,
            "retribusi_asing": 10000,
            "parking_motor": 2000,
            "parking_mobil": 5000,
            "open_hour": "07:00",
            "close_hour": "17:00",
            "coordinates": {"lat": -7.2211, "lon": 109.9189},
            "notes": "Telaga kecil yang tenang. Jarang dikunjungi wisatawan",
            "description": "Telaga tersembunyi di kawasan Dieng. Suasana alami dan sepi.",
        },
        {
            "id": 27,
            "name": "Batu Pandang Ratapan Angin",
            "category": "Alam",
            "retribusi_lokal": 0,
            "retribusi_asing": 0,
            "parking_motor": 0,
            "parking_mobil": 0,
            "open_hour": "00:00",
            "close_hour": "23:59",
            "coordinates": {"lat": -7.2115, "lon": 109.9171},
            "notes": "Spot foto gratis. View sunrise dan sunset",
            "description": "Batu besar untuk view point. Gratis akses, lokasi dekat Batu Ratapan Angin.",
        },
        {
            "id": 28,
            "name": "Pasar Carica Dieng",
            "category": "Kuliner",
            "retribusi_lokal": 0,
            "retribusi_asing": 0,
            "parking_motor": 0,
            "parking_mobil": 0,
            "open_hour": "06:00",
            "close_hour": "18:00",
            "coordinates": {"lat": -7.2067, "lon": 109.9108},
            "notes": "Pusat oleh-oleh carica, keripik kentang, dan purwaceng",
            "description": "Pasar oleh-oleh khas Dieng. Wajib beli carica dan keripik kentang Dieng.",
        },
        {
            "id": 29,
            "name": "Jalur Setapak Kawah Sileri",
            "category": "Alam",
            "retribusi_lokal": 10000,
            "retribusi_asing": 20000,
            "parking_motor": 3000,
            "parking_mobil": 5000,
            "open_hour": "07:00",
            "close_hour": "16:00",
            "coordinates": {"lat": -7.1992, "lon": 109.9268},
            "notes": "Trek pendek menuju Kawah Sileri. WAJIB ikuti jalur resmi",
            "description": "Jalur trekking menuju Kawah Sileri. Pemandangan vulkanik spektakuler.",
        },
        {
            "id": 30,
            "name": "Camping Ground Sikunir",
            "category": "Rekreasi",
            "retribusi_lokal": 25000,
            "retribusi_asing": 40000,
            "parking_motor": 5000,
            "parking_mobil": 10000,
            "open_hour": "00:00",
            "close_hour": "23:59",
            "coordinates": {"lat": -7.2239, "lon": 109.8994},
            "notes": "Area camping di kaki Bukit Sikunir. Toilet tersedia. Bawa sleeping bag tebal!",
            "description": "Area camping dekat Bukit Sikunir. Pengalaman bermalam di dataran tinggi Dieng.",
        },
        {
            "id": 31,
            "name": "Padang Savana Dieng",
            "category": "Alam",
            "retribusi_lokal": 5000,
            "retribusi_asing": 10000,
            "parking_motor": 2000,
            "parking_mobil": 5000,
            "open_hour": "06:00",
            "close_hour": "18:00",
            "coordinates": {"lat": -7.2275, "lon": 109.9011},
            "notes": "Padang rumput luas dengan view Gunung Sindoro-Sumbing",
            "description": "Hamparan padang rumput dengan pemandangan Gunung Sindoro dan Sumbing.",
        },
        {
            "id": 32,
            "name": "Desa Wisata Sembungan",
            "category": "Budaya",
            "retribusi_lokal": 0,
            "retribusi_asing": 0,
            "parking_motor": 0,
            "parking_mobil": 0,
            "open_hour": "00:00",
            "close_hour": "23:59",
            "coordinates": {"lat": -7.2233, "lon": 109.8969},
            "notes": "Desa tertinggi di Pulau Jawa. Suasana asri dan udara segar",
            "description": "Desa tertinggi di Pulau Jawa (2.300 mdpl). Kehidupan masyarakat petani dataran tinggi.",
        },
    ]

    path = os.path.join(DATA_DIR, "dieng_retribusi.json")
    with open(path, "w") as f:
        json.dump(retribusi, f, indent=2, ensure_ascii=False)
    print(f"  {len(retribusi)} destinasi disimpan: {path}")
    return retribusi


def scrape_realtime_current():
    """
    Scrape data cuaca realtime terkini untuk monitoring live.
    Data disimpan terpisah untuk keperluan realtime monitoring.
    """
    print("\n" + "=" * 60)
    print("DITA Realtime Weather Scraper")
    print("=" * 60)
    
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={LAT}&longitude={LON}"
        f"&current=temperature_2m,precipitation,relative_humidity_2m,"
        f"apparent_temperature,wind_speed_10m,wind_direction_10m,"
        f"surface_pressure,visibility,dew_point_2m,cloud_cover,weather_code"
        f"&hourly=temperature_2m,precipitation,relative_humidity_2m"
        f"&timezone={TIMEZONE}"
        f"&forecast_days=1"
    )
    
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        
        # Tambahkan timestamp
        import datetime
        data["scraped_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        path = os.path.join(DATA_DIR, "dieng_realtime_current.json")
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        
        print(f"  Realtime data saved: {path}")
        print(f"  Temperature: {data['current']['temperature_2m']}°C")
        print(f"  Humidity: {data['current']['relative_humidity_2m']}%")
        print(f"  Visibility: {data['current']['visibility']/1000:.1f} km")
        
        return data
    except Exception as e:
        print(f"  ERROR: {e}")
        return None


def scrape_latest_historical():
    """
    Scrape data historis terbaru (30 hari terakhir) untuk update model.
    Digunakan untuk incremental training tanpa perlu scrape ulang semua tahun.
    """
    print("\n" + "=" * 60)
    print("DITA Latest Historical Scraper (30 hari terakhir)")
    print("=" * 60)
    
    import datetime
    # Gunakan tanggal kemarin sebagai end date (archive API tidak punya data hari ini)
    end = datetime.date.today() - datetime.timedelta(days=1)
    start = end - datetime.timedelta(days=30)
    
    url = (
        f"https://archive-api.open-meteo.com/v1/archive"
        f"?latitude={LAT}&longitude={LON}"
        f"&start_date={start}&end_date={end}"
        f"&hourly={HOURLY_VARS}"
        f"&timezone={TIMEZONE}"
    )
    
    print(f"  Fetching {start} to {end}...", end=" ", flush=True)
    try:
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        n = len(data.get("hourly", {}).get("time", []))
        print(f"OK - {n:,} records")
        
        path = os.path.join(DATA_DIR, "dieng_historical_latest_30d.json")
        with open(path, "w") as f:
            json.dump(data, f, separators=(",", ":"))
        print(f"  Saved: {path}")
        
        return data
    except Exception as e:
        print(f"ERROR - {e}")
        return None


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Argumen opsional: --weather-only, --retribusi-only, --realtime, --latest
    args = sys.argv[1:]
    
    # Mode realtime: hanya scrape data terkini
    if "--realtime" in args:
        scrape_realtime_current()
        sys.exit(0)
    
    # Mode latest: scrape 30 hari terakhir untuk update model
    if "--latest" in args:
        scrape_latest_historical()
        sys.exit(0)
    
    # Mode normal: scrape full historical
    run_weather = "--retribusi-only" not in args
    run_retribusi = "--weather-only" not in args

    if run_weather:
        datasets = scrape_weather()
        print(f"\nWeather scraping selesai: {len(datasets)}/{len(YEARS)} tahun berhasil")

    if run_retribusi:
        retribusi = scrape_retribusi()

    print("\nScraping selesai. Jalankan training untuk upgrade model:")
    print("  python -m app.models.train_weather_model")
    print("  python -m app.models.train_route_model")
    print("\nUntuk realtime monitoring:")
    print("  python scraper/scrape.py --realtime")
    print("  python scraper/scrape.py --latest")
