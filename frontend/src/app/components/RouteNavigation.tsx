import { useState, useEffect } from "react";
import {
  Navigation, AlertTriangle, CheckCircle, Clock, MapPin, ChevronRight,
  Shield, Car, CloudFog, Thermometer, AlertCircle,
  TriangleAlert, Zap, Route, Info, Phone, Star,
} from "lucide-react";
import { motion, AnimatePresence } from "motion/react";
import { useThemeColors } from "../hooks/useThemeColors";
import RouteMap from "./RouteMap";

type RouteStatus = "aman" | "waspada" | "bahaya";

type Waypoint = {
  km: number;
  name: string;
  note?: string;
  incident?: { level: RouteStatus; desc: string };
};

type RouteData = {
  id: string;
  from: string;
  to: string;
  distance: string;
  normalTime: string;
  currentTime: string;
  status: RouteStatus;
  road: string;
  rating: number;
  conditions: string[];
  waypoints: Waypoint[];
  tip: string;
};

const routes: RouteData[] = [
  {
    id: "wonosobo",
    from: "Wonosobo",
    to: "Dieng",
    distance: "26 km",
    normalTime: "45 mnt",
    currentTime: "~70 mnt",
    status: "waspada",
    road: "Jalan Provinsi (via Kejajar)",
    rating: 4.2,
    conditions: ["Kabut tebal pagi–siang", "Tikungan tajam km 8–14", "Jalur paling umum", "Aspal cukup baik"],
    waypoints: [
      { km: 0, name: "Terminal Wonosobo" },
      { km: 5, name: "Pertigaan Kejajar", note: "Ambil kiri menuju Dieng" },
      { km: 8, name: "Km 8: Tikungan Tajam", incident: { level: "waspada", desc: "Jalan menyempit, tikungan 180°. Kurangi kecepatan maks 20 km/j." } },
      { km: 12, name: "Desa Sembungan (Desa Tertinggi Jawa)", note: "Ketinggian 2.306 mdpl, suhu mulai sangat dingin" },
      { km: 14, name: "Persimpangan Bukit Sikunir", note: "Belok kiri untuk Sikunir" },
      { km: 20, name: "Km 20: Kabut Tebal", incident: { level: "waspada", desc: "Visibilitas < 50 m. Nyalakan lampu hazard, ikuti batas marka jalan." } },
      { km: 26, name: "Pusat Dieng Plateau ✅" },
    ],
    tip: "Berangkat sebelum pukul 07.00 atau setelah 11.00 untuk menghindari puncak kabut pagi.",
  },
  {
    id: "banjarnegara",
    from: "Banjarnegara",
    to: "Dieng",
    distance: "44 km",
    normalTime: "1 jam 20 mnt",
    currentTime: "~1 jam 20 mnt",
    status: "aman",
    road: "Jalan Nasional (via Batur)",
    rating: 4.8,
    conditions: ["Jalan lebih lebar & lurus", "Pemandangan perkebunan kentang", "Kondisi normal", "Minim tikungan ekstrem"],
    waypoints: [
      { km: 0, name: "Kota Banjarnegara" },
      { km: 15, name: "Kecamatan Batur", note: "Kawasan sentra kentang Dieng" },
      { km: 25, name: "Desa Pejawaran", note: "Bahan bakar tersedia di sini" },
      { km: 35, name: "Pertigaan Dieng", note: "Lurus menuju pusat Dieng" },
      { km: 44, name: "Pusat Dieng Plateau ✅" },
    ],
    tip: "Rute paling nyaman dan aman. Direkomendasikan untuk kendaraan besar atau pertama kali ke Dieng.",
  },
  {
    id: "temanggung",
    from: "Temanggung / Parakan",
    to: "Dieng",
    distance: "58 km",
    normalTime: "1 jam 45 mnt",
    currentTime: "DITUTUP",
    status: "bahaya",
    road: "Jalan Kabupaten (via Kaloran)",
    rating: 2.1,
    conditions: ["⚠️ LONGSOR di km 18", "Jalan rusak parah km 15–22", "Ditutup sementara sejak 28 Mei", "Estimasi buka kembali: belum diketahui"],
    waypoints: [
      { km: 0, name: "Parakan, Temanggung" },
      { km: 10, name: "Kecamatan Kaloran" },
      { km: 15, name: "Km 15: Jalan Rusak Parah", incident: { level: "waspada", desc: "Aspal amblas, banyak lubang besar. Kecepatan maks 15 km/j." } },
      { km: 18, name: "Km 18: LONGSOR 🔴", incident: { level: "bahaya", desc: "Material longsor menutup 100% badan jalan. TIDAK BISA DILALUI. Putar balik!" } },
      { km: 58, name: "Dieng (tidak dapat dicapai via rute ini)" },
    ],
    tip: "HINDARI rute ini. Gunakan jalur Wonosobo atau Banjarnegara sebagai alternatif.",
  },
];

