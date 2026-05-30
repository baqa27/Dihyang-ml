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
  { id: 1, name: 'Tiket Kawasan', lat: -7.2069, lng: 109.91, type: 'attraction', rating: 4.2, cost: 15000, desc: 'Tiket wajib saat melintasi gerbang utama kawasan Dieng. Retribusi ini masuk ke dana PEMDA untuk pemeliharaan fasilitas umum.' },
  { id: 2, name: 'Pandangan Petama', lat: -7.258, lng: 109.925, type: 'attraction', rating: 4.3, cost: 10000, desc: 'Menawarkan sisi lain untuk menikmati keindahan lanskap Telaga Menjer dari atas. Selain sebagai spot pandang, area ini juga menyediakan lahan yang bisa dimanfaatkan wisatawan untuk mendirikan tenda (camping) dan kegiatan rekreasi luar ruang lainnya.' },
  { id: 3, name: 'Telaga Menjer', lat: -7.26, lng: 109.92, type: 'attraction', rating: 4.3, cost: 5000, desc: 'Danau vulkanik terluas di area Garung. Pengunjung bisa menyewa perahu kayu dengan biaya Rp 20.000,00 atau berfoto dengan latar pegunungan yang asri.' },
  { id: 4, name: 'Bukit Cinta', lat: -7.255, lng: 109.918, type: 'attraction', rating: 4.5, cost: 15000, desc: 'Spot rekreasi dan berfoto dengan sudut pandang dari ketinggian yang menghadap langsung ke Telaga Menjer.' },
  { id: 5, name: 'Kahyangan Skyline', lat: -7.257, lng: 109.922, type: 'attraction', rating: 4.5, cost: 20000, desc: 'Destinasi modern bernuansa outdoor. Memiliki ikon jembatan kaca dan jaring gantung sebagai spot foto dengan latar Telaga Menjer.' },
  { id: 6, name: 'Bukit Saroja', lat: -7.235, lng: 109.88, type: 'attraction', rating: 4.1, cost: 25000, desc: 'Wisata alam yang menawarkan jalur pendakian via Desa Tieng. Memiliki trek yang relatif mudah sehingga sangat direkomendasikan bagi pengunjung yang hobi hiking santai. Menawarkan pemandangan alam yang indah dan merupakan lokasi yang sangat cocok untuk menikmati sunrise (matahari terbit).' },
  { id: 7, name: 'Panama', lat: -7.245, lng: 109.89, type: 'entertainment', rating: 4.2, cost: 10000, desc: 'Dikenal sebagai Kebun Teh Panama. Memiliki fasilitas boardwalk (jembatan kayu) di tengah hamparan kebun teh untuk pejalan kaki dan spot foto.' },
  { id: 8, name: 'Swiss Van Java', lat: -7.25, lng: 109.91, type: 'attraction', rating: 4.3, cost: 10000, desc: 'Area viewpoint dengan lanskap pegunungan hijau dan tatanan alam yang sering disandingkan dengan keindahan pedesaan Swiss.' },
  { id: 9, name: 'Curug Sikarim', lat: -7.23, lng: 109.892, type: 'attraction', rating: 4.4, cost: 15000, desc: 'Air terjun eksotis dengan debit air deras. Akses jalannya menanjak tajam dan cukup ekstrem, menuntut kondisi kendaraan yang prima.' },
  { id: 10, name: 'Telaga Cebong', lat: -7.224, lng: 109.899, type: 'attraction', rating: 4.5, cost: 0, desc: 'Titik kumpul utama dan area camping ground bagi wisatawan yang bersiap untuk melakukan pendakian ke Bukit Sikunir saat subuh.' },
  { id: 11, name: 'Bukit Sikunir', lat: -7.225, lng: 109.9, type: 'attraction', rating: 4.8, cost: 15000, desc: 'Destinasi terpopuler untuk berburu Golden Sunrise. Jalur pendakiannya berupa anak tangga yang tertata, memakan waktu sekitar 30-45 menit.' },
  { id: 12, name: 'Gunung Bismo Via Sikunang', lat: -7.24, lng: 109.87, type: 'attraction', rating: 4.1, cost: 35000, desc: 'Jalur pendakian Gunung Bismo yang relatif lebih singkat. Biaya parkir dihitung untuk tarif menginap (camping).' },
  { id: 13, name: 'Kawah Sikidang Pintu A dan Komplek Candi Arjuna', lat: -7.2125, lng: 109.9064, type: 'attraction', rating: 4.2, cost: 35000, desc: 'Tiket terusan (bundling) untuk dua ikon wisata Dieng. Pintu A adalah gerbang utama yang terintegrasi dengan deretan panjang kios oleh-oleh.' },
  { id: 14, name: 'Kawah Sikidang Pintu B dan Komplek Candi Arjuna', lat: -7.213, lng: 109.907, type: 'attraction', rating: 4.3, cost: 35000, desc: 'Tiket terusan (bundling). Akses alternatif dengan rute perjalanan yang relatif lebih dekat karena hanya putar balik. Pengunjung tidak perlu berjalan jauh melewati deretan kios, sehingga sangat cocok untuk wisatawan yang tidak kuat berjalan jauh atau lansia.' },
  { id: 15, name: 'Candi Bima', lat: -7.2153, lng: 109.9142, type: 'culture', rating: 4.2, cost: 0, desc: 'Candi dengan corak arsitektur khas India Utara. Berlokasi tepat di pinggir jalan utama menuju Kawah Sikidang Pintu A.' },
  { id: 16, name: 'Dieng Pelataue Theater', lat: -7.2083, lng: 109.9056, type: 'culture', rating: 4.5, cost: 10000, desc: 'Teater bioskop mini (Dieng Plateau Theater) yang memutar film dokumenter tentang sejarah letusan gunung, geografi, dan budaya masyarakat Dieng.' },
  { id: 17, name: 'Batu Pandang Ratapan Angin', lat: -7.2108, lng: 109.9167, type: 'attraction', rating: 4.4, cost: 15000, desc: 'Destinasi favorit berisi bebatuan tebing menjulang tinggi. Ini adalah titik terbaik untuk melihat gradasi warna Telaga Warna dan Telaga Pengilon dari atas.' },
  { id: 18, name: 'Telaga Warna', lat: -7.2167, lng: 109.915, type: 'attraction', rating: 4.5, cost: 27000, desc: 'Danau vulkanik di kawasan konservasi BKSDA yang airnya bisa memantulkan warna berbeda karena kandungan sulfur. Area ini rimbun dan sakral karena di pulaunya terdapat banyak gua.' },
  { id: 19, name: 'Kebun Teh Tambi', lat: -7.27, lng: 109.85, type: 'entertainment', rating: 4.2, cost: 10000, desc: 'Wisata agro peninggalan Belanda. Wisatawan bisa berkeliling hamparan kebun teh yang luas, atau mengikuti tur pabrik teh (ada biaya terpisah).' },
  { id: 20, name: 'Taman Langit', lat: -7.22, lng: 109.885, type: 'entertainment', rating: 4.3, cost: 15000, desc: 'Area wisata dataran tinggi yang didesain untuk bersantai menikmati lanskap perbukitan. Merupakan spot yang sangat direkomendasikan untuk melihat sunrise, dengan suasana dan pemandangan yang hampir sama indahnya dengan Watu Angkruk.' },
  { id: 21, name: 'Watu Angkruk', lat: -7.22, lng: 109.887, type: 'attraction', rating: 4.4, cost: 15000, desc: 'Destinasi populer untuk melihat sunrise tanpa perlu mendaki jauh. Tersedia spot jembatan kaca (glass skywalk) dan kereta kencana tembaga.' },
  { id: 22, name: 'Bukit Sikapuk', lat: -7.218, lng: 109.883, type: 'attraction', rating: 4.5, cost: 15000, desc: 'Area lereng bukit yang menawarkan pemandangan hamparan awan dan pegunungan. Alternatif yang tenang untuk menikmati sunrise dan berfoto.' },
  { id: 23, name: 'Gunung Pakuwaja via Parikesit', lat: -7.21, lng: 109.875, type: 'attraction', rating: 4.6, cost: 30000, desc: 'Jalur pendakian menuju ikon batu vertikal raksasa yang dipercaya sebagai \'paku\' penguat Pulau Jawa. Tarif parkir berlaku untuk inap.' },
  { id: 24, name: 'Gunung Prau via Igirmranak', lat: -7.19, lng: 109.92, type: 'attraction', rating: 4.1, cost: 35000, desc: 'Jalur pendakian Prau yang relatif landai namun berdurasi lebih panjang. Cocok untuk pendaki yang ingin menghindari keramaian. Tarif parkir inap.' },
  { id: 25, name: 'Gunung Prau via Patakbanteng', lat: -7.185, lng: 109.915, type: 'attraction', rating: 4.2, cost: 40000, desc: 'Jalur pendakian Gunung Prau yang paling ramai dan populer. Treknya menanjak namun rutenya paling singkat menuju area sabana. Tarif parkir inap.' },
  { id: 26, name: 'Gunung Prau via Kali Lembu', lat: -7.192, lng: 109.91, type: 'attraction', rating: 4.3, cost: 35000, desc: 'Jalur alternatif menuju puncak Prau yang lebih tenang. Didominasi trek panjang melipir perbukitan. Tarif parkir inap.' },
  { id: 27, name: 'Gunung Paru via Dieng', lat: -7.195, lng: 109.905, type: 'attraction', rating: 4.4, cost: 30000, desc: 'Rute pendakian klasik dari kawasan inti Dieng, akan melintasi area yang sering disebut sebagai Bukit Teletubbies.' },
  { id: 28, name: 'Tuk Bimolukar', lat: -7.2119, lng: 109.9094, type: 'attraction', rating: 4.5, cost: 5000, desc: 'Mata air kuno yang disucikan dan bersejarah. Airnya sangat dingin, dan penduduk lokal percaya bahwa mencuci muka di sini dapat membuat awet muda.' },
  { id: 29, name: 'Bukit Scoter', lat: -7.206, lng: 109.908, type: 'attraction', rating: 4.6, cost: 15000, desc: 'Bukit landai yang sangat dekat dengan pusat desa Dieng Kulon. Spot santai terbaik untuk melihat lanskap desa, persawahan, dan kawasan candi.' },
  { id: 30, name: 'Bukit Sipandu', lat: -7.24, lng: 109.93, type: 'attraction', rating: 4.1, cost: 15000, desc: 'Berada di perbatasan Banjarnegara dan Batang. Menawarkan lanskap sabana dan padang rumput ilalang dengan view pegunungan utara Jawa.' },
  { id: 31, name: 'D-Qiano Water Park', lat: -7.205, lng: 109.902, type: 'entertainment', rating: 4.2, cost: 15000, desc: 'Taman rekreasi air terbesar di area Dieng. Menyediakan kolam renang air panas bumi alami, dilengkapi berbagai fasilitas seluncuran air.' },
  { id: 32, name: 'Banyu Alam Hot Spring', lat: -7.203, lng: 109.9, type: 'entertainment', rating: 4.3, cost: 15000, desc: 'Pemandian air panas alami yang ideal untuk berendam merelaksasikan otot-otot di tengah cuaca Dieng yang membekukan.' },
  { id: 33, name: 'Pemandian Air Panas Bitingan', lat: -7.209, lng: 109.912, type: 'entertainment', rating: 4.4, cost: 5000, desc: 'Fasilitas pemandian tradisional berbahan dasar mata air panas vulkanik yang dikelola secara komunal oleh warga lokal setempat.' },
  { id: 34, name: 'Museum Kailasa', lat: -7.2075, lng: 109.9058, type: 'culture', rating: 4.5, cost: 5000, desc: 'Museum geologi dan sejarah terlengkap di Dieng. Menyimpan artefak candi, informasi pembentukan alam, letusan kawah, hingga kehidupan sosial budaya.' },
  { id: 35, name: 'Candi Gatot Kaca', lat: -7.2097, lng: 109.9089, type: 'culture', rating: 4.6, cost: 0, desc: 'Situs peninggalan Mataram Kuno yang terdiri dari candi tunggal. Dapat dikunjungi tanpa tiket karena letaknya di ruang terbuka tepi jalan.' },
  { id: 36, name: 'Telaga Merdada', lat: -7.2189, lng: 109.9178, type: 'attraction', rating: 4.1, cost: 5000, desc: 'Telaga dengan area terluas di kawasan Dataran Tinggi Dieng. Perairan ini tidak beracun sehingga sering digunakan untuk kayak dan irigasi pertanian.' },
  { id: 37, name: 'Telaga Sewiwi', lat: -7.2195, lng: 109.92, type: 'attraction', rating: 4.2, cost: 0, desc: 'Telaga kecil nan rindang yang biasanya dinikmati saat wisatawan melintas. Pemandangannya hening dan belum banyak infrastruktur komersial.' },
  { id: 38, name: 'Telaga Sedringo', lat: -7.222, lng: 109.925, type: 'attraction', rating: 4.3, cost: 10000, desc: 'Sering disebut sebagai Telaga Dringo. Akses jalannya ekstrem, namun pemandangannya sangat indah bak Ranu Kumbolo, menjadikannya surga camping.' },
  { id: 39, name: 'Kawah Candradimuka', lat: -7.2042, lng: 109.9125, type: 'attraction', rating: 4.4, cost: 15000, desc: 'Kawah legendaris yang dikaitkan dengan mitos pewayangan tempat penyucian Gatotkaca. Suasananya masih sangat natural dan cukup tersembunyi.' },
  { id: 40, name: 'Kebun Teh Kertosari', lat: -7.265, lng: 109.86, type: 'entertainment', rating: 4.5, cost: 7000, desc: 'Wisata agro alternatif berupa hamparan perkebunan teh yang menghijau dengan udara sejuk, cocok untuk sekadar bersantai menjauh dari keramaian.' },
  { id: 41, name: 'Dieng Park', lat: -7.216, lng: 109.914, type: 'attraction', rating: 4.6, cost: 15000, desc: 'Kawasan bukit yang menawarkan titik pantau strategis untuk menikmati pemandangan Telaga Warna dari atas. Tempat ini merupakan destinasi yang sangat lengkap karena ideal digunakan untuk melihat sunrise (matahari terbit) pada pagi hari dan sunset (matahari terbenam) pada sore hari.' },
  { id: 42, name: 'Kebun Teh Sikatok', lat: -7.268, lng: 109.855, type: 'entertainment', rating: 4.1, cost: 10000, desc: 'Destinasi agro dengan hamparan daun teh yang memanjakan mata. Terdapat titian jembatan kayu memanjang yang estetik untuk spot berfoto.' },
  { id: 43, name: 'Taman Rumah Peri', lat: -7.204, lng: 109.904, type: 'entertainment', rating: 4.2, cost: 10000, desc: 'Tempat wisata ramah anak dan keluarga yang dikonsep khusus dengan spot foto unik berupa rumah-rumah kurcaci dan dekorasi miniatur ala negeri dongeng.' },
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
