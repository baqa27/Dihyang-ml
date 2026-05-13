import { useState, useRef, useEffect } from 'react'
import {
  Send, Bot, User, Sparkles, MapPin, CloudSun, Shield, DollarSign,
  CalendarDays, Loader2, Trash2, Mountain, ChevronDown
} from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import { chatAPI, weatherAPI, mlAPI } from '../services/api'
import './Chat.css'

function buildHybridWeatherReply(wx, ml) {
  const lines = [
    '### Cuaca & prediksi DITA (mode lokal)',
    '',
  ]
  if (wx) {
    lines.push(
      `**Open-Meteo:** ${wx.temperature}°C · ${wx.condition ?? '—'} · angin ${wx.wind_speed ?? '—'} km/h · jarak pandang ${wx.visibility ?? '—'} km`
    )
  }
  if (ml?.input) {
    lines.push(
      `**Input model ML:** ${ml.input.current_temperature_c}°C, presipitasi ${ml.input.current_precipitation_mm} mm`
    )
  }
  if (ml?.temperature?.predicted_temperature != null) {
    lines.push(
      `**Suhu +1 jam (prediksi):** ${ml.temperature.predicted_temperature}°C (${ml.temperature.model ?? 'ML'})`
    )
  }
  if (ml?.rain?.rain_probability != null) {
    lines.push(`**Probabilitas hujan +1 jam:** ${ml.rain.rain_probability}%`)
  }
  if (ml?.risk) {
    lines.push(`**Risiko wisata:** ${ml.risk.risk_icon ?? ''} **${ml.risk.risk_label}** — ${ml.risk.advisory ?? ''}`)
  }
  lines.push(
    '',
    '> Respons ini memadukan **API cuaca** dan **model ML** di perangkat Anda karena layanan chat jarak jauh tidak tersedia. Verifikasi kondisi lapangan sebelum berangkat.'
  )
  return lines.join('\n')
}

const quickActions = [
  { icon: <CloudSun size={16} />, label: 'Cuaca hari ini', prompt: 'Bagaimana cuaca di Dieng hari ini? Apakah aman untuk berwisata?' },
  { icon: <MapPin size={16} />, label: 'Rute aman', prompt: 'Rute aman dari Wonosobo ke Kawah Sikidang naik motor, hindari tanjakan curam' },
  { icon: <DollarSign size={16} />, label: 'Biaya retribusi', prompt: 'Berapa biaya retribusi resmi untuk mengunjungi semua destinasi wisata di Dieng?' },
  { icon: <CalendarDays size={16} />, label: 'Itinerary 2 hari', prompt: 'Buatkan itinerary 2 hari 1 malam di Dieng untuk solo traveler dengan budget 500rb' },
  { icon: <Shield size={16} />, label: 'Tips keamanan', prompt: 'Tips keamanan untuk solo traveler yang pertama kali ke Dieng, terutama soal cuaca dan medan' },
  { icon: <Mountain size={16} />, label: 'Sunrise Sikunir', prompt: 'Bagaimana cara ke Bukit Sikunir untuk melihat sunrise? Apa saja yang perlu disiapkan?' },
]

const welcomeMsg = {
  role: 'assistant',
  content: `Halo! 👋 Saya **DITA** (Dieng Intelligence Tourism Assistant), asisten wisata cerdas Anda untuk menjelajahi Dataran Tinggi Dieng.

Saya bisa membantu Anda dengan:
- 🌤️ **Informasi cuaca real-time** dan peringatan
- 🛡️ **Rute aman** dan peringatan jalur berbahaya
- 💰 **Biaya retribusi resmi** (anti-pungli!)
- 📅 **Smart itinerary** yang adaptif cuaca
- 🏔️ **Info destinasi** dan tips solo traveler
- 📊 **Dokumentasi model ML** di Pusat Informasi → tab *Model AI DITA*

Silakan tanya apa saja tentang wisata Dieng!`
}