const incidents = [
  { id: 1, time: "05:32", level: "bahaya" as RouteStatus, icon: TriangleAlert, title: "Longsor km 18 Jalur Temanggung", desc: "Material longsor menutup total badan jalan. Jalur tidak bisa dilalui. Gunakan alternatif Wonosobo.", route: "Temanggung → Dieng" },
  { id: 2, time: "06:15", level: "waspada" as RouteStatus, icon: CloudFog, title: "Kabut Tebal Jalur Wonosobo km 20–26", desc: "Visibilitas di bawah 50 meter. Nyalakan lampu utama dan hazard. Kurangi kecepatan.", route: "Wonosobo → Dieng" },
  { id: 3, time: "04:50", level: "waspada" as RouteStatus, icon: Thermometer, title: "Embun Beku (Jalanan Licin Dini Hari)", desc: "Suhu 2°C menyebabkan embun beku di permukaan jalan pukul 01.00–06.00. Waspadai jalan licin.", route: "Semua Jalur Dieng" },
  { id: 4, time: "Kemarin", level: "waspada" as RouteStatus, icon: AlertCircle, title: "Tikungan km 8 Jalur Wonosobo (Penyempitan)", desc: "Pengerjaan talud jalan menyempitkan lajur. Bergantian dengan kendaraan dari arah berlawanan.", route: "Wonosobo → Dieng" },
  { id: 5, time: "2 hari lalu", level: "aman" as RouteStatus, icon: CheckCircle, title: "Jalur Banjarnegara (Kondisi Normal)", desc: "Tidak ada hambatan. Jalan dalam kondisi baik. Rute paling direkomendasikan saat ini.", route: "Banjarnegara → Dieng" },
];

const safetyChecklist = [
  { icon: "🌡️", text: "Cek suhu malam - di bawah 5°C wajib jaket berlapis" },
  { icon: "🌫️", text: "Pantau prakiraan kabut sebelum berangkat" },
  { icon: "⛽", text: "Isi bensin penuh di Wonosobo - SPBU terbatas di Dieng" },
  { icon: "💡", text: "Pastikan lampu kendaraan berfungsi baik" },
  { icon: "🛞", text: "Cek kondisi ban - jalur berliku & basah" },
  { icon: "📱", text: "Simpan nomor darurat lokal sebelum sinyal hilang" },
  { icon: "🧭", text: "Unduh peta offline - sinyal sering lemah di jalur" },
  { icon: "🚑", text: "Puskesmas Kejajar: +62 286 3397xxx" },
];

const statusConfig = {
  aman: { bg: "#d1fae5", border: "#6ee7b7", text: "#065f46", badge: "#059669", label: "AMAN", icon: CheckCircle, dot: "#10b981" },
  waspada: { bg: "#fffbeb", border: "#fcd34d", text: "#92400e", badge: "#f59e0b", label: "WASPADA", icon: AlertTriangle, dot: "#f59e0b" },
  bahaya: { bg: "#fef2f2", border: "#fca5a5", text: "#7f1d1d", badge: "#ef4444", label: "BAHAYA", icon: AlertCircle, dot: "#ef4444" },
};

const VEHICLES = ["Mobil", "Motor", "Bus/Travel"] as const;
const FILTERS = ["Semua", "Aman", "Waspada", "Bahaya"] as const;

