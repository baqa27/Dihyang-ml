"""
Script konversi Data-Wisata-Dieng.csv → dieng_retribusi.json
Menghasilkan format JSON yang sesuai dengan kebutuhan backend DITA.
"""
import csv
import json
import os

CSV_PATH = os.path.join(os.path.dirname(__file__), "wisata_dieng.csv")
JSON_PATH = os.path.join(os.path.dirname(__file__), "dieng_retribusi.json")

# Estimasi koordinat untuk setiap destinasi (berdasarkan data yang sudah ada + estimasi geografis)
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

# Kategorisasi otomatis berdasarkan nama
def categorize(name: str) -> str:
    n = name.lower()
    if any(k in n for k in ["kawah"]):
        return "Alam - Kawah"
    if any(k in n for k in ["telaga"]):
        return "Alam - Telaga"
    if any(k in n for k in ["gunung", "bukit", "pandangan", "pandang"]):
        return "Alam - Pendakian/Viewpoint"
    if any(k in n for k in ["candi", "museum", "theater", "pelataue"]):
        return "Budaya/Edukasi"
    if any(k in n for k in ["kebun teh", "panama"]):
        return "Agrowisata"
    if any(k in n for k in ["water park", "hot spring", "pemandian"]):
        return "Rekreasi Air"
    if any(k in n for k in ["curug"]):
        return "Alam - Air Terjun"
    if any(k in n for k in ["taman"]):
        return "Rekreasi"
    if any(k in n for k in ["tiket kawasan"]):
        return "Umum"
    return "Alam"


def main():
    results = []
    with open(CSV_PATH, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        for idx, row in enumerate(reader, start=1):
            name = row["Nama Tempat Wisata"].strip()
            if not name:
                continue
            
            wni = int(row["Tiket WNI (Rp.)"].strip() or 0)
            wna = int(row["Tiket WNA (Rp.)"].strip() or 0)
            parkir_r2 = int(row["Parkir Roda 2"].strip() or 0)
            parkir_r4 = int(row["Parkir Roda 4"].strip() or 0)
            keterangan = row["Keterangan"].strip()
            
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
            results.append(entry)
    
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"Berhasil mengkonversi {len(results)} destinasi ke {JSON_PATH}")


if __name__ == "__main__":
    main()