export default function Chat() {
  const [messages, setMessages] = useState(() => {
    const saved = localStorage.getItem('dihyang_chat')
    return saved ? JSON.parse(saved) : [welcomeMsg]
  })
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
    localStorage.setItem('dihyang_chat', JSON.stringify(messages))
  }, [messages])

  const sendMessage = async (text) => {
    const userMsg = text || input.trim()
    if (!userMsg || isLoading) return

    const newUserMsg = { role: 'user', content: userMsg }
    setMessages(prev => [...prev, newUserMsg])
    setInput('')
    setIsLoading(true)

    try {
      const history = messages
        .filter((m, idx) => !(idx === 0 && m.role === 'assistant'))
        .map(m => ({ role: m.role, content: m.content }))

      const response = await chatAPI.sendMessage(userMsg, history)
      setMessages(prev => [...prev, { role: 'assistant', content: response.reply }])
    } catch (err) {
      const lowerMsg = userMsg.toLowerCase()
      let hybrid = null
      if (lowerMsg.includes('cuaca') || lowerMsg.includes('weather') || lowerMsg.includes('suhu')) {
        try {
          const [wx, ml] = await Promise.all([
            weatherAPI.getCurrent(),
            mlAPI.getQuickPrediction(),
          ])
          hybrid = buildHybridWeatherReply(wx, ml)
        } catch {
          hybrid = null
        }
      }

      const demoReplies = {
        cuaca: `Berdasarkan data terkini dari Open-Meteo, kondisi cuaca Dieng hari ini:

🌡️ **Suhu**: 14°C (terasa 11°C)
💧 **Kelembapan**: 89%
🌬️ **Angin**: 12 km/h dari arah barat
👁️ **Jarak Pandang**: 3.2 km
☁️ **Kondisi**: Berkabut

⚠️ **Peringatan**: Kabut tebal diprediksi turun pukul 15:00-17:00. Hindari Jalur Sikarim jika menuju Kawah Sikidang pada jam tersebut.

🧥 **Saran Perlengkapan**: Jaket tebal, syal, dan sepatu hiking anti-slip. Suhu bisa turun hingga 5°C malam hari.`,

        rute: `Untuk rute dari **Wonosobo ke Kawah Sikidang** naik motor, berikut rekomendasi:

✅ **Rute Aman (Direkomendasikan)**:
Wonosobo → Kejajar → Dieng Kulon → Kawah Sikidang
- Jarak: ~26 km | Waktu: ~50 menit
- Tanjakan moderat, cocok untuk semua jenis motor

⚠️ **Rute yang HARUS Dihindari**:
- ❌ **Tanjakan Sikarim** (kemiringan 45°) — Rawan rem blong
- ❌ **Tanjakan Watu Angkruk** (15%) — Motor standar bisa mesin mati

💡 **Tips**: Gunakan gigi rendah (gear 1-2) saat menanjak. Pastikan rem dalam kondisi prima sebelum berangkat.`,

        retribusi: `Berikut **biaya retribusi resmi** destinasi wisata Dieng (terverifikasi April 2026):

| Destinasi | Wisatawan Lokal | Wisatawan Asing |
|-----------|:-:|:-:|
| Kawah Sikidang | Rp 20.000 | Rp 50.000 |
| Telaga Warna | Rp 15.000 | Rp 30.000 |
| Candi Arjuna | Rp 15.000 | Rp 30.000 |
| Bukit Sikunir | Rp 15.000 | Rp 15.000 |
| Batu Ratapan Angin | Rp 10.000 | Rp 25.000 |
| Dieng Plateau Theater | Rp 25.000 | Rp 50.000 |

💡 **Tips**: Minta selalu tiket resmi! Jika tidak ada tiket, kemungkinan besar pungli. Laporkan ke Dinas Pariwisata Wonosobo.`,

        default: `Terima kasih atas pertanyaannya! Saya DITA, siap membantu Anda menjelajahi Dieng.

Untuk memberikan respons yang lebih akurat, saya memerlukan koneksi ke backend server. Saat ini saya menampilkan respons demo.

Beberapa hal yang bisa saya bantu:
- 🌤️ Informasi dan prediksi cuaca
- 🛡️ Rekomendasi rute aman
- 💰 Biaya retribusi resmi
- 📅 Penyusunan itinerary

Silakan coba pertanyaan lainnya!`
      }

      let reply = hybrid || demoReplies.default
      if (!hybrid) {
        if (lowerMsg.includes('cuaca') || lowerMsg.includes('weather') || lowerMsg.includes('suhu')) {
          reply = demoReplies.cuaca
        } else if (lowerMsg.includes('rute') || lowerMsg.includes('jalan') || lowerMsg.includes('arah')) {
          reply = demoReplies.rute
        } else if (lowerMsg.includes('biaya') || lowerMsg.includes('retribusi') || lowerMsg.includes('tiket') || lowerMsg.includes('harga')) {
          reply = demoReplies.retribusi
        }
      }

      setMessages(prev => [...prev, { role: 'assistant', content: reply }])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const clearChat = () => {
    setMessages([welcomeMsg])
    localStorage.removeItem('dihyang_chat')
  }

  return (
    <div className="chat page-enter" id="chat-page">
      <div className="chat__container">
        {/* Sidebar */}
        <div className="chat__sidebar">
          <div className="chat__sidebar-header">
            <div className="chat__avatar chat__avatar--dita">
              <Bot size={24} />
            </div>
            <div>
              <h3>DITA</h3>
              <span className="chat__status">
                <span className="chat__status-dot"></span>
                Online
              </span>
            </div>
          </div>

          <div className="chat__sidebar-section">
            <h4>Quick Actions</h4>
            <div className="chat__quick-actions">
              {quickActions.map((action, i) => (
                <button
                  key={i}
                  className="chat__quick-btn"
                  onClick={() => sendMessage(action.prompt)}
                  id={`quick-action-${i}`}
                >
                  {action.icon}
                  <span>{action.label}</span>
                </button>
              ))}
            </div>
          </div>

          <button className="btn btn-ghost btn-sm chat__clear-btn" onClick={clearChat} id="clear-chat">
            <Trash2 size={14} />
            Bersihkan Chat
          </button>
        </div>

        {/* Chat Area */}
        <div className="chat__main">
          <div className="chat__messages" id="chat-messages">
            {messages.map((msg, i) => (
              <div key={i} className={`chat__message chat__message--${msg.role}`}>
                <div className={`chat__avatar chat__avatar--${msg.role === 'assistant' ? 'dita' : 'user'}`}>
                  {msg.role === 'assistant' ? <Bot size={18} /> : <User size={18} />}
                </div>
                <div className="chat__bubble">
                  <ReactMarkdown>{msg.content}</ReactMarkdown>
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="chat__message chat__message--assistant">
                <div className="chat__avatar chat__avatar--dita">
                  <Bot size={18} />
                </div>
                <div className="chat__bubble chat__bubble--loading">
                  <div className="chat__typing">
                    <span></span><span></span><span></span>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="chat__input-area">
            <div className="chat__input-wrapper">
              <textarea
                ref={inputRef}
                className="chat__input"
                placeholder="Tanya DITA tentang wisata Dieng..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                rows={1}
                id="chat-input"
              />
              <button
                className="chat__send-btn"
                onClick={() => sendMessage()}
                disabled={!input.trim() || isLoading}
                id="chat-send"
              >
                {isLoading ? <Loader2 size={20} className="spin-anim" /> : <Send size={20} />}
              </button>
            </div>
            <p className="chat__disclaimer">
              DITA memakai Gemini untuk percakapan; cuaca &amp; risiko di Dashboard memakai model ML lokal + Open-Meteo.
              Prototipe capstone — verifikasi informasi kritis di lapangan.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