// Route characteristics for ML prediction
const ROUTE_ML_PROFILES: Record<string, { gradient: number; width: number; curve_count: number; guardrail: number; surface: string; elevation: number; lighting: number; visibility: number }> = {
  wonosobo:     { gradient: 18, width: 4.5, curve_count: 12, guardrail: 0, surface: "aspal", elevation: 2100, lighting: 0, visibility: 3 },
  banjarnegara: { gradient: 10, width: 6.0, curve_count: 5,  guardrail: 1, surface: "aspal", elevation: 2060, lighting: 1, visibility: 6 },
  temanggung:   { gradient: 28, width: 3.5, curve_count: 15, guardrail: 0, surface: "rusak", elevation: 2200, lighting: 0, visibility: 2 },
};

function StarRating({ rating }: { rating: number }) {
  return (
    <div className="flex items-center gap-0.5">
      {[1, 2, 3, 4, 5].map((s) => (
        <Star
          key={s}
          className="w-3 h-3"
          style={{
            color: s <= Math.round(rating) ? "#f59e0b" : "#d1d5db",
            fill: s <= Math.round(rating) ? "#f59e0b" : "none",
          }}
        />
      ))}
      <span className="text-[11px] ml-1" style={{ color: "#6b7280" }}>{rating}</span>
    </div>
  );
}

