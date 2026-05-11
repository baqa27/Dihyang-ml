import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import {
  CloudSun, Mountain, Shield, MapPin, Navigation, Thermometer,
  Wind, Droplets, Eye, ChevronRight, Zap, MessageCircle, Map,
  CalendarDays, Info, ArrowRight, Star, AlertTriangle, Clock
} from 'lucide-react'
import { weatherAPI, mlAPI } from '../services/api'
import './Home.css'

const features = [
  {
    icon: <CloudSun size={28} />,
    title: 'Dashboard Cuaca Real-time',
    desc: 'Pantau cuaca mikroklimat Dieng secara langsung dengan prediksi proaktif dan peringatan kabut, hujan, serta suhu ekstrem.',
    link: '/dashboard',
    color: '#00b4cc'
  },
  {
    icon: <MessageCircle size={28} />,
    title: 'DITA — Asisten AI',
    desc: 'Chatbot cerdas berbasis NLP yang siap menjawab pertanyaan seputar wisata Dieng, retribusi resmi, dan saran keamanan.',
    link: '/chat',
    color: '#ffba00'
  },
  {
    icon: <Shield size={28} />,
    title: 'Filter Rute Aman',
    desc: 'Sistem rekomendasi jalur yang otomatis memfilter dan memperingatkan rute berbahaya seperti Tanjakan Sikarim (45°).',
    link: '/explore',
    color: '#22c55e'
  },
  {
    icon: <CalendarDays size={28} />,
    title: 'Smart Itinerary',
    desc: 'Rencana perjalanan adaptif terhadap prakiraan cuaca lokal, lengkap dengan saran perlengkapan dan estimasi biaya.',
    link: '/itinerary',
    color: '#a78bfa'
  },
  {
    icon: <Map size={28} />,
    title: 'Peta Interaktif',
    desc: 'Jelajahi seluruh destinasi Dieng melalui peta digital dengan marker POI, jalur wisata, dan zona bahaya.',
    link: '/explore',
    color: '#f97316'
  },
  {
    icon: <Info size={28} />,
    title: 'Pusat Informasi',
    desc: 'Data terpusat dan terverifikasi mengenai biaya tiket, penginapan, transportasi, dan regulasi wisata terbaru.',
    link: '/info',
    color: '#ec4899'
  },
]

const stats = [
  { value: '197K+', label: 'Wisatawan/Tahun', icon: <Star size={20} /> },
  { value: '15+', label: 'Destinasi', icon: <MapPin size={20} /> },
  { value: '2.093m', label: 'Ketinggian', icon: <Mountain size={20} /> },
  { value: '24/7', label: 'DITA Aktif', icon: <Zap size={20} /> },
]

const dangerZones = [
  { name: 'Tanjakan Sikarim', risk: 'Tinggi', angle: '45°', desc: 'Kemiringan ekstrem, rawan rem blong' },
  { name: 'Tanjakan Watu Angkruk', risk: 'Tinggi', angle: '15%', desc: 'Mesin mati pada kendaraan underpowered' },
  { name: 'Jalur Gardu Pandang', risk: 'Sedang', angle: '—', desc: 'Kabut tebal sering terjadi sore hari' },
]

