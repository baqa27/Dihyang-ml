import { useState } from 'react'
import {
  CalendarDays, Clock, MapPin, CloudSun, DollarSign, Shield,
  ChevronRight, Loader2, Sparkles, Users, Car, Bike, Wallet,
  Shirt, Mountain, Sun, Moon, Coffee
} from 'lucide-react'
import { itineraryAPI } from '../services/api'
import './Itinerary.css'

const demoItinerary = {
  title: 'Itinerary 2 Hari 1 Malam — Solo Traveler',
  budget: 'Rp 500.000',
  weatherNote: '⚠️ Kabut tebal diprediksi sore hari (15:00-17:00). Hindari jalur Sikarim pada jam tersebut.',
  gear: ['Jaket tebal/windbreaker', 'Sepatu hiking anti-slip', 'Syal/buff pelindung', 'Jas hujan', 'Senter/headlamp', 'Air mineral 1.5L'],
  days: [
    {
      day: 'Hari 1',
      date: 'Sabtu',
      items: [
        { time: '04:00', title: 'Sunrise di Bukit Sikunir', desc: 'Berangkat dari penginapan. Bawa jaket tebal, suhu ~5°C. Trek 30 menit ke puncak.', cost: 15000, icon: <Sun size={16} />, type: 'attraction' },
        { time: '07:00', title: 'Sarapan di Warung Lokal', desc: 'Mie Ongklok khas Dieng. Hangat & mengenyangkan untuk energi seharian.', cost: 15000, icon: <Coffee size={16} />, type: 'food' },
        { time: '08:30', title: 'Candi Arjuna', desc: 'Kompleks candi Hindu tertua di Jawa. Durasi kunjungan ~45 menit.', cost: 15000, icon: <Mountain size={16} />, type: 'attraction' },
        { time: '10:00', title: 'Kawah Sikidang', desc: 'Kawah aktif dengan fumarola. Jaga jarak aman dari lubang kawah.', cost: 20000, icon: <Mountain size={16} />, type: 'attraction' },
        { time: '12:00', title: 'Makan Siang', desc: 'Carica & kentang goreng Dieng di area Kawah Sikidang.', cost: 20000, icon: <Coffee size={16} />, type: 'food' },
        { time: '13:30', title: 'Telaga Warna & Pengilon', desc: 'Dua telaga bersebelahan. Trekking ringan ~1 jam. ⚠️ Kembali sebelum 15:00 (kabut).', cost: 15000, icon: <Mountain size={16} />, type: 'attraction' },
        { time: '15:00', title: 'Dieng Plateau Theater', desc: 'Film 4D sejarah Dieng. Tempat berteduh saat kabut turun.', cost: 25000, icon: <Mountain size={16} />, type: 'attraction' },
        { time: '17:00', title: 'Check-in Homestay', desc: 'Istirahat di homestay daerah Dieng Kulon. Malam bisa turun ke 3°C!', cost: 150000, icon: <Moon size={16} />, type: 'stay' },
      ]
    },
    {
      day: 'Hari 2',
      date: 'Minggu',
      items: [
        { time: '06:00', title: 'Sarapan Pagi', desc: 'Sarapan hangat di homestay sebelum lanjut eksplorasi.', cost: 0, icon: <Coffee size={16} />, type: 'food' },
        { time: '07:30', title: 'Batu Ratapan Angin', desc: 'View point terbaik untuk foto panorama dataran Dieng.', cost: 10000, icon: <Mountain size={16} />, type: 'attraction' },
        { time: '09:00', title: 'Kawah Candradimuka', desc: 'Kawah legendaris. Trek ringan dengan pemandangan mistis.', cost: 10000, icon: <Mountain size={16} />, type: 'attraction' },
        { time: '11:00', title: 'Beli Oleh-oleh', desc: 'Carica, keripik kentang, purwaceng di pasar Dieng.', cost: 50000, icon: <DollarSign size={16} />, type: 'shopping' },
        { time: '12:30', title: 'Makan Siang & Pulang', desc: 'Mie Ongklok terakhir sebelum perjalanan pulang. Hati-hati di turunan!', cost: 15000, icon: <Coffee size={16} />, type: 'food' },
      ]
    }
  ]
}

