import { useState, useEffect, useCallback } from 'react'
import {
  CalendarDays, Clock, CloudSun, DollarSign,
  Loader2, Sparkles, Users, Car, Bike, Wallet,
  Shirt, Mountain, Sun, Moon, Coffee, Trash2, RotateCcw
} from 'lucide-react'
import { itineraryAPI } from '../services/api'
import './Itinerary.css'

// Demo data tanpa JSX icons — icons di-render via getIconForType()
const DEMO_ITINERARIES = {
  '1d': {
    title: 'Itinerary 1 Hari — Solo Traveler',
    budget: 'Rp 300.000',
    weatherNote: '⚠️ Cuaca Dieng berubah cepat. Siapkan jaket dan jas hujan setiap saat.',
    gear: ['Jaket tebal/windbreaker', 'Sepatu hiking anti-slip', 'Jas hujan', 'Air mineral 1.5L'],
    days: [
      {
        day: 'Hari 1',
        date: 'Eksplorasi Seharian',
        items: [
          { time: '07:00', title: 'Sarapan di Warung Lokal', desc: 'Mie Ongklok khas Dieng. Hangat & mengenyangkan.', cost: 15000, type: 'food' },
          { time: '08:00', title: 'Candi Arjuna', desc: 'Kompleks candi Hindu tertua di Jawa. Durasi kunjungan ~45 menit.', cost: 15000, type: 'attraction' },
          { time: '09:30', title: 'Kawah Sikidang', desc: 'Kawah aktif dengan fumarola. Jaga jarak aman dari lubang kawah.', cost: 20000, type: 'attraction' },
          { time: '11:00', title: 'Telaga Warna & Pengilon', desc: 'Dua telaga bersebelahan. Trekking ringan ~1 jam.', cost: 15000, type: 'attraction' },
          { time: '12:30', title: 'Makan Siang', desc: 'Carica & kentang goreng Dieng di area wisata.', cost: 20000, type: 'food' },
          { time: '14:00', title: 'Dieng Plateau Theater', desc: 'Film 4D sejarah Dieng. Tempat berteduh jika kabut.', cost: 25000, type: 'attraction' },
          { time: '15:30', title: 'Beli Oleh-oleh & Pulang', desc: 'Carica, keripik kentang di Pasar Carica Dieng.', cost: 50000, type: 'shopping' },
        ]
      }
    ]
  },
  '2d1n': {
    title: 'Itinerary 2 Hari 1 Malam — Solo Traveler',
    budget: 'Rp 500.000',
    weatherNote: '⚠️ Kabut tebal diprediksi sore hari (15:00-17:00). Hindari jalur Sikarim pada jam tersebut.',
    gear: ['Jaket tebal/windbreaker', 'Sepatu hiking anti-slip', 'Syal/buff pelindung', 'Jas hujan', 'Senter/headlamp', 'Air mineral 1.5L'],
    days: [
      {
        day: 'Hari 1',
        date: 'Sabtu',
        items: [
          { time: '04:00', title: 'Sunrise di Bukit Sikunir', desc: 'Berangkat dari penginapan. Bawa jaket tebal, suhu ~5°C. Trek 30 menit ke puncak.', cost: 15000, type: 'attraction' },
          { time: '07:00', title: 'Sarapan di Warung Lokal', desc: 'Mie Ongklok khas Dieng. Hangat & mengenyangkan untuk energi seharian.', cost: 15000, type: 'food' },
          { time: '08:30', title: 'Candi Arjuna', desc: 'Kompleks candi Hindu tertua di Jawa. Durasi kunjungan ~45 menit.', cost: 15000, type: 'attraction' },
          { time: '10:00', title: 'Kawah Sikidang', desc: 'Kawah aktif dengan fumarola. Jaga jarak aman dari lubang kawah.', cost: 20000, type: 'attraction' },
          { time: '12:00', title: 'Makan Siang', desc: 'Carica & kentang goreng Dieng di area Kawah Sikidang.', cost: 20000, type: 'food' },
          { time: '13:30', title: 'Telaga Warna & Pengilon', desc: 'Dua telaga bersebelahan. Trekking ringan ~1 jam. ⚠️ Kembali sebelum 15:00 (kabut).', cost: 15000, type: 'attraction' },
          { time: '15:00', title: 'Dieng Plateau Theater', desc: 'Film 4D sejarah Dieng. Tempat berteduh saat kabut turun.', cost: 25000, type: 'attraction' },
          { time: '17:00', title: 'Check-in Homestay', desc: 'Istirahat di homestay daerah Dieng Kulon. Malam bisa turun ke 3°C!', cost: 150000, type: 'stay' },
        ]
      },
      {
        day: 'Hari 2',
        date: 'Minggu',
        items: [
          { time: '06:00', title: 'Sarapan Pagi', desc: 'Sarapan hangat di homestay sebelum lanjut eksplorasi.', cost: 0, type: 'food' },
          { time: '07:30', title: 'Batu Ratapan Angin', desc: 'View point terbaik untuk foto panorama dataran Dieng.', cost: 10000, type: 'attraction' },
          { time: '09:00', title: 'Kawah Candradimuka', desc: 'Kawah legendaris. Trek ringan dengan pemandangan mistis.', cost: 10000, type: 'attraction' },
          { time: '11:00', title: 'Beli Oleh-oleh', desc: 'Carica, keripik kentang, purwaceng di Pasar Carica Dieng.', cost: 50000, type: 'shopping' },
          { time: '12:30', title: 'Makan Siang & Pulang', desc: 'Mie Ongklok terakhir sebelum perjalanan pulang. Hati-hati di turunan!', cost: 15000, type: 'food' },
        ]
      }
    ]
  },
  '3d2n': {
    title: 'Itinerary 3 Hari 2 Malam — Solo Traveler',
    budget: 'Rp 800.000',
    weatherNote: '⚠️ Perjalanan panjang: siapkan perlengkapan lengkap. Cuaca bisa berubah drastis.',
    gear: ['Jaket tebal/windbreaker', 'Sepatu hiking', 'Syal/buff', 'Jas hujan', 'Senter/headlamp', 'Air mineral', 'P3K dasar', 'Power bank'],
    days: [
      {
        day: 'Hari 1',
        date: 'Jumat',
        items: [
          { time: '08:00', title: 'Candi Arjuna & Gatotkaca', desc: 'Eksplorasi kompleks candi bersejarah.', cost: 15000, type: 'attraction' },
          { time: '10:00', title: 'Kawah Sikidang', desc: 'Kawah vulkanik aktif. Jaga jarak aman.', cost: 20000, type: 'attraction' },
          { time: '12:00', title: 'Makan Siang', desc: 'Mie Ongklok dan carica segar.', cost: 20000, type: 'food' },
          { time: '13:30', title: 'Telaga Warna & Pengilon', desc: 'Dua telaga bersebelahan. View indah!', cost: 15000, type: 'attraction' },
          { time: '15:00', title: 'Dieng Plateau Theater', desc: 'Film 4D sejarah Dieng. Berteduh dari kabut.', cost: 25000, type: 'attraction' },
          { time: '17:00', title: 'Check-in Homestay', desc: 'Istirahat di Dieng Kulon.', cost: 150000, type: 'stay' },
        ]
      },
      {
        day: 'Hari 2',
        date: 'Sabtu',
        items: [
          { time: '04:00', title: 'Sunrise Bukit Sikunir', desc: 'Golden sunrise! Bawa jaket tebal, suhu ~5°C.', cost: 15000, type: 'attraction' },
          { time: '07:00', title: 'Sarapan', desc: 'Sarapan hangat di homestay.', cost: 0, type: 'food' },
          { time: '08:30', title: 'Kawah Sileri', desc: 'Kawah terbesar Dieng. Ikuti jalur resmi!', cost: 15000, type: 'attraction' },
          { time: '10:30', title: 'Batu Ratapan Angin', desc: 'Panorama 360° dataran Dieng.', cost: 10000, type: 'attraction' },
          { time: '12:00', title: 'Makan Siang', desc: 'Kentang goreng Dieng dan teh panas.', cost: 20000, type: 'food' },
          { time: '14:00', title: 'Padang Savana & Desa Sembungan', desc: 'Desa tertinggi di Pulau Jawa. Pemandangan menakjubkan.', cost: 5000, type: 'attraction' },
          { time: '17:00', title: 'Kembali ke Homestay', desc: 'Istirahat & persiapan hari terakhir.', cost: 0, type: 'stay' },
        ]
      },
      {
        day: 'Hari 3',
        date: 'Minggu',
        items: [
          { time: '06:00', title: 'Sarapan Pagi', desc: 'Sarapan hangat terakhir di Dieng.', cost: 0, type: 'food' },
          { time: '07:30', title: 'Candi Bima', desc: 'Candi unik dengan arsitektur berbeda.', cost: 10000, type: 'attraction' },
          { time: '09:00', title: 'Museum Kailasa', desc: 'Koleksi artefak dan info geologi Dieng.', cost: 10000, type: 'attraction' },
          { time: '10:30', title: 'Beli Oleh-oleh', desc: 'Pasar Carica Dieng. Carica, keripik, purwaceng.', cost: 75000, type: 'shopping' },
          { time: '12:00', title: 'Makan Siang & Pulang', desc: 'Perjalanan pulang. Hati-hati turunan!', cost: 15000, type: 'food' },
        ]
      }
    ]
  },
}

