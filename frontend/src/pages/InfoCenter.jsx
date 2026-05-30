import { useState, useEffect } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import {
  Info, Shield, DollarSign, Bed, Navigation, AlertTriangle, MapPin,
  Cpu, Loader2, Zap, BarChart3
} from 'lucide-react'
import { mlAPI } from '../services/api'
import './InfoCenter.css'

const infoCategories = [
  { id: 'retribusi', label: 'Biaya Retribusi', icon: <DollarSign size={18} /> },
  { id: 'transportasi', label: 'Transportasi', icon: <Navigation size={18} /> },
  { id: 'penginapan', label: 'Penginapan', icon: <Bed size={18} /> },
  { id: 'regulasi', label: 'Regulasi & Keamanan', icon: <Shield size={18} /> },
  { id: 'model-ai', label: 'Model AI DITA', icon: <Cpu size={18} /> },
]

const retribusiData = [
  // === Data dari CSV asli (riset lapangan tim PJK-GM067) ===
  { name: 'Tiket Kawasan', local: 15000, asing: 50000, parkirMotor: 0, parkirMobil: 0, note: 'Wajib saat melintasi gerbang utama' },
  { name: 'Pandangan Pertama', local: 10000, asing: 10000, parkirMotor: 2000, parkirMobil: 5000 },
  { name: 'Telaga Menjer', local: 5000, asing: 15000, parkirMotor: 2000, parkirMobil: 5000 },
  { name: 'Bukit Cinta', local: 15000, asing: 15000, parkirMotor: 5000, parkirMobil: 10000 },
  { name: 'Kahyangan Skyline', local: 20000, asing: 20000, parkirMotor: 2000, parkirMobil: 5000 },
  { name: 'Bukit Saroja', local: 25000, asing: 25000, parkirMotor: 10000, parkirMobil: 20000 },
  { name: 'Panama (Kebun Teh)', local: 10000, asing: 10000, parkirMotor: 3000, parkirMobil: 5000 },
  { name: 'Swiss Van Java', local: 10000, asing: 10000, parkirMotor: 0, parkirMobil: 0 },
  { name: 'Curug Sikarim', local: 15000, asing: 15000, parkirMotor: 5000, parkirMobil: 10000 },
  { name: 'Telaga Cebong', local: 0, asing: 0, parkirMotor: 5000, parkirMobil: 15000, note: 'Gratis masuk, bayar parkir' },
  { name: 'Bukit Sikunir', local: 15000, asing: 30000, parkirMotor: 5000, parkirMobil: 15000 },
  { name: 'Gunung Bismo via Sikunang', local: 35000, asing: 35000, parkirMotor: 10000, parkirMobil: 20000 },
  { name: 'Kawah Sikidang + Candi Arjuna (Pintu A)', local: 35000, asing: 50000, parkirMotor: 5000, parkirMobil: 10000, note: 'Tiket bundling' },
  { name: 'Kawah Sikidang + Candi Arjuna (Pintu B)', local: 35000, asing: 50000, parkirMotor: 2000, parkirMobil: 10000, note: 'Akses alternatif, lebih dekat' },
  { name: 'Candi Bima', local: 0, asing: 0, parkirMotor: 2000, parkirMobil: 5000, note: 'Gratis' },
  { name: 'Dieng Plateau Theater', local: 10000, asing: 15000, parkirMotor: 2000, parkirMobil: 5000 },
  { name: 'Batu Pandang Ratapan Angin', local: 15000, asing: 20000, parkirMotor: 2000, parkirMobil: 5000 },
  { name: 'Telaga Warna', local: 27000, asing: 60000, parkirMotor: 5000, parkirMobil: 10000, note: 'Kawasan BKSDA' },
  { name: 'Kebun Teh Tambi', local: 10000, asing: 10000, parkirMotor: 2000, parkirMobil: 7000 },
  { name: 'Taman Langit', local: 15000, asing: 15000, parkirMotor: 5000, parkirMobil: 10000 },
  { name: 'Watu Angkruk', local: 15000, asing: 15000, parkirMotor: 3000, parkirMobil: 7000 },
  { name: 'Bukit Sikapuk', local: 15000, asing: 15000, parkirMotor: 3000, parkirMobil: 7000 },
  { name: 'Gunung Pakuwaja via Parikesit', local: 30000, asing: 30000, parkirMotor: 10000, parkirMobil: 25000 },
  { name: 'Gunung Prau via Igirmranak', local: 35000, asing: 30000, parkirMotor: 10000, parkirMobil: 25000 },
  { name: 'Gunung Prau via Patakbanteng', local: 40000, asing: 40000, parkirMotor: 10000, parkirMobil: 20000 },
  { name: 'Gunung Prau via Kali Lembu', local: 35000, asing: 35000, parkirMotor: 10000, parkirMobil: 25000 },
  { name: 'Gunung Prau via Dieng', local: 30000, asing: 30000, parkirMotor: 10000, parkirMobil: 25000 },
  { name: 'Tuk Bimolukar', local: 5000, asing: 5000, parkirMotor: 2000, parkirMobil: 2000 },
  { name: 'Bukit Scoter', local: 15000, asing: 15000, parkirMotor: 2000, parkirMobil: 5000 },
  { name: 'Bukit Sipandu', local: 15000, asing: 15000, parkirMotor: 5000, parkirMobil: 15000 },
  { name: 'D-Qiano Water Park', local: 15000, asing: 30000, parkirMotor: 2000, parkirMobil: 5000 },
  { name: 'Banyu Alam Hot Spring', local: 15000, asing: 15000, parkirMotor: 3000, parkirMobil: 5000 },
  { name: 'Pemandian Air Panas Bitingan', local: 5000, asing: 5000, parkirMotor: 2000, parkirMobil: 0 },
  { name: 'Museum Kailasa', local: 5000, asing: 30000, parkirMotor: 2000, parkirMobil: 5000 },
  { name: 'Candi Gatot Kaca', local: 0, asing: 0, parkirMotor: 2000, parkirMobil: 5000, note: 'Gratis' },
  { name: 'Telaga Merdada', local: 5000, asing: 5000, parkirMotor: 2000, parkirMobil: 5000 },
  { name: 'Telaga Sewiwi', local: 0, asing: 0, parkirMotor: 2000, parkirMobil: 5000, note: 'Gratis' },
  { name: 'Telaga Sedringo', local: 10000, asing: 15000, parkirMotor: 3000, parkirMobil: 5000 },
  { name: 'Kawah Candradimuka', local: 15000, asing: 15000, parkirMotor: 2000, parkirMobil: 7000 },
  { name: 'Kebun Teh Kertosari', local: 7000, asing: 7000, parkirMotor: 5000, parkirMobil: 10000 },
  { name: 'Dieng Park', local: 15000, asing: 60000, parkirMotor: 5000, parkirMobil: 10000 },
  { name: 'Kebun Teh Sikatok', local: 10000, asing: 10000, parkirMotor: 2000, parkirMobil: 5000 },
  { name: 'Taman Rumah Peri', local: 10000, asing: 10000, parkirMotor: 2000, parkirMobil: 5000 },
]

