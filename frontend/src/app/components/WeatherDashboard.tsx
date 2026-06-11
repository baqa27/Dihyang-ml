import { useState, useEffect } from "react";
import {
  AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend,
} from "recharts";
import {
  Thermometer, Droplets, Wind, Eye, Sun, CloudRain, Cloud, CloudSnow,
  AlertTriangle, CheckCircle, MapPin, ChevronDown, RefreshCw, Bell,
} from "lucide-react";
import { useThemeColors } from "../hooks/useThemeColors";
import { apiService } from "../../services/api.service";
import { APIError } from "../../config/api";

const locations = ["Dieng Plateau", "Sikunir", "Kawah Sikidang", "Telaga Warna", "Gunung Prau", "Wonosobo"];

const forecastData = [
  { day: "Sen", date: "2 Jun", icon: "🌫️", maxTemp: 16, minTemp: 7, rain: 10, condition: "Berkabut", wind: 8, humidity: 90 },
  { day: "Sel", date: "3 Jun", icon: "⛅", maxTemp: 18, minTemp: 8, rain: 25, condition: "Berawan", wind: 11, humidity: 82 },
  { day: "Rab", date: "4 Jun", icon: "🌧️", maxTemp: 14, minTemp: 6, rain: 78, condition: "Hujan Lebat", wind: 18, humidity: 95 },
  { day: "Kam", date: "5 Jun", icon: "🌦️", maxTemp: 15, minTemp: 7, rain: 40, condition: "Hujan Ringan", wind: 13, humidity: 87 },
  { day: "Jum", date: "6 Jun", icon: "⛅", maxTemp: 17, minTemp: 8, rain: 15, condition: "Berawan", wind: 9, humidity: 80 },
  { day: "Sab", date: "7 Jun", icon: "☀️", maxTemp: 19, minTemp: 5, rain: 3, condition: "Cerah", wind: 7, humidity: 72 },
  { day: "Min", date: "8 Jun", icon: "☀️", maxTemp: 20, minTemp: 4, rain: 0, condition: "Cerah - Sunrise Ideal!", wind: 6, humidity: 68 },
];

const tempTrendData = [
  { time: "04:00", suhu: 5, terasa: 3 },
  { time: "06:00", suhu: 7, terasa: 5 },
  { time: "08:00", suhu: 10, terasa: 8 },
  { time: "10:00", suhu: 14, terasa: 12 },
  { time: "12:00", suhu: 17, terasa: 15 },
  { time: "14:00", suhu: 18, terasa: 16 },
  { time: "16:00", suhu: 15, terasa: 13 },
  { time: "18:00", suhu: 11, terasa: 9 },
  { time: "20:00", suhu: 8, terasa: 6 },
  { time: "22:00", suhu: 6, terasa: 4 },
];

const rainfallData = [
  { day: "Sen", curah: 5, peluang: 10 },
  { day: "Sel", curah: 20, peluang: 35 },
  { day: "Rab", curah: 52, peluang: 85 },
  { day: "Kam", curah: 18, peluang: 42 },
  { day: "Jum", curah: 8, peluang: 20 },
  { day: "Sab", curah: 2, peluang: 8 },
  { day: "Min", curah: 0, peluang: 5 },
];

const alerts = [
  {
    level: "danger",
    icon: "🧊",
    title: "Potensi Embun Beku (Embun Upas)",
    desc: "Suhu dini hari diprediksi 2–4°C di Dieng Plateau. Waspadai jalur licin. Gunakan pakaian berlapis & alas kaki anti-selip.",
    time: "5 mnt lalu",
  },
  {
    level: "warning",
    icon: "🌧️",
    title: "Hujan Lebat - Rabu, 4 Jun",
    desc: "Curah hujan tinggi diprediksi di kawasan Kawah Sikidang & Telaga Warna. Tunda aktivitas outdoor jika memungkinkan.",
    time: "20 mnt lalu",
  },
  {
    level: "info",
    icon: "🌄",
    title: "Sunrise Ideal - Minggu, 8 Jun",
    desc: "Langit diprediksi cerah tanpa awan di Bukit Sikunir & Gunung Prau. Waktu terbaik untuk menikmati golden sunrise!",
    time: "1 jam lalu",
  },
];

