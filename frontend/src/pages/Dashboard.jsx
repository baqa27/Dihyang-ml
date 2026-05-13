import { useState, useEffect, useRef, useCallback } from 'react'
import {
  CloudSun, Thermometer, Droplets, Wind, Eye, ArrowUp, ArrowDown,
  CloudRain, Sun, CloudFog, AlertTriangle, Clock, TrendingUp,
  Calendar, RefreshCw, Zap, Gauge, Activity, Wifi, WifiOff,
} from 'lucide-react'
import {
  AreaChart, Area, LineChart, Line, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts'
import { weatherAPI, mlAPI, realtimeAPI } from '../services/api'
import './Dashboard.css'

// ── Konstanta ─────────────────────────────────────────────────────────────────
const REFRESH_INTERVAL_MS = 5 * 60 * 1000  // 5 menit fallback
const REALTIME_ENABLED = true  // Toggle WebSocket realtime

const WMO_ICON = (code) => {
  if (code === 0)  return <Sun size={18} />
  if (code <= 3)   return <CloudSun size={18} />
  if (code <= 48)  return <CloudFog size={18} />
  if (code <= 65)  return <CloudRain size={18} />
  return <CloudRain size={18} />
}

const TOOLTIP_STYLE = {
  backgroundColor: 'rgba(15, 23, 42, 0.95)',
  border: '1px solid rgba(255,255,255,0.1)',
  borderRadius: '8px',
  padding: '10px 14px',
  color: '#f1f5f9',
  fontSize: '0.82rem',
}

// ── Helpers ───────────────────────────────────────────────────────────────────
function windDirLabel(deg) {
  const dirs = ['U','TL','T','TG','S','BD','B','BL']
  return dirs[Math.round(deg / 45) % 8]
}

function timeAgo(isoStr) {
  const diff = Math.floor((Date.now() - new Date(isoStr)) / 1000)
  if (diff < 60)  return `${diff}d lalu`
  if (diff < 3600) return `${Math.floor(diff/60)}m lalu`
  return `${Math.floor(diff/3600)}j lalu`
}

// Buat alert dinamis dari data ML + cuaca
function buildAlerts(ml, weather) {
  const alerts = []
  if (!ml && !weather) return alerts

  const risk = ml?.risk
  const rain = ml?.rain

  if (risk?.risk_label === 'Bahaya') {
    alerts.push({
      type: 'danger',
      icon: <AlertTriangle size={16} />,
      msg: risk.advisory || 'Kondisi berbahaya terdeteksi. Hindari jalur ekstrem.',
    })
  } else if (risk?.risk_label === 'Waspada') {
    alerts.push({
      type: 'warning',
      icon: <CloudFog size={16} />,
      msg: risk.advisory || 'Harap berhati-hati. Kondisi cuaca berpotensi berubah.',
    })
  }

  if (rain?.will_rain) {
    alerts.push({
      type: 'warning',
      icon: <CloudRain size={16} />,
      msg: `Probabilitas hujan ${rain.rain_probability}% dalam 1 jam ke depan. ${rain.advisory}`,
    })
  }

  if (weather?.visibility < 2) {
    alerts.push({
      type: 'danger',
      icon: <CloudFog size={16} />,
      msg: `Jarak pandang sangat rendah (${weather.visibility} km). Hindari Tanjakan Sikarim dan jalur curam.`,
    })
  } else if (weather?.visibility < 4) {
    alerts.push({
      type: 'warning',
      icon: <Eye size={16} />,
      msg: `Jarak pandang terbatas (${weather.visibility} km). Berkendara dengan hati-hati.`,
    })
  }

  if (weather?.temperature < 8) {
    alerts.push({
      type: 'info',
      icon: <Thermometer size={16} />,
      msg: `Suhu sangat dingin ${weather.temperature}°C. Wajib bawa jaket tebal, syal, dan sarung tangan.`,
    })
  } else if (weather?.temperature < 12) {
    alerts.push({
      type: 'info',
      icon: <Thermometer size={16} />,
      msg: `Suhu dingin ${weather.temperature}°C. Pastikan membawa jaket dan pakaian berlapis.`,
    })
  }

  if (alerts.length === 0) {
    alerts.push({
      type: 'info',
      icon: <Sun size={16} />,
      msg: 'Kondisi cuaca saat ini aman untuk berwisata. Tetap patuhi rambu dan bawa perlengkapan dasar.',
    })
  }

  return alerts
}

// ── Komponen utama ────────────────────────────────────────────────────────────
export default function Dashboard() {
  const [weather,    setWeather]    = useState(null)
  const [mlData,     setMlData]     = useState(null)
  const [hourly,     setHourly]     = useState([])
  const [forecast,   setForecast]   = useState([])
  const [loading,    setLoading]    = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [lastUpdate, setLastUpdate] = useState(null)
  const [online,     setOnline]     = useState(true)
  const timerRef = useRef(null)

  // ── Fetch semua data ──
  const fetchAll = useCallback(async (isManual = false) => {
    if (isManual) setRefreshing(true)

    try {
      const [wxRes, mlRes, hourlyRes, forecastRes] = await Promise.allSettled([
        weatherAPI.getCurrent(),
        mlAPI.getDashboardPredictions(),
        weatherAPI.getHourlyToday(),
        weatherAPI.getForecast(),
      ])

      if (wxRes.status === 'fulfilled')       setWeather(wxRes.value)
      if (hourlyRes.status === 'fulfilled')   setHourly(hourlyRes.value?.hourly || [])
      if (forecastRes.status === 'fulfilled') setForecast(forecastRes.value?.forecast || [])

      if (mlRes.status === 'fulfilled' && mlRes.value?.success) {
        const d = mlRes.value
        setMlData({
          input: {
            current_temperature_c:    d.current.temperature,
            current_precipitation_mm: d.current.precipitation,
            humidity_pct:             d.current.humidity,
            visibility_km:            d.current.visibility_km,
          },
          temperature: {
            predicted_temperature: d.predictions.temperature.predicted,
            change:                d.predictions.temperature.change,
            advisory:              d.predictions.temperature.advisory,
            model:                 d.models.temperature,
          },
          rain: {
            will_rain:        d.predictions.rain.will_rain,
            rain_probability: d.predictions.rain.probability,
            advisory:         d.predictions.rain.advisory,
          },
          risk: {
            risk_label:  d.predictions.risk.label,
            risk_icon:   d.predictions.risk.icon,
            risk_color:  d.predictions.risk.color,
            advisory:    d.predictions.risk.advisory,
            confidence:  d.predictions.risk.confidence,
          },
        })
      }

      setOnline(true)
      setLastUpdate(new Date().toISOString())
    } catch {
      setOnline(false)
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }, [])

  // ── Mount + auto-refresh + WebSocket ──
  useEffect(() => {
    fetchAll()
    
    // Setup WebSocket realtime jika enabled
    let unsubscribe
    if (REALTIME_ENABLED) {
      realtimeAPI.dashboard.connect()
        .then(() => {
          console.log('[Dashboard] WebSocket realtime connected')
          unsubscribe = realtimeAPI.dashboard.subscribe((data) => {
            if (data.type === 'dashboard_update' || data.type === 'dashboard_initial') {
              console.log('[Dashboard] Realtime update received:', data.timestamp)
              
              // Update weather dari realtime data
              if (data.data?.current) {
                setWeather(prev => ({
                  ...prev,
                  temperature: data.data.current.temperature,
                  precipitation: data.data.current.precipitation,
                  humidity: data.data.current.humidity,
                  visibility: data.data.current.visibility_km,
                  wind_speed: data.data.current.windspeed,
                }))
              }
              
              // Update ML predictions dari realtime data
              if (data.data?.predictions) {
                setMlData(prev => ({
                  ...prev,
                  temperature: data.data.predictions.temperature,
                  rain: data.data.predictions.rain,
                  risk: data.data.predictions.risk,
                }))
              }
              
              setLastUpdate(data.timestamp)
              setOnline(true)
            }
          })
        })
        .catch(err => {
          console.error('[Dashboard] WebSocket connection failed:', err)
          setOnline(false)
        })
    }
    
    // Fallback polling untuk data lengkap
    timerRef.current = setInterval(() => fetchAll(), REFRESH_INTERVAL_MS)
    
    return () => {
      clearInterval(timerRef.current)
      if (unsubscribe) unsubscribe()
      if (REALTIME_ENABLED) realtimeAPI.dashboard.disconnect()
    }
  }, [fetchAll])

  // ── Derived ──
  const alerts  = buildAlerts(mlData, weather)
  const riskColor = mlData?.risk?.risk_color || '#22c55e'

  // Highlight jam sekarang di chart hourly
  const currentHour = new Date().getHours()
  const hourlyWithCurrent = hourly.map((h, i) => ({
    ...h,
    isCurrent: i === currentHour,
  }))

  // ── Loading skeleton ──
  if (loading) {
    return (
      <div className="dashboard page-enter">
        <div className="container">
          <div className="dashboard__loading">
            <div className="dashboard__loading-spinner" />
            <p>Memuat data cuaca real-time Dieng...</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="dashboard page-enter">
      <div className="container">

        {/* ── Header ── */}
        <div className="dashboard__header">
          <div>
            <h1>Dashboard <span className="text-gradient">Cuaca</span></h1>
            <p>
              Monitor kondisi cuaca mikroklimat Dieng secara real-time
              {lastUpdate && (
                <span className="dashboard__last-update">
                  {online
                    ? <><Wifi size={12} /> {REALTIME_ENABLED ? 'Realtime WebSocket' : `Diperbarui ${timeAgo(lastUpdate)}`}</>
                    : <><WifiOff size={12} /> Offline — data terakhir {timeAgo(lastUpdate)}</>
                  }
                </span>
              )}
            </p>
          </div>
          <button
            className="btn btn-outline btn-sm"
            onClick={() => fetchAll(true)}
            disabled={refreshing}
            id="refresh-weather"
          >
            <RefreshCw size={16} className={refreshing ? 'spin-anim' : ''} />
            {refreshing ? 'Memperbarui...' : 'Refresh'}
          </button>
        </div>

        {/* ── Overview Cards ── */}
        <div className="dashboard__overview">
          {/* Main temp card */}
          <div className="overview-card overview-card--main glass-card-static">
            <div className="overview-card__top">
              <CloudSun size={24} />
              <span>Sekarang · Dieng {weather?.elevation ? `${weather.elevation}m` : '2.060m'}</span>
            </div>
            <div className="overview-card__temp">
              <span className="overview-card__temp-val">
                {weather?.temperature ?? '—'}°
              </span>
              <div className="overview-card__temp-meta">
                <span className="overview-card__condition">
                  {weather?.condition_label || weather?.condition || 'Memuat...'}
                </span>
                <span className="overview-card__feels">
                  Terasa {weather?.feels_like ?? '—'}°C
                </span>
                {weather?.precipitation > 0 && (
                  <span className="overview-card__precip">
                    <CloudRain size={12} /> {weather.precipitation} mm
                  </span>
                )}
              </div>
            </div>
            <div className="overview-card__range">
              <span><ArrowUp size={14} /> {weather?.high ?? '—'}°</span>
              <span><ArrowDown size={14} /> {weather?.low ?? '—'}°</span>
            </div>
          </div>

          {/* Metric cards */}
          {[
            {
              icon: <Droplets size={22} />,
              label: 'Kelembapan',
              value: weather ? `${weather.humidity}%` : '—',
              sub: weather?.dewpoint != null ? `Titik embun ${weather.dewpoint}°C` : null,
              color: '#00b4cc',
            },
            {
              icon: <Wind size={22} />,
              label: 'Angin',
              value: weather ? `${weather.wind_speed} km/h` : '—',
              sub: weather?.wind_direction != null
                ? windDirLabel(weather.wind_direction)
                : null,
              color: '#a78bfa',
            },
            {
              icon: <Eye size={22} />,
              label: 'Jarak Pandang',
              value: weather ? `${weather.visibility} km` : '—',
              sub: weather?.visibility < 2 ? '⚠️ Sangat Rendah'
                 : weather?.visibility < 5 ? '⚠️ Terbatas' : null,
              color: '#f59e0b',
            },
            {
              icon: <Gauge size={22} />,
              label: 'Tekanan Udara',
              value: weather ? `${weather.pressure} hPa` : '—',
              sub: weather?.cloudcover != null ? `Awan ${weather.cloudcover}%` : null,
              color: '#22c55e',
            },
          ].map((card, i) => (
            <div key={i} className="overview-card glass-card-static">
              <div className="overview-card__top" style={{ color: card.color }}>
                {card.icon}
              </div>
              <span className="overview-card__label">{card.label}</span>
              <span className="overview-card__value">{card.value}</span>
              {card.sub && (
                <span className="overview-card__sub">{card.sub}</span>
              )}
            </div>
          ))}
        </div>

        {/* ── ML Prediction Card ── */}
        {mlData && (
          <div
            className="dashboard__ml-card glass-card-static"
            style={{ borderLeft: `4px solid ${riskColor}` }}
          >
            <div className="dashboard__ml-card__header">
              <div className="dashboard__ml-card__title">
                <Zap size={16} style={{ color: '#00b4cc' }} />
                <span>Prediksi AI — Machine Learning DITA</span>
              </div>
              <div className="dashboard__ml-card__badges">
                {mlData.temperature && (
                  <div className="ml-badge">
                    <span className="ml-badge__label">Suhu +1 jam</span>
                    <span className="ml-badge__value" style={{ color: '#00b4cc' }}>
                      {mlData.temperature.predicted_temperature}°C
                      <small style={{ color: mlData.temperature.change >= 0 ? '#f59e0b' : '#60a5fa' }}>
                        {' '}({mlData.temperature.change >= 0 ? '+' : ''}{mlData.temperature.change}°)
                      </small>
                    </span>
                  </div>
                )}
                {mlData.rain && (
                  <div className="ml-badge">
                    <span className="ml-badge__label">Prob. Hujan</span>
                    <span className="ml-badge__value" style={{ color: '#a78bfa' }}>
                      {mlData.rain.rain_probability}%
                    </span>
                  </div>
                )}
                {mlData.risk && (
                  <div className="ml-badge">
                    <span className="ml-badge__label">Status Risiko</span>
                    <span className="ml-badge__value" style={{ color: riskColor }}>
                      {mlData.risk.risk_icon} {mlData.risk.risk_label}
                    </span>
                  </div>
                )}
              </div>
            </div>

            <p className="dashboard__ml-card__advisory">
              {mlData.risk?.advisory}
            </p>

            {/* Confidence bar */}
            {mlData.risk?.confidence && (
              <div className="dashboard__ml-card__confidence">
                {[
                  { key: 'aman',    label: 'Aman',    color: '#22c55e' },
                  { key: 'waspada', label: 'Waspada', color: '#f59e0b' },
                  { key: 'bahaya',  label: 'Bahaya',  color: '#ef4444' },
                ].map(({ key, label, color }) => (
                  <div key={key} className="conf-bar">
                    <span className="conf-bar__label">{label}</span>
                    <div className="conf-bar__track">
                      <div
                        className="conf-bar__fill"
                        style={{
                          width: `${mlData.risk.confidence[key]}%`,
                          background: color,
                        }}
                      />
                    </div>
                    <span className="conf-bar__pct">{mlData.risk.confidence[key]}%</span>
                  </div>
                ))}
              </div>
            )}

            <p className="dashboard__ml-disclaimer">
              Prototipe penelitian PJK-GM067 — bukan prakiraan resmi BMKG.
              Model: Random Forest + Gradient Boosting, data Open-Meteo + historis 2022-2024.
              Selalu cek kondisi lapangan sebelum berangkat.
            </p>
          </div>
        )}

        {/* ── Alerts Dinamis ── */}
        <div className="dashboard__alerts">
          <h3>
            <AlertTriangle size={18} />
            Peringatan Proaktif
            <span className="dashboard__alerts-live">
              <Activity size={12} /> Live
            </span>
          </h3>
          <div className="alerts-list">
            {alerts.map((alert, i) => (
              <div key={i} className={`alert-item alert-item--${alert.type}`}>
                <div className="alert-item__icon">{alert.icon}</div>
                <div className="alert-item__content">
                  <p>{alert.msg}</p>
                  {lastUpdate && (
                    <span className="alert-item__time">
                      <Clock size={12} /> {timeAgo(lastUpdate)}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* ── Charts ── */}
        <div className="dashboard__charts">

          {/* Suhu per jam hari ini */}
          <div className="chart-card glass-card-static" id="chart-temperature">
            <h3>
              <TrendingUp size={18} />
              Suhu Hari Ini (°C)
              {hourly.length > 0 && <span className="chart-badge">Real-time</span>}
            </h3>
            <div className="chart-card__body">
              {hourly.length > 0 ? (
                <ResponsiveContainer width="100%" height={280}>
                  <AreaChart data={hourlyWithCurrent}>
                    <defs>
                      <linearGradient id="tempGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%"   stopColor="#00b4cc" stopOpacity={0.35} />
                        <stop offset="100%" stopColor="#00b4cc" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                    <XAxis
                      dataKey="hour"
                      tick={{ fill: '#64748b', fontSize: 11 }}
                      axisLine={false} tickLine={false}
                      interval={3}
                    />
                    <YAxis
                      tick={{ fill: '#64748b', fontSize: 11 }}
                      axisLine={false} tickLine={false}
                      domain={['auto', 'auto']}
                    />
                    <Tooltip
                      contentStyle={TOOLTIP_STYLE}
                      formatter={(v) => [`${v}°C`, 'Suhu']}
                    />
                    <Area
                      type="monotone" dataKey="temp"
                      stroke="#00b4cc" strokeWidth={2}
                      fill="url(#tempGrad)" dot={false}
                      name="Suhu (°C)"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              ) : (
                <div className="chart-empty">Memuat data...</div>
              )}
            </div>
          </div>

          {/* Kelembapan per jam */}
          <div className="chart-card glass-card-static" id="chart-humidity">
            <h3>
              <Droplets size={18} />
              Kelembapan Hari Ini (%)
              {hourly.length > 0 && <span className="chart-badge">Real-time</span>}
            </h3>
            <div className="chart-card__body">
              {hourly.length > 0 ? (
                <ResponsiveContainer width="100%" height={280}>
                  <LineChart data={hourlyWithCurrent}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                    <XAxis
                      dataKey="hour"
                      tick={{ fill: '#64748b', fontSize: 11 }}
                      axisLine={false} tickLine={false}
                      interval={3}
                    />
                    <YAxis
                      tick={{ fill: '#64748b', fontSize: 11 }}
                      axisLine={false} tickLine={false}
                      domain={[50, 100]}
                    />
                    <Tooltip
                      contentStyle={TOOLTIP_STYLE}
                      formatter={(v) => [`${v}%`, 'Kelembapan']}
                    />
                    <Line
                      type="monotone" dataKey="humidity"
                      stroke="#a78bfa" strokeWidth={2}
                      dot={false} name="Kelembapan (%)"
                    />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="chart-empty">Memuat data...</div>
              )}
            </div>
          </div>

          {/* Prakiraan 7 hari */}
          <div className="chart-card glass-card-static" id="chart-weekly">
            <h3>
              <Calendar size={18} />
              Prakiraan 7 Hari
              {forecast.length > 0 && <span className="chart-badge">Open-Meteo</span>}
            </h3>
            <div className="chart-card__body">
              {forecast.length > 0 ? (
                <div className="weekly-forecast">
                  {forecast.map((day, i) => (
                    <div key={i} className={`weekly-item ${i === 0 ? 'weekly-item--today' : ''}`}>
                      <span className="weekly-item__day">
                        {i === 0 ? 'Hari ini' : day.day}
                      </span>
                      <div className="weekly-item__icon">
                        {WMO_ICON(day.weather_code)}
                      </div>
                      <div className="weekly-item__temps">
                        <span className="weekly-item__high">{day.high}°</span>
                        <div className="weekly-item__bar">
                          <div
                            className="weekly-item__bar-fill"
                            style={{ height: `${Math.min(((day.high - day.low) / 15) * 100, 100)}%` }}
                          />
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
              ) : (
                <div className="chart-empty">Memuat prakiraan...</div>
              )}
            </div>
          </div>

          {/* Curah hujan per jam */}
          <div className="chart-card glass-card-static" id="chart-rainfall">
            <h3>
              <CloudRain size={18} />
              Curah Hujan Hari Ini (mm)
              {hourly.length > 0 && <span className="chart-badge">Real-time</span>}
            </h3>
            <div className="chart-card__body">
              {hourly.length > 0 ? (
                <ResponsiveContainer width="100%" height={280}>
                  <BarChart data={hourlyWithCurrent}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                    <XAxis
                      dataKey="hour"
                      tick={{ fill: '#64748b', fontSize: 10 }}
                      axisLine={false} tickLine={false}
                      interval={3}
                    />
                    <YAxis
                      tick={{ fill: '#64748b', fontSize: 11 }}
                      axisLine={false} tickLine={false}
                    />
                    <Tooltip
                      contentStyle={TOOLTIP_STYLE}
                      formatter={(v) => [`${v} mm`, 'Curah Hujan']}
                    />
                    <Bar
                      dataKey="precip"
                      fill="rgba(0, 180, 204, 0.6)"
                      radius={[4, 4, 0, 0]}
                      name="Curah Hujan (mm)"
                    />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="chart-empty">Memuat data...</div>
              )}
            </div>
          </div>

        </div>

        {/* ── Auto-refresh indicator ── */}
        <div className="dashboard__footer">
          <span>
            <Activity size={12} />
            {REALTIME_ENABLED 
              ? 'Realtime WebSocket aktif · Auto-update setiap 5 menit (fallback)'
              : 'Auto-refresh setiap 5 menit'
            }
            {lastUpdate && ` · Terakhir: ${new Date(lastUpdate).toLocaleTimeString('id-ID')}`}
          </span>
        </div>

      </div>
    </div>
  )
}