const safetyTips = [
  { title: 'Persiapan Suhu Ekstrem', desc: 'Bawa jaket tebal, sarung tangan, dan kupluk. Suhu malam hari bisa mencapai 0-5°C, terutama di bulan Juli-Agustus saat fenomena "Embun Upas" (bun upas).' },
  { title: 'Kewaspadaan Berkendara', desc: 'Gunakan gigi 1 atau 2 saat melewati tanjakan curam. Jika mesin motor matic tidak kuat di tanjakan 15% (Watu Angkruk), minta penumpang untuk turun sejenak.' },
  { title: 'Hindari Gas Beracun', desc: 'Selalu ikuti jalur yang telah ditentukan di area kawah. Jangan melompati pagar pembatas karena risiko gas CO2 yang tidak berbau dan tidak berwarna.' },
  { title: 'Waspada Pungli', desc: 'Selalu minta karcis resmi berlogo Pemkab Wonosobo atau Banjarnegara saat membayar tiket masuk. Hindari membayar kepada oknum tanpa karcis.' },
]

const TAB_IDS = new Set(infoCategories.map(c => c.id))

export default function InfoCenter() {
  const [searchParams] = useSearchParams()
  const [activeTab, setActiveTab] = useState('retribusi')
  const [modelInfo, setModelInfo] = useState(null)
  const [modelLoading, setModelLoading] = useState(false)
  const [modelError, setModelError] = useState(false)

  useEffect(() => {
    const tab = searchParams.get('tab')
    if (tab && TAB_IDS.has(tab)) setActiveTab(tab)
  }, [searchParams])

  useEffect(() => {
    if (activeTab !== 'model-ai') return
    setModelLoading(true)
    setModelError(false)
    mlAPI.getModelInfo()
      .then(setModelInfo)
      .catch(() => setModelError(true))
      .finally(() => setModelLoading(false))
  }, [activeTab])

  return (
    <div className="info-center page-enter" id="info-page">
      <div className="container">
        <div className="info-center__header">
          <span className="badge badge-primary"><Info size={12} /> Pusat Data Terverifikasi</span>
          <h1>Pusat <span className="text-gradient">Informasi</span></h1>
          <p>Panduan lengkap dan resmi untuk memastikan perjalanan Anda di Dieng aman dan nyaman.</p>
        </div>

        <div className="info-center__content">
          {/* Sidebar Navigation */}
          <div className="info-sidebar glass-card-static">
            {infoCategories.map(cat => (
              <button
                key={cat.id}
                className={`info-nav-btn ${activeTab === cat.id ? 'active' : ''}`}
                onClick={() => setActiveTab(cat.id)}
              >
                {cat.icon}
                {cat.label}
              </button>
            ))}
            
            <div className="info-sidebar__alert">
              <AlertTriangle size={16} />
              <p>Data terakhir diperbarui: <strong>April 2026</strong>. Informasi bersumber dari Dinas Pariwisata terkait.</p>
            </div>
          </div>

          {/* Main Content Area */}
          <div className="info-main glass-card-static">
            {activeTab === 'retribusi' && (
              <div className="info-section animate-fade-in">
                <h2><DollarSign size={24} /> Biaya Retribusi Resmi</h2>
                <p className="info-desc">Daftar harga tiket masuk destinasi wisata di Dieng. Pastikan Anda menerima karcis resmi sebagai bukti pembayaran.</p>
                
                <div className="table-responsive">
                  <table className="info-table">
                    <thead>
                      <tr>
                        <th>Destinasi Wisata</th>
                        <th>Wisatawan Lokal (IDR)</th>
                        <th>Wisatawan Asing (IDR)</th>
                        <th>Parkir Motor</th>
                        <th>Parkir Mobil</th>
                      </tr>
                    </thead>
                    <tbody>
                      {retribusiData.map((item, i) => (
                        <tr key={i}>
                          <td>
                            {item.name}
                            {item.note ? <span style={{fontSize:'0.75rem',color:'var(--text-muted)',display:'block'}}>{item.note}</span> : null}
                          </td>
                          <td>{item.local === 0 ? <span style={{color:'var(--success-300)'}}>Gratis</span> : `Rp ${item.local.toLocaleString('id-ID')}`}</td>
                          <td>{item.asing === 0 ? <span style={{color:'var(--success-300)'}}>Gratis</span> : `Rp ${item.asing.toLocaleString('id-ID')}`}</td>
                          <td>{item.parkirMotor === 0 ? <span style={{color:'var(--success-300)'}}>Gratis</span> : `Rp ${item.parkirMotor.toLocaleString('id-ID')}`}</td>
                          <td>{item.parkirMobil === 0 ? <span style={{color:'var(--success-300)'}}>Gratis</span> : `Rp ${item.parkirMobil.toLocaleString('id-ID')}`}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                
                <div className="info-card info-card--warning">
                  <AlertTriangle size={20} />
                  <div>
                    <h4>Laporkan Pungli!</h4>
                    <p>Jika Anda menemukan praktik pungutan liar, segera laporkan ke pos pengaduan atau hubungi kontak resmi Dinas Pariwisata Wonosobo.</p>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'regulasi' && (
              <div className="info-section animate-fade-in">
                <h2><Shield size={24} /> Regulasi & Tips Keamanan</h2>
                <p className="info-desc">Panduan penting untuk keselamatan Anda selama berada di dataran tinggi Dieng.</p>
                
                <div className="safety-grid">
                  {safetyTips.map((tip, i) => (
                    <div key={i} className="safety-card glass-card">
                      <Shield size={20} className="safety-card__icon" />
                      <h4>{tip.title}</h4>
                      <p>{tip.desc}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {activeTab === 'transportasi' && (
              <div className="info-section animate-fade-in">
                <h2><Navigation size={24} /> Panduan Transportasi</h2>
                <p className="info-desc">Opsi transportasi terbaik untuk menuju dan berkeliling di kawasan Dieng.</p>
                
                <div className="transport-list">
                  <div className="transport-item">
                    <h4>Bus Umum (Wonosobo - Dieng)</h4>
                    <p>Berangkat dari Terminal Mendolo atau Alun-alun Wonosobo. Ongkos sekitar Rp 20.000 - 25.000. Waktu tempuh 1-1.5 jam.</p>
                  </div>
                  <div className="transport-item">
                    <h4>Sewa Motor (Wonosobo)</h4>
                    <p>Mulai dari Rp 80.000 - 150.000 / hari. Sangat disarankan untuk solo traveler, pastikan rem dan ban dalam kondisi prima.</p>
                  </div>
                  <div className="transport-item">
                    <h4>Ojek Wisata Dieng</h4>
                    <p>Tersedia di area Dieng Kulon untuk rute jarak dekat. Harga bervariasi antara Rp 15.000 - 50.000 tergantung jarak. Sepakati harga sebelum naik.</p>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'penginapan' && (
              <div className="info-section animate-fade-in">
                <h2><Bed size={24} /> Rekomendasi Penginapan</h2>
                <p className="info-desc">Area strategis untuk menginap selama berada di Dieng.</p>
                
                <div className="accommodation-areas">
                  <div className="area-card">
                    <MapPin size={20} className="area-card__icon" />
                    <div className="area-card__content">
                      <h4>Desa Dieng Kulon & Wetan</h4>
                      <p>Lokasi paling strategis. Dekat dengan Candi Arjuna, Kawah Sikidang, dan minimarket. Harga homestay mulai Rp 150.000 - 500.000 / malam.</p>
                    </div>
                  </div>
                  <div className="area-card">
                    <MapPin size={20} className="area-card__icon" />
                    <div className="area-card__content">
                      <h4>Desa Sembungan</h4>
                      <p>Desa tertinggi di Pulau Jawa. Sangat cocok jika target utama Anda adalah Sunrise Sikunir. Suhu lebih dingin dari Dieng Kulon.</p>
                    </div>
                  </div>
                  <div className="area-card">
                    <MapPin size={20} className="area-card__icon" />
                    <div className="area-card__content">
                      <h4>Kota Wonosobo</h4>
                      <p>Banyak pilihan hotel berbintang. Cocok jika Anda mencari fasilitas lengkap dan suhu yang tidak terlalu ekstrem, namun butuh 1 jam perjalanan ke Dieng.</p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'model-ai' && (
              <div className="info-section info-section--model animate-fade-in">
                <h2><Cpu size={24} /> Model AI &amp; Predictive Analytics</h2>
                <p className="info-desc">
                  Ringkasan teknis model lokal DITA (cuaca, risiko, rute). Data evaluasi bersumber dari{' '}
                  <code className="info-code">evaluation_report.json</code> di backend.
                </p>

                {modelLoading && (
                  <div className="info-model-loading">
                    <Loader2 size={28} className="spin-anim" />
                    <span>Memuat metadata model…</span>
                  </div>
                )}

                {modelError && (
                  <div className="info-card info-card--warning">
                    <AlertTriangle size={20} />
                    <div>
                      <h4>Backend tidak terjangkau</h4>
                      <p>Jalankan API FastAPI (port 8000) dan pastikan proxy Vite aktif agar endpoint <code className="info-code">/api/ml/model-info</code> dapat diakses.</p>
                    </div>
                  </div>
                )}

                {!modelLoading && !modelError && modelInfo && (
                  <>
                    <div className="info-model-status glass-card">
                      <Zap size={20} />
                      <div>
                        <strong>Status pemuatan model</strong>
                        <p>{modelInfo.models_loaded ? 'Semua artefak .pkl termuat — prediksi siap dipakai.' : 'Model belum terlatih atau gagal dimuat — sistem memakai fallback rule-based.'}</p>
                      </div>
                    </div>

                    {modelInfo.dataset && (
                      <div className="info-model-dataset">
                        <h4><BarChart3 size={18} /> Dataset cuaca (training)</h4>
                        <ul>
                          <li>Lokasi: {modelInfo.dataset.location}</li>
                          <li>Periode: {modelInfo.dataset.period}</li>
                          <li>Rekaman: {modelInfo.dataset.total_records?.toLocaleString?.('id-ID') ?? modelInfo.dataset.total_records}</li>
                          <li>Fitur rekayasa: {modelInfo.dataset.features_engineered}</li>
                        </ul>
                      </div>
                    )}

                    {modelInfo.models && (
                      <div className="info-model-grid">
                        {Object.entries(modelInfo.models).map(([key, spec]) => (
                          <div key={key} className="info-model-card glass-card">
                            <h4>{spec.type ?? key}</h4>
                            <p className="info-model-card__slug">{key.replace(/_/g, ' ')}</p>
                            {spec.metrics && (
                              <dl className="info-model-metrics">
                                {Object.entries(spec.metrics).map(([mk, mv]) => (
                                  <div key={mk}>
                                    <dt>{mk}</dt>
                                    <dd>
                                      {typeof mv === 'number'
                                        ? mv.toLocaleString('id-ID', { maximumFractionDigits: 6 })
                                        : String(mv)}
                                    </dd>
                                  </div>
                                ))}
                              </dl>
                            )}
                            {spec.note && <p className="info-model-note">{spec.note}</p>}
                          </div>
                        ))}
                      </div>
                    )}

                    <div className="info-card info-card--muted">
                      <Shield size={20} />
                      <div>
                        <h4>Disclaimer</h4>
                        <p>
                          Prediksi ini prototipe penelitian capstone (PJK-GM067), bukan pengganti prakiraan resmi BMKG atau
                          penilaian risiko profesional. Keputusan berkendara dan berwisata tetap menjadi tanggung jawab pengguna.
                        </p>
                      </div>
                    </div>

                    <Link to="/dashboard" className="btn btn-primary btn-sm info-model-cta">
                      Lihat prediksi live di Dashboard
                    </Link>
                  </>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
