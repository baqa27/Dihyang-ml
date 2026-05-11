import { useState, useEffect } from 'react'
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet'
import L from 'leaflet'
import {
  MapPin, AlertTriangle, Filter, Mountain, Navigation, Eye, Car,
  Bike, Bus, ChevronDown, Star, Clock, DollarSign, Shield
} from 'lucide-react'
import './Explore.css'

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
  { id: 1, name: 'Kawah Sikidang', lat: -7.2125, lng: 109.9064, type: 'attraction', rating: 4.5, cost: 20000, desc: 'Kawah vulkanik aktif dengan aktivitas fumarola. Spot utama wisata Dieng.' },
  { id: 2, name: 'Telaga Warna', lat: -7.2167, lng: 109.9150, type: 'attraction', rating: 4.6, cost: 15000, desc: 'Danau dengan warna air yang berubah-ubah karena kandungan sulfur.' },
  { id: 3, name: 'Candi Arjuna', lat: -7.2069, lng: 109.9103, type: 'culture', rating: 4.4, cost: 15000, desc: 'Kompleks candi Hindu abad ke-7, peninggalan tertua di Jawa.' },
  { id: 4, name: 'Bukit Sikunir', lat: -7.2250, lng: 109.9000, type: 'attraction', rating: 4.8, cost: 15000, desc: 'Spot sunrise terbaik di Dieng. Golden Sunrise yang terkenal.' },
  { id: 5, name: 'Batu Ratapan Angin', lat: -7.2108, lng: 109.9167, type: 'attraction', rating: 4.3, cost: 10000, desc: 'Tebing dengan pemandangan lembah dan gunung yang memukau.' },
  { id: 6, name: 'Dieng Plateau Theater', lat: -7.2083, lng: 109.9056, type: 'entertainment', rating: 4.2, cost: 25000, desc: 'Teater 4D yang menampilkan sejarah dan geologi Dieng.' },
  { id: 7, name: 'Kawah Candradimuka', lat: -7.2042, lng: 109.9125, type: 'attraction', rating: 4.1, cost: 10000, desc: 'Kawah dengan legenda Gatot Kaca. Pemandangan mistis.' },
  { id: 8, name: 'Telaga Pengilon', lat: -7.2175, lng: 109.9167, type: 'attraction', rating: 4.4, cost: 0, desc: 'Danau jernih yang memantulkan langit seperti cermin.' },
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
              {dangerPoints.map(dp => (
                <div key={dp.id} className="explore__danger-item">
                  <div className="explore__danger-dot"></div>
                  <div>
                    <strong>{dp.name}</strong>
                    <span>{dp.desc}</span>
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