export default function RouteNavigation() {
  const [expandedRoute, setExpandedRoute] = useState<string | null>("wonosobo");
  const [activeTab, setActiveTab] = useState<"rute" | "insiden" | "keselamatan">("rute");
  const [filter, setFilter] = useState<typeof FILTERS[number]>("Semua");
  const [vehicle, setVehicle] = useState<typeof VEHICLES[number]>("Mobil");
  const [showClosed, setShowClosed] = useState(true);
  const colors = useThemeColors();

  const [mapHeight, setMapHeight] = useState(680);
  useEffect(() => {
    const handleResize = () => {
      setMapHeight(window.innerWidth >= 1024 ? 680 : 450);
    };
    handleResize();
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  // ML route safety predictions keyed by route id
  const [mlSafety, setMlSafety] = useState<Record<string, any>>({});

  // Map frontend vehicle label to backend vehicle code
  const vehicleMap: Record<string, string> = { "Mobil": "car", "Motor": "motorcycle", "Bus/Travel": "bus" };

  useEffect(() => {
    const fetchRouteSafety = async () => {
      const vehicleCode = vehicleMap[vehicle] || "car";
      const results: Record<string, any> = {};

      await Promise.all(
        Object.entries(ROUTE_ML_PROFILES).map(async ([routeId, profile]) => {
          try {
            const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";
            const res = await fetch(`${apiUrl}/api/ml/predict/route-safety`, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                gradient: profile.gradient,
                width: profile.width,
                visibility: profile.visibility,
                guardrail: profile.guardrail,
                surface: profile.surface,
                elevation: profile.elevation,
                curve_count: profile.curve_count,
                lighting: profile.lighting,
                vehicle: vehicleCode,
                weather: "kabut",
              }),
            });
            if (res.ok) {
              results[routeId] = await res.json();
            }
          } catch (err) {
            console.error(`Error fetching route safety for ${routeId}:`, err);
          }
        })
      );

      setMlSafety(results);
    };

    fetchRouteSafety();
  }, [vehicle]);

  const filteredRoutes = routes.filter((r) => {
    if (!showClosed && r.status === "bahaya") return false;
    if (filter === "Semua") return true;
    return r.status === filter.toLowerCase();
  });

  return (
    <section id="rute" className="py-20 px-4" style={{ backgroundColor: colors.bgAlt }}>
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 mb-10">
          <div>
            <div
              className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-sm font-medium mb-3"
              style={{ backgroundColor: colors.bgTint, color: colors.successText }}
            >
              <Navigation className="w-3.5 h-3.5" />
              Real-Time Road Intelligence
            </div>
            <h2 className="text-3xl font-bold" style={{ color: colors.textPrimary }}>
              Navigasi Rute & Peringatan Keselamatan
            </h2>
            <p className="mt-1.5 text-sm max-w-lg" style={{ color: colors.textSecondary }}>
              Status jalur menuju Dieng secara real-time, termasuk insiden longsor, kabut, dan
              kondisi jalan terkini. Selalu cek sebelum berangkat!
            </p>
          </div>

          {/* Summary badges */}
          <div className="flex gap-2 flex-wrap">
            {(["aman", "waspada", "bahaya"] as RouteStatus[]).map((s) => {
              const sc = statusConfig[s];
              const count = routes.filter((r) => r.status === s).length;
              return (
                <div
                  key={s}
                  className="flex items-center gap-2 px-3 py-2 rounded-xl border"
                  style={{ backgroundColor: sc.bg, borderColor: sc.border }}
                >
                  <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: sc.dot }} />
                  <span className="text-xs font-bold" style={{ color: sc.text }}>
                    {count} Jalur {sc.label}
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Tabs */}
        <div
          className="flex gap-1 p-1 rounded-2xl mb-8 w-fit"
          style={{ backgroundColor: colors.border }}
        >
          {([
            { id: "rute", label: "🗺️ Status Rute" },
            { id: "insiden", label: "⚠️ Laporan Insiden" },
            { id: "keselamatan", label: "🛡️ Tips Keselamatan" },
          ] as const).map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className="px-5 py-2.5 rounded-xl text-sm font-semibold transition-all"
              style={{
                backgroundColor: activeTab === tab.id ? colors.navBg : "transparent",
                color: activeTab === tab.id ? "#ffffff" : colors.textSecondary,
                boxShadow: activeTab === tab.id ? "0 2px 8px rgba(0,0,0,0.2)" : "none",
              }}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* ─── TAB: Status Rute ─── */}
        {activeTab === "rute" && (
          <div
            className="flex flex-col lg:flex-row rounded-3xl overflow-hidden border shadow-lg h-[900px] lg:h-[680px]"
            style={{ borderColor: colors.border }}
          >
            {/* ── Left Sidebar ── */}
            <div
              className="flex flex-col overflow-hidden w-full lg:w-[360px] h-[450px] lg:h-full flex-shrink-0 border-b lg:border-b-0 lg:border-r"
              style={{
                backgroundColor: colors.bgSurface,
                borderColor: colors.border,
              }}
            >
              {/* Sidebar header: title + filter */}
              <div
                className="px-4 pt-4 pb-3 border-b flex-shrink-0"
                style={{ borderColor: colors.borderLight }}
              >
                <div
                  className="text-[10px] font-bold uppercase tracking-widest mb-3"
                  style={{ color: colors.textMuted }}
                >
                  Jalur Destinasi
                </div>
                <div className="flex gap-1.5 flex-wrap">
                  {FILTERS.map((f) => (
                    <button
                      key={f}
                      onClick={() => setFilter(f)}
                      className="px-3 py-1 rounded-full text-xs font-semibold transition-all"
                      style={{
                        backgroundColor: filter === f ? colors.primary : colors.bgTint,
                        color: filter === f ? "#fff" : colors.textSecondary,
                      }}
                    >
                      {f}
                    </button>
                  ))}
                </div>
              </div>

              {/* Vehicle selector */}
              <div
                className="px-4 py-3 border-b flex-shrink-0"
                style={{ borderColor: colors.borderLight }}
              >
                <div
                  className="text-[10px] font-bold uppercase tracking-widest mb-2"
                  style={{ color: colors.textMuted }}
                >
                  Kendaraan Anda
                </div>
                <div className="flex gap-2 mb-2">
                  {VEHICLES.map((v) => (
                    <button
                      key={v}
                      onClick={() => setVehicle(v)}
                      className="flex-1 py-1.5 rounded-xl text-xs font-semibold border transition-all"
                      style={{
                        backgroundColor: vehicle === v ? colors.primary : colors.bgInput,
                        color: vehicle === v ? "#fff" : colors.textSecondary,
                        borderColor: vehicle === v ? colors.primary : colors.border,
                      }}
                    >
                      {v}
                    </button>
                  ))}
                </div>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={showClosed}
                    onChange={(e) => setShowClosed(e.target.checked)}
                    className="w-3.5 h-3.5 rounded"
                    style={{ accentColor: colors.primary }}
                  />
                  <span className="text-xs" style={{ color: colors.textSecondary }}>
                    Tampilkan jalur ditutup
                  </span>
                </label>
              </div>

              {/* Route list - scrollable */}
              <div className="flex-1 overflow-y-auto">
                <div
                  className="px-4 pt-3 pb-1 text-[10px] font-bold uppercase tracking-widest"
                  style={{ color: colors.textMuted }}
                >
                  Go Rute
                </div>

                <div className="px-3 pb-3 space-y-2">
                  {filteredRoutes.map((route) => {
                    const cfg = statusConfig[route.status];
                    const StatusIcon = cfg.icon;
                    const isActive = expandedRoute === route.id;

                    return (
                      <div
                        key={route.id}
                        className="rounded-2xl border cursor-pointer transition-all overflow-hidden"
                        style={{
                          backgroundColor: isActive ? cfg.bg : colors.bgSurface,
                          borderColor: isActive ? cfg.border : colors.border,
                        }}
                        onClick={() => setExpandedRoute(isActive ? null : route.id)}
                      >
                        {/* Card top */}
                        <div className="p-3">
                          <div className="flex items-start gap-3">
                            <div
                              className="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0"
                              style={{ backgroundColor: cfg.badge }}
                            >
                              <StatusIcon className="w-4 h-4 text-white" />
                            </div>
                            <div className="flex-1 min-w-0">
                              <div
                                className="font-bold text-sm leading-tight mb-0.5"
                                style={{ color: colors.textPrimary }}
                              >
                                {route.from} → {route.to}
                              </div>
                              <div className="text-[10px] mb-1.5 truncate" style={{ color: colors.textMuted }}>
                                {route.road}
                              </div>
                              <div className="flex items-center gap-2 flex-wrap mb-1.5">
                                <span
                                  className="px-2 py-0.5 rounded-full text-[10px] font-bold text-white"
                                  style={{ backgroundColor: cfg.badge }}
                                >
                                  {cfg.label}
                                </span>
                                <span
                                  className="flex items-center gap-1 text-[10px]"
                                  style={{ color: colors.textMuted }}
                                >
                                  <Route className="w-3 h-3" /> {route.distance}
                                </span>
                                <span
                                  className="flex items-center gap-1 text-[10px] font-semibold"
                                  style={{ color: route.status === "bahaya" ? "#dc2626" : colors.textSecondary }}
                                >
                                  <Clock className="w-3 h-3" /> {route.currentTime}
                                </span>
                              </div>
                              <StarRating rating={route.rating} />
                              {mlSafety[route.id] && (
                                <div
                                  className="mt-1.5 flex items-center gap-1.5 text-[10px] font-semibold px-2 py-1 rounded-lg"
                                  style={{
                                    backgroundColor: mlSafety[route.id].safety_class === 0 ? "#d1fae5" : mlSafety[route.id].safety_class === 1 ? "#fef3c7" : "#fee2e2",
                                    color: mlSafety[route.id].safety_class === 0 ? "#065f46" : mlSafety[route.id].safety_class === 1 ? "#92400e" : "#991b1b",
                                  }}
                                >
                                  <Shield className="w-3 h-3" />
                                  🤖 ML: {mlSafety[route.id].safety_icon} {mlSafety[route.id].safety_label} untuk {vehicle}
                                  <span className="opacity-60">
                                    ({mlSafety[route.id].confidence?.aman}% aman)
                                  </span>
                                </div>
                              )}
                            </div>
                          </div>
                        </div>

                        {/* Expanded: waypoints */}
                        <AnimatePresence>
                          {isActive && (
                            <motion.div
                              initial={{ height: 0, opacity: 0 }}
                              animate={{ height: "auto", opacity: 1 }}
                              exit={{ height: 0, opacity: 0 }}
                              transition={{ duration: 0.22 }}
                              style={{ overflow: "hidden" }}
                            >
                              <div
                                className="px-3 pt-2 pb-3 border-t"
                                style={{ borderColor: cfg.border }}
                              >
                                <div
                                  className="text-[10px] font-bold uppercase tracking-wider mb-2 flex items-center gap-1"
                                  style={{ color: colors.textMuted }}
                                >
                                  <MapPin className="w-3 h-3" style={{ color: colors.primary }} />
                                  Titik Perjalanan
                                </div>
                                <div className="relative">
                                  <div
                                    className="absolute left-[14px] top-2 bottom-2 w-0.5"
                                    style={{ backgroundColor: colors.border }}
                                  />
                                  <div className="space-y-2">
                                    {route.waypoints.map((wp, i) => {
                                      const hasInc = !!wp.incident;
                                      const incCfg = hasInc ? statusConfig[wp.incident!.level] : null;
                                      return (
                                        <div key={i} className="flex gap-3 relative">
                                          <div className="w-7 flex-shrink-0 flex justify-center pt-1">
                                            <div
                                              className="w-2.5 h-2.5 rounded-full border-2 border-white shadow-sm z-10 relative"
                                              style={{
                                                backgroundColor: hasInc
                                                  ? incCfg!.badge
                                                  : i === 0 || i === route.waypoints.length - 1
                                                  ? colors.primary
                                                  : colors.borderLight,
                                              }}
                                            />
                                          </div>
                                          <div className="flex-1 pb-1">
                                            <div
                                              className="text-[11px] font-semibold leading-tight"
                                              style={{ color: colors.textPrimary }}
                                            >
                                              {wp.name}
                                            </div>
                                            <div
                                              className="text-[10px]"
                                              style={{ color: colors.textMuted }}
                                            >
                                              km {wp.km}
                                            </div>
                                            {wp.note && (
                                              <div
                                                className="text-[10px] mt-0.5"
                                                style={{ color: colors.textSecondary }}
                                              >
                                                {wp.note}
                                              </div>
                                            )}
                                            {hasInc && (
                                              <div
                                                className="mt-1 p-2 rounded-lg text-[10px] border"
                                                style={{
                                                  backgroundColor: incCfg!.bg,
                                                  borderColor: incCfg!.border,
                                                  color: incCfg!.text,
                                                }}
                                              >
                                                <span className="font-bold flex items-center gap-1 mb-0.5">
                                                  <TriangleAlert className="w-3 h-3" /> {incCfg!.label}
                                                </span>
                                                {wp.incident!.desc}
                                              </div>
                                            )}
                                          </div>
                                        </div>
                                      );
                                    })}
                                  </div>
                                </div>
                                <div
                                  className="mt-2 p-2 rounded-xl text-[10px] flex items-start gap-1.5"
                                  style={{ backgroundColor: colors.bgTint, color: colors.successText }}
                                >
                                  <Info className="w-3 h-3 flex-shrink-0 mt-0.5" style={{ color: colors.primary }} />
                                  <span>💡 {route.tip}</span>
                                </div>
                              </div>
                            </motion.div>
                          )}
                        </AnimatePresence>
                      </div>
                    );
                  })}
                </div>

                {/* Emergency contacts */}
                <div
                  className="mx-3 mb-4 rounded-2xl p-4"
                  style={{ background: colors.gradientNav }}
                >
                  <div className="flex items-center gap-2 mb-3">
                    <Phone className="w-3.5 h-3.5 text-white" />
                    <span className="font-bold text-xs text-white">Kontak Darurat Dieng</span>
                  </div>
                  <div className="space-y-2">
                    {[
                      { name: "SAR Wonosobo", number: "0286-321xxx" },
                      { name: "Puskesmas Kejajar", number: "0286-3397xxx" },
                      { name: "Polsek Kejajar", number: "0286-3398xxx" },
                      { name: "Damkar Wonosobo", number: "113" },
                    ].map((contact) => (
                      <div key={contact.name} className="flex items-center justify-between">
                        <span className="text-[11px]" style={{ color: colors.primaryLight }}>
                          {contact.name}
                        </span>
                        <span className="text-[11px] font-bold text-white">{contact.number}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* ── Map Panel ── */}
            <div className="flex-1 relative z-0 h-[450px] lg:h-full">
              <RouteMap
                activeRouteId={expandedRoute}
                onRouteClick={(id) => setExpandedRoute(expandedRoute === id ? null : id)}
                height={mapHeight}
              />
            </div>
          </div>
        )}

        {/* ─── TAB: Insiden ─── */}
        {activeTab === "insiden" && (
          <div className="space-y-4">
            {incidents.map((inc) => {
              const cfg = statusConfig[inc.level];
              const Icon = inc.icon;
              return (
                <motion.div
                  key={inc.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="rounded-2xl border p-5 flex items-start gap-4"
                  style={{ backgroundColor: cfg.bg, borderColor: cfg.border }}
                >
                  <div
                    className="w-11 h-11 rounded-2xl flex items-center justify-center flex-shrink-0"
                    style={{ backgroundColor: cfg.badge }}
                  >
                    <Icon className="w-5 h-5 text-white" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 flex-wrap mb-1">
                      <span
                        className="px-2.5 py-0.5 rounded-full text-xs font-bold text-white"
                        style={{ backgroundColor: cfg.badge }}
                      >
                        {cfg.label}
                      </span>
                      <span className="font-semibold text-sm" style={{ color: "#1f2937" }}>
                        {inc.title}
                      </span>
                    </div>
                    <p className="text-sm mb-2" style={{ color: "#4b5563" }}>{inc.desc}</p>
                    <div className="flex items-center gap-3 text-xs" style={{ color: "#9ca3af" }}>
                      <span className="flex items-center gap-1">
                        <Navigation className="w-3 h-3" /> {inc.route}
                      </span>
                      <span className="flex items-center gap-1">
                        <Clock className="w-3 h-3" /> {inc.time}
                      </span>
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </div>
        )}

        {/* ─── TAB: Keselamatan ─── */}
        {activeTab === "keselamatan" && (
          <div className="grid md:grid-cols-2 gap-6">
            {/* Checklist */}
            <div
              className="rounded-3xl border shadow-sm p-6"
              style={{ backgroundColor: colors.bgSurface, borderColor: colors.border }}
            >
              <div className="flex items-center gap-2 mb-5">
                <Shield className="w-5 h-5" style={{ color: colors.primary }} />
                <h3 className="font-bold text-base" style={{ color: colors.textPrimary }}>
                  Checklist Keselamatan Sebelum Berangkat
                </h3>
              </div>
              <div className="space-y-3">
                {safetyChecklist.map((item, i) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.05 }}
                    className="flex items-start gap-3 p-3 rounded-xl"
                    style={{ backgroundColor: colors.bgTint }}
                  >
                    <span className="text-lg flex-shrink-0">{item.icon}</span>
                    <span className="text-sm" style={{ color: colors.textPrimary }}>{item.text}</span>
                  </motion.div>
                ))}
              </div>
            </div>

            {/* Kondisi spesifik Dieng */}
            <div className="space-y-4">
              {[
                {
                  icon: CloudFog,
                  title: "Kabut Tebal (Pagi & Sore)",
                  color: "#0ea5e9",
                  bg: colors.infoBg,
                  items: ["Nyalakan lampu utama + hazard", "Ikuti marka jalan tengah", "Jaga jarak aman 30+ meter", "Berhenti jika visibilitas < 20 m"],
                },
                {
                  icon: Thermometer,
                  title: "Embun Beku / Jalanan Licin",
                  color: "#7c3aed",
                  bg: "#f5f3ff",
                  items: ["Berangkat setelah matahari terbit (06.30+)", "Hindari rem mendadak", "Gunakan ban dengan tapak baik", "Waspadai tikungan & turunan"],
                },
                {
                  icon: Car,
                  title: "Medan Berliku & Terjal",
                  color: "#d97706",
                  bg: colors.warningBg,
                  items: ["Gunakan gigi rendah saat turunan", "Klakson sebelum tikungan buta", "Tidak mendahului di tikungan", "Parkir di bahu jalan yang aman"],
                },
              ].map(({ icon: Icon, title, color, bg, items }) => (
                <div
                  key={title}
                  className="rounded-2xl border p-4"
                  style={{ backgroundColor: bg, borderColor: `${color}30` }}
                >
                  <div className="flex items-center gap-2 mb-3">
                    <Icon className="w-4 h-4" style={{ color }} />
                    <span className="font-semibold text-sm" style={{ color: colors.textPrimary }}>{title}</span>
                  </div>
                  <ul className="space-y-1.5">
                    {items.map((item, i) => (
                      <li key={i} className="text-xs flex items-start gap-2" style={{ color: colors.textSecondary }}>
                        <ChevronRight className="w-3 h-3 mt-0.5 flex-shrink-0" style={{ color }} />
                        {item}
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
