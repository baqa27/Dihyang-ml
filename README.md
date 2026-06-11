# Dihyang Web — Dieng Intelligence Tourism Assistant (DITA)

> **Tim Capstone PJK-GM067** | Pijak × IBM SkillsBuild  
> Tema: AI for Smart Tourism Experience  
> **🔴 REALTIME MONITORING ENABLED** — WebSocket + Auto-Scraping

---

## 📋 Project Overview

Dihyang Web adalah platform pariwisata cerdas berbasis AI yang dirancang untuk mengatasi kesenjangan informasi keamanan di kawasan wisata Dataran Tinggi Dieng, Wonosobo. Dengan chatbot DITA, wisatawan mendapatkan rekomendasi rute aman, prediksi cuaca, dan informasi retribusi resmi secara **real-time**.

### ✨ Fitur Realtime
- **WebSocket Dashboard** — Update cuaca setiap 5 menit secara otomatis.
- **Auto-Scraping** — Data cuaca terbaru disinkronkan langsung dari Open-Meteo API.
- **ML Predictions** — Prediksi suhu, hujan, dan risiko keselamatan secara real-time.
- **Auto-Retrain** — Model ML diperbarui otomatis setiap minggu dengan data latih terbaru.

## 🏗️ Architecture

```
CAPSTONE/
├── backend/                    # FastAPI Backend (Python 3.13)
│   ├── app/
│   │   ├── main.py             # Entry point utama API
│   │   ├── config.py           # Konfigurasi sistem & Environment
│   │   ├── models/             # Modul AI & Machine Learning
│   │   │   ├── saved/          # Berkas model latih (.pkl) & laporan evaluasi
│   │   │   │   ├── evaluation_report.json          # Metrik evaluasi Model 1, 2, & 3
│   │   │   │   ├── itinerary_model_report.json     # Metrik evaluasi Model 5
│   │   │   │   ├── itinerary_recommender.pkl       # Random Forest Recommendation Model
│   │   │   │   ├── itinerary_scaler.pkl
│   │   │   │   ├── itinerary_training_sample.csv
│   │   │   │   ├── rain_classifier.pkl             # Gradient Boosting Rain Classifier
│   │   │   │   ├── rain_scaler.pkl
│   │   │   │   ├── risk_classifier.pkl             # Gradient Boosting Risk Classifier
│   │   │   │   ├── risk_scaler.pkl
│   │   │   │   ├── route_safety_model.pkl          # Random Forest Route Safety Classifier
│   │   │   │   ├── route_scaler.pkl
│   │   │   │   ├── temperature_model.pkl           # Random Forest Temperature Regressor
│   │   │   │   ├── temp_scaler.pkl
│   │   │   │   ├── le_budget_itinerary.pkl         # Label Encoders
│   │   │   │   ├── le_physical_itinerary.pkl
│   │   │   │   ├── le_style_itinerary.pkl
│   │   │   │   ├── le_surface.pkl
│   │   │   │   ├── le_type_itinerary.pkl
│   │   │   │   ├── le_vehicle.pkl
│   │   │   │   ├── le_vehicle_itinerary.pkl
│   │   │   │   └── le_weather.pkl
│   │   │   ├── predict.py      # Engine inferensi ML
│   │   │   ├── knowledge_base.py # KB kustom untuk NLP Chatbot
│   │   │   ├── rag_engine.py   # RAG Context retrieval
│   │   │   ├── itinerary_engine.py # Penjadwal rencana perjalanan
│   │   │   ├── model_versioning.py # Versi & metrik model
│   │   │   ├── train_weather_model.py
│   │   │   ├── train_itinerary_model.py
│   │   │   └── train_route_model.py
│   │   ├── routers/            # Router Endpoint API
│   │   │   ├── chat.py         # Asisten NLP DITA
│   │   │   ├── itinerary.py    # Perencana rencana perjalanan cerdas
│   │   │   ├── weather.py      # Informasi data cuaca
│   │   │   ├── destinations.py # Galeri destinasi wisata
│   │   │   ├── predictions.py  # Inferensi ML predictions
│   │   │   └── realtime.py     # Kontrol WebSocket & retrain scheduler
│   │   └── data/               # Basis data Chroma DB & berkas dataset
│   │       ├── chroma_db/      # Vektor data untuk chatbot RAG
│   │       ├── data_wisata.csv
│   │       ├── dieng_historical_2022.json
│   │       ├── dieng_historical_2023.json
│   │       ├── dieng_historical_2024.json
│   │       ├── dieng_historical_2025.json
│   │       ├── dieng_historical_2026.json
│   │       ├── dieng_historical_combined.json
│   │       ├── dieng_realtime_current.json
│   │       ├── dieng_retribusi.json
│   │       ├── dieng_route_dataset.csv
│   │       └── convert_csv_to_json.py
│   ├── notebooks/              # Jupyter Notebooks untuk analisis AI/ML
│   │   ├── 01_EDA_weather.ipynb
│   │   ├── 02_weather_models.ipynb
│   │   ├── 03_route_safety_model.ipynb
│   │   └── 04_nlp_chatbot_analysis.ipynb
│   └── scraper/                # Skrip pengambilan data dari API cuaca
│
├── frontend/                   # React.js + Vite Frontend (TypeScript)
│   └── src/
│       ├── app/
│       │   ├── App.tsx         # Halaman utama aplikasi (SPA)
│       │   ├── pages/          # Halaman mandiri tambahan
│       │   │   ├── Bantuan.tsx    # Pusat Bantuan & FAQ
│       │   │   └── Perusahaan.tsx # Hubungi kami & Profil tim
│       │   ├── components/     # Komponen UI dashboard interaktif
│       │   │   ├── HeroSection.tsx
│       │   │   ├── WeatherDashboard.tsx
│       │   │   ├── RouteMap.tsx
│       │   │   ├── RouteNavigation.tsx
│       │   │   ├── SmartItinerary.tsx
│       │   │   ├── ChatbotSection.tsx
│       │   │   ├── FloatingChatbot.tsx
│       │   │   ├── Footer.tsx
│       │   │   ├── Navbar.tsx
│       │   │   ├── NotificationPanel.tsx
│       │   │   ├── ThemeProvider.tsx
│       │   │   └── InfoCenter.tsx
│       │   └── hooks/          # React Custom Hooks
│       │       └── useThemeColors.ts
│       ├── config/
│       │   └── api.ts          # Centralized API fetch wrapper
│       ├── services/
│       │   └── api.service.ts  # Jembatan request API ke backend
│       └── main.tsx            # Entry point aplikasi
│
└── README.md
```

