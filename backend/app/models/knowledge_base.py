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
    # === Data dari CSV asli (riset lapangan tim PJK-GM067) ===
    "Tiket Kawasan": {"lokal": 15000, "asing": 50000, "parkir_motor": 0, "parkir_mobil": 0},
    "Pandangan Pertama": {"lokal": 10000, "asing": 10000, "parkir_motor": 2000, "parkir_mobil": 5000},
    "Telaga Menjer": {"lokal": 5000, "asing": 15000, "parkir_motor": 2000, "parkir_mobil": 5000},
    "Bukit Cinta": {"lokal": 15000, "asing": 15000, "parkir_motor": 5000, "parkir_mobil": 10000},
    "Kahyangan Skyline": {"lokal": 20000, "asing": 20000, "parkir_motor": 2000, "parkir_mobil": 5000},
    "Bukit Saroja": {"lokal": 25000, "asing": 25000, "parkir_motor": 10000, "parkir_mobil": 20000},
    "Panama (Kebun Teh)": {"lokal": 10000, "asing": 10000, "parkir_motor": 3000, "parkir_mobil": 5000},
    "Swiss Van Java": {"lokal": 10000, "asing": 10000, "parkir_motor": 0, "parkir_mobil": 0},
    "Curug Sikarim": {"lokal": 15000, "asing": 15000, "parkir_motor": 5000, "parkir_mobil": 10000},
    "Telaga Cebong": {"lokal": 0, "asing": 0, "parkir_motor": 5000, "parkir_mobil": 15000},
    "Bukit Sikunir": {"lokal": 15000, "asing": 30000, "parkir_motor": 5000, "parkir_mobil": 15000},
    "Gunung Bismo Via Sikunang": {"lokal": 35000, "asing": 35000, "parkir_motor": 10000, "parkir_mobil": 20000},
    "Kawah Sikidang + Candi Arjuna (Pintu A)": {"lokal": 35000, "asing": 50000, "parkir_motor": 5000, "parkir_mobil": 10000},
    "Kawah Sikidang + Candi Arjuna (Pintu B)": {"lokal": 35000, "asing": 50000, "parkir_motor": 2000, "parkir_mobil": 10000},
    "Candi Bima": {"lokal": 0, "asing": 0, "parkir_motor": 2000, "parkir_mobil": 5000},
    "Dieng Plateau Theater": {"lokal": 10000, "asing": 15000, "parkir_motor": 2000, "parkir_mobil": 5000},
    "Batu Pandang Ratapan Angin": {"lokal": 15000, "asing": 20000, "parkir_motor": 2000, "parkir_mobil": 5000},
    "Telaga Warna": {"lokal": 27000, "asing": 60000, "parkir_motor": 5000, "parkir_mobil": 10000},
    "Kebun Teh Tambi": {"lokal": 10000, "asing": 10000, "parkir_motor": 2000, "parkir_mobil": 7000},
    "Taman Langit": {"lokal": 15000, "asing": 15000, "parkir_motor": 5000, "parkir_mobil": 10000},
    "Watu Angkruk": {"lokal": 15000, "asing": 15000, "parkir_motor": 3000, "parkir_mobil": 7000},
    "Bukit Sikapuk": {"lokal": 15000, "asing": 15000, "parkir_motor": 3000, "parkir_mobil": 7000},
    "Gunung Pakuwaja via Parikesit": {"lokal": 30000, "asing": 30000, "parkir_motor": 10000, "parkir_mobil": 25000},
    "Gunung Prau via Igirmranak": {"lokal": 35000, "asing": 30000, "parkir_motor": 10000, "parkir_mobil": 25000},
    "Gunung Prau via Patakbanteng": {"lokal": 40000, "asing": 40000, "parkir_motor": 10000, "parkir_mobil": 20000},
    "Gunung Prau via Kali Lembu": {"lokal": 35000, "asing": 35000, "parkir_motor": 10000, "parkir_mobil": 25000},
    "Gunung Prau via Dieng": {"lokal": 30000, "asing": 30000, "parkir_motor": 10000, "parkir_mobil": 25000},
    "Tuk Bimolukar": {"lokal": 5000, "asing": 5000, "parkir_motor": 2000, "parkir_mobil": 2000},
    "Bukit Scoter": {"lokal": 15000, "asing": 15000, "parkir_motor": 2000, "parkir_mobil": 5000},
    "Bukit Sipandu": {"lokal": 15000, "asing": 15000, "parkir_motor": 5000, "parkir_mobil": 15000},
    "D-Qiano Water Park": {"lokal": 15000, "asing": 30000, "parkir_motor": 2000, "parkir_mobil": 5000},
    "Banyu Alam Hot Spring": {"lokal": 15000, "asing": 15000, "parkir_motor": 3000, "parkir_mobil": 5000},
    "Pemandian Air Panas Bitingan": {"lokal": 5000, "asing": 5000, "parkir_motor": 2000, "parkir_mobil": 0},
    "Museum Kailasa": {"lokal": 5000, "asing": 30000, "parkir_motor": 2000, "parkir_mobil": 5000},
    "Candi Gatot Kaca": {"lokal": 0, "asing": 0, "parkir_motor": 2000, "parkir_mobil": 5000},
    "Telaga Merdada": {"lokal": 5000, "asing": 5000, "parkir_motor": 2000, "parkir_mobil": 5000},
    "Telaga Sewiwi": {"lokal": 0, "asing": 0, "parkir_motor": 2000, "parkir_mobil": 5000},
    "Telaga Sedringo": {"lokal": 10000, "asing": 15000, "parkir_motor": 3000, "parkir_mobil": 5000},
    "Kawah Candradimuka": {"lokal": 15000, "asing": 15000, "parkir_motor": 2000, "parkir_mobil": 7000},
    "Kebun Teh Kertosari": {"lokal": 7000, "asing": 7000, "parkir_motor": 5000, "parkir_mobil": 10000},
    "Dieng Park": {"lokal": 15000, "asing": 60000, "parkir_motor": 5000, "parkir_mobil": 10000},
    "Kebun Teh Sikatok": {"lokal": 10000, "asing": 10000, "parkir_motor": 2000, "parkir_mobil": 5000},
    "Taman Rumah Peri": {"lokal": 10000, "asing": 10000, "parkir_motor": 2000, "parkir_mobil": 5000},
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
# 3. DATA DESTINASI WISATA (dari CSV asli + data existing)
# ─────────────────────────────────────────────
DESTINATIONS = [
    # === Dari CSV riset lapangan ===
    {"name": "Pandangan Pertama", "type": "Alam", "description": "Menawarkan sisi lain untuk menikmati keindahan lanskap Telaga Menjer dari atas. Area ini juga menyediakan lahan camping dan rekreasi luar ruang.", "tips": "Cocok untuk camping dan menikmati panorama Telaga Menjer.", "duration": "30-60 menit", "coordinates": {"lat": -7.2580, "lng": 109.9250}},
    {"name": "Telaga Menjer", "type": "Alam", "description": "Danau vulkanik terluas di area Garung. Pengunjung bisa menyewa perahu kayu Rp 20.000 atau berfoto dengan latar pegunungan.", "tips": "Sewa perahu Rp 20.000. Datang pagi untuk cahaya terbaik.", "duration": "45-60 menit", "coordinates": {"lat": -7.2600, "lng": 109.9200}},
    {"name": "Bukit Cinta", "type": "Alam", "description": "Spot rekreasi dan berfoto dengan sudut pandang dari ketinggian yang menghadap langsung ke Telaga Menjer.", "tips": "Spot foto populer. Bawa kamera!", "duration": "30-45 menit", "coordinates": {"lat": -7.2550, "lng": 109.9180}},
    {"name": "Kahyangan Skyline", "type": "Rekreasi", "description": "Destinasi modern bernuansa outdoor. Memiliki ikon jembatan kaca dan jaring gantung sebagai spot foto.", "tips": "Hati-hati di jembatan kaca. Spot foto Instagram terbaik.", "duration": "45-60 menit", "coordinates": {"lat": -7.2570, "lng": 109.9220}},
    {"name": "Bukit Saroja", "type": "Alam", "description": "Wisata alam via Desa Tieng. Trek relatif mudah, cocok untuk hiking santai. Lokasi terbaik untuk menikmati sunrise.", "tips": "Berangkat subuh untuk sunrise. Trek mudah cocok pemula.", "duration": "2-3 jam", "coordinates": {"lat": -7.2350, "lng": 109.8800}},
    {"name": "Panama (Kebun Teh)", "type": "Agrowisata", "description": "Kebun Teh Panama dengan fasilitas boardwalk di tengah hamparan kebun teh untuk pejalan kaki dan spot foto.", "tips": "Nikmati boardwalk di tengah kebun teh. Cocok untuk foto.", "duration": "30-60 menit", "coordinates": {"lat": -7.2450, "lng": 109.8900}},
    {"name": "Swiss Van Java", "type": "Alam", "description": "Area viewpoint dengan lanskap pegunungan hijau yang sering disandingkan dengan keindahan pedesaan Swiss.", "tips": "Spot foto landscape terbaik. Gratis parkir.", "duration": "20-30 menit", "coordinates": {"lat": -7.2500, "lng": 109.9100}},
    {"name": "Curug Sikarim", "type": "Alam", "description": "Air terjun eksotis dengan debit air deras. Akses jalannya menanjak tajam dan cukup ekstrem.", "tips": "Pastikan kendaraan prima! Akses jalan menanjak tajam dan ekstrem.", "duration": "45-60 menit", "coordinates": {"lat": -7.2300, "lng": 109.8920}},
    {"name": "Telaga Cebong", "type": "Alam", "description": "Titik kumpul utama dan camping ground bagi wisatawan yang bersiap mendaki Bukit Sikunir saat subuh.", "tips": "Base camp Sikunir. Gratis tiket masuk, bayar parkir saja.", "duration": "30 menit", "coordinates": {"lat": -7.2240, "lng": 109.8990}},
    {"name": "Bukit Sikunir", "type": "Alam", "description": "Destinasi terpopuler untuk berburu Golden Sunrise. Jalur pendakiannya berupa anak tangga, memakan waktu 30-45 menit.", "tips": "Berangkat 03:30-04:00 subuh. Jaket SANGAT tebal wajib (3-5°C). Headlamp wajib.", "duration": "2-3 jam", "coordinates": {"lat": -7.2250, "lng": 109.9000}},
    {"name": "Kawah Sikidang + Candi Arjuna", "type": "Alam/Budaya", "description": "Tiket bundling untuk dua ikon wisata Dieng. Pintu A terintegrasi dengan kios oleh-oleh, Pintu B lebih dekat.", "tips": "Pintu B lebih cocok untuk lansia. Jaga jarak 2m dari kawah.", "duration": "60-90 menit", "coordinates": {"lat": -7.2125, "lng": 109.9064}},
    {"name": "Candi Bima", "type": "Budaya", "description": "Candi dengan corak arsitektur khas India Utara. Berlokasi tepat di pinggir jalan utama. Gratis tanpa tiket.", "tips": "Gratis! Arsitektur unik berbeda dari candi Dieng lainnya.", "duration": "15-20 menit", "coordinates": {"lat": -7.2153, "lng": 109.9142}},
    {"name": "Dieng Plateau Theater", "type": "Edukasi", "description": "Teater bioskop mini yang memutar film dokumenter tentang sejarah letusan gunung, geografi, dan budaya Dieng.", "tips": "Durasi ~30 menit. Tempat berteduh bagus saat kabut/hujan.", "duration": "30-45 menit", "coordinates": {"lat": -7.2083, "lng": 109.9056}},
    {"name": "Batu Pandang Ratapan Angin", "type": "Alam", "description": "Destinasi favorit berisi bebatuan tebing menjulang. Titik terbaik melihat gradasi warna Telaga Warna dan Pengilon dari atas.", "tips": "Angin sangat kencang! Pegang topi dan barang berharga.", "duration": "30-45 menit", "coordinates": {"lat": -7.2108, "lng": 109.9167}},
    {"name": "Telaga Warna", "type": "Alam", "description": "Danau vulkanik di kawasan konservasi BKSDA yang airnya memantulkan warna berbeda karena kandungan sulfur. Area rimbun dan sakral.", "tips": "Bawa kamera! Warna terbaik saat pagi cerah. Trek ~30 menit.", "duration": "60-90 menit", "coordinates": {"lat": -7.2167, "lng": 109.9150}},
    {"name": "Kebun Teh Tambi", "type": "Agrowisata", "description": "Wisata agro peninggalan Belanda. Bisa berkeliling kebun teh atau mengikuti tur pabrik teh (biaya terpisah).", "tips": "Tur pabrik teh tersedia dengan biaya terpisah.", "duration": "60-90 menit", "coordinates": {"lat": -7.2700, "lng": 109.8500}},
    {"name": "Taman Langit", "type": "Alam", "description": "Area wisata dataran tinggi untuk bersantai menikmati lanskap perbukitan. Sangat direkomendasikan untuk sunrise dan sunset.", "tips": "Cocok untuk sunrise dan sunset. Pemandangan hampir sama indahnya dengan Watu Angkruk.", "duration": "30-60 menit", "coordinates": {"lat": -7.2200, "lng": 109.8850}},
    {"name": "Watu Angkruk", "type": "Alam", "description": "Destinasi populer untuk sunrise tanpa perlu mendaki jauh. Tersedia jembatan kaca (glass skywalk) dan kereta kencana tembaga.", "tips": "Sunrise tanpa hiking! Ada glass skywalk dan kereta kencana.", "duration": "45-60 menit", "coordinates": {"lat": -7.2200, "lng": 109.8870}},
    {"name": "Bukit Sikapuk", "type": "Alam", "description": "Area lereng bukit dengan pemandangan hamparan awan dan pegunungan. Alternatif tenang untuk sunrise dan berfoto.", "tips": "Lebih sepi dari Sikunir. Cocok yang tidak suka keramaian.", "duration": "45-60 menit", "coordinates": {"lat": -7.2180, "lng": 109.8830}},
    {"name": "Gunung Prau", "type": "Alam", "description": "Gunung populer dengan sabana di puncak. Tersedia 4 jalur pendakian: Patakbanteng (paling populer), Igirmranak, Kali Lembu, dan via Dieng.", "tips": "Via Patakbanteng paling populer tapi menanjak. Tarif parkir berlaku inap.", "duration": "5-8 jam", "coordinates": {"lat": -7.1850, "lng": 109.9150}},
    {"name": "Gunung Pakuwaja", "type": "Alam", "description": "Jalur pendakian menuju batu vertikal raksasa yang dipercaya sebagai 'paku' penguat Pulau Jawa.", "tips": "Tarif parkir berlaku untuk inap/camping.", "duration": "4-6 jam", "coordinates": {"lat": -7.2100, "lng": 109.8750}},
    {"name": "Gunung Bismo", "type": "Alam", "description": "Jalur pendakian via Sikunang yang relatif lebih singkat.", "tips": "Biaya parkir dihitung tarif menginap (camping).", "duration": "5-7 jam", "coordinates": {"lat": -7.2400, "lng": 109.8700}},
    {"name": "Tuk Bimolukar", "type": "Budaya", "description": "Mata air kuno yang disucikan dan bersejarah. Airnya sangat dingin, dipercaya membuat awet muda.", "tips": "Hormati adat setempat. Air sangat dingin!", "duration": "15-20 menit", "coordinates": {"lat": -7.2119, "lng": 109.9094}},
    {"name": "Bukit Scoter", "type": "Alam", "description": "Bukit landai dekat pusat desa Dieng Kulon. Spot santai melihat lanskap desa, persawahan, dan kawasan candi.", "tips": "Sangat dekat pusat desa. Cocok untuk santai.", "duration": "30-45 menit", "coordinates": {"lat": -7.2060, "lng": 109.9080}},
    {"name": "Bukit Sipandu", "type": "Alam", "description": "Di perbatasan Banjarnegara dan Batang. Menawarkan sabana dan padang rumput ilalang dengan view pegunungan utara Jawa.", "tips": "View pegunungan utara Jawa. Bawa jaket.", "duration": "1-2 jam", "coordinates": {"lat": -7.2400, "lng": 109.9300}},
    {"name": "D-Qiano Water Park", "type": "Rekreasi", "description": "Taman rekreasi air terbesar di Dieng. Kolam renang air panas bumi alami dengan berbagai fasilitas seluncuran.", "tips": "Bawa baju ganti dan handuk. Air panas alami!", "duration": "2-3 jam", "coordinates": {"lat": -7.2050, "lng": 109.9020}},
    {"name": "Banyu Alam Hot Spring", "type": "Rekreasi", "description": "Pemandian air panas alami yang ideal untuk berendam merelaksasikan otot di cuaca Dieng yang dingin.", "tips": "Cocok setelah hiking. Bawa handuk.", "duration": "1-2 jam", "coordinates": {"lat": -7.2030, "lng": 109.9000}},
    {"name": "Pemandian Air Panas Bitingan", "type": "Rekreasi", "description": "Pemandian tradisional berbahan dasar mata air panas vulkanik yang dikelola komunal oleh warga lokal.", "tips": "Harga murah Rp 5.000. Dikelola warga lokal.", "duration": "1-2 jam", "coordinates": {"lat": -7.2090, "lng": 109.9120}},
    {"name": "Museum Kailasa", "type": "Edukasi", "description": "Museum geologi dan sejarah terlengkap di Dieng. Menyimpan artefak candi, informasi letusan kawah, dan kehidupan sosial budaya.", "tips": "Kunjungi sebelum ke candi untuk pemahaman sejarah lebih baik.", "duration": "30-45 menit", "coordinates": {"lat": -7.2075, "lng": 109.9058}},
    {"name": "Candi Gatot Kaca", "type": "Budaya", "description": "Situs peninggalan Mataram Kuno, candi tunggal. Gratis karena letaknya di ruang terbuka tepi jalan.", "tips": "Gratis! Kunjungi bersamaan dengan Candi Arjuna.", "duration": "15-20 menit", "coordinates": {"lat": -7.2097, "lng": 109.9089}},
    {"name": "Telaga Merdada", "type": "Alam", "description": "Telaga terluas di kawasan Dieng. Tidak beracun, sering digunakan untuk kayak dan irigasi pertanian.", "tips": "Aman untuk kayak. Suasana lebih sepi dari Telaga Warna.", "duration": "30-45 menit", "coordinates": {"lat": -7.2189, "lng": 109.9178}},
    {"name": "Telaga Sewiwi", "type": "Alam", "description": "Telaga kecil nan rindang yang biasanya dinikmati saat melintas. Belum banyak infrastruktur komersial.", "tips": "Gratis! Pemandangan hening dan alami.", "duration": "15-20 menit", "coordinates": {"lat": -7.2195, "lng": 109.9200}},
    {"name": "Telaga Sedringo", "type": "Alam", "description": "Sering disebut Telaga Dringo. Akses ekstrem namun pemandangan indah bak Ranu Kumbolo, surga camping.", "tips": "Akses jalan ekstrem! Pastikan kendaraan prima. Cocok camping.", "duration": "1-2 jam", "coordinates": {"lat": -7.2220, "lng": 109.9250}},
    {"name": "Kawah Candradimuka", "type": "Alam", "description": "Kawah legendaris dikaitkan dengan mitos Gatotkaca. Suasana masih natural dan tersembunyi.", "tips": "Kawah tidak selalu aktif. Suasana mistis dan natural.", "duration": "30-45 menit", "coordinates": {"lat": -7.2042, "lng": 109.9125}},
    {"name": "Kebun Teh Kertosari", "type": "Agrowisata", "description": "Wisata agro alternatif berupa hamparan perkebunan teh yang menghijau dengan udara sejuk.", "tips": "Lebih sepi dari Tambi. Cocok untuk bersantai.", "duration": "30-60 menit", "coordinates": {"lat": -7.2650, "lng": 109.8600}},
    {"name": "Dieng Park", "type": "Alam", "description": "Kawasan bukit dengan titik pantau strategis untuk Telaga Warna dari atas. Ideal untuk sunrise dan sunset.", "tips": "Cocok untuk sunrise DAN sunset. View Telaga Warna dari atas.", "duration": "45-60 menit", "coordinates": {"lat": -7.2160, "lng": 109.9140}},
    {"name": "Kebun Teh Sikatok", "type": "Agrowisata", "description": "Destinasi agro dengan titian jembatan kayu memanjang yang estetik untuk spot berfoto.", "tips": "Jembatan kayu estetik untuk foto.", "duration": "30-60 menit", "coordinates": {"lat": -7.2680, "lng": 109.8550}},
    {"name": "Taman Rumah Peri", "type": "Rekreasi", "description": "Tempat wisata ramah anak dan keluarga dengan spot foto rumah-rumah kurcaci dan dekorasi miniatur ala negeri dongeng.", "tips": "Sangat cocok untuk keluarga dan anak-anak.", "duration": "30-60 menit", "coordinates": {"lat": -7.2040, "lng": 109.9040}},
    # === Data existing (tidak ada di CSV) ===
    {"name": "Desa Wisata Sembungan", "type": "Budaya", "description": "Desa tertinggi di Pulau Jawa (2.300 mdpl). Kehidupan petani dataran tinggi.", "tips": "Mampir ke kedai kopi lokal. Suasana asri.", "duration": "1-2 jam", "coordinates": {"lat": -7.2233, "lng": 109.8969}},
    {"name": "Pasar Carica Dieng", "type": "Kuliner", "description": "Pasar oleh-oleh khas Dieng. Wajib beli carica dan keripik kentang.", "tips": "Harga bisa ditawar. Beli carica dalam sirup.", "duration": "30-45 menit", "coordinates": {"lat": -7.2067, "lng": 109.9108}},
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
