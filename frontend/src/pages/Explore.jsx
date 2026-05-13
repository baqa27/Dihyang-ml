import { useState, useEffect } from 'react'
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet'
import L from 'leaflet'
import {
  MapPin, AlertTriangle, Filter, Mountain, Navigation, Eye, Car,
  Bike, Bus, ChevronDown, Star, Clock, DollarSign, Shield
} from 'lucide-react'
import './Explore.css'
import { mlAPI, weatherAPI } from '../services/api'

// Fitur rute untuk model ML (selaras backend train_route_model / dataset lapangan)
const ROUTE_ML_DEFAULTS = {
  d1: { gradient: 45, width: 3, visibility: 2, guardrail: 0, surface: 'aspal', elevation: 1800, curve_count: 15, lighting: 0 },
  d2: { gradient: 35, width: 3.5, visibility: 3, guardrail: 0, surface: 'aspal', elevation: 1900, curve_count: 12, lighting: 0 },
  d3: { gradient: 18, width: 3.5, visibility: 3, guardrail: 0, surface: 'aspal', elevation: 2100, curve_count: 12, lighting: 0 },
}

function conditionToMlWeather(condition) {
  const s = (condition || '').toLowerCase()
  if (s.includes('hujan')) return 'hujan'
  if (s.includes('kabut') || s.includes('berkabut')) return 'kabut'
  if (s.includes('cerah')) return 'cerah'
  return 'mendung'
}

// Fix leaflet default marker icon
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
})

const createIcon = (color) => L.divIcon({
  className: 'custom-marker',
  html: `<div style="background:${color};width:28px;height:28px;border-radius:50%;border:3px solid white;box-shadow:0 2px 8px rgba(0,0,0,0.3);display:flex;align-items:center;justify-content:center;"></div>`,
  iconSize: [28, 28],
  iconAnchor: [14, 14],
})

const destinations = [
  // Kawah & Fenomena Alam
  { id: 1, name: 'Kawah Sikidang', lat: -7.2125, lng: 109.9064, type: 'attraction', rating: 4.5, cost: 20000, desc: 'Kawah vulkanik aktif dengan aktivitas fumarola. Spot utama wisata Dieng.' },
  { id: 2, name: 'Kawah Candradimuka', lat: -7.2042, lng: 109.9125, type: 'attraction', rating: 4.1, cost: 10000, desc: 'Kawah legendaris dalam cerita Mahabharata. Pemandangan mistis.' },
  { id: 3, name: 'Kawah Sileri', lat: -7.1986, lng: 109.9278, type: 'attraction', rating: 4.3, cost: 15000, desc: 'Kawah terbesar di Dieng. Hati-hati gas beracun!' },
  { id: 4, name: 'Kawah Nagasari', lat: -7.2011, lng: 109.9205, type: 'attraction', rating: 4.0, cost: 10000, desc: 'Kawah kecil yang masih aktif. Akses mudah dari Kawah Sileri.' },
  // Telaga
  { id: 5, name: 'Telaga Warna', lat: -7.2167, lng: 109.9150, type: 'attraction', rating: 4.6, cost: 15000, desc: 'Danau dengan warna air yang berubah-ubah karena kandungan sulfur.' },
  { id: 6, name: 'Telaga Pengilon', lat: -7.2175, lng: 109.9167, type: 'attraction', rating: 4.4, cost: 0, desc: 'Danau jernih yang memantulkan langit seperti cermin. Gratis!' },
  { id: 7, name: 'Telaga Merdada', lat: -7.2189, lng: 109.9178, type: 'attraction', rating: 4.2, cost: 5000, desc: 'Telaga tenang di tengah pegunungan. Cocok untuk relaksasi.' },
  { id: 8, name: 'Telaga Balekambang', lat: -7.2211, lng: 109.9189, type: 'attraction', rating: 4.0, cost: 5000, desc: 'Telaga tersembunyi. Suasana alami dan sepi.' },
  // Candi & Budaya
  { id: 9, name: 'Candi Arjuna', lat: -7.2069, lng: 109.9103, type: 'culture', rating: 4.4, cost: 15000, desc: 'Kompleks candi Hindu abad ke-7, peninggalan tertua di Jawa.' },
  { id: 10, name: 'Candi Gatotkaca', lat: -7.2097, lng: 109.9089, type: 'culture', rating: 4.2, cost: 10000, desc: 'Candi Hindu dengan relief indah. Dekat Candi Arjuna.' },
  { id: 11, name: 'Candi Bima', lat: -7.2153, lng: 109.9142, type: 'culture', rating: 4.3, cost: 10000, desc: 'Candi unik dengan arsitektur berbeda dari candi Dieng lainnya.' },
  // View Point & Sunrise
  { id: 12, name: 'Bukit Sikunir', lat: -7.2250, lng: 109.9000, type: 'attraction', rating: 4.8, cost: 15000, desc: 'Spot sunrise terbaik di Dieng. Golden Sunrise yang terkenal.' },
  { id: 13, name: 'Batu Ratapan Angin', lat: -7.2108, lng: 109.9167, type: 'attraction', rating: 4.3, cost: 10000, desc: 'View point panorama 360° dataran Dieng. Spot foto Instagram!' },
  { id: 14, name: 'Bukit Pangonan', lat: -7.2267, lng: 109.9022, type: 'attraction', rating: 4.2, cost: 10000, desc: 'Alternatif sunrise selain Sikunir. Lebih sepi.' },
  { id: 15, name: 'Gardu Pandang Tieng', lat: -7.2100, lng: 109.9050, type: 'attraction', rating: 4.1, cost: 10000, desc: 'View point panorama lembah Tieng dan pegunungan.' },
  // Edukasi & Hiburan
  { id: 16, name: 'Dieng Plateau Theater', lat: -7.2083, lng: 109.9056, type: 'entertainment', rating: 4.2, cost: 25000, desc: 'Teater 4D menampilkan sejarah dan geologi Dieng.' },
  { id: 17, name: 'Museum Kailasa', lat: -7.2075, lng: 109.9058, type: 'entertainment', rating: 4.0, cost: 10000, desc: 'Museum arkeologi dan geologi Dieng.' },
  // Wisata Lainnya
  { id: 18, name: 'Padang Savana Dieng', lat: -7.2275, lng: 109.9011, type: 'attraction', rating: 4.3, cost: 5000, desc: 'Hamparan padang rumput dengan view Gunung Sindoro-Sumbing.' },
  { id: 19, name: 'Desa Wisata Sembungan', lat: -7.2233, lng: 109.8969, type: 'culture', rating: 4.4, cost: 0, desc: 'Desa tertinggi di Pulau Jawa (2.300 mdpl). Gratis!' },
  { id: 20, name: 'Camping Ground Sikunir', lat: -7.2239, lng: 109.8994, type: 'attraction', rating: 4.5, cost: 25000, desc: 'Area camping di kaki Bukit Sikunir. Bawa sleeping bag tebal!' },
]