## 🧠 AI/ML Models

| # | Model | Algorithm | Metric | Score |
|---|-------|-----------|--------|-------|
| 1 | Temperature Prediction | Random Forest Regressor | R² | **0.9958** (CV: **0.9951**) |
| 2 | Rain Prediction | Gradient Boosting Classifier | Accuracy / F1 | **95.85%** / **93.88%** |
| 3 | Tourism Risk Classification | Gradient Boosting Classifier | Accuracy | **98.03%** |
| 4 | Route Safety Classification | Random Forest Classifier | Accuracy | **100%** (CV: **99.6%**) |
| 5 | Itinerary Recommendation | Random Forest Regressor (Hybrid) | Test RMSE / MAE | **0.5579** / **0.4318** |

### NLP Architecture (DITA Chatbot)
- **Gemini API** — Model Bahasa Besar (LLM) untuk menghasilkan respons kontekstual yang natural.
- **Custom Knowledge Base** — Injeksi data lokal tervalidasi menggunakan pendekatan RAG (Retrieval-Augmented Generation) melalui Chroma DB.
- **Rule-based Fallback** — Klasifikasi intent lokal secara offline (10+ intent dasar) apabila koneksi API terputus atau kunci API tidak terpasang.

## 🚀 Quick Start

### Prerequisites
- Python 3.13+
- Node.js 18+ (npm / pnpm)

### 1. Backend Setup
```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate    # Windows
# source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt

# Mengambil data cuaca historis (2022-2026)
python scraper/scrape.py

# Mengambil data realtime terbaru
python scraper/scrape.py --realtime

# Melatih model Machine Learning lokal
python -m app.models.train_weather_model
python -m app.models.train_route_model
python -m app.models.train_itinerary_model

# Jalankan server FastAPI dengan auto-reload
uvicorn app.main:app --reload
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### 3. Environment Variables
Buat berkas `backend/.env` untuk backend:
```env
ENVIRONMENT=development
GEMINI_API_KEY=your_gemini_api_key_here
ALLOWED_ORIGINS=http://localhost:5173
```

Buat berkas `frontend/.env` untuk frontend (jika ingin mengubah alamat host backend):
```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

