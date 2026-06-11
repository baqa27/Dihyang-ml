"""
==============================================================================
DITA Smart Itinerary Engine — ML-Based Recommendation System
==============================================================================
Sistem ML untuk generate itinerary dengan Hybrid Recommendation:
  1. ML Recommendation Model (Random Forest - Content-based + Collaborative)
  2. Rule-based Fallback (jika model belum di-train)
  3. Weather-adaptive planning
  4. Budget optimization

Model: Random Forest Regressor trained on synthetic user-activity interactions
Input: user preferences (budget, interests, travel_style, vehicle)
Output: ranked activities with predicted ratings (1-5 stars)

Author: Tim PJK-GM067 (Ida Masruroh — AI Engineer)
==============================================================================
"""

import os
import json
import random
import numpy as np
import pandas as pd
import joblib
from typing import List, Dict, Any
from datetime import datetime, timedelta


MODEL_DIR = os.path.join(os.path.dirname(__file__), 'saved')


class DiengItineraryEngine:
    """
    ML-based itinerary recommendation engine.
    Uses trained Random Forest model to predict activity ratings.
    Falls back to rule-based system if model not trained.
    """
    
    def __init__(self):
        self.activities_db = self._build_activities_database()
        self.route_graph = self._build_route_graph()
        self.model_loaded = False
        self.ml_model = None
        self.scaler = None
        self.label_encoders = {}
        self._load_ml_model()
    
    def _load_ml_model(self):
        """Load ML recommendation model jika sudah di-train."""
        try:
            self.ml_model = joblib.load(os.path.join(MODEL_DIR, 'itinerary_recommender.pkl'))
            self.scaler = joblib.load(os.path.join(MODEL_DIR, 'itinerary_scaler.pkl'))
            self.label_encoders = {
                'budget': joblib.load(os.path.join(MODEL_DIR, 'le_budget_itinerary.pkl')),
                'style': joblib.load(os.path.join(MODEL_DIR, 'le_style_itinerary.pkl')),
                'vehicle': joblib.load(os.path.join(MODEL_DIR, 'le_vehicle_itinerary.pkl')),
                'type': joblib.load(os.path.join(MODEL_DIR, 'le_type_itinerary.pkl')),
                'physical': joblib.load(os.path.join(MODEL_DIR, 'le_physical_itinerary.pkl')),
            }
            self.model_loaded = True
            print("[OK] ML Itinerary Recommendation Model loaded successfully!")
        except Exception as e:
            print(f"[INFO] ML model belum di-train. Gunakan rule-based system: {e}")
            self.model_loaded = False
        
    def _build_activities_database(self) -> List[Dict[str, Any]]:
        """Database lengkap aktivitas wisata Dieng dengan metadata."""
        return [
            # === KATEGORI: SUNRISE & NATURE ===
            {
                "id": "sikunir_sunrise",
                "name": "Sunrise Bukit Sikunir",
                "location": "Bukit Sikunir, Sembungan",
                "type": "attraction",
                "interests": ["alam", "fotografi", "petualangan", "sunrise"],
                "duration_hours": 3.5,
                "start_time": "04:30",
                "cost_per_person": 25000,
                "physical_level": "medium",  # easy, medium, hard
                "weather_sensitive": True,
                "best_months": [5, 6, 7, 8, 9],  # Mei-Sept (musim kemarau)
                "vehicle_access": ["motorcycle", "car"],
                "tips": "Bawa senter, jaket tebal, dan berangkat jam 3:30 subuh. Cek cuaca sebelum naik.",
                "priority_score": 95,  # semakin tinggi semakin prioritas
            },
            {
                "id": "prau_trekking",
                "name": "Trekking Gunung Prau",
                "location": "Gunung Prau (2.565 mdpl)",
                "type": "attraction",
                "interests": ["petualangan", "alam", "fotografi", "trekking"],
                "duration_hours": 6.0,
                "start_time": "06:00",
                "cost_per_person": 50000,
                "physical_level": "hard",
                "weather_sensitive": True,
                "best_months": [4, 5, 6, 7, 8, 9],
                "vehicle_access": ["motorcycle", "car"],
                "tips": "Gunakan pemandu lokal. Bawa bekal, air 2L, dan P3K. Hindari saat hujan.",
                "priority_score": 85,
            },
            {
                "id": "telaga_warna",
                "name": "Telaga Warna & Pengilon",
                "location": "Dieng Wetan",
                "type": "attraction",
                "interests": ["alam", "fotografi", "keluarga"],
                "duration_hours": 2.0,
                "start_time": "09:00",
                "cost_per_person": 10000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Warna telaga berubah sesuai musim. Pagi hari lebih tenang.",
                "priority_score": 90,
            },
            {
                "id": "batu_ratapan_angin",
                "name": "Batu Ratapan Angin",
                "location": "Dieng Plateau",
                "type": "attraction",
                "interests": ["alam", "fotografi", "keluarga"],
                "duration_hours": 1.5,
                "start_time": "15:00",
                "cost_per_person": 5000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Spot sunset terbaik. Datang sore untuk cahaya golden hour.",
                "priority_score": 80,
            },
            
            # === KATEGORI: KAWAH & GEOLOGI ===
            {
                "id": "kawah_sikidang",
                "name": "Kawah Sikidang",
                "location": "Dieng Wetan",
                "type": "attraction",
                "interests": ["alam", "geologi", "keluarga", "edukasi"],
                "duration_hours": 1.5,
                "start_time": "09:00",
                "cost_per_person": 15000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Jangan lewati batas aman. Gunakan masker jika bau belerang menyengat.",
                "priority_score": 88,
            },
            {
                "id": "kawah_sileri",
                "name": "Kawah Sileri",
                "location": "Kepakisan",
                "type": "attraction",
                "interests": ["alam", "geologi"],
                "duration_hours": 1.5,
                "start_time": "10:00",
                "cost_per_person": 10000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car"],
                "tips": "Kawah terbesar di Dieng. Patuhi radius aman 200m dari kawah aktif.",
                "priority_score": 70,
            },
            {
                "id": "kawah_candradimuka",
                "name": "Kawah Candradimuka",
                "location": "Dieng Wetan",
                "type": "attraction",
                "interests": ["alam", "geologi", "fotografi"],
                "duration_hours": 1.0,
                "start_time": "11:00",
                "cost_per_person": 5000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car"],
                "tips": "Kawah paling aktif. Jalur pendek tapi jalan licin saat hujan.",
                "priority_score": 65,
            },
            
            # === KATEGORI: SEJARAH & BUDAYA ===
            {
                "id": "candi_arjuna",
                "name": "Kompleks Candi Arjuna",
                "location": "Dieng Kulon",
                "type": "attraction",
                "interests": ["budaya", "sejarah", "fotografi", "keluarga"],
                "duration_hours": 2.0,
                "start_time": "08:00",
                "cost_per_person": 20000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Candi Hindu tertua di Jawa (abad 7-8 M). Pagi hari tidak ramai.",
                "priority_score": 92,
            },
            {
                "id": "museum_kailasa",
                "name": "Museum Kailasa Dieng",
                "location": "Dieng Kulon",
                "type": "attraction",
                "interests": ["budaya", "sejarah", "edukasi"],
                "duration_hours": 1.0,
                "start_time": "09:00",
                "cost_per_person": 5000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Alternatif indoor saat hujan. Koleksi artefak Dieng kuno.",
                "priority_score": 60,
            },
            {
                "id": "dieng_theater",
                "name": "Dieng Plateau Theater",
                "location": "Dieng Kulon",
                "type": "attraction",
                "interests": ["budaya", "edukasi", "keluarga"],
                "duration_hours": 1.0,
                "start_time": "14:00",
                "cost_per_person": 15000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Film dokumenter tentang Dieng. Cocok saat cuaca buruk.",
                "priority_score": 55,
            },
            
            # === KATEGORI: AGROWISATA & DESA ===
            {
                "id": "agrowisata_tambi",
                "name": "Kebun Teh Tambi",
                "location": "Kejajar, Wonosobo",
                "type": "attraction",
                "interests": ["alam", "fotografi", "keluarga", "kuliner"],
                "duration_hours": 2.5,
                "start_time": "09:00",
                "cost_per_person": 10000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Tur kebun teh + tasting. Udara sejuk dan pemandangan hijau.",
                "priority_score": 75,
            },
            {
                "id": "desa_sembungan",
                "name": "Desa Sembungan",
                "location": "Sembungan (desa tertinggi Jawa)",
                "type": "attraction",
                "interests": ["budaya", "alam", "fotografi"],
                "duration_hours": 2.0,
                "start_time": "10:00",
                "cost_per_person": 0,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car"],
                "tips": "Desa tertinggi Jawa (2.300 mdpl). Wisata desa dan ladang kentang.",
                "priority_score": 70,
            },
            {
                "id": "telaga_menjer",
                "name": "Telaga Menjer",
                "location": "Garung, Wonosobo",
                "type": "attraction",
                "interests": ["alam", "fotografi", "keluarga"],
                "duration_hours": 2.0,
                "start_time": "09:00",
                "cost_per_person": 15000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Danau buatan terbesar di Wonosobo. Ada perahu dan spot foto.",
                "priority_score": 68,
            },
            
            # === KATEGORI: AIR TERJUN ===
            {
                "id": "curug_sikarim",
                "name": "Air Terjun Sikarim",
                "location": "Sembungan",
                "type": "attraction",
                "interests": ["alam", "petualangan", "fotografi"],
                "duration_hours": 2.5,
                "start_time": "08:00",
                "cost_per_person": 5000,
                "physical_level": "medium",
                "weather_sensitive": True,
                "best_months": [10, 11, 12, 1, 2, 3],  # Musim hujan (air deras)
                "vehicle_access": ["motorcycle"],
                "tips": "Jalur trekking 30 menit. Hindari saat hujan deras (jalur licin).",
                "priority_score": 72,
            },
            {
                "id": "telaga_cebong",
                "name": "Telaga Cebong",
                "location": "Sembungan",
                "type": "attraction",
                "interests": ["alam", "fotografi"],
                "duration_hours": 1.5,
                "start_time": "10:00",
                "cost_per_person": 5000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car"],
                "tips": "Telaga kecil yang tenang. Spot foto refleksi pegunungan.",
                "priority_score": 60,
            },
            
            # === KATEGORI: KULINER ===
            {
                "id": "mie_ongklok",
                "name": "Makan Mie Ongklok Khas Wonosobo",
                "location": "Wonosobo / Dieng",
                "type": "food",
                "interests": ["kuliner"],
                "duration_hours": 1.0,
                "start_time": "12:00",
                "cost_per_person": 15000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Mie tebal kuah kental. Hangat untuk cuaca dingin Dieng.",
                "priority_score": 85,
            },
            {
                "id": "carica",
                "name": "Berburu Carica & Oleh-oleh",
                "location": "Pusat Dieng / Wonosobo",
                "type": "food",
                "interests": ["kuliner", "belanja"],
                "duration_hours": 1.0,
                "start_time": "15:00",
                "cost_per_person": 30000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Carica (manisan pepaya) khas Dieng. Beli di toko resmi.",
                "priority_score": 65,
            },
            {
                "id": "kopi_dieng",
                "name": "Ngopi di Warung Kopi Dieng",
                "location": "Dieng Kulon",
                "type": "food",
                "interests": ["kuliner", "santai"],
                "duration_hours": 1.0,
                "start_time": "16:00",
                "cost_per_person": 10000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Kopi Dieng hangat sambil lihat sunset. Cocok untuk rileks sore.",
                "priority_score": 60,
            },
            
            # === KATEGORI: RELAKSASI ===
            {
                "id": "pemandian_kalianget",
                "name": "Pemandian Air Panas Kalianget",
                "location": "Wonosobo",
                "type": "attraction",
                "interests": ["relaksasi", "keluarga"],
                "duration_hours": 2.0,
                "start_time": "14:00",
                "cost_per_person": 15000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Air panas alami. Cocok untuk recovery setelah trekking.",
                "priority_score": 70,
            },
            
            # === KATEGORI TAMBAHAN: HIDDEN GEMS ===
            {
                "id": "gua_jaran",
                "name": "Gua Jaran",
                "location": "Dieng Kulon",
                "type": "attraction",
                "interests": ["alam", "petualangan", "sejarah"],
                "duration_hours": 1.0,
                "start_time": "10:00",
                "cost_per_person": 5000,
                "physical_level": "medium",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car"],
                "tips": "Gua alami dengan legenda lokal. Bawa senter.",
                "priority_score": 62,
            },
            {
                "id": "gardu_pandang",
                "name": "Gardu Pandang Tieng",
                "location": "Dieng Plateau",
                "type": "attraction",
                "interests": ["alam", "fotografi"],
                "duration_hours": 1.0,
                "start_time": "16:00",
                "cost_per_person": 10000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car"],
                "tips": "View 360° pegunungan Dieng. Spot sunset alternatif.",
                "priority_score": 68,
            },
            {
                "id": "sumur_jalatunda",
                "name": "Sumur Jalatunda",
                "location": "Dieng Kulon",
                "type": "attraction",
                "interests": ["budaya", "sejarah", "spiritual"],
                "duration_hours": 0.5,
                "start_time": "09:00",
                "cost_per_person": 5000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Sumur bersejarah dengan air jernih. Situs spiritual.",
                "priority_score": 58,
            },
            {
                "id": "pasar_wonosobo",
                "name": "Pasar Tradisional Wonosobo",
                "location": "Wonosobo",
                "type": "attraction",
                "interests": ["budaya", "kuliner", "belanja"],
                "duration_hours": 1.5,
                "start_time": "08:00",
                "cost_per_person": 0,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Pasar tradisional dengan produk lokal. Tawar-menawar OK.",
                "priority_score": 60,
            },
            {
                "id": "candi_gatotkaca",
                "name": "Candi Gatotkaca",
                "location": "Dieng Kulon",
                "type": "attraction",
                "interests": ["budaya", "sejarah", "fotografi"],
                "duration_hours": 1.0,
                "start_time": "10:00",
                "cost_per_person": 10000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Candi Hindu dengan relief Gatotkaca. Dekat Candi Arjuna.",
                "priority_score": 75,
            },
            {
                "id": "candi_bima",
                "name": "Candi Bima",
                "location": "Dieng Kulon",
                "type": "attraction",
                "interests": ["budaya", "sejarah", "arsitektur"],
                "duration_hours": 1.0,
                "start_time": "11:00",
                "cost_per_person": 10000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Arsitektur unik mirip candi India Selatan.",
                "priority_score": 73,
            },
            {
                "id": "telaga_dringo",
                "name": "Telaga Dringo",
                "location": "Dieng Kulon",
                "type": "attraction",
                "interests": ["alam", "fotografi", "santai"],
                "duration_hours": 1.0,
                "start_time": "14:00",
                "cost_per_person": 5000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car"],
                "tips": "Telaga tenang dengan view pegunungan.",
                "priority_score": 63,
            },
            {
                "id": "camping_sikunir",
                "name": "Camping Ground Sikunir",
                "location": "Sembungan",
                "type": "attraction",
                "interests": ["petualangan", "alam", "camping"],
                "duration_hours": 12.0,
                "start_time": "17:00",
                "cost_per_person": 25000,
                "physical_level": "medium",
                "weather_sensitive": True,
                "best_months": [4, 5, 6, 7, 8, 9],
                "vehicle_access": ["motorcycle", "car"],
                "tips": "Camping malam di ketinggian. Bawa sleeping bag tebal!",
                "priority_score": 78,
            },
            {
                "id": "sunrise_pangonan",
                "name": "Sunrise Bukit Pangonan",
                "location": "Dieng Kulon",
                "type": "attraction",
                "interests": ["alam", "fotografi", "sunrise"],
                "duration_hours": 2.5,
                "start_time": "04:30",
                "cost_per_person": 10000,
                "physical_level": "easy",
                "weather_sensitive": True,
                "best_months": [5, 6, 7, 8, 9],
                "vehicle_access": ["motorcycle", "car"],
                "tips": "Alternatif Sikunir yang lebih sepi. Trek lebih mudah.",
                "priority_score": 82,
            },
            {
                "id": "homestay_experience",
                "name": "Homestay Experience di Desa Sembungan",
                "location": "Sembungan",
                "type": "hotel",
                "interests": ["budaya", "santai", "keluarga"],
                "duration_hours": 12.0,
                "start_time": "18:00",
                "cost_per_person": 100000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car"],
                "tips": "Menginap di desa tertinggi Jawa. Interaksi dengan warga lokal.",
                "priority_score": 80,
            },
            {
                "id": "jamu_tradisional",
                "name": "Minum Jamu Tradisional Dieng",
                "location": "Dieng Kulon",
                "type": "food",
                "interests": ["kuliner", "budaya"],
                "duration_hours": 0.5,
                "start_time": "08:00",
                "cost_per_person": 5000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Jamu hangat untuk menghangatkan badan di pagi hari.",
                "priority_score": 55,
            },
            {
                "id": "tahu_tempe_dieng",
                "name": "Wisata Kuliner Tahu & Tempe Dieng",
                "location": "Dieng Kulon",
                "type": "food",
                "interests": ["kuliner"],
                "duration_hours": 1.0,
                "start_time": "12:00",
                "cost_per_person": 20000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Tahu dan tempe khas Dieng yang terkenal di seluruh Jawa.",
                "priority_score": 65,
            },
            {
                "id": "kentang_bakar",
                "name": "Kentang Bakar Pinggir Jalan",
                "location": "Dieng Plateau",
                "type": "food",
                "interests": ["kuliner", "santai"],
                "duration_hours": 0.5,
                "start_time": "16:00",
                "cost_per_person": 10000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Kentang lokal Dieng yang dibakar. Cemilan sore yang hangat.",
                "priority_score": 67,
            },
            {
                "id": "soto_dieng",
                "name": "Soto Khas Dieng",
                "location": "Dieng Kulon",
                "type": "food",
                "interests": ["kuliner"],
                "duration_hours": 1.0,
                "start_time": "19:00",
                "cost_per_person": 18000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Soto hangat untuk makan malam di suhu dingin Dieng.",
                "priority_score": 70,
            },
            {
                "id": "ladang_kentang",
                "name": "Foto di Ladang Kentang Dieng",
                "location": "Sembungan",
                "type": "attraction",
                "interests": ["fotografi", "alam", "keluarga"],
                "duration_hours": 1.0,
                "start_time": "10:00",
                "cost_per_person": 5000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car"],
                "tips": "Ladang kentang yang hijau dan luas. Spot foto Instagramable.",
                "priority_score": 72,
            },
            {
                "id": "workshop_batik",
                "name": "Workshop Batik Dieng",
                "location": "Dieng Kulon",
                "type": "attraction",
                "interests": ["budaya", "edukasi", "keluarga"],
                "duration_hours": 2.0,
                "start_time": "14:00",
                "cost_per_person": 50000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Belajar membatik dengan motif khas Dieng. Bawa pulang hasilnya.",
                "priority_score": 68,
            },
            # DESTINASI SEKITAR WONOSOBO (15 aktivitas)
            {
                "id": "embung_kledung",
                "name": "Embung Kledung",
                "location": "Kledung, Wonosobo",
                "type": "attraction",
                "interests": ["alam", "fotografi", "santai"],
                "duration_hours": 2.0,
                "start_time": "15:00",
                "cost_per_person": 5000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Danau buatan dengan sunset indah. Spot foto hits!",
                "priority_score": 75,
            },
            {
                "id": "waduk_wadaslintang",
                "name": "Waduk Wadaslintang",
                "location": "Wonosobo",
                "type": "attraction",
                "interests": ["alam", "fotografi", "keluarga"],
                "duration_hours": 2.5,
                "start_time": "09:00",
                "cost_per_person": 10000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Waduk terbesar di Wonosobo. Pemandangan pegunungan 360°.",
                "priority_score": 73,
            },
            {
                "id": "curug_pitu",
                "name": "Curug Pitu (7 Air Terjun)",
                "location": "Garung, Wonosobo",
                "type": "attraction",
                "interests": ["alam", "petualangan", "fotografi"],
                "duration_hours": 3.0,
                "start_time": "08:00",
                "cost_per_person": 15000,
                "physical_level": "medium",
                "weather_sensitive": True,
                "best_months": [10, 11, 12, 1, 2],
                "vehicle_access": ["motorcycle", "car"],
                "tips": "Trek moderate 2 km. Air deras saat musim hujan.",
                "priority_score": 78,
            },
            {
                "id": "curug_lawe",
                "name": "Air Terjun Curug Lawe",
                "location": "Wonosobo",
                "type": "attraction",
                "interests": ["alam", "petualangan"],
                "duration_hours": 2.0,
                "start_time": "10:00",
                "cost_per_person": 10000,
                "physical_level": "medium",
                "weather_sensitive": True,
                "best_months": [11, 12, 1, 2, 3],
                "vehicle_access": ["motorcycle", "car"],
                "tips": "Air terjun tersembunyi. Jalur licin saat hujan.",
                "priority_score": 71,
            },
            {
                "id": "kebun_strawberry",
                "name": "Kebun Strawberry Wonosobo",
                "location": "Kejajar",
                "type": "attraction",
                "interests": ["keluarga", "anak", "kuliner"],
                "duration_hours": 1.5,
                "start_time": "10:00",
                "cost_per_person": 30000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": [4, 5, 6, 7, 8, 9],
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Petik langsung strawberry segar. Cocok untuk keluarga.",
                "priority_score": 76,
            },
            {
                "id": "puncak_suroloyo",
                "name": "Puncak Suroloyo",
                "location": "Kulon Progo (dekat Wonosobo)",
                "type": "attraction",
                "interests": ["alam", "sunrise", "fotografi"],
                "duration_hours": 3.0,
                "start_time": "05:00",
                "cost_per_person": 10000,
                "physical_level": "medium",
                "weather_sensitive": True,
                "best_months": [5, 6, 7, 8, 9],
                "vehicle_access": ["motorcycle", "car"],
                "tips": "View 5 gunung: Merapi, Merbabu, Sindoro, Sumbing, Lawu.",
                "priority_score": 80,
            },
            {
                "id": "alun_alun_wonosobo",
                "name": "Alun-alun Wonosobo",
                "location": "Pusat Kota Wonosobo",
                "type": "attraction",
                "interests": ["kuliner", "keluarga", "santai"],
                "duration_hours": 1.5,
                "start_time": "18:00",
                "cost_per_person": 0,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Pusat kota dengan pedagang kaki lima. Ramai malam hari.",
                "priority_score": 68,
            },
            {
                "id": "kampung_batik_wonosobo",
                "name": "Kampung Batik Wonosobo",
                "location": "Wonosobo",
                "type": "attraction",
                "interests": ["budaya", "belanja", "edukasi"],
                "duration_hours": 2.0,
                "start_time": "14:00",
                "cost_per_person": 0,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Sentra batik lokal. Bisa belajar membatik.",
                "priority_score": 66,
            },
            {
                "id": "desa_kalilembu",
                "name": "Desa Wisata Kalilembu",
                "location": "Kalilembu, Wonosobo",
                "type": "attraction",
                "interests": ["budaya", "keluarga", "edukasi"],
                "duration_hours": 2.5,
                "start_time": "10:00",
                "cost_per_person": 25000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car"],
                "tips": "Desa wisata dengan aktivitas pertanian tradisional.",
                "priority_score": 70,
            },
            {
                "id": "sentra_bambu",
                "name": "Sentra Kerajinan Bambu",
                "location": "Wonosobo",
                "type": "attraction",
                "interests": ["budaya", "belanja"],
                "duration_hours": 1.0,
                "start_time": "15:00",
                "cost_per_person": 0,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Kerajinan bambu khas Wonosobo. Harga terjangkau.",
                "priority_score": 62,
            },
            {
                "id": "pasar_malam_wonosobo",
                "name": "Pasar Malam Wonosobo",
                "location": "Wonosobo",
                "type": "attraction",
                "interests": ["kuliner", "keluarga", "santai"],
                "duration_hours": 2.0,
                "start_time": "19:00",
                "cost_per_person": 50000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Pasar malam dengan aneka jajanan dan permainan.",
                "priority_score": 69,
            },
            {
                "id": "pabrik_tahu",
                "name": "Pabrik Tahu Baxo Wonosobo",
                "location": "Wonosobo",
                "type": "attraction",
                "interests": ["kuliner", "edukasi"],
                "duration_hours": 1.0,
                "start_time": "09:00",
                "cost_per_person": 10000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Tour pabrik tahu legendaris. Beli langsung di pabrik.",
                "priority_score": 64,
            },
            {
                "id": "taman_kyai_langgeng",
                "name": "Taman Kyai Langgeng",
                "location": "Magelang (dekat Wonosobo)",
                "type": "attraction",
                "interests": ["keluarga", "anak", "santai"],
                "duration_hours": 3.0,
                "start_time": "10:00",
                "cost_per_person": 20000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["car", "bus"],
                "tips": "Taman wisata keluarga. Ada kebun binatang mini.",
                "priority_score": 72,
            },
            {
                "id": "museum_kartini",
                "name": "Museum Kartini Wonosobo",
                "location": "Wonosobo",
                "type": "attraction",
                "interests": ["budaya", "sejarah", "edukasi"],
                "duration_hours": 1.0,
                "start_time": "10:00",
                "cost_per_person": 5000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Museum sejarah R.A. Kartini. Cocok saat hujan.",
                "priority_score": 58,
            },
            {
                "id": "kalianget_heritage",
                "name": "Kalianget Heritage Trail",
                "location": "Wonosobo",
                "type": "attraction",
                "interests": ["budaya", "sejarah", "fotografi"],
                "duration_hours": 1.5,
                "start_time": "14:00",
                "cost_per_person": 10000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Jalur heritage Belanda era kolonial.",
                "priority_score": 65,
            },
            
            # KULINER KHAS (20 aktivitas)
            {
                "id": "mie_ongklok_pakdhe",
                "name": "Warung Mie Ongklok Pak Dhe",
                "location": "Wonosobo",
                "type": "food",
                "interests": ["kuliner"],
                "duration_hours": 1.0,
                "start_time": "12:00",
                "cost_per_person": 15000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Mie ongklok paling legendaris di Wonosobo.",
                "priority_score": 80,
            },
            {
                "id": "sate_kelinci",
                "name": "Sate Kelinci Pak Joko",
                "location": "Dieng Kulon",
                "type": "food",
                "interests": ["kuliner"],
                "duration_hours": 1.0,
                "start_time": "19:00",
                "cost_per_person": 35000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Sate kelinci khas Dieng. Daging empuk bumbu kacang.",
                "priority_score": 78,
            },
            {
                "id": "pecel_lele",
                "name": "Pecel Lele Dieng",
                "location": "Dieng Plateau",
                "type": "food",
                "interests": ["kuliner"],
                "duration_hours": 1.0,
                "start_time": "18:00",
                "cost_per_person": 20000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Lele goreng sambal segar. Cocok untuk makan malam.",
                "priority_score": 70,
            },
            {
                "id": "nasi_goreng_kambing",
                "name": "Nasi Goreng Kambing Wonosobo",
                "location": "Wonosobo",
                "type": "food",
                "interests": ["kuliner"],
                "duration_hours": 1.0,
                "start_time": "20:00",
                "cost_per_person": 25000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Nasi goreng kambing dengan bumbu khas. Buka malam.",
                "priority_score": 72,
            },
            {
                "id": "ayam_geprek",
                "name": "Ayam Geprek Dieng",
                "location": "Dieng Kulon",
                "type": "food",
                "interests": ["kuliner"],
                "duration_hours": 1.0,
                "start_time": "19:00",
                "cost_per_person": 18000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Ayam geprek pedas hangat. Level sambal bisa request.",
                "priority_score": 68,
            },
            {
                "id": "bakso_urat",
                "name": "Bakso Urat Wonosobo",
                "location": "Wonosobo",
                "type": "food",
                "interests": ["kuliner"],
                "duration_hours": 1.0,
                "start_time": "12:00",
                "cost_per_person": 15000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Bakso urat kenyal dengan kuah hangat. Cocok saat dingin.",
                "priority_score": 69,
            },
            {
                "id": "sop_buntut",
                "name": "Sop Buntut Pak Kumis",
                "location": "Wonosobo",
                "type": "food",
                "interests": ["kuliner"],
                "duration_hours": 1.0,
                "start_time": "12:00",
                "cost_per_person": 40000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Sop buntut premium dengan daging empuk.",
                "priority_score": 75,
            },
            {
                "id": "gudeg_yudjum",
                "name": "Gudeg Yu Djum Cabang Wonosobo",
                "location": "Wonosobo",
                "type": "food",
                "interests": ["kuliner"],
                "duration_hours": 1.0,
                "start_time": "11:00",
                "cost_per_person": 22000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Gudeg khas Jogja. Tersedia di Wonosobo.",
                "priority_score": 71,
            },
            {
                "id": "wedang_uwuh",
                "name": "Wedang Uwuh Tradisional",
                "location": "Dieng Kulon",
                "type": "food",
                "interests": ["kuliner", "budaya"],
                "duration_hours": 0.5,
                "start_time": "17:00",
                "cost_per_person": 8000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Minuman rempah hangat khas Jawa. Menghangatkan badan.",
                "priority_score": 67,
            },
            {
                "id": "es_dawet",
                "name": "Es Dawet Ayu Wonosobo",
                "location": "Wonosobo",
                "type": "food",
                "interests": ["kuliner"],
                "duration_hours": 0.5,
                "start_time": "14:00",
                "cost_per_person": 7000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": [4, 5, 6, 7, 8, 9, 10],
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Es dawet segar dengan gula merah. Cocok siang hari.",
                "priority_score": 66,
            },
            {
                "id": "kopi_jos",
                "name": "Kopi Jos Wonosobo",
                "location": "Wonosobo",
                "type": "food",
                "interests": ["kuliner"],
                "duration_hours": 0.5,
                "start_time": "19:00",
                "cost_per_person": 8000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Kopi diseduh dengan arang panas. Sensasi unik!",
                "priority_score": 73,
            },
            {
                "id": "carica_factory",
                "name": "Carica Original Factory Tour",
                "location": "Wonosobo",
                "type": "food",
                "interests": ["kuliner", "edukasi"],
                "duration_hours": 1.5,
                "start_time": "10:00",
                "cost_per_person": 20000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Tour pabrik carica + tasting. Beli langsung di pabrik.",
                "priority_score": 74,
            },
            {
                "id": "tempe_mendoan_asli",
                "name": "Tempe Mendoan Asli Dieng",
                "location": "Dieng Kulon",
                "type": "food",
                "interests": ["kuliner"],
                "duration_hours": 0.5,
                "start_time": "16:00",
                "cost_per_person": 5000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Tempe mendoan crispy khas Dieng. Cemilan sore.",
                "priority_score": 68,
            },
            {
                "id": "sate_maranggi",
                "name": "Sate Maranggi Dieng",
                "location": "Dieng Plateau",
                "type": "food",
                "interests": ["kuliner"],
                "duration_hours": 1.0,
                "start_time": "19:00",
                "cost_per_person": 30000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Sate daging sapi bumbu khas Purwakarta.",
                "priority_score": 71,
            },
            {
                "id": "nasi_liwet",
                "name": "Nasi Liwet Bu Tini",
                "location": "Wonosobo",
                "type": "food",
                "interests": ["kuliner"],
                "duration_hours": 1.0,
                "start_time": "12:00",
                "cost_per_person": 18000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Nasi liwet Solo style. Porsi besar dan mengenyangkan.",
                "priority_score": 70,
            },
            {
                "id": "ikan_bakar_telaga",
                "name": "Ikan Bakar Telaga",
                "location": "Telaga Menjer",
                "type": "food",
                "interests": ["kuliner", "alam"],
                "duration_hours": 1.5,
                "start_time": "12:00",
                "cost_per_person": 40000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Ikan bakar segar dari Telaga Menjer. View danau.",
                "priority_score": 76,
            },
            {
                "id": "sup_ikan_mas",
                "name": "Sup Ikan Mas Telaga Menjer",
                "location": "Telaga Menjer",
                "type": "food",
                "interests": ["kuliner"],
                "duration_hours": 1.0,
                "start_time": "12:00",
                "cost_per_person": 35000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Sup ikan mas segar dengan kuah bening.",
                "priority_score": 72,
            },
            {
                "id": "warung_tenda_malam",
                "name": "Warung Tenda Malam Hari",
                "location": "Alun-alun Wonosobo",
                "type": "food",
                "interests": ["kuliner", "santai"],
                "duration_hours": 1.5,
                "start_time": "20:00",
                "cost_per_person": 25000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Aneka makanan malam di tenda. Suasana ramai.",
                "priority_score": 69,
            },
            {
                "id": "street_food_tour",
                "name": "Street Food Tour Wonosobo",
                "location": "Wonosobo",
                "type": "food",
                "interests": ["kuliner", "budaya"],
                "duration_hours": 2.0,
                "start_time": "18:00",
                "cost_per_person": 50000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Tour jajanan kaki lima Wonosobo. Guided tour tersedia.",
                "priority_score": 74,
            },
            {
                "id": "cafe_modern_dieng",
                "name": "Coffee Shop Modern Dieng",
                "location": "Dieng Kulon",
                "type": "food",
                "interests": ["kuliner", "santai", "fotografi"],
                "duration_hours": 1.5,
                "start_time": "15:00",
                "cost_per_person": 35000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Cafe modern dengan view pegunungan. Instagramable.",
                "priority_score": 75,
            },
            
            # FOTOGRAFI & INSTAGRAMABLE (15 aktivitas)
            {
                "id": "spot_edelweiss",
                "name": "Spot Foto Bunga Edelweiss",
                "location": "Jalur Prau",
                "type": "attraction",
                "interests": ["fotografi", "alam"],
                "duration_hours": 1.0,
                "start_time": "11:00",
                "cost_per_person": 5000,
                "physical_level": "medium",
                "weather_sensitive": True,
                "best_months": [6, 7, 8, 9],
                "vehicle_access": ["motorcycle"],
                "tips": "Bunga edelweiss endemik. Jangan dipetik (dilindungi)!",
                "priority_score": 77,
            },
            {
                "id": "instagram_telaga_warna",
                "name": "Instagram Spot Telaga Warna",
                "location": "Telaga Warna",
                "type": "attraction",
                "interests": ["fotografi", "alam"],
                "duration_hours": 0.5,
                "start_time": "10:00",
                "cost_per_person": 0,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Spot foto dengan frame telaga berwarna. Free!",
                "priority_score": 79,
            },
            {
                "id": "spot_sunset_gardu",
                "name": "Spot Sunset Gardu Pandang",
                "location": "Gardu Pandang Tieng",
                "type": "attraction",
                "interests": ["fotografi", "alam", "sunset"],
                "duration_hours": 1.0,
                "start_time": "17:00",
                "cost_per_person": 5000,
                "physical_level": "easy",
                "weather_sensitive": True,
                "best_months": [5, 6, 7, 8, 9],
                "vehicle_access": ["motorcycle", "car"],
                "tips": "Golden hour terbaik pukul 17:00-18:00.",
                "priority_score": 78,
            },
            {
                "id": "selfie_point_sikidang",
                "name": "Selfie Point Kawah Sikidang",
                "location": "Kawah Sikidang",
                "type": "attraction",
                "interests": ["fotografi"],
                "duration_hours": 0.5,
                "start_time": "10:00",
                "cost_per_person": 0,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Selfie dengan latar kawah aktif. Jaga jarak aman!",
                "priority_score": 74,
            },
            {
                "id": "ladang_bunga_matahari",
                "name": "Foto Ladang Bunga Matahari",
                "location": "Dieng Plateau",
                "type": "attraction",
                "interests": ["fotografi", "alam", "keluarga"],
                "duration_hours": 1.0,
                "start_time": "09:00",
                "cost_per_person": 10000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": [2, 3, 7, 8],
                "vehicle_access": ["motorcycle", "car"],
                "tips": "Ladang bunga matahari seasonal. Cek jadwal tanam.",
                "priority_score": 76,
            },
            {
                "id": "negeri_awan",
                "name": "Spot Foto Negeri Di Atas Awan",
                "location": "Sikunir",
                "type": "attraction",
                "interests": ["fotografi", "alam", "sunrise"],
                "duration_hours": 2.0,
                "start_time": "05:00",
                "cost_per_person": 15000,
                "physical_level": "medium",
                "weather_sensitive": True,
                "best_months": [5, 6, 7, 8, 9],
                "vehicle_access": ["motorcycle", "car"],
                "tips": "Foto di atas awan saat sunrise. Magic moment!",
                "priority_score": 85,
            },
            {
                "id": "cafe_instagramable_dieng",
                "name": "Instagramable Cafe Dieng",
                "location": "Dieng Kulon",
                "type": "food",
                "interests": ["fotografi", "kuliner", "santai"],
                "duration_hours": 1.5,
                "start_time": "15:00",
                "cost_per_person": 40000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Cafe dengan interior kekinian. Spot foto indoor.",
                "priority_score": 73,
            },
            {
                "id": "spot_foto_kebun_teh",
                "name": "Spot Foto Kebun Teh Tambi",
                "location": "Tambi, Kejajar",
                "type": "attraction",
                "interests": ["fotografi", "alam"],
                "duration_hours": 1.0,
                "start_time": "09:00",
                "cost_per_person": 5000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Hamparan hijau kebun teh. Pagi lebih segar.",
                "priority_score": 78,
            },
            {
                "id": "sunrise_point_alt",
                "name": "Sunrise Point Alternatif",
                "location": "Bukit Pangonan",
                "type": "attraction",
                "interests": ["fotografi", "sunrise", "alam"],
                "duration_hours": 2.5,
                "start_time": "04:30",
                "cost_per_person": 10000,
                "physical_level": "medium",
                "weather_sensitive": True,
                "best_months": [5, 6, 7, 8, 9],
                "vehicle_access": ["motorcycle", "car"],
                "tips": "Alternatif Sikunir yang lebih sepi. View sama indah.",
                "priority_score": 81,
            },
            {
                "id": "milky_way_spot",
                "name": "Milky Way Photography Spot",
                "location": "Sembungan",
                "type": "attraction",
                "interests": ["fotografi", "alam", "astrofotografi"],
                "duration_hours": 3.0,
                "start_time": "23:00",
                "cost_per_person": 0,
                "physical_level": "easy",
                "weather_sensitive": True,
                "best_months": [4, 5, 6, 7, 8, 9],
                "vehicle_access": ["motorcycle", "car"],
                "tips": "Langit gelap minim polusi cahaya. Bawa tripod!",
                "priority_score": 82,
            },
            {
                "id": "spot_sindoro_sumbing",
                "name": "Spot Foto Latar Sindoro-Sumbing",
                "location": "Dieng Plateau",
                "type": "attraction",
                "interests": ["fotografi", "alam"],
                "duration_hours": 0.5,
                "start_time": "08:00",
                "cost_per_person": 0,
                "physical_level": "easy",
                "weather_sensitive": True,
                "best_months": [5, 6, 7, 8, 9],
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "View 2 gunung kembar. Pagi cerah best time.",
                "priority_score": 75,
            },
            {
                "id": "traditional_village_photo",
                "name": "Traditional Village Photo Tour",
                "location": "Sembungan",
                "type": "attraction",
                "interests": ["fotografi", "budaya"],
                "duration_hours": 2.0,
                "start_time": "10:00",
                "cost_per_person": 15000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car"],
                "tips": "Foto aktivitas warga desa. Minta izin sebelum foto.",
                "priority_score": 72,
            },
            {
                "id": "rumah_hobbit",
                "name": "Spot Foto Rumah Hobbit Dieng",
                "location": "Dieng Kulon",
                "type": "attraction",
                "interests": ["fotografi", "keluarga"],
                "duration_hours": 0.5,
                "start_time": "10:00",
                "cost_per_person": 5000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Rumah berbentuk hobbit. Spot foto unik.",
                "priority_score": 70,
            },
            {
                "id": "vintage_bridge",
                "name": "Instagramable Bridge Wonosobo",
                "location": "Wonosobo",
                "type": "attraction",
                "interests": ["fotografi"],
                "duration_hours": 0.5,
                "start_time": "15:00",
                "cost_per_person": 0,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Jembatan klasik era Belanda. Spot foto vintage.",
                "priority_score": 68,
            },
            {
                "id": "spot_foto_vintage",
                "name": "Spot Foto Vintage Dieng",
                "location": "Dieng Kulon",
                "type": "attraction",
                "interests": ["fotografi"],
                "duration_hours": 1.0,
                "start_time": "14:00",
                "cost_per_person": 10000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Properti vintage untuk foto. Sewa kostum tersedia.",
                "priority_score": 71,
            },
            
            # AKTIVITAS KELUARGA & ANAK (10 aktivitas)
            {
                "id": "playground_wonosobo",
                "name": "Playground Taman Kota Wonosobo",
                "location": "Wonosobo",
                "type": "attraction",
                "interests": ["keluarga", "anak"],
                "duration_hours": 2.0,
                "start_time": "15:00",
                "cost_per_person": 5000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Taman bermain anak lengkap. Cocok sore hari.",
                "priority_score": 65,
            },
            {
                "id": "mini_zoo",
                "name": "Mini Zoo Wonosobo",
                "location": "Wonosobo",
                "type": "attraction",
                "interests": ["keluarga", "anak", "edukasi"],
                "duration_hours": 1.5,
                "start_time": "10:00",
                "cost_per_person": 15000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Kebun binatang mini. Bisa kasih makan hewan.",
                "priority_score": 70,
            },
            {
                "id": "kolam_renang_anak",
                "name": "Kolam Renang Anak Kalianget",
                "location": "Wonosobo",
                "type": "attraction",
                "interests": ["keluarga", "anak", "santai"],
                "duration_hours": 2.0,
                "start_time": "10:00",
                "cost_per_person": 20000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": [3, 4, 5, 6, 7, 8, 9, 10],
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Kolam renang air hangat. Aman untuk anak.",
                "priority_score": 72,
            },
            {
                "id": "naik_kuda_telaga",
                "name": "Naik Kuda Keliling Telaga",
                "location": "Telaga Menjer",
                "type": "attraction",
                "interests": ["keluarga", "anak", "petualangan"],
                "duration_hours": 1.0,
                "start_time": "10:00",
                "cost_per_person": 25000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Menunggang kuda untuk anak. Didampingi pemandu.",
                "priority_score": 74,
            },
            {
                "id": "peternakan_sapi",
                "name": "Peternakan Sapi Perah Edukasi",
                "location": "Kejajar",
                "type": "attraction",
                "interests": ["keluarga", "anak", "edukasi"],
                "duration_hours": 1.5,
                "start_time": "09:00",
                "cost_per_person": 20000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car"],
                "tips": "Belajar memerah susu sapi. Minum susu segar.",
                "priority_score": 73,
            },
            {
                "id": "mewarnai_gerabah",
                "name": "Mewarnai Gerabah Tradisional",
                "location": "Wonosobo",
                "type": "attraction",
                "interests": ["keluarga", "anak", "budaya"],
                "duration_hours": 1.5,
                "start_time": "14:00",
                "cost_per_person": 25000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Workshop mewarnai gerabah. Bawa pulang hasil karya.",
                "priority_score": 68,
            },
            {
                "id": "story_telling_dieng",
                "name": "Story Telling Legenda Dieng",
                "location": "Dieng Theater",
                "type": "attraction",
                "interests": ["keluarga", "anak", "budaya"],
                "duration_hours": 1.0,
                "start_time": "15:00",
                "cost_per_person": 15000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Dongeng legenda Dieng untuk anak. Interaktif.",
                "priority_score": 66,
            },
            {
                "id": "kids_workshop_carica",
                "name": "Kids Workshop Membuat Carica",
                "location": "Wonosobo",
                "type": "attraction",
                "interests": ["keluarga", "anak", "edukasi"],
                "duration_hours": 1.5,
                "start_time": "10:00",
                "cost_per_person": 30000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Anak belajar proses membuat carica. Fun & edukatif.",
                "priority_score": 70,
            },
            {
                "id": "layang_layang_savana",
                "name": "Bermain Layang-layang di Savana",
                "location": "Padang Savana Dieng",
                "type": "attraction",
                "interests": ["keluarga", "anak", "alam"],
                "duration_hours": 1.5,
                "start_time": "14:00",
                "cost_per_person": 10000,
                "physical_level": "easy",
                "weather_sensitive": True,
                "best_months": [5, 6, 7, 8, 9],
                "vehicle_access": ["motorcycle", "car"],
                "tips": "Angin kencang ideal untuk layang-layang. Sewa tersedia.",
                "priority_score": 71,
            },
            {
                "id": "family_picnic",
                "name": "Family Picnic Area Telaga Dringo",
                "location": "Telaga Dringo",
                "type": "attraction",
                "interests": ["keluarga", "santai"],
                "duration_hours": 2.0,
                "start_time": "11:00",
                "cost_per_person": 5000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car"],
                "tips": "Area piknik keluarga di tepi telaga. Bawa bekal.",
                "priority_score": 69,
            },
            
            # RELAKSASI & WELLNESS (5 aktivitas)
            {
                "id": "spa_jamu_tradisional",
                "name": "Spa Tradisional Jamu",
                "location": "Wonosobo",
                "type": "attraction",
                "interests": ["relaksasi", "budaya"],
                "duration_hours": 2.0,
                "start_time": "14:00",
                "cost_per_person": 75000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Spa dengan ramuan jamu tradisional. Sangat rileks.",
                "priority_score": 74,
            },
            {
                "id": "yoga_sunrise",
                "name": "Yoga Sunrise di Sikunir",
                "location": "Bukit Sikunir",
                "type": "attraction",
                "interests": ["relaksasi", "alam", "sunrise"],
                "duration_hours": 2.0,
                "start_time": "05:00",
                "cost_per_person": 50000,
                "physical_level": "medium",
                "weather_sensitive": True,
                "best_months": [5, 6, 7, 8, 9],
                "vehicle_access": ["motorcycle", "car"],
                "tips": "Yoga session saat sunrise. Instruktur tersedia.",
                "priority_score": 78,
            },
            {
                "id": "meditation_retreat",
                "name": "Meditation Retreat Dieng",
                "location": "Sembungan",
                "type": "attraction",
                "interests": ["relaksasi", "spiritual"],
                "duration_hours": 3.0,
                "start_time": "06:00",
                "cost_per_person": 100000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car"],
                "tips": "Meditasi guided di ketinggian. Tenang & damai.",
                "priority_score": 72,
            },
            {
                "id": "hot_stone_massage",
                "name": "Hot Stone Massage Dieng",
                "location": "Dieng Kulon",
                "type": "attraction",
                "interests": ["relaksasi"],
                "duration_hours": 1.5,
                "start_time": "15:00",
                "cost_per_person": 85000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Massage dengan batu panas. Ideal setelah trekking.",
                "priority_score": 73,
            },
            {
                "id": "reflexology_wonosobo",
                "name": "Reflexology Wonosobo",
                "location": "Wonosobo",
                "type": "attraction",
                "interests": ["relaksasi"],
                "duration_hours": 1.0,
                "start_time": "18:00",
                "cost_per_person": 50000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Pijat refleksi kaki. Menghilangkan pegal setelah jalan.",
                "priority_score": 70,
            },
            
            # BUDAYA & EDUKASI (5 aktivitas)
            {
                "id": "pabrik_kecap",
                "name": "Kunjungan Pabrik Kecap",
                "location": "Wonosobo",
                "type": "attraction",
                "interests": ["budaya", "edukasi"],
                "duration_hours": 1.5,
                "start_time": "10:00",
                "cost_per_person": 15000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Tour pabrik kecap tradisional. Beli langsung di pabrik.",
                "priority_score": 64,
            },
            {
                "id": "gamelan_music",
                "name": "Belajar Musik Gamelan",
                "location": "Wonosobo",
                "type": "attraction",
                "interests": ["budaya", "edukasi"],
                "duration_hours": 2.0,
                "start_time": "14:00",
                "cost_per_person": 40000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Workshop gamelan Jawa. Belajar memainkan gamelan.",
                "priority_score": 67,
            },
            {
                "id": "traditional_dance",
                "name": "Traditional Dance Performance",
                "location": "Dieng Theater",
                "type": "attraction",
                "interests": ["budaya", "keluarga"],
                "duration_hours": 1.0,
                "start_time": "19:00",
                "cost_per_person": 25000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Pertunjukan tari tradisional Jawa. Weekend only.",
                "priority_score": 69,
            },
            {
                "id": "pottery_making",
                "name": "Pottery Making Class",
                "location": "Wonosobo",
                "type": "attraction",
                "interests": ["budaya", "edukasi", "keluarga"],
                "duration_hours": 2.0,
                "start_time": "10:00",
                "cost_per_person": 35000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Belajar membuat gerabah dari tanah liat. Hands-on.",
                "priority_score": 68,
            },
            {
                "id": "cooking_class",
                "name": "Local Cooking Class",
                "location": "Dieng Kulon",
                "type": "attraction",
                "interests": ["budaya", "kuliner", "edukasi"],
                "duration_hours": 3.0,
                "start_time": "09:00",
                "cost_per_person": 75000,
                "physical_level": "easy",
                "weather_sensitive": False,
                "best_months": list(range(1, 13)),
                "vehicle_access": ["motorcycle", "car", "bus"],
                "tips": "Belajar masak makanan khas Dieng. Makan hasil masakan.",
                "priority_score": 76,
            },
        ]

    
    def _build_route_graph(self) -> Dict[str, List[str]]:
        """Graf routing untuk menentukan urutan aktivitas yang efisien."""
        return {
            "Dieng Kulon": ["Dieng Wetan", "Sembungan", "Wonosobo"],
            "Dieng Wetan": ["Dieng Kulon", "Kepakisan", "Sembungan"],
            "Sembungan": ["Dieng Kulon", "Dieng Wetan"],
            "Wonosobo": ["Dieng Kulon", "Kejajar", "Garung"],
            "Kejajar": ["Wonosobo", "Dieng Kulon"],
            "Kepakisan": ["Dieng Wetan"],
            "Garung": ["Wonosobo"],
        }
    
    def generate_smart_itinerary(
        self,
        duration_days: int,
        budget_per_day: int,
        interests: List[str],
        travel_style: str,
        vehicle: str,
        weather_condition: str = "normal",
        current_month: int = None,
    ) -> Dict[str, Any]:
        """
        Generate itinerary cerdas berdasarkan preferensi user tanpa API AI.
        
        Args:
            duration_days: Jumlah hari trip (1-10)
            budget_per_day: Budget harian per orang (Rp)
            interests: List minat ["alam", "budaya", "kuliner", etc]
            travel_style: "solo", "couple", "family", "group"
            vehicle: "motorcycle", "car", "bus"
            weather_condition: "cerah", "hujan", "kabut"
            current_month: Bulan saat ini (1-12)
        """
        if current_month is None:
            current_month = datetime.now().month
        
        # Filter aktivitas sesuai kriteria
        filtered = self._filter_activities(
            interests, vehicle, weather_condition, current_month
        )
        
        # Score dan rank aktivitas
        scored = self._score_activities(
            filtered, budget_per_day, travel_style, weather_condition
        )
        
        # Generate daily plans
        daily_plans = self._build_daily_plans(
            scored, duration_days, budget_per_day, weather_condition
        )
        
        return {
            "days": daily_plans,
            "meta": {
                "source": "ml_model" if self.model_loaded else "rule_based",
                "model_type": "Random Forest Regressor" if self.model_loaded else "Rule-based Scoring",
                "requestedDays": duration_days,
                "totalCost": sum(d.get("daily_cost", 0) for d in daily_plans),
                "message": f"Itinerary generated by {'ML Recommendation Model' if self.model_loaded else 'Rule-based System'}",
            }
        }
    
    def _filter_activities(
        self, interests, vehicle, weather, month
    ) -> List[Dict]:
        """Filter aktivitas yang sesuai dengan preferensi."""
        filtered = []
        for act in self.activities_db:
            # Filter by vehicle access
            if vehicle not in act.get("vehicle_access", []):
                continue
            
            # Filter by weather sensitivity
            if weather in ["hujan", "kabut"] and act.get("weather_sensitive", False):
                continue
            
            # Filter by season (best_months)
            if month not in act.get("best_months", list(range(1, 13))):
                act = act.copy()
                act["priority_score"] -= 10  # penalty tapi tetap masuk
            
            # Boost score if interest matches
            matched_interests = set(interests) & set(act.get("interests", []))
            if interests and matched_interests:
                act = act.copy()
                act["priority_score"] += len(matched_interests) * 5
            
            filtered.append(act)
        
        return filtered
    
    def _score_activities(
        self, activities, budget, travel_style, weather
    ) -> List[Dict]:
        """
        Score dan rank aktivitas menggunakan ML model (jika tersedia).
        Fallback ke rule-based jika model belum di-train.
        """
        if self.model_loaded:
            return self._score_activities_ml(activities, budget, travel_style, weather)
        else:
            return self._score_activities_rulebased(activities, budget, travel_style, weather)
    
    def _score_activities_ml(
        self, activities, budget, travel_style, weather
    ) -> List[Dict]:
        """Score activities menggunakan trained ML model."""
        # Determine budget level
        if budget < 400_000:
            budget_level = 'low'
        elif budget < 1_000_000:
            budget_level = 'medium'
        else:
            budget_level = 'high'
        
        scored = []
        for act in activities:
            # Prepare features for ML model
            interest_match = 0  # Will be updated by caller
            
            try:
                # Encode categorical variables
                budget_enc = self.label_encoders['budget'].transform([budget_level])[0]
                style_enc = self.label_encoders['style'].transform([travel_style])[0]
                vehicle_enc = self.label_encoders['vehicle'].transform([act.get('vehicle_access', ['car'])[0]])[0]
                type_enc = self.label_encoders['type'].transform([act['type']])[0]
                physical_enc = self.label_encoders['physical'].transform([act['physical_level']])[0]
            except:
                # Fallback to default values if encoding fails
                budget_enc = 0
                style_enc = 0
                vehicle_enc = 0
                type_enc = 0
                physical_enc = 0
            
            # Build feature vector
            features = np.array([[
                act['cost_per_person'],
                act['duration_hours'],
                act['priority_score'],
                int(act['weather_sensitive']),
                budget,
                interest_match,  # placeholder
                1,  # vehicle_compatible (already filtered)
                budget_enc,
                style_enc,
                vehicle_enc,
                type_enc,
                physical_enc,
            ]])
            
            # Scale features
            features_scaled = self.scaler.transform(features)
            
            # Predict rating (1-5)
            predicted_rating = self.ml_model.predict(features_scaled)[0]
            
            # Convert rating to score (0-100)
            ml_score = predicted_rating * 20  # 5 stars = 100 points
            
            act = act.copy()
            act["final_score"] = float(ml_score)
            act["ml_rating"] = round(float(predicted_rating), 2)
            scored.append(act)
        
        # Sort by final score
        scored.sort(key=lambda x: x["final_score"], reverse=True)
        return scored
    
    def _score_activities_rulebased(
        self, activities, budget, travel_style, weather
    ) -> List[Dict]:
        """Score activities using rule-based system (fallback)."""
        scored = []
        for act in activities:
            score = act["priority_score"]
            cost = act.get("cost_per_person", 0)
            
            # Budget consideration
            if cost > budget * 0.5:
                score -= 20
            elif cost < budget * 0.2:
                score += 10
            
            # Travel style adjustment
            physical = act.get("physical_level", "easy")
            if travel_style == "family":
                if physical == "easy":
                    score += 15
                elif physical == "hard":
                    score -= 20
            elif travel_style == "solo" and physical == "hard":
                score += 10
            
            # Weather bonus
            if weather in ["hujan", "kabut"]:
                if not act.get("weather_sensitive", False):
                    score += 15
            
            act = act.copy()
            act["final_score"] = score
            scored.append(act)
        
        # Sort by final score
        scored.sort(key=lambda x: x["final_score"], reverse=True)
        return scored
    
    def _build_daily_plans(
        self, activities, days, budget, weather
    ) -> List[Dict]:
        """Build rencana harian dengan distribusi aktivitas yang seimbang."""
        daily_plans = []
        used_activities = set()
        
        for day_num in range(1, days + 1):
            day_activities = []
            day_cost = 0
            current_hour = 7  # Mulai jam 7 pagi
            
            # Alokasi 3-5 aktivitas per hari
            target_activities = 4 if day_num <= 3 else 3
            
            for act in activities:
                if act["id"] in used_activities:
                    continue
                
                # Budget check
                if day_cost + act.get("cost_per_person", 0) > budget * 1.2:
                    continue
                
                # Time check (jangan melebihi jam 18:00)
                if current_hour + act["duration_hours"] > 18:
                    continue
                
                # Special: Sunrise activities hanya hari 2-3
                if "sunrise" in act.get("interests", []) and day_num not in [2, 3]:
                    continue
                
                # Special: Trekking berat hanya hari 3-5 (setelah aklimatisasi)
                if act.get("physical_level") == "hard" and day_num < 3:
                    continue
                
                # Add activity
                time_str = f"{int(current_hour):02d}:{int((current_hour % 1) * 60):02d}"
                day_activities.append({
                    "time": time_str,
                    "name": act["name"],
                    "location": act["location"],
                    "duration": f"{act['duration_hours']:.1f} jam",
                    "type": act["type"],
                    "note": act.get("tips", ""),
                    "cost": act.get("cost_per_person", 0),
                    "weatherOk": not act.get("weather_sensitive", False) or weather == "cerah",
                })
                
                used_activities.add(act["id"])
                day_cost += act.get("cost_per_person", 0)
                current_hour += act["duration_hours"]
                
                if len(day_activities) >= target_activities:
                    break
            
            # Ensure at least 1 meal
            if not any(a["type"] == "food" for a in day_activities):
                meal = {
                    "time": "12:00",
                    "name": "Makan Siang Lokal",
                    "location": "Dieng Plateau",
                    "duration": "1 jam",
                    "type": "food",
                    "note": "Coba kuliner khas Dieng",
                    "cost": 25000,
                    "weatherOk": True,
                }
                day_activities.insert(len(day_activities) // 2, meal)
                day_cost += 25000
            
            daily_plans.append({
                "day": day_num,
                "date": f"Hari ke-{day_num}",
                "weather": self._get_weather_context(weather),
                "warning": self._get_weather_warning(weather),
                "activities": day_activities,
                "daily_cost": day_cost,
            })
        
        return daily_plans
    
    def _get_weather_context(self, weather: str) -> Dict:
        """Generate weather context untuk display."""
        contexts = {
            "cerah": {
                "icon": "☀️",
                "condition": "Cerah",
                "temp": "15°C",
                "rain": 10,
            },
            "hujan": {
                "icon": "🌧️",
                "condition": "Hujan",
                "temp": "12°C",
                "rain": 80,
            },
            "kabut": {
                "icon": "🌫️",
                "condition": "Berkabut",
                "temp": "10°C",
                "rain": 30,
            },
            "normal": {
                "icon": "⛅",
                "condition": "Berawan",
                "temp": "14°C",
                "rain": 25,
            },
        }
        return contexts.get(weather, contexts["normal"])
    
    def _get_weather_warning(self, weather: str) -> str:
        """Generate weather warning jika perlu."""
        warnings = {
            "hujan": "⚠️ Hujan terpantau. Utamakan aktivitas indoor dan hindari jalur licin.",
            "kabut": "⚠️ Kabut tebal berpotensi mengganggu visibilitas. Berkendara hati-hati.",
        }
        return warnings.get(weather, "")


# Singleton instance
_engine = None

def get_itinerary_engine():
    global _engine
    if _engine is None:
        _engine = DiengItineraryEngine()
    return _engine