const dangerPoints = [
  { id: 'd1', name: 'Tanjakan Sikarim', lat: -7.2300, lng: 109.8920, angle: '45°', risk: 'Tinggi', desc: 'Kemiringan ekstrem. Rem blong sering terjadi.' },
  { id: 'd2', name: 'Tanjakan Watu Angkruk', lat: -7.2350, lng: 109.8980, angle: '15%', risk: 'Tinggi', desc: 'Mesin mati pada kendaraan underpowered.' },
  { id: 'd3', name: 'Jalur Gardu Pandang', lat: -7.2150, lng: 109.9200, angle: '—', risk: 'Sedang', desc: 'Kabut tebal sering terjadi sore hari.' },
]

const vehicleFilters = [
  { value: 'all', label: 'Semua Kendaraan', icon: <Navigation size={16} /> },
  { value: 'car', label: 'Mobil', icon: <Car size={16} /> },
  { value: 'motorcycle', label: 'Motor', icon: <Bike size={16} /> },
  { value: 'bus', label: 'Bus/Travel', icon: <Bus size={16} /> },
]

const diengCenter = [-7.2125, 109.9100]

export default function Explore() {
  const [selectedType, setSelectedType] = useState('all')
  const [vehicleType, setVehicleType] = useState('all')
  const [showDanger, setShowDanger] = useState(true)
  const [selectedDest, setSelectedDest] = useState(null)
  const [routeMl, setRouteMl] = useState({})
  const [routeMlLoading, setRouteMlLoading] = useState(false)

  useEffect(() => {
    let cancelled = false
    ;(async () => {
      setRouteMlLoading(true)
      const next = {}
      let condition = 'Cerah/Berawan'
      try {
        const w = await weatherAPI.getCurrent()
        condition = w.condition || condition
      } catch {
        /* tetap default */
      }
      const weather = conditionToMlWeather(condition)
      const veh = vehicleType === 'car' ? 'car' : vehicleType === 'bus' ? 'bus' : 'motorcycle'
      try {
        for (const dp of dangerPoints) {
          const spec = ROUTE_ML_DEFAULTS[dp.id]
          if (!spec) continue
          try {
            next[dp.id] = await mlAPI.predictRouteSafety({ ...spec, vehicle: veh, weather })
          } catch {
            next[dp.id] = null
          }
        }
      } finally {
        if (!cancelled) {
          setRouteMl(next)
        }
        setRouteMlLoading(false)
      }
    })()
    return () => { cancelled = true }
  }, [vehicleType])

  const filteredDestinations = selectedType === 'all'
    ? destinations
    : destinations.filter(d => d.type === selectedType)

  return (
    <div className="explore page-enter" id="explore-page">
      <div className="explore__container">
        {/* Sidebar */}
        <div className="explore__sidebar">
          <div className="explore__sidebar-header">
            <h2><MapPin size={22} /> Jelajahi Dieng</h2>
            <p>Temukan destinasi wisata dan rute aman</p>
          </div>

          {/* Filters */}
          <div className="explore__filters">
            <div className="explore__filter-group">
              <label><Filter size={14} /> Jenis Destinasi</label>
              <div className="explore__filter-btns">
                {[
                  { value: 'all', label: 'Semua' },
                  { value: 'attraction', label: 'Wisata Alam' },
                  { value: 'culture', label: 'Budaya' },
                  { value: 'entertainment', label: 'Hiburan' },
                ].map(f => (
                  <button
                    key={f.value}
                    className={`explore__filter-btn ${selectedType === f.value ? 'active' : ''}`}
                    onClick={() => setSelectedType(f.value)}
                  >
                    {f.label}
                  </button>
                ))}
              </div>
            </div>

            <div className="explore__filter-group">
              <label><Car size={14} /> Kendaraan Anda</label>
              <div className="explore__filter-btns">
                {vehicleFilters.map(v => (
                  <button
                    key={v.value}
                    className={`explore__filter-btn ${vehicleType === v.value ? 'active' : ''}`}
                    onClick={() => setVehicleType(v.value)}
                  >
                    {v.icon}
                    {v.label}
                  </button>
                ))}
              </div>
            </div>

            <label className="explore__checkbox">
              <input
                type="checkbox"
                checked={showDanger}
                onChange={(e) => setShowDanger(e.target.checked)}
              />
              <AlertTriangle size={14} />
              Tampilkan zona bahaya
            </label>
          </div>

          {/* Destination List */}
          <div className="explore__list">
            <h4>{filteredDestinations.length} Destinasi</h4>
            {filteredDestinations.map(dest => (
              <div
                key={dest.id}
                className={`explore__item ${selectedDest?.id === dest.id ? 'active' : ''}`}
                onClick={() => setSelectedDest(dest)}
                id={`dest-${dest.id}`}
              >
                <div className="explore__item-header">
                  <h5>{dest.name}</h5>
                  <span className="explore__item-rating">
                    <Star size={12} />
                    {dest.rating}
                  </span>
                </div>
                <p className="explore__item-desc">{dest.desc}</p>
                <div className="explore__item-meta">
                  <span><DollarSign size={12} /> Rp {dest.cost.toLocaleString('id-ID')}</span>
                </div>
              </div>
            ))}
          </div>

          {/* Danger Zones */}
          {showDanger && (
            <div className="explore__danger">
              <h4><AlertTriangle size={16} /> Zona Rawan ({dangerPoints.length})</h4>
              {routeMlLoading && (
                <p className="explore__danger-ml-hint">Memuat prediksi keamanan rute (ML)…</p>
              )}
              <p className="explore__danger-disclaimer">
                Label ML memakai fitur medan + kendaraan + cuaca (Random Forest). Hasil mendukung keputusan Anda, bukan pengganti penilaian ahli keselamatan.
              </p>
              {dangerPoints.map(dp => (
                <div key={dp.id} className="explore__danger-item">
                  <div className="explore__danger-dot"></div>
                  <div>
                    <strong>{dp.name}</strong>
                    <span>{dp.desc}</span>
                    {routeMl[dp.id] && (
                      <span className="explore__danger-ml">
                        {routeMl[dp.id].safety_icon} Model: {routeMl[dp.id].safety_label}
                        {' '}({routeMl[dp.id].model})
                      </span>
                    )}
                  </div>
                  <span className={`badge badge-${dp.risk === 'Tinggi' ? 'danger' : 'warning'}`}>
                    {dp.angle}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Map */}
        <div className="explore__map" id="map-container">
          <MapContainer
            center={diengCenter}
            zoom={14}
            style={{ height: '100%', width: '100%' }}
            scrollWheelZoom={true}
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />

            {/* Destination Markers */}
            {filteredDestinations.map(dest => (
              <Marker
                key={dest.id}
                position={[dest.lat, dest.lng]}
                icon={createIcon('#00b4cc')}
                eventHandlers={{ click: () => setSelectedDest(dest) }}
              >
                <Popup>
                  <div style={{ minWidth: 200 }}>
                    <h4 style={{ margin: '0 0 4px', fontSize: '14px' }}>{dest.name}</h4>
                    <p style={{ margin: '0 0 4px', fontSize: '12px', color: '#666' }}>{dest.desc}</p>
                    <div style={{ display: 'flex', gap: '8px', fontSize: '12px' }}>
                      <span>⭐ {dest.rating}</span>
                      <span>💰 Rp {dest.cost.toLocaleString('id-ID')}</span>
                    </div>
                  </div>
                </Popup>
              </Marker>
            ))}

            {/* Danger Markers */}
            {showDanger && dangerPoints.map(dp => (
              <Marker
                key={dp.id}
                position={[dp.lat, dp.lng]}
                icon={createIcon('#ef4444')}
              >
                <Popup>
                  <div style={{ minWidth: 180 }}>
                    <h4 style={{ margin: '0 0 4px', fontSize: '14px', color: '#dc2626' }}>⚠️ {dp.name}</h4>
                    <p style={{ margin: '0 0 4px', fontSize: '12px', color: '#666' }}>{dp.desc}</p>
                    <p style={{ margin: 0, fontSize: '12px' }}>
                      <strong>Kemiringan: {dp.angle}</strong> | Risiko: {dp.risk}
                    </p>
                  </div>
                </Popup>
              </Marker>
            ))}
          </MapContainer>
        </div>
      </div>
    </div>
  )
}