export default function Itinerary() {
  const [duration, setDuration] = useState('2d1n')
  const [travelStyle, setTravelStyle] = useState('solo')
  const [budget, setBudget] = useState('500000')
  const [vehicle, setVehicle] = useState('motorcycle')
  const [itinerary, setItinerary] = useState(() => {
    try {
      const saved = localStorage.getItem('dihyang_itinerary')
      return saved ? JSON.parse(saved) : null
    } catch (e) {
      localStorage.removeItem('dihyang_itinerary')
      return null
    }
  })
  const [loading, setLoading] = useState(false)

  const generateItinerary = async () => {
    setLoading(true)
    try {
      const result = await itineraryAPI.generate({
        duration, travelStyle, budget: parseInt(budget), vehicle
      })
      setItinerary(result)
      localStorage.setItem('dihyang_itinerary', JSON.stringify(result))
    } catch {
      // Use demo data
      setItinerary(demoItinerary)
      // Remove icons before stringify to avoid React child object errors
      const safeDemo = { ...demoItinerary, days: demoItinerary.days.map(d => ({ ...d, items: d.items.map(i => ({...i, icon: undefined})) })) }
      localStorage.setItem('dihyang_itinerary', JSON.stringify(safeDemo))
    } finally {
      setLoading(false)
    }
  }

  const totalCost = itinerary?.days?.reduce((sum, day) =>
    sum + day.items.reduce((s, item) => s + (item.cost || 0), 0), 0
  ) || 0

  const getTypeColor = (type) => {
    const colors = {
      attraction: '#00b4cc',
      food: '#f59e0b',
      stay: '#a78bfa',
      shopping: '#22c55e',
    }
    return colors[type] || '#64748b'
  }

  const getIconForType = (type) => {
    switch(type) {
      case 'food': return <Coffee size={16} />
      case 'stay': return <Moon size={16} />
      case 'shopping': return <DollarSign size={16} />
      case 'attraction':
      default:
        return <Mountain size={16} />
    }
  }

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
                  { value: '1d', label: '1 Hari' },
                  { value: '2d1n', label: '2H 1M' },
                  { value: '3d2n', label: '3H 2M' },
                ].map(opt => (
                  <button
                    key={opt.value}
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
                  { value: 'solo', label: 'Solo', icon: <Users size={14} /> },
                  { value: 'couple', label: 'Pasangan', icon: <Users size={14} /> },
                  { value: 'family', label: 'Keluarga', icon: <Users size={14} /> },
                  { value: 'group', label: 'Rombongan', icon: <Users size={14} /> },
                ].map(opt => (
                  <button
                    key={opt.value}
                    className={`config-btn ${travelStyle === opt.value ? 'active' : ''}`}
                    onClick={() => setTravelStyle(opt.value)}
                  >
                    {opt.icon} {opt.label}
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
                  onChange={(e) => setBudget(e.target.value)}
                  placeholder="500000"
                  id="budget-input"
                />
              </div>
            </div>

            <div className="config-field">
              <label>Kendaraan</label>
              <div className="config-options">
                {[
                  { value: 'motorcycle', label: 'Motor', icon: <Bike size={14} /> },
                  { value: 'car', label: 'Mobil', icon: <Car size={14} /> },
                ].map(opt => (
                  <button
                    key={opt.value}
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
              {loading ? <Loader2 size={18} className="spin-anim" /> : <Sparkles size={18} />}
              {loading ? 'Menyusun Rencana...' : 'Buat Itinerary'}
            </button>
          </div>

          {/* Result */}
          <div className="itinerary-result">
            {!itinerary && !loading && (
              <div className="itinerary-empty glass-card-static">
                <CalendarDays size={48} />
                <h3>Belum ada itinerary</h3>
                <p>Atur preferensi perjalanan Anda, lalu klik "Buat Itinerary" untuk mendapatkan rencana perjalanan yang adaptif terhadap cuaca.</p>
              </div>
            )}

            {itinerary && (
              <div className="itinerary-content animate-fade-in-up">
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

                {/* Gear Recommendation */}
                <div className="itinerary-gear glass-card-static">
                  <h4><Shirt size={16} /> Perlengkapan Wajib</h4>
                  <div className="gear-list">
                    {itinerary.gear.map((item, i) => (
                      <span key={i} className="gear-item">✓ {item}</span>
                    ))}
                  </div>
                </div>

                {/* Timeline */}
                {itinerary.days.map((day, di) => (
                  <div key={di} className="itinerary-day">
                    <div className="itinerary-day__header">
                      <h3>{day.day} — {day.date}</h3>
                    </div>
                    <div className="itinerary-timeline">
                      {day.items.map((item, ii) => (
                        <div key={ii} className="timeline-item" style={{ '--item-color': getTypeColor(item.type) }}>
                          <div className="timeline-item__time">
                            <Clock size={12} />
                            {item.time}
                          </div>
                          <div className="timeline-item__dot"></div>
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