## 🔄 Realtime Features

### Auto-Scraping
Server otomatis mengunduh data cuaca terbaru setiap **5 menit** ketika aktif berjalan.
```bash
# Pengambilan manual
python scraper/scrape.py --realtime      # Data cuaca terkini
python scraper/scrape.py --latest        # 30 hari terakhir untuk retrain
```

### WebSocket Endpoints
- `ws://<host>/api/realtime/ws/weather` — Pembaruan cuaca real-time.
- `ws://<host>/api/realtime/ws/predictions` — Pembaruan prediksi ML secara real-time.
- `ws://<host>/api/realtime/ws/dashboard` — Kombinasi data cuaca dan prediksi.

### Auto-Retrain
Model ML otomatis dilatih kembali setiap **7 hari** menggunakan data cuaca terbaru.
```bash
# Pemicu manual
curl -X POST http://localhost:8000/api/realtime/retrain

# Memeriksa status penjadwal
curl http://localhost:8000/api/realtime/status
```

## 📊 API Endpoints

### Weather & Realtime
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/weather/current` | GET | Data cuaca terbaru hasil scrape |
| `/api/weather/forecast` | GET | Prakiraan cuaca harian Dieng |
| `/api/weather/hourly-today` | GET | Prakiraan cuaca per jam hari ini |
| `/api/weather/historical` | GET | Akses dataset historis |
| `/api/realtime/status` | GET | Memeriksa status scheduler realtime |
| `/api/realtime/retrain` | POST | Memicu retrain model secara manual |
| `/api/realtime/ws/weather` | WS | WebSocket update data cuaca harian |
| `/api/realtime/ws/predictions` | WS | WebSocket update inferensi prediksi ML |
| `/api/realtime/ws/dashboard` | WS | WebSocket gabungan data cuaca & prediksi |

### AI & ML
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chat` | POST | NLP Chatbot DITA (Gemini + RAG + Fallback) |
| `/api/itinerary/generate` | POST | AI-powered itinerary generator |
| `/api/itinerary/generate-smart` | POST | Smart itinerary generator |
| `/api/itinerary/activities` | GET | Daftar rekomendasi aktivitas wisata |
| `/api/ml/model-info` | GET | Informasi metrik & performa evaluasi model |
| `/api/ml/predict/quick` | GET | Prediksi cepat parameter cuaca hari ini |
| `/api/ml/predict/dashboard` | GET | Kombinasi dashboard prediksi ML |
| `/api/ml/predict/temperature` | POST | Prediksi suhu berdasar variabel input |
| `/api/ml/predict/rain` | POST | Prediksi curah hujan berdasar variabel input |
| `/api/ml/predict/risk` | POST | Prediksi tingkat risiko keselamatan wisata |
| `/api/ml/predict/route-safety` | POST | Klasifikasi keamanan jalur rute |

### Destinations
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/destinations` | GET | Memperoleh daftar informasi 20 destinasi Dieng |

## 👥 Team

| Name | Role | ID |
|------|------|----|
| Titi Alfiana Pramesti | Project Manager | APC466D6X0031 |
| Ida Masruroh | AI Engineer | APC466D6X0040 |
| Muhammad Sultan Baqa | Back-End Developer | APC466D6Y0108 |
| Muhammad Khoirur Rosyid | Front-End Developer | APC466D6Y0366 |
| Annisa Oktora Nurusyifa | UI/UX Designer | APC466D6X0036 |

## 📚 Tech Stack

- **Frontend:** React 18 (TypeScript), Vite, Leaflet.js, Recharts, Framer Motion (motion/react)
- **Backend:** FastAPI, Uvicorn, Python 3.13, SlowAPI Rate Limiter
- **AI/ML:** scikit-learn, pandas, numpy, Google Gemini API, Chroma DB (Vector Store)
- **Data:** Open-Meteo API, custom datasets

---

*© 2026 Tim PJK-GM067 — Pijak × IBM SkillsBuild Capstone Project*