const TYPE_COLORS = {
  attraction: '#00b4cc',
  food: '#f59e0b',
  stay: '#a78bfa',
  shopping: '#22c55e',
  culture: '#00b4cc',
}

function getTypeColor(type) {
  return TYPE_COLORS[type] || '#64748b'
}

function getIconForType(type) {
  switch (type) {
    case 'food': return <Coffee size={16} />
    case 'stay': return <Moon size={16} />
    case 'shopping': return <DollarSign size={16} />
    case 'attraction':
    case 'culture':
    default:
      return <Mountain size={16} />
  }
}

export default function Itinerary() {
  // State untuk form inputs
  const [duration, setDuration] = useState('2d1n')
  const [travelStyle, setTravelStyle] = useState('solo')
  const [budget, setBudget] = useState('500000')
  const [vehicle, setVehicle] = useState('motorcycle')
  
  // State untuk hasil dan UI
  const [itinerary, setItinerary] = useState(null)
  const [loading, setLoading] = useState(false)
  const [isDemo, setIsDemo] = useState(false)
  const [error, setError] = useState(null)

  // Get demo data berdasarkan durasi yang dipilih
  const getDemoForDuration = useCallback((dur) => {
    return DEMO_ITINERARIES[dur] || DEMO_ITINERARIES['2d1n']
  }, [])

  const generateItinerary = async () => {
    setLoading(true)
    setIsDemo(false)
    setError(null)
    setItinerary(null)
    
    const currentPreferences = {
      duration,
      travelStyle,
      budget: parseInt(budget) || 500000,
      vehicle,
    }
    
    try {
      const result = await itineraryAPI.generate(currentPreferences)
      
      // Bersihkan field icon jika ada (dari Gemini response)
      const clean = sanitizeItinerary(result)
      clean._generatedAt = new Date().toISOString()
      clean._preferences = currentPreferences
      
      setItinerary(clean)
    } catch (err) {
      console.error('[Itinerary] Generate error:', err)
      // Fallback ke demo yang sesuai durasi
      const demo = { 
        ...getDemoForDuration(duration), 
        _generatedAt: new Date().toISOString(),
        _preferences: currentPreferences,
      }
      setItinerary(demo)
      setIsDemo(true)
    } finally {
      setLoading(false)
    }
  }

  // Hapus field yang tidak bisa di-serialize (React elements, functions, dll)
  function sanitizeItinerary(data) {
    if (!data) return data
    return {
      ...data,
      days: (data.days || []).map(day => ({
        ...day,
        items: (day.items || []).map(({ icon, ...rest }) => rest),
      })),
    }
  }

  const clearItinerary = () => {
    setItinerary(null)
    setIsDemo(false)
    setError(null)
    setDuration('2d1n')
    setTravelStyle('solo')
    setBudget('500000')
    setVehicle('motorcycle')
  }

  const totalCost = itinerary?.days?.reduce(
    (sum, day) => sum + day.items.reduce((s, item) => s + (item.cost || 0), 0),
    0
  ) ?? 0

  return (
    <div className="itinerary-page page-enter" id="itinerary-page">
      <div className="container">
        <div className="itinerary-page__header">
          <span className="badge badge-primary"><Sparkles size={12} /> AI-Powered</span>
          <h1>Smart <span className="text-gradient">Itinerary</span></h1>
          <p>Rencana perjalanan adaptif terhadap prakiraan cuaca lokal Dieng</p>
        </div>

        <div className="itinerary-page__layout">
          {/* Config Panel */}
          <div className="itinerary-config glass-card-static">
            <h3>Konfigurasi Perjalanan</h3>

            <div className="config-field">
              <label>Durasi</label>
              <div className="config-options">
                {[
                  { value: '1d',   label: '1 Hari' },
                  { value: '2d1n', label: '2H 1M' },
                  { value: '3d2n', label: '3H 2M' },
                ].map(opt => (
                  <button
                    key={opt.value}
                    type="button"
                    className={`config-btn ${duration === opt.value ? 'active' : ''}`}
                    onClick={() => setDuration(opt.value)}
                  >
                    {opt.label}
                  </button>
                ))}
              </div>
            </div>

            <div className="config-field">
              <label>Gaya Wisata</label>
              <div className="config-options">
                {[
                  { value: 'solo',   label: 'Solo' },
                  { value: 'couple', label: 'Pasangan' },
                  { value: 'family', label: 'Keluarga' },
                  { value: 'group',  label: 'Rombongan' },
                ].map(opt => (
                  <button
                    key={opt.value}
                    type="button"
                    className={`config-btn ${travelStyle === opt.value ? 'active' : ''}`}
                    onClick={() => setTravelStyle(opt.value)}
                  >
                    <Users size={13} /> {opt.label}
                  </button>
                ))}
              </div>
            </div>

            <div className="config-field">
              <label>Budget</label>
              <div className="config-input-group">
                <span>Rp</span>
                <input
                  type="number"
                  className="input-field"
                  value={budget}
                  min="100000"
                  step="50000"
                  onChange={e => setBudget(e.target.value)}
                  placeholder="500000"
                  id="budget-input"
                />
              </div>
            </div>

            <div className="config-field">
              <label>Kendaraan</label>
              <div className="config-options">
                {[
                  { value: 'motorcycle', label: 'Motor',  icon: <Bike size={14} /> },
                  { value: 'car',        label: 'Mobil',  icon: <Car  size={14} /> },
                ].map(opt => (
                  <button
                    key={opt.value}
                    type="button"
                    className={`config-btn ${vehicle === opt.value ? 'active' : ''}`}
                    onClick={() => setVehicle(opt.value)}
                  >
                    {opt.icon} {opt.label}
                  </button>
                ))}
              </div>
            </div>

            <button
              className="btn btn-primary btn-lg"
              onClick={generateItinerary}
              disabled={loading}
              style={{ width: '100%', marginTop: '8px' }}
              id="generate-itinerary"
            >
              {loading
                ? <><Loader2 size={18} className="spin-anim" /> Menyusun Rencana...</>
                : <><Sparkles size={18} /> Buat Itinerary</>
              }
            </button>

            {itinerary && !loading && (
              <button
                className="btn btn-outline btn-sm"
                onClick={clearItinerary}
                style={{ width: '100%' }}
              >
                <RotateCcw size={14} /> Reset & Buat Baru
              </button>
            )}
          </div>

          {/* Result */}
          <div className="itinerary-result">
            {loading && (
              <div className="itinerary-empty glass-card-static">
                <Loader2 size={40} className="spin-anim" style={{ color: 'var(--primary-400)' }} />
                <h3>Menyusun itinerary...</h3>
                <p>DITA sedang menganalisis cuaca dan menyusun rencana perjalanan terbaik untuk Anda.</p>
              </div>
            )}

            {!itinerary && !loading && (
              <div className="itinerary-empty glass-card-static">
                <CalendarDays size={48} />
                <h3>Belum ada itinerary</h3>
                <p>Atur preferensi perjalanan Anda, lalu klik "Buat Itinerary" untuk mendapatkan rencana perjalanan yang adaptif terhadap cuaca.</p>
              </div>
            )}

            {itinerary && !loading && (
              <div className="itinerary-content animate-fade-in-up" key={itinerary._generatedAt || Date.now()}>
                {isDemo && (
                  <div className="itinerary-demo-notice">
                    <span>⚠️ Menampilkan contoh itinerary (backend tidak terjangkau). Pastikan server berjalan untuk hasil AI.</span>
                  </div>
                )}

                {/* Summary */}
                <div className="itinerary-summary glass-card-static">
                  <h2>{itinerary.title}</h2>
                  <div className="itinerary-summary__meta">
                    <span><Wallet size={14} /> Budget: {itinerary.budget}</span>
                    <span><DollarSign size={14} /> Total: Rp {totalCost.toLocaleString('id-ID')}</span>
                  </div>
                  {itinerary.weatherNote && (
                    <div className="itinerary-weather-note">
                      <CloudSun size={16} />
                      <span>{itinerary.weatherNote}</span>
                    </div>
                  )}
                </div>

                {/* Gear */}
                {itinerary.gear?.length > 0 && (
                  <div className="itinerary-gear glass-card-static">
                    <h4><Shirt size={16} /> Perlengkapan Wajib</h4>
                    <div className="gear-list">
                      {itinerary.gear.map((item, i) => (
                        <span key={i} className="gear-item">✓ {item}</span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Timeline per hari */}
                {itinerary.days.map((day, di) => (
                  <div key={di} className="itinerary-day">
                    <div className="itinerary-day__header">
                      <h3>{day.day}{day.date ? ` — ${day.date}` : ''}</h3>
                    </div>
                    <div className="itinerary-timeline">
                      {day.items.map((item, ii) => (
                        <div
                          key={ii}
                          className="timeline-item"
                          style={{ '--item-color': getTypeColor(item.type) }}
                        >
                          <div className="timeline-item__time">
                            <Clock size={12} />
                            {item.time}
                          </div>
                          <div className="timeline-item__dot" />
                          <div className="timeline-item__content glass-card">
                            <div className="timeline-item__icon" style={{ color: getTypeColor(item.type) }}>
                              {getIconForType(item.type)}
                            </div>
                            <div className="timeline-item__info">
                              <h5>{item.title}</h5>
                              <p>{item.desc}</p>
                              {item.cost > 0 && (
                                <span className="timeline-item__cost">
                                  Rp {item.cost.toLocaleString('id-ID')}
                                </span>
                              )}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
