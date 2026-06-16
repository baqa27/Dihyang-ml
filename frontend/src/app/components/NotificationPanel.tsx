import { useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import {
  Bell, X, CheckCircle, AlertTriangle, AlertCircle, Info,
  CloudFog, Thermometer, Navigation, CloudRain, TriangleAlert, Clock,
} from "lucide-react";
import { useThemeColors } from "../hooks/useThemeColors";

type NotifLevel = "bahaya" | "peringatan" | "info" | "aman";

type Notif = {
  id: number;
  level: NotifLevel;
  icon: React.ElementType;
  title: string;
  desc: string;
  time: string;
  category: "cuaca" | "rute" | "wisata";
  read: boolean;
};

const initialNotifs: Notif[] = [
  {
    id: 1,
    level: "bahaya",
    icon: TriangleAlert,
    title: "Longsor km 18 - Jalur Temanggung DITUTUP",
    desc: "Jalur Temanggung–Dieng tidak bisa dilalui. Gunakan jalur Wonosobo atau Banjarnegara sebagai alternatif.",
    time: "5 mnt lalu",
    category: "rute",
    read: false,
  },
  {
    id: 2,
    level: "bahaya",
    icon: Thermometer,
    title: "Potensi Embun Beku Dini Hari Ini",
    desc: "Suhu 2–4°C diprediksi pukul 01.00–06.00. Waspadai jalanan licin. Gunakan pakaian berlapis.",
    time: "12 mnt lalu",
    category: "cuaca",
    read: false,
  },
  {
    id: 3,
    level: "peringatan",
    icon: CloudFog,
    title: "Kabut Tebal - Jalur Wonosobo km 20–26",
    desc: "Visibilitas di bawah 50 meter. Nyalakan lampu hazard dan kurangi kecepatan hingga 20 km/j.",
    time: "25 mnt lalu",
    category: "rute",
    read: false,
  },
  {
    id: 4,
    level: "peringatan",
    icon: CloudRain,
    title: "Hujan Lebat Diprediksi Rabu, 4 Juni",
    desc: "Curah hujan tinggi di kawasan Kawah Sikidang & Telaga Warna. Pertimbangkan penjadwalan ulang aktivitas outdoor.",
    time: "1 jam lalu",
    category: "cuaca",
    read: false,
  },
  {
    id: 5,
    level: "info",
    icon: Navigation,
    title: "Jalur Banjarnegara - Kondisi Normal",
    desc: "Tidak ada hambatan di jalur Banjarnegara–Dieng. Rute paling direkomendasikan hari ini.",
    time: "2 jam lalu",
    category: "rute",
    read: true,
  },
  {
    id: 6,
    level: "aman",
    icon: CheckCircle,
    title: "Cuaca Ideal Akhir Pekan - Sunrise Sempurna",
    desc: "Sabtu–Minggu diprediksi cerah tanpa awan. Bukit Sikunir & Gunung Prau kondisi ideal untuk sunrise.",
    time: "3 jam lalu",
    category: "wisata",
    read: true,
  },
  {
    id: 7,
    level: "info",
    icon: AlertCircle,
    title: "Tikungan km 8 Jalur Wonosobo - Penyempitan",
    desc: "Pengerjaan talud menyempitkan lajur di km 8. Bergantian kendaraan. Estimasi selesai 7 Juni.",
    time: "Kemarin",
    category: "rute",
    read: true,
  },
];

const levelConfig: Record<NotifLevel, { bg: string; border: string; badge: string; text: string; label: string }> = {
  bahaya: { bg: "#fef2f2", border: "#fecaca", badge: "#ef4444", text: "#dc2626", label: "Bahaya" },
  peringatan: { bg: "#fffbeb", border: "#fde68a", badge: "#f59e0b", text: "#d97706", label: "Peringatan" },
  info: { bg: "#eff6ff", border: "#bfdbfe", badge: "#3b82f6", text: "#2563eb", label: "Info" },
  aman: { bg: "#f0fdf4", border: "#bbf7d0", badge: "#10b981", text: "#059669", label: "Aman" },
};

const categoryLabel: Record<string, string> = {
  cuaca: "🌡️ Cuaca",
  rute: "🗺️ Rute",
  wisata: "🏔️ Wisata",
};

interface Props {
  isOpen: boolean;
  onClose: () => void;
}

export default function NotificationPanel({ isOpen, onClose }: Props) {
  const [notifs, setNotifs] = useState<Notif[]>(initialNotifs);
  const [filter, setFilter] = useState<"semua" | "cuaca" | "rute" | "wisata">("semua");
  const c = useThemeColors();

  const unreadCount = notifs.filter((n) => !n.read).length;

  const markAllRead = () => setNotifs((prev) => prev.map((n) => ({ ...n, read: true })));
  const markRead = (id: number) => setNotifs((prev) => prev.map((n) => n.id === id ? { ...n, read: true } : n));
  const dismiss = (id: number) => setNotifs((prev) => prev.filter((n) => n.id !== id));

  const filtered = notifs.filter((n) => filter === "semua" || n.category === filter);

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <div className="fixed inset-0 z-40" onClick={onClose} />

          {/* Panel */}
          <motion.div
            initial={{ opacity: 0, y: -8, scale: 0.97 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -8, scale: 0.97 }}
            transition={{ duration: 0.18, ease: "easeOut" }}
            className="fixed sm:absolute top-16 sm:top-full left-4 sm:left-auto right-4 sm:right-0 w-auto sm:w-96 mt-2 rounded-2xl shadow-2xl overflow-hidden z-50"
            style={{
              backgroundColor: c.bgSurface,
              border: `1px solid ${c.border}`,
              boxShadow: "0 20px 50px rgba(0,0,0,0.15), 0 0 0 1px rgba(0,0,0,0.05)",
            }}
          >
            {/* Header */}
            <div
              className="px-5 py-4 flex items-center justify-between border-b"
              style={{ borderColor: c.borderLight, backgroundColor: c.bgTint }}
            >
              <div>
                <div className="flex items-center gap-2">
                  <Bell className="w-4 h-4" style={{ color: c.primary }} />
                  <span className="font-bold text-sm" style={{ color: c.textPrimary }}>Notifikasi</span>
                  {unreadCount > 0 && (
                    <span
                      className="px-2 py-0.5 rounded-full text-[10px] font-bold text-white"
                      style={{ backgroundColor: "#ef4444" }}
                    >
                      {unreadCount} baru
                    </span>
                  )}
                </div>
                <p className="text-[10px] mt-0.5" style={{ color: c.textMuted }}>
                  Peringatan cuaca, rute, & wisata Dieng real-time
                </p>
              </div>
              <div className="flex items-center gap-2">
                {unreadCount > 0 && (
                  <button
                    onClick={markAllRead}
                    className="text-[10px] font-medium transition-colors"
                    style={{ color: c.primary }}
                  >
                    Tandai semua dibaca
                  </button>
                )}
                <button
                  onClick={onClose}
                  className="p-1.5 rounded-lg transition-colors"
                  style={{ color: c.textMuted }}
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Filter tabs */}
            <div 
              className="flex gap-1 px-4 py-2.5 border-b overflow-x-auto scrollbar-none max-w-full" 
              style={{ borderColor: c.borderLight, backgroundColor: c.bgTint, WebkitOverflowScrolling: "touch", touchAction: "pan-x" }}
            >
              {(["semua", "cuaca", "rute", "wisata"] as const).map((f) => (
                <button
                  key={f}
                  onClick={() => setFilter(f)}
                  className="flex-shrink-0 px-3 py-1 rounded-lg text-[11px] font-semibold capitalize transition-all"
                  style={{
                    backgroundColor: filter === f ? c.navBg : "transparent",
                    color: filter === f ? "#ffffff" : c.textSecondary,
                  }}
                >
                  {f === "semua" ? "Semua" : categoryLabel[f]}
                </button>
              ))}
            </div>

            {/* Notifications list */}
            <div className="overflow-y-auto" style={{ maxHeight: "400px" }}>
              {filtered.length === 0 ? (
                <div className="py-10 text-center">
                  <Bell className="w-8 h-8 mx-auto mb-2" style={{ color: c.border }} />
                  <p className="text-sm" style={{ color: c.textMuted }}>Tidak ada notifikasi</p>
                </div>
              ) : (
                <div className="divide-y" style={{ borderColor: c.borderLight }}>
                  {filtered.map((notif) => {
                    const cfg = levelConfig[notif.level];
                    const Icon = notif.icon;
                    return (
                      <div
                        key={notif.id}
                        className="px-4 py-3.5 flex items-start gap-3 transition-colors relative cursor-pointer"
                        style={{ backgroundColor: notif.read ? "transparent" : `${cfg.bg}80` }}
                        onClick={() => markRead(notif.id)}
                      >
                        {/* Unread indicator */}
                        {!notif.read && (
                          <div
                            className="absolute left-0 top-0 bottom-0 w-0.5 rounded-r-full"
                            style={{ backgroundColor: cfg.badge }}
                          />
                        )}

                        {/* Icon */}
                        <div
                          className="w-8 h-8 rounded-xl flex items-center justify-center flex-shrink-0 mt-0.5"
                          style={{ backgroundColor: cfg.bg, border: `1.5px solid ${cfg.border}` }}
                        >
                          <Icon className="w-4 h-4" style={{ color: cfg.badge }} />
                        </div>

                        {/* Content */}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-start justify-between gap-2">
                            <div className="flex-1">
                              <div className="flex items-center gap-1.5 mb-0.5 flex-wrap">
                                <span
                                  className="px-1.5 py-0.5 rounded text-[9px] font-bold"
                                  style={{ backgroundColor: cfg.badge, color: "#fff" }}
                                >
                                  {cfg.label.toUpperCase()}
                                </span>
                                <span className="text-[10px]" style={{ color: c.textMuted }}>
                                  {categoryLabel[notif.category]}
                                </span>
                              </div>
                              <p
                                className="text-xs font-semibold leading-tight mb-0.5"
                                style={{ color: c.textPrimary }}
                              >
                                {notif.title}
                              </p>
                              <p className="text-[11px] leading-relaxed" style={{ color: c.textSecondary }}>
                                {notif.desc}
                              </p>
                              <div className="flex items-center gap-1 mt-1.5">
                                <Clock className="w-3 h-3" style={{ color: c.textMuted }} />
                                <span className="text-[10px]" style={{ color: c.textMuted }}>{notif.time}</span>
                              </div>
                            </div>
                            <button
                              onClick={(e) => { e.stopPropagation(); dismiss(notif.id); }}
                              className="p-1 rounded-lg transition-colors flex-shrink-0"
                            >
                              <X className="w-3 h-3" style={{ color: c.textMuted }} />
                            </button>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            {/* Footer */}
            <div
              className="px-4 py-3 border-t text-center"
              style={{ borderColor: c.borderLight, backgroundColor: c.bgTint }}
            >
              <p className="text-[10px]" style={{ color: c.textMuted }}>
                🔔 Notifikasi diperbarui otomatis setiap 5 menit
              </p>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