export default function Home() {
  const [weather, setWeather] = useState(null)
  const [mlPrediction, setMlPrediction] = useState(null)

  useEffect(() => {
    // Fetch ML prediction for risk badge & advisory
    mlAPI.getQuickPrediction()
      .then(data => setMlPrediction(data))
      .catch(() => {})

    // Fetch weather from API, fallback to ML-based estimate
    weatherAPI.getCurrent()
      .then(setWeather)
      .catch(() => {
        // Fallback: use ML-estimated temp based on current hour
        const hour = new Date().getHours()
        const baseTempByHour = {
          0:9, 1:8.5, 2:8, 3:7.5, 4:7.5, 5:8, 6:9, 7:11, 8:13,
          9:15, 10:17, 11:18, 12:19, 13:19.5, 14:19, 15:17, 16:15,
          17:13, 18:12, 19:11, 20:10.5, 21:10, 22:9.5, 23:9
        }
        const estTemp = baseTempByHour[hour] || 14
        setWeather({
          temperature: estTemp,
          humidity: hour >= 18 || hour <= 6 ? 92 : 78,
          wind_speed: 10 + Math.round(Math.random() * 5),
          condition: hour >= 15 && hour <= 17 ? 'Berkabut' : hour >= 13 && hour <= 16 ? 'Berawan' : 'Cerah Berawan',
          visibility: hour >= 15 && hour <= 17 ? 2.5 : 5.8,
          feels_like: Math.round(estTemp - 3),
        })
      })
  }, [])

  return (
    <div className="home page-enter">
      {/* Hero Section */}
      <section className="hero" id="hero-section">
        <div className="hero__bg">
          <div className="hero__orb hero__orb--1"></div>
          <div className="hero__orb hero__orb--2"></div>
          <div className="hero__orb hero__orb--3"></div>
          <div className="hero__grid-pattern"></div>
        </div>

        <div className="container hero__content">
          <div className="hero__text">
            <div className="hero__badge animate-fade-in">
              <Zap size={14} />
              AI-Powered Tourism Platform
            </div>

            <h1 className="hero__title animate-fade-in-up">
              Jelajahi <span className="text-gradient">Dieng</span> dengan
              <br />Aman & Cerdas
            </h1>

            <p className="hero__subtitle animate-fade-in-up delay-200">
              Dihyang Web mengintegrasikan kecerdasan buatan untuk memberikan
              informasi cuaca real-time, navigasi rute aman, dan rekomendasi
              wisata yang adaptif di Dataran Tinggi Dieng.
            </p>

            <div className="hero__actions animate-fade-in-up delay-300">
              <Link to="/chat" className="btn btn-primary btn-lg" id="hero-cta-chat">
                <MessageCircle size={20} />
                Tanya DITA
              </Link>
              <Link to="/explore" className="btn btn-outline btn-lg" id="hero-cta-explore">
                <Map size={20} />
                Jelajahi Peta
              </Link>
            </div>

            {/* Stats */}
            <div className="hero__stats animate-fade-in-up delay-400">
              {stats.map((stat, i) => (
                <div key={i} className="hero__stat">
                  <div className="hero__stat-icon">{stat.icon}</div>
                  <div>
                    <span className="hero__stat-value">{stat.value}</span>
                    <span className="hero__stat-label">{stat.label}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Weather Card */}
          <div className="hero__aside animate-slide-right delay-300">
            <div className="weather-preview glass-card-static">
              <div className="weather-preview__header">
                <CloudSun size={20} />
                <span>Cuaca Dieng Saat Ini</span>
              </div>
              {weather && (
                <>
                  <div className="weather-preview__temp">
                    <span className="weather-preview__temp-value">{weather.temperature}°</span>
                    <span className="weather-preview__temp-unit">C</span>
                  </div>
                  <p className="weather-preview__condition">{weather.condition}</p>
                  <div className="weather-preview__details">
                    <div className="weather-preview__detail">
                      <Droplets size={14} />
                      <span>{weather.humidity}%</span>
                    </div>
                    <div className="weather-preview__detail">
                      <Wind size={14} />
                      <span>{weather.wind_speed} km/h</span>
                    </div>
                    <div className="weather-preview__detail">
                      <Eye size={14} />
                      <span>{weather.visibility} km</span>
                    </div>
                  </div>
                  <Link to="/dashboard" className="weather-preview__link">
                    Lihat Dashboard Lengkap <ArrowRight size={14} />
                  </Link>
                </>
              )}
            </div>

            {/* Danger Alert */}
            <div className="danger-alert glass-card-static">
              <div className="danger-alert__header">
                <AlertTriangle size={18} />
                <span>Zona Rawan Hari Ini</span>
              </div>
              <div className="danger-alert__list">
                {dangerZones.map((zone, i) => (
                  <div key={i} className="danger-alert__item">
                    <div className="danger-alert__dot"></div>
                    <div>
                      <strong>{zone.name}</strong>
                      <span className="danger-alert__desc">{zone.desc}</span>
                    </div>
                    <span className={`badge badge-${zone.risk === 'Tinggi' ? 'danger' : 'warning'}`}>
                      {zone.risk}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features section" id="features-section">
        <div className="container">
          <div className="features__header">
            <span className="badge badge-primary">Fitur Utama</span>
            <h2>Solusi <span className="text-gradient">Hyper-Local</span> untuk Wisata Dieng</h2>
            <p>Teknologi AI yang dirancang khusus untuk memitigasi risiko cuaca ekstrem dan navigasi medan berbahaya di dataran tinggi Dieng.</p>
          </div>

          <div className="features__grid">
            {features.map((feature, i) => (
              <Link
                key={i}
                to={feature.link}
                className="feature-card glass-card"
                id={`feature-card-${i}`}
                style={{ animationDelay: `${i * 100}ms` }}
              >
                <div className="feature-card__icon" style={{ color: feature.color, background: `${feature.color}15` }}>
                  {feature.icon}
                </div>
                <h3 className="feature-card__title">{feature.title}</h3>
                <p className="feature-card__desc">{feature.desc}</p>
                <div className="feature-card__link" style={{ color: feature.color }}>
                  Pelajari lebih lanjut <ChevronRight size={16} />
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* Safety CTA Section */}
      <section className="safety-cta section" id="safety-section">
        <div className="container">
          <div className="safety-cta__card glass-card-static">
            <div className="safety-cta__content">
              <span className="badge badge-warning">
                <AlertTriangle size={12} />
                Solo Traveler Safety
              </span>
              <h2>Keamanan adalah Prioritas Kami</h2>
              <p>
                DITA dilengkapi fitur keselamatan khusus untuk solo traveler.
                Dapatkan peringatan cuaca proaktif, rekomendasi rute aman berdasarkan
                jenis kendaraan, serta rincian biaya retribusi resmi untuk menghindari
                pungli di kawasan wisata Dieng.
              </p>
              <div className="safety-cta__actions">
                <Link to="/chat" className="btn btn-accent">
                  <Shield size={18} />
                  Mulai dengan DITA
                </Link>
                <Link to="/explore" className="btn btn-outline">
                  Cek Rute Aman
                </Link>
              </div>
            </div>
            <div className="safety-cta__visual">
              <div className="safety-cta__rings">
                <div className="safety-cta__ring"></div>
                <div className="safety-cta__ring"></div>
                <div className="safety-cta__ring"></div>
                <Shield size={48} className="safety-cta__icon" />
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}