export default function WeatherDashboard() {
  const [selectedLocation, setSelectedLocation] = useState("Dieng Plateau");
  const [showLocationMenu, setShowLocationMenu] = useState(false);
  const [activeDay, setActiveDay] = useState(0);
  const c = useThemeColors();

  const [currentWeather, setCurrentWeather] = useState<any>(null);
  const [forecastList, setForecastList] = useState<any[]>([]);
  const [hourlyToday, setHourlyToday] = useState<any[]>([]);
  const [mlDashboard, setMlDashboard] = useState<any>(null);
  const [isSyncing, setIsSyncing] = useState(false);

  const fetchWeatherData = async () => {
    setIsSyncing(true);
    try {
      const [currentRes, forecastRes, hourlyRes, mlRes] = await Promise.all([
        apiService.getCurrentWeather().catch(() => null),
        apiService.getForecast().catch(() => null),
        apiService.getHourlyToday().catch(() => null),
        apiService.getDashboardPredictions().catch(() => null),
      ]);

      if (currentRes) setCurrentWeather(currentRes);
      if (forecastRes?.forecast) setForecastList(forecastRes.forecast);
      if (hourlyRes?.hourly) setHourlyToday(hourlyRes.hourly);
      if (mlRes?.success) setMlDashboard(mlRes);
    } catch (err) {
      console.error("Error fetching weather data from API:", err);
      if (err instanceof APIError) {
        console.error(`API Error [${err.statusCode}]: ${err.message}`);
      }
    } finally {
      setIsSyncing(false);
    }
  };

  useEffect(() => {
    fetchWeatherData();
  }, []);

  const displayCurrentTemp = currentWeather ? Math.round(currentWeather.temperature) : 13;
  const displayConditionLabel = currentWeather 
    ? `${currentWeather.condition_label} | ${mlDashboard?.predictions?.risk?.advisory || 'Bawa Jaket!'}` 
    : "Berkabut (Bawa Jaket!)";
  const displayConditionIcon = currentWeather ? (
    currentWeather.condition === "Cerah" ? "☀️" : 
    currentWeather.condition === "Berawan" ? "⛅" : 
    currentWeather.condition === "Berkabut" ? "🌫️" : 
    currentWeather.condition === "Gerimis" ? "🌦️" : 
    currentWeather.condition === "Hujan" ? "🌧️" : "🌫️"
  ) : "🌫️";

  const displayHumidity = currentWeather ? `${currentWeather.humidity}%` : "89%";
  const displayWindSpeed = currentWeather ? `${currentWeather.wind_speed} km/h` : "8 km/h";
  const displayVisibility = currentWeather ? `${currentWeather.visibility} km` : "2 km";
  
  // Custom display mapping for WMO codes / prediction labels
  const displayUvOrRisk = mlDashboard?.predictions?.risk?.label 
    ? `${mlDashboard.predictions.risk.label}`
    : "2 (Rendah)";

  const displayForecastData = forecastList.length > 0 ? forecastList.map((item: any) => ({
    day: item.day,
    date: item.date.substring(8) + " " + ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agt", "Sep", "Okt", "Nov", "Des"][parseInt(item.date.substring(5, 7)) - 1],
    icon: item.condition === "Cerah" ? "☀️" : 
          item.condition === "Berawan" ? "⛅" : 
          item.condition === "Berkabut" ? "🌫️" : 
          item.condition === "Gerimis" ? "🌦️" : 
          item.condition === "Hujan" ? "🌧️" : "🌫️",
    maxTemp: Math.round(item.high),
    minTemp: Math.round(item.low),
    rain: item.rain,
    condition: item.condition_label,
    wind: Math.round(item.wind),
    humidity: 80
  })) : forecastData;

  const displayTempTrendData = hourlyToday.length > 0 ? hourlyToday.filter((_, idx) => idx % 2 === 0).map((item: any) => ({
    time: item.hour,
    suhu: Math.round(item.temp),
    terasa: Math.round(item.temp - 2)
  })) : tempTrendData;

  const displayRainfallData = forecastList.length > 0 ? forecastList.map((item: any) => ({
    day: item.day,
    curah: Math.round(item.precip_mm),
    peluang: item.rain
  })) : rainfallData;

  const dynamicAlerts = [];
  if (currentWeather && currentWeather.temperature <= 6) {
    dynamicAlerts.push({
      level: "danger",
      icon: "🧊",
      title: `Suhu Ekstrem Terdeteksi (${currentWeather.temperature}°C)`,
      desc: `Potensi Embun Beku (Embun Upas) tinggi di Dieng. Permukaan jalan licin dini hari. Harap gunakan pakaian tebal & ekstra hati-hati.`,
      time: "Ditinjau Real-time",
    });
  } else if (mlDashboard?.predictions?.risk?.level > 0) {
    const isDanger = mlDashboard.predictions.risk.level === 2;
    dynamicAlerts.push({
      level: isDanger ? "danger" : "warning",
      icon: isDanger ? "🔴" : "⚠️",
      title: `Peringatan Resiko Cuaca: ${mlDashboard.predictions.risk.label}`,
      desc: mlDashboard.predictions.risk.advisory || `Waspadai perubahan cuaca cepat di kawasan Dieng.`,
      time: "Ditinjau Real-time",
    });
  }

  if (mlDashboard?.predictions?.rain?.will_rain) {
    dynamicAlerts.push({
      level: "warning",
      icon: "🌧️",
      title: "Potensi Hujan Segera",
      desc: mlDashboard.predictions.rain.advisory || "Model DITA mendeteksi probabilitas hujan tinggi dalam waktu dekat.",
      time: "Ditinjau Real-time",
    });
  }

  const displayAlerts = dynamicAlerts.length > 0 ? dynamicAlerts : alerts;

  const alertColors: Record<string, { bg: string; border: string; badge: string; badgeText: string }> = {
    danger: { bg: c.dangerBg, border: c.dangerBorder, badge: c.dangerBadge, badgeText: "BAHAYA" },
    warning: { bg: c.warningBg, border: c.warningBorder, badge: c.warningBadge, badgeText: "PERINGATAN" },
    info: { bg: c.successBg, border: c.successBorder, badge: c.successBadge, badgeText: "INFO BAIK" },
  };

  return (
    <section className="py-20 px-4" style={{ backgroundColor: c.bgAlt }}>
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span
                className="px-3 py-1 rounded-full text-xs font-semibold"
                style={{ backgroundColor: c.bgTint, color: c.successText }}
              >
                🌤️ REAL-TIME
              </span>
              <span className="text-xs" style={{ color: c.textMuted }}>
                Diperbarui 2 menit lalu
              </span>
            </div>
            <h2 className="text-3xl font-bold" style={{ color: c.textPrimary }}>
              Dashboard Prediksi Cuaca
            </h2>
            <p className="mt-1 text-sm" style={{ color: c.textSecondary }}>
              Data cuaca real-time & prakiraan 7 hari berbasis AI
            </p>
          </div>
          <div className="flex items-center gap-3">
            <div className="relative">
              <button
                className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium border shadow-sm"
                style={{ backgroundColor: c.bgSurface, borderColor: c.border, color: c.textPrimary }}
                onClick={() => setShowLocationMenu(!showLocationMenu)}
              >
                <MapPin className="w-4 h-4" style={{ color: c.primary }} />
                {selectedLocation}
                <ChevronDown className="w-4 h-4" />
              </button>
              {showLocationMenu && (
                <div
                  className="absolute right-0 mt-1 w-48 rounded-xl shadow-xl border z-30"
                  style={{ backgroundColor: c.bgSurface, borderColor: c.border }}
                >
                  {locations.map((loc) => (
                    <button
                      key={loc}
                      className="block w-full text-left px-4 py-2.5 text-sm first:rounded-t-xl last:rounded-b-xl transition-colors"
                      style={{ color: loc === selectedLocation ? c.primary : c.textPrimary }}
                      onClick={() => { setSelectedLocation(loc); setShowLocationMenu(false); }}
                    >
                      {loc}
                    </button>
                  ))}
                </div>
              )}
            </div>
            <button
              onClick={fetchWeatherData}
              disabled={isSyncing}
              className={`p-2.5 rounded-xl border shadow-sm transition-all hover:scale-105 disabled:opacity-50`}
              style={{ backgroundColor: c.bgSurface, borderColor: c.border }}
            >
              <RefreshCw className={`w-4 h-4 ${isSyncing ? "animate-spin" : ""}`} style={{ color: c.primary }} />
            </button>
            <button
              className="p-2.5 rounded-xl border shadow-sm transition-colors"
              style={{ backgroundColor: c.bgSurface, borderColor: c.border }}
            >
              <Bell className="w-4 h-4" style={{ color: c.primary }} />
            </button>
          </div>
        </div>

        {/* Alerts */}
        <div className="space-y-3 mb-8">
          {displayAlerts.map((alert, i) => {
            const colors = alertColors[alert.level];
            return (
              <div
                key={i}
                className="flex items-start gap-4 p-4 rounded-2xl border"
                style={{ backgroundColor: colors.bg, borderColor: colors.border }}
              >
                <span className="text-2xl flex-shrink-0 mt-0.5">{alert.icon}</span>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1 flex-wrap">
                    <span
                      className="px-2 py-0.5 rounded-full text-xs font-bold text-white"
                      style={{ backgroundColor: colors.badge }}
                    >
                      {colors.badgeText}
                    </span>
                    <span className="font-semibold text-sm" style={{ color: c.textPrimary }}>
                      {alert.title}
                    </span>
                  </div>
                  <p className="text-sm" style={{ color: c.textSecondary }}>{alert.desc}</p>
                </div>
                <span className="text-xs flex-shrink-0 mt-1" style={{ color: c.textMuted }}>
                  {alert.time}
                </span>
              </div>
            );
          })}
        </div>

        {/* Main Grid */}
        <div className="grid lg:grid-cols-3 gap-6 mb-6">
          {/* Current Weather */}
          <div
            className="rounded-3xl p-6 text-white col-span-1"
            style={{ background: c.gradientWeatherCard }}
          >
            <div className="text-sm font-medium mb-1 opacity-80">Sekarang | {selectedLocation}</div>
            <div className="flex items-center justify-between mb-4">
              <div className="text-6xl font-bold">{displayCurrentTemp}°C</div>
              <span className="text-6xl">{displayConditionIcon}</span>
            </div>
            <div className="text-lg font-medium opacity-90 mb-5">{displayConditionLabel}</div>
            <div className="grid grid-cols-2 gap-3">
              {[
                { icon: Droplets, label: "Kelembaban", value: displayHumidity },
                { icon: Wind, label: "Angin", value: displayWindSpeed },
                { icon: Eye, label: "Jarak Pandang", value: displayVisibility },
                { icon: Sun, label: "Kondisi / Resiko", value: displayUvOrRisk },
              ].map(({ icon: Icon, label, value }) => (
                <div key={label} className="rounded-xl p-3" style={{ backgroundColor: "rgba(255,255,255,0.15)" }}>
                  <div className="flex items-center gap-1.5 mb-1 opacity-75">
                    <Icon className="w-3.5 h-3.5" />
                    <span className="text-xs">{label}</span>
                  </div>
                  <div className="font-semibold text-sm">{value}</div>
                </div>
              ))}
            </div>
          </div>

          {/* 7-Day Forecast */}
          <div
            className="rounded-3xl p-5 col-span-2 shadow-sm border"
            style={{ backgroundColor: c.bgSurface, borderColor: c.border }}
          >
            <h3 className="font-bold text-base mb-4" style={{ color: c.textPrimary }}>
              Prakiraan 7 Hari
            </h3>
            <div className="grid grid-cols-7 gap-2">
              {displayForecastData.map((day, i) => (
                <button
                  key={i}
                  onClick={() => setActiveDay(i)}
                  className="flex flex-col items-center gap-1.5 p-2 rounded-2xl transition-all hover:scale-105"
                  style={{
                    backgroundColor: activeDay === i ? c.navBg : day.rain >= 50 ? c.dangerBg : c.bgTint,
                    border: day.rain >= 50 ? `1.5px solid ${c.dangerBorder}` : "1.5px solid transparent",
                    transform: activeDay === i ? "scale(1.05)" : "scale(1)",
                  }}
                >
                  <div className="text-[10px] font-semibold" style={{ color: activeDay === i ? c.primaryLight : c.textMuted }}>
                    {day.day}
                  </div>
                  <span className="text-xl">{day.icon}</span>
                  <div className="text-xs font-bold" style={{ color: activeDay === i ? "#ffffff" : c.textPrimary }}>
                    {day.maxTemp}°
                  </div>
                  <div className="text-[10px]" style={{ color: activeDay === i ? c.primaryLight : c.textMuted }}>
                    {day.minTemp}°
                  </div>
                  {day.rain >= 50 && (
                    <div
                      className="text-[9px] px-1.5 py-0.5 rounded-full font-medium"
                      style={{ backgroundColor: activeDay === i ? "rgba(239,68,68,0.3)" : c.dangerBg, color: activeDay === i ? "#fca5a5" : c.dangerText }}
                    >
                      {day.rain}%
                    </div>
                  )}
                </button>
              ))}
            </div>
            {/* Detail */}
            <div
              className="mt-4 p-4 rounded-2xl"
              style={{ backgroundColor: c.bgTint }}
            >
              <div className="text-sm font-semibold mb-3" style={{ color: c.textPrimary }}>
                {displayForecastData[activeDay]?.day}, {displayForecastData[activeDay]?.date} - {displayForecastData[activeDay]?.condition}
              </div>
              <div className="grid grid-cols-4 gap-3">
                {[
                  { label: "Maks / Min", value: `${displayForecastData[activeDay]?.maxTemp}° / ${displayForecastData[activeDay]?.minTemp}°` },
                  { label: "Curah Hujan", value: `${displayForecastData[activeDay]?.rain}%` },
                  { label: "Angin", value: `${displayForecastData[activeDay]?.wind} km/h` },
                  { label: "Kelembaban", value: `${displayForecastData[activeDay]?.humidity}%` },
                ].map(({ label, value }) => (
                  <div key={label} className="text-center">
                    <div className="text-xs mb-0.5" style={{ color: c.textSecondary }}>{label}</div>
                    <div className="text-sm font-bold" style={{ color: c.textPrimary }}>{value}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Charts */}
        <div className="grid md:grid-cols-2 gap-6">
          {/* Temperature Trend */}
          <div
            className="rounded-3xl p-6 shadow-sm border"
            style={{ backgroundColor: c.bgSurface, borderColor: c.border }}
          >
            <div className="flex items-center justify-between mb-5">
              <div>
                <h3 className="font-bold text-base" style={{ color: c.textPrimary }}>
                  Tren Suhu Harian
                </h3>
                <p className="text-xs mt-0.5" style={{ color: c.textMuted }}>Hari ini • {selectedLocation}</p>
              </div>
              <Thermometer className="w-5 h-5" style={{ color: c.primary }} />
            </div>
            <ResponsiveContainer width="100%" height={200}>
              <AreaChart data={displayTempTrendData} margin={{ top: 5, right: 5, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="tempGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={c.primary} stopOpacity={0.3} />
                    <stop offset="95%" stopColor={c.primary} stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="feelsGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={c.accent} stopOpacity={0.2} />
                    <stop offset="95%" stopColor={c.accent} stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke={c.borderLight} />
                <XAxis dataKey="time" tick={{ fontSize: 10, fill: c.textMuted }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 10, fill: c.textMuted }} axisLine={false} tickLine={false} domain={[0, 22]} unit="°" />
                <Tooltip
                  contentStyle={{ borderRadius: "12px", border: "none", boxShadow: "0 4px 20px rgba(0,0,0,0.1)", backgroundColor: c.bgSurface, color: c.textPrimary }}
                  formatter={(value: number, name: string) => [`${value}°C`, name]}
                />
                <Legend iconType="circle" iconSize={8} />
                <Area key="suhu" type="monotone" dataKey="suhu" name="Suhu" stroke={c.primary} strokeWidth={2.5} fill="url(#tempGrad)" dot={false} activeDot={{ r: 5 }} />
                <Area key="terasa" type="monotone" dataKey="terasa" name="Terasa Seperti" stroke={c.accent} strokeWidth={2} fill="url(#feelsGrad)" dot={false} strokeDasharray="4 4" activeDot={{ r: 4 }} />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          {/* Rainfall Chart */}
          <div
            className="rounded-3xl p-6 shadow-sm border"
            style={{ backgroundColor: c.bgSurface, borderColor: c.border }}
          >
            <div className="flex items-center justify-between mb-5">
              <div>
                <h3 className="font-bold text-base" style={{ color: c.textPrimary }}>
                  Prakiraan Curah Hujan
                </h3>
                <p className="text-xs mt-0.5" style={{ color: c.textMuted }}>7 hari ke depan • mm & peluang %</p>
              </div>
              <CloudRain className="w-5 h-5" style={{ color: "#0ea5e9" }} />
            </div>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={displayRainfallData} margin={{ top: 5, right: 5, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke={c.borderLight} />
                <XAxis dataKey="day" tick={{ fontSize: 10, fill: c.textMuted }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 10, fill: c.textMuted }} axisLine={false} tickLine={false} />
                <Tooltip
                  contentStyle={{ borderRadius: "12px", border: "none", boxShadow: "0 4px 20px rgba(0,0,0,0.1)", backgroundColor: c.bgSurface, color: c.textPrimary }}
                  formatter={(value: number, name: string) => [
                    name === "Curah Hujan (mm)" ? `${value} mm` : `${value}%`,
                    name,
                  ]}
                />
                <Legend iconType="circle" iconSize={8} />
                <Bar key="curah" dataKey="curah" name="Curah Hujan (mm)" fill="#0ea5e9" radius={[6, 6, 0, 0]} maxBarSize={30} />
                <Bar key="peluang" dataKey="peluang" name="Peluang (%)" fill="#bae6fd" radius={[6, 6, 0, 0]} maxBarSize={30} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </section>
  );
}
