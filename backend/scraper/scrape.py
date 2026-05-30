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
    Membaca dari file wisata_dieng.csv jika tersedia, atau mengembalikan data terstruktur.
    """
    print("\n" + "=" * 60)
    print("DITA Retribusi Scraper - Data Lapangan Tim")
    print("=" * 60)
    
    import csv
    csv_path = os.path.join(DATA_DIR, "wisata_dieng.csv")
    path = os.path.join(DATA_DIR, "dieng_retribusi.json")
    
    if os.path.exists(csv_path):
        print(f"  Reading from CSV: {csv_path}")
        # Estimasi koordinat untuk setiap destinasi
        COORDINATES = {
            "Tiket Kawasan": {"lat": -7.2069, "lon": 109.9100},
            "Pandangan Petama": {"lat": -7.2580, "lon": 109.9250},
            "Telaga Menjer": {"lat": -7.2600, "lon": 109.9200},
            "Bukit Cinta": {"lat": -7.2550, "lon": 109.9180},
            "Kahyangan Skyline": {"lat": -7.2570, "lon": 109.9220},
            "Bukit Saroja": {"lat": -7.2350, "lon": 109.8800},
            "Panama": {"lat": -7.2450, "lon": 109.8900},
            "Swiss Van Java": {"lat": -7.2500, "lon": 109.9100},
            "Curug Sikarim": {"lat": -7.2300, "lon": 109.8920},
            "Telaga Cebong": {"lat": -7.2240, "lon": 109.8990},
            "Bukit Sikunir": {"lat": -7.2250, "lon": 109.9000},
            "Gunung Bismo Via Sikunang": {"lat": -7.2400, "lon": 109.8700},
            "Kawah Sikidang Pintu A dan Komplek Candi Arjuna": {"lat": -7.2125, "lon": 109.9064},
            "Kawah Sikidang Pintu B dan Komplek Candi Arjuna": {"lat": -7.2130, "lon": 109.9070},
            "Candi Bima": {"lat": -7.2153, "lon": 109.9142},
            "Dieng Pelataue Theater": {"lat": -7.2083, "lon": 109.9056},
            "Batu Pandang Ratapan Angin": {"lat": -7.2108, "lon": 109.9167},
            "Telaga Warna": {"lat": -7.2167, "lon": 109.9150},
            "Kebun Teh Tambi": {"lat": -7.2700, "lon": 109.8500},
            "Taman Langit": {"lat": -7.2200, "lon": 109.8850},
            "Watu Angkruk": {"lat": -7.2200, "lon": 109.8870},
            "Bukit Sikapuk": {"lat": -7.2180, "lon": 109.8830},
            "Gunung Pakuwaja via Parikesit": {"lat": -7.2100, "lon": 109.8750},
            "Gunung Prau via Igirmranak": {"lat": -7.1900, "lon": 109.9200},
            "Gunung Prau via Patakbanteng": {"lat": -7.1850, "lon": 109.9150},
            "Gunung Prau via Kali Lembu": {"lat": -7.1920, "lon": 109.9100},
            "Gunung Paru via Dieng": {"lat": -7.1950, "lon": 109.9050},
            "Tuk Bimolukar": {"lat": -7.2119, "lon": 109.9094},
            "Bukit Scoter": {"lat": -7.2060, "lon": 109.9080},
            "Bukit Sipandu": {"lat": -7.2400, "lon": 109.9300},
            "D-Qiano Water Park": {"lat": -7.2050, "lon": 109.9020},
            "Banyu Alam Hot Spring": {"lat": -7.2030, "lon": 109.9000},
            "Pemandian Air Panas Bitingan": {"lat": -7.2090, "lon": 109.9120},
            "Museum Kailasa": {"lat": -7.2075, "lon": 109.9058},
            "Candi Gatot Kaca": {"lat": -7.2097, "lon": 109.9089},
            "Telaga Merdada": {"lat": -7.2189, "lon": 109.9178},
            "Telaga Sewiwi": {"lat": -7.2195, "lon": 109.9200},
            "Telaga Sedringo": {"lat": -7.2220, "lon": 109.9250},
            "Kawah Candradimuka": {"lat": -7.2042, "lon": 109.9125},
            "Kebun Teh Kertosari": {"lat": -7.2650, "lon": 109.8600},
            "Dieng Park": {"lat": -7.2160, "lon": 109.9140},
            "Kebun Teh Sikatok": {"lat": -7.2680, "lon": 109.8550},
            "Taman Rumah Peri": {"lat": -7.2040, "lon": 109.9040},
        }
        
        def categorize(name: str) -> str:
            n = name.lower()
            if "kawah" in n: return "Alam - Kawah"
            if "telaga" in n: return "Alam - Telaga"
            if any(k in n for k in ["gunung", "bukit", "pandangan", "pandang"]): return "Alam - Pendakian/Viewpoint"
            if any(k in n for k in ["candi", "museum", "theater", "pelataue"]): return "Budaya/Edukasi"
            if any(k in n for k in ["kebun teh", "panama"]): return "Agrowisata"
            if any(k in n for k in ["water park", "hot spring", "pemandian"]): return "Rekreasi Air"
            if "curug" in n: return "Alam - Air Terjun"
            if "taman" in n: return "Rekreasi"
            if "tiket kawasan" in n: return "Umum"
            return "Alam"

        retribusi = []
        with open(csv_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f, delimiter=";")
            for idx, row in enumerate(reader, start=1):
                name = row.get("Nama Tempat Wisata", "").strip()
                if not name:
                    continue
                wni = int(row.get("Tiket WNI (Rp.)", "0").strip() or 0)
                wna = int(row.get("Tiket WNA (Rp.)", "0").strip() or 0)
                parkir_r2 = int(row.get("Parkir Roda 2", "0").strip() or 0)
                parkir_r4 = int(row.get("Parkir Roda 4", "0").strip() or 0)
                keterangan = row.get("Keterangan", "").strip()
                
                coords = COORDINATES.get(name, {"lat": -7.2100, "lon": 109.9100})
                
                entry = {
                    "id": idx,
                    "name": name,
                    "category": categorize(name),
                    "retribusi_lokal": wni,
                    "retribusi_asing": wna,
                    "parking_motor": parkir_r2,
                    "parking_mobil": parkir_r4,
                    "open_hour": "07:00",
                    "close_hour": "17:00",
                    "coordinates": coords,
                    "notes": keterangan[:100] if len(keterangan) > 100 else keterangan,
                    "description": keterangan,
                }
                retribusi.append(entry)
    else:
        # Fallback to loading the JSON file directly if it exists, so we don't break/overwrite it with old hardcoded list
        if os.path.exists(path):
            print(f"  wisata_dieng.csv not found. Loading existing: {path}")
            with open(path, "r", encoding="utf-8") as f:
                retribusi = json.load(f)
        else:
            print("  Warning: No source data found for retribusi.")
            retribusi = []
            
    with open(path, "w", encoding="utf-8") as f:
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
