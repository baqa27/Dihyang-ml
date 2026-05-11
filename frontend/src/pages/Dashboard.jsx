import { useState, useEffect } from 'react'
import {
  CloudSun, Thermometer, Droplets, Wind, Eye, ArrowUp, ArrowDown,
  CloudRain, Sun, CloudFog, AlertTriangle, Clock, TrendingUp,
  Calendar, RefreshCw, Zap
} from 'lucide-react'
import { LineChart, Line, AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { weatherAPI, mlAPI } from '../services/api'
import './Dashboard.css'

// Dieng-realistic temperature pattern (consistent with ML training data)
const baseTempByHour = {
  0:9, 1:8.5, 2:8, 3:7.5, 4:7.5, 5:8, 6:9, 7:11, 8:13,
  9:15, 10:17, 11:18, 12:19, 13:19.5, 14:19, 15:17, 16:15,
  17:13, 18:12, 19:11, 20:10.5, 21:10, 22:9.5, 23:9
}
const hourlyData = Array.from({ length: 24 }, (_, i) => ({
  hour: `${i.toString().padStart(2, '0')}:00`,
  temp: Math.round((baseTempByHour[i] || 14) + (Math.random() - 0.5) * 2),
  humidity: Math.round(i >= 18 || i <= 6 ? 90 + Math.random() * 5 : 70 + Math.random() * 10),
  wind: Math.round(8 + Math.sin(i / 12 * Math.PI) * 6 + Math.random() * 2),
}))

const weeklyData = [
  { day: 'Sen', high: 18, low: 7, rain: 20, condition: 'Cerah' },
  { day: 'Sel', high: 16, low: 8, rain: 45, condition: 'Berawan' },
  { day: 'Rab', high: 14, low: 6, rain: 80, condition: 'Hujan' },
  { day: 'Kam', high: 15, low: 7, rain: 30, condition: 'Berkabut' },
  { day: 'Jum', high: 17, low: 8, rain: 15, condition: 'Cerah' },
  { day: 'Sab', high: 19, low: 9, rain: 10, condition: 'Cerah' },
  { day: 'Min', high: 16, low: 7, rain: 55, condition: 'Berawan' },
]

const monthlyTrend = Array.from({ length: 30 }, (_, i) => ({
  date: `${(i + 1).toString().padStart(2, '0')}/05`,
  avgTemp: Math.round(12 + Math.sin(i / 30 * Math.PI * 2) * 4 + Math.random() * 2),
  rainfall: Math.round(Math.random() * 25 + (i > 10 && i < 20 ? 15 : 0)),
}))

const alerts = [
  { type: 'danger', icon: <CloudFog size={16} />, msg: 'Kabut tebal diprediksi turun dalam 30 menit, hindari Jalur Sikarim jika menuju Kawah Sikidang', time: '10 menit lalu' },
  { type: 'warning', icon: <CloudRain size={16} />, msg: 'Hujan ringan diprediksi pukul 14:00-16:00. Siapkan jas hujan jika berwisata outdoor.', time: '25 menit lalu' },
  { type: 'info', icon: <Thermometer size={16} />, msg: 'Suhu terendah malam ini diprediksi 5°C. Gunakan jaket tebal dan selimut ekstra.', time: '1 jam lalu' },
]

const getConditionIcon = (condition) => {
  switch (condition) {
    case 'Cerah': return <Sun size={18} />
    case 'Berawan': return <CloudSun size={18} />
    case 'Hujan': return <CloudRain size={18} />
    case 'Berkabut': return <CloudFog size={18} />
    default: return <CloudSun size={18} />
  }
}

export default function Dashboard() {
  const currentHour = new Date().getHours()
  const estTemp = baseTempByHour[currentHour] || 14
  
  const [weather, setWeather] = useState({
    temperature: estTemp,
    feels_like: Math.round(estTemp - 3),
    humidity: currentHour >= 18 || currentHour <= 6 ? 92 : 78,
    wind_speed: 10 + Math.round(Math.random() * 5),
    visibility: currentHour >= 15 && currentHour <= 17 ? 2.5 : 5.8,
    condition: currentHour >= 15 && currentHour <= 17 ? 'Berkabut' : currentHour >= 13 && currentHour <= 16 ? 'Berawan' : 'Cerah Berawan',
    pressure: 1013,
    uv_index: currentHour >= 10 && currentHour <= 14 ? 5 : 2,
    high: 19,
    low: 7,
  })
  const [loading, setLoading] = useState(false)
  const [mlPrediction, setMlPrediction] = useState(null)

  useEffect(() => {
    // Fetch ML prediction on mount
    mlAPI.getQuickPrediction()
      .then(data => setMlPrediction(data))
      .catch(() => {})
  }, [])

  const refreshWeather = () => {
    setLoading(true)
    weatherAPI.getCurrent()
      .then(data => setWeather(prev => ({ ...prev, ...data })))
      .catch(() => {})
      .finally(() => setLoading(false))
  }

  const customTooltipStyle = {
    backgroundColor: 'rgba(15, 23, 42, 0.95)',
    border: '1px solid rgba(255,255,255,0.1)',
    borderRadius: '8px',
    padding: '10px 14px',
    color: '#f1f5f9',
    fontSize: '0.82rem',
  }

  return (
    <div className="dashboard page-enter">
      <div className="container">
        {/* Page Header */}
        <div className="dashboard__header">
          <div>
            <h1>Dashboard <span className="text-gradient">Cuaca</span></h1>
            <p>Monitor kondisi cuaca mikroklimat Dieng secara real-time</p>
          </div>
          <button className="btn btn-outline btn-sm" onClick={refreshWeather} id="refresh-weather">
            <RefreshCw size={16} className={loading ? 'spin-anim' : ''} />
            Refresh
          </button>
        </div>

        {/* Weather Overview Cards */}
        <div className="dashboard__overview">
          <div className="overview-card overview-card--main glass-card-static">
            <div className="overview-card__top">
              <CloudSun size={24} />
              <span>Sekarang</span>
            </div>
            <div className="overview-card__temp">
              <span className="overview-card__temp-val">{weather.temperature}°</span>
              <div className="overview-card__temp-meta">
                <span className="overview-card__condition">{weather.condition}</span>
                <span className="overview-card__feels">Terasa {weather.feels_like}°C</span>
              </div>
            </div>
            <div className="overview-card__range">
              <span><ArrowUp size={14} /> {weather.high}°</span>
              <span><ArrowDown size={14} /> {weather.low}°</span>
            </div>
          </div>

          {[
            { icon: <Droplets size={22} />, label: 'Kelembapan', value: `${weather.humidity}%`, color: '#00b4cc' },
            { icon: <Wind size={22} />, label: 'Kecepatan Angin', value: `${weather.wind_speed} km/h`, color: '#a78bfa' },
            { icon: <Eye size={22} />, label: 'Jarak Pandang', value: `${weather.visibility} km`, color: '#f59e0b' },
            { icon: <Thermometer size={22} />, label: 'Tekanan Udara', value: `${weather.pressure} hPa`, color: '#22c55e' },
          ].map((card, i) => (
            <div key={i} className="overview-card glass-card-static">
              <div className="overview-card__top" style={{ color: card.color }}>
                {card.icon}
              </div>
              <span className="overview-card__label">{card.label}</span>
              <span className="overview-card__value">{card.value}</span>
            </div>
          ))}
        </div>

        {/* ML Prediction Card */}
        {mlPrediction && (
          <div className="dashboard__ml-prediction glass-card-static" style={{ marginBottom: '1.5rem', padding: '1.2rem 1.5rem', borderLeft: `4px solid ${mlPrediction.risk?.risk_color || '#22c55e'}` }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.3rem' }}>
                  <Zap size={16} style={{ color: '#00b4cc' }} />
                  <span style={{ fontSize: '0.75rem', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Prediksi AI (Machine Learning)</span>
                </div>
                <p style={{ color: '#f1f5f9', margin: '0.3rem 0', fontSize: '0.9rem' }}>
                  {mlPrediction.risk?.advisory || 'Model AI sedang memproses data cuaca...'}
                </p>
              </div>
              <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                {mlPrediction.temperature && (
                  <div style={{ textAlign: 'center' }}>
                    <span style={{ fontSize: '0.7rem', color: '#94a3b8' }}>Prediksi Suhu</span>
                    <div style={{ fontSize: '1.3rem', fontWeight: 700, color: '#00b4cc' }}>
                      {mlPrediction.temperature.predicted_temperature}°C
                    </div>
                  </div>
                )}
                {mlPrediction.rain && (
                  <div style={{ textAlign: 'center' }}>
                    <span style={{ fontSize: '0.7rem', color: '#94a3b8' }}>Probabilitas Hujan</span>
                    <div style={{ fontSize: '1.3rem', fontWeight: 700, color: '#a78bfa' }}>
                      {mlPrediction.rain.rain_probability}%
                    </div>
                  </div>
                )}
                {mlPrediction.risk && (
                  <div style={{ textAlign: 'center' }}>
                    <span style={{ fontSize: '0.7rem', color: '#94a3b8' }}>Status Risiko</span>
                    <div style={{ fontSize: '1.3rem', fontWeight: 700, color: mlPrediction.risk.risk_color }}>
                      {mlPrediction.risk.risk_icon} {mlPrediction.risk.risk_label}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Alerts */}
        <div className="dashboard__alerts">
          <h3><AlertTriangle size={18} /> Peringatan Proaktif</h3>
          <div className="alerts-list">
            {alerts.map((alert, i) => (
              <div key={i} className={`alert-item alert-item--${alert.type}`} id={`alert-${i}`}>
                <div className="alert-item__icon">{alert.icon}</div>
                <div className="alert-item__content">
                  <p>{alert.msg}</p>
                  <span className="alert-item__time"><Clock size={12} /> {alert.time}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Charts Grid */}
        <div className="dashboard__charts">
          {/* Temperature Chart */}
          <div className="chart-card glass-card-static" id="chart-temperature">
            <h3><TrendingUp size={18} /> Suhu Hari Ini (°C)</h3>
            <div className="chart-card__body">
              <ResponsiveContainer width="100%" height={280}>
                <AreaChart data={hourlyData}>
                  <defs>
                    <linearGradient id="tempGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#00b4cc" stopOpacity={0.3} />
                      <stop offset="100%" stopColor="#00b4cc" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                  <XAxis dataKey="hour" tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} interval={3} />
                  <YAxis tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} domain={['auto', 'auto']} />
                  <Tooltip contentStyle={customTooltipStyle} />
                  <Area type="monotone" dataKey="temp" stroke="#00b4cc" strokeWidth={2} fill="url(#tempGradient)" dot={false} name="Suhu (°C)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Humidity Chart */}
          <div className="chart-card glass-card-static" id="chart-humidity">
            <h3><Droplets size={18} /> Kelembapan Hari Ini (%)</h3>
            <div className="chart-card__body">
              <ResponsiveContainer width="100%" height={280}>
                <LineChart data={hourlyData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                  <XAxis dataKey="hour" tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} interval={3} />
                  <YAxis tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
                  <Tooltip contentStyle={customTooltipStyle} />
                  <Line type="monotone" dataKey="humidity" stroke="#a78bfa" strokeWidth={2} dot={false} name="Kelembapan (%)" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Weekly Forecast */}
          <div className="chart-card glass-card-static" id="chart-weekly">
            <h3><Calendar size={18} /> Prakiraan 7 Hari</h3>
            <div className="chart-card__body">
              <div className="weekly-forecast">
                {weeklyData.map((day, i) => (
                  <div key={i} className="weekly-item">
                    <span className="weekly-item__day">{day.day}</span>
                    <div className="weekly-item__icon">{getConditionIcon(day.condition)}</div>
                    <div className="weekly-item__temps">
                      <span className="weekly-item__high">{day.high}°</span>
                      <div className="weekly-item__bar">
                        <div className="weekly-item__bar-fill" style={{ height: `${((day.high - day.low) / 15) * 100}%` }}></div>
                      </div>
                      <span className="weekly-item__low">{day.low}°</span>
                    </div>
                    <div className="weekly-item__rain">
                      <Droplets size={12} />
                      <span>{day.rain}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Monthly Rainfall */}
          <div className="chart-card glass-card-static" id="chart-rainfall">
            <h3><CloudRain size={18} /> Curah Hujan Bulanan (mm)</h3>
            <div className="chart-card__body">
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={monthlyTrend}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                  <XAxis dataKey="date" tick={{ fill: '#64748b', fontSize: 10 }} axisLine={false} tickLine={false} interval={4} />
                  <YAxis tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
                  <Tooltip contentStyle={customTooltipStyle} />
                  <Bar dataKey="rainfall" fill="rgba(0, 180, 204, 0.6)" radius={[4, 4, 0, 0]} name="Curah Hujan (mm)" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
