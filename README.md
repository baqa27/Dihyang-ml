# Dihyang Web — Dieng Intelligence Tourism Assistant (DITA)

> **Tim Capstone PJK-GM067** | Pijak × IBM SkillsBuild  
> Tema: AI for Smart Tourism Experience  
> **🔴 REALTIME MONITORING ENABLED** — WebSocket + Auto-Scraping

---

## 📋 Project Overview

Dihyang Web adalah platform pariwisata cerdas berbasis AI yang dirancang untuk mengatasi kesenjangan informasi keamanan di kawasan wisata Dataran Tinggi Dieng, Wonosobo. Dengan chatbot DITA, wisatawan mendapatkan rekomendasi rute aman, prediksi cuaca, dan informasi retribusi resmi secara **real-time**.

### ✨ Fitur Realtime
- **WebSocket Dashboard** — Update cuaca setiap 5 menit otomatis
- **Auto-Scraping** — Data cuaca terbaru dari Open-Meteo API
- **ML Predictions** — Prediksi suhu, hujan, dan risiko secara realtime
- **Auto-Retrain** — Model ML diperbarui otomatis setiap minggu dengan data terbaru

## 🏗️ Architecture

```
CAPSTONE/
├── backend/                    # FastAPI Backend (Python 3.13)
│   ├── app/
│   │   ├── main.py             # Entry point
│   │   ├── models/             # AI/ML Module
│   │   │   ├── saved/          # Trained model files (.pkl)
│   │   │   ├── predict.py      # ML inference engine
│   │   │   ├── knowledge_base.py   # NLP custom knowledge base
│   │   │   ├── train_weather_model.py
│   │   │   └── train_route_model.py
│   │   ├── routers/            # API endpoints
│   │   │   ├── chat.py         # DITA NLP chatbot
│   │   │   ├── itinerary.py    # Smart itinerary generator
│   │   │   ├── weather.py      # Weather data API
│   │   │   ├── destinations.py # Destination info
│   │   │   └── predictions.py  # ML prediction endpoints
│   │   └── data/               # Datasets
│   │       ├── dieng_historical_2023.json
│   │       ├── dieng_retribusi.json
│   │       └── dieng_route_dataset.csv
│   ├── notebooks/              # Jupyter Notebooks (AI/ML)
│   │   ├── 01_EDA_weather.ipynb
│   │   ├── 02_weather_models.ipynb
│   │   ├── 03_route_safety_model.ipynb
│   │   ├── 04_nlp_chatbot_analysis.ipynb
│   │   └── figures/
│   ├── scraper/                # Data collection scripts
│   └── .env                    # Environment variables
│
├── frontend/                   # React + Vite Frontend
│   └── src/
│       ├── pages/              # Page components
│       │   ├── Home.jsx        # Landing page
│       │   ├── Dashboard.jsx   # Weather dashboard
│       │   ├── Explore.jsx     # Destination explorer
│       │   ├── Itinerary.jsx   # Smart itinerary
│       │   ├── Chat.jsx        # DITA chatbot
│       │   └── InfoCenter.jsx  # Info center
│       ├── components/         # Reusable components
│       └── services/           # API service layer
│
└── README.md
```

## 🧠 AI/ML Models

| # | Model | Algorithm | Metric | Score |
|---|-------|-----------|--------|-------|
| 1 | Temperature Prediction | Random Forest Regressor | R² | **0.9951** |
| 2 | Rain Prediction | Gradient Boosting Classifier | F1 | **0.7244** |
| 3 | Tourism Risk Classification | Gradient Boosting Classifier | Accuracy | **98.57%** |
| 4 | Route Safety Classification | Random Forest Classifier | Accuracy | **100%** |

### NLP Architecture (DITA Chatbot)
- **Gemini API** — LLM for contextual responses
- **Custom Knowledge Base** — Verified local data (RAG-style injection)
- **Rule-based Fallback** — Offline intent classification (10+ intents)

## 🚀 Quick Start

### Prerequisites
- Python 3.13+
- Node.js 18+

### 1. Backend Setup
```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate    # Windows
pip install -r requirements.txt

# Scrape data cuaca historis (2022-2025)
python scraper/scrape.py

# Scrape data realtime
python scraper/scrape.py --realtime

# Train ML models
python -m app.models.train_weather_model
python -m app.models.train_route_model

# Jalankan server (dengan realtime scheduler)
uvicorn app.main:app --reload
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### 3. Environment Variables
Create `backend/.env`:
```env
GEMINI_API_KEY=your_api_key_here
```

## 🔄 Realtime Features

### Auto-Scraping
Server otomatis scrape data cuaca setiap **5 menit** saat berjalan:
```bash
# Manual trigger
python scraper/scrape.py --realtime      # Data cuaca terkini
python scraper/scrape.py --latest        # 30 hari terakhir untuk retrain
```

### WebSocket Endpoints
- `ws://localhost:8000/api/realtime/ws/weather` — Weather updates
- `ws://localhost:8000/api/realtime/ws/predictions` — ML predictions
- `ws://localhost:8000/api/realtime/ws/dashboard` — Combined dashboard

### Auto-Retrain
Model ML otomatis retrain setiap **7 hari** dengan data terbaru:
```bash
# Manual trigger
curl -X POST http://localhost:8000/api/realtime/retrain

# Check status
curl http://localhost:8000/api/realtime/status
```

## 📊 API Endpoints

### Weather & Realtime
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/weather/current` | GET | Current weather data |
| `/api/weather/historical` | GET | Historical weather dataset |
| `/api/realtime/status` | GET | Realtime system status |
| `/api/realtime/retrain` | POST | Trigger manual retrain |
| `ws://.../realtime/ws/weather` | WS | Weather WebSocket |
| `ws://.../realtime/ws/dashboard` | WS | Dashboard WebSocket |

### AI & ML
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chat` | POST | DITA NLP chatbot |
| `/api/itinerary/generate` | POST | AI-powered itinerary |
| `/api/ml/model-info` | GET | ML model metrics |
| `/api/ml/predict/quick` | GET | Real-time prediction |
| `/api/ml/predict/dashboard` | GET | Dashboard predictions |
| `/api/ml/predict/temperature` | POST | Temperature prediction |
| `/api/ml/predict/rain` | POST | Rain prediction |
| `/api/ml/predict/risk` | POST | Tourism risk level |
| `/api/ml/predict/route-safety` | POST | Route safety classification |

### Destinations
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/destinations/` | GET | Destination information |

## 👥 Team

| Name | Role | ID |
|------|------|----|
| Titi Alfiana Pramesti | Project Manager | APC466D6X0031 |
| Ida Masruroh | AI Engineer | APC466D6X0040 |
| Muhammad Sultan Baqa | Back-End Developer | APC466D6Y0108 |
| Muhammad Khoirur Rosyid | Front-End Developer | APC466D6Y0366 |
| Annisa Oktora Nurusyifa | UI/UX Designer | APC466D6X0036 |

## 📚 Tech Stack

- **Frontend:** React 18, Vite, Leaflet.js, Recharts
- **Backend:** FastAPI, Python 3.13
- **AI/ML:** scikit-learn, pandas, numpy, Gemini API
- **Data:** Open-Meteo API, custom datasets

---

*© 2026 Tim PJK-GM067 — Pijak × IBM SkillsBuild Capstone Project*
