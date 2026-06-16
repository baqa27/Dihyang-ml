import { useState, useEffect } from "react";
import { Search, Calendar, MapPin, Star, Users, Cloud, TrendingUp, Thermometer, Wind, X } from "lucide-react";
import { motion, AnimatePresence } from "motion/react";
import { useThemeColors } from "../hooks/useThemeColors";

const spots = [
  "Candi Arjuna", "Kawah Sikidang", "Telaga Warna", "Bukit Sikunir",
  "Gunung Prau", "Batu Ratapan Angin",
];

const SPOT_IMAGES: Record<string, string> = {
  "arjuna": "https://travelspromo.com/wp-content/uploads/2021/11/penampakan-bangunan-candi-di-komplek-wisata-Candi-Arjuna-e1638334989524.jpg?w=800&q=80",
  "sikidang": "https://rentalmobilbintaro.com/wp-content/uploads/2025/01/6-keindahan-kawah-sikidang-dieng-yang-memukau-wisatawan.jpg?w=800&q=80",
  "cinta": "https://visitcentraljava.com/wp-content/uploads/2024/05/image-5.png?w=800&q=80",
  "Angin": "https://visitcentraljava.com/wp-content/uploads/2025/01/image-7.png?w=800&q=80",
  "prau": "https://ik.imagekit.io/tvlk/blog/2024/12/Jalur-Pendakian-Gunung-Prau-1.jpg?tr=q-70,c-at_max,w-500,h-250,dpr-2?w=800&q=80",
  "sikunir": "https://ik.imagekit.io/tvlk/blog/2024/08/shutterstock_2054600033.jpg?tr=q-70,c-at_max,w-500,h-250,dpr-2?w=800&q=80",
  "warna": "https://visitjawatengah.jatengprov.go.id/assets/images/d3fdb015-2b5c-4e49-9f82-e531b70969ad.jpg?w=800&q=80",
  "pandangan": "https://assets.pikiran-rakyat.com/crop/0x0:0x0/720x0/filters:watermark(file/2017/cms/img/watermark.png,-0,0,0)/photo/2025/10/23/2134351431.jpeg?w=800&q=80",
  "menjer": "https://static.promediateknologi.id/crop/0x0:0x0/0x0/webp/photo/p2/22/2024/03/09/IMG_20240309_190236_700_x_400_piksel-3939426436.jpg?w=800&q=80",
  "kahyangan": "https://salsawisata.com/wp-content/uploads/2023/08/KAHYANGAN-SKYLINE-Wonosobo.avif?w=800&q=80",
  "tiket": "https://sisihidupku.wordpress.com/wp-content/uploads/2015/08/gerbang-memasuki-kawasan-dieng-plateau1.jpg?w=800&q=80",
  "saroja": "https://phinemo.com/wp-content/uploads/2018/04/28427591_1580232275424618_5600191630867955712_n-e1522999121930.jpg?w=800&q=80",
};

const getSpotImage = (name: string) => {
  const lowerName = name.toLowerCase();
  for (const key in SPOT_IMAGES) {
    if (lowerName.includes(key)) return SPOT_IMAGES[key];
  }
  // Default Dieng landscape fallback
  return "https://images.unsplash.com/photo-1555773744-f6c0d85cdce2?w=800&q=80";
};

const stats = [
  { icon: MapPin, value: "20+", label: "Destinasi Wisata" },
  { icon: Cloud, value: "98%", label: "Akurasi Cuaca" },
  { icon: Users, value: "10K+", label: "Wisatawan/Bulan" },
  { icon: Star, value: "4.9", label: "Rating Platform" },
];

export default function HeroSection() {
  const [searchQuery, setSearchQuery] = useState("");
  const [date, setDate] = useState("");
  const [destinations, setDestinations] = useState<any[]>([]);
  const [selectedSpot, setSelectedSpot] = useState<any | null>(null);
  const [currentWeather, setCurrentWeather] = useState<any>(null);
  const c = useThemeColors();

  useEffect(() => {
    const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";

    fetch(`${apiUrl}/api/destinations`)
      .then(res => res.json())
      .then(data => {
        if (data && data.length > 0) setDestinations(data);
      })
      .catch(err => console.error("Error fetching destinations:", err));

    fetch(`${apiUrl}/api/weather/current`)
      .then(res => res.json())
      .then(data => setCurrentWeather(data))
      .catch(err => console.error("Error fetching weather:", err));
  }, []);

  // Use dynamic spots from API if available, fallback to static
  const activeSpots = destinations.length > 0
    ? destinations.slice(0, 6).map(d => d.name)
    : spots;

  const displayTemp = currentWeather ? Math.round(currentWeather.temperature) : 13;
  const displayCondition = currentWeather ? currentWeather.condition_label : "Berkabut - Bawa jaket tebal!";
  const displayHumidity = currentWeather ? `${currentWeather.humidity}%` : "89%";
  const displayWind = currentWeather ? `${currentWeather.wind_speed} km/h` : "8 km/h";
  const displayIcon = currentWeather ? (
    currentWeather.condition === "Cerah" ? "☀️" :
      currentWeather.condition === "Berawan" ? "⛅" :
        currentWeather.condition === "Berkabut" ? "🌫️" :
          currentWeather.condition === "Gerimis" ? "🌦️" :
            currentWeather.condition === "Hujan" ? "🌧️" : "🌫️"
  ) : "🌫️";

  return (
    <div className="relative min-h-screen flex items-center pt-16 overflow-hidden">
      {/* Background */}
      <div
        className="absolute inset-0 z-0"
        style={{
          backgroundImage:
            "url('https://images.unsplash.com/photo-1555773744-f6c0d85cdce2?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&q=80&w=1920')",
          backgroundSize: "cover",
          backgroundPosition: "center 40%",
        }}
      />
      {/* Gradient Overlay */}
      <div
        className="absolute inset-0 z-10"
        style={{ background: c.gradientHeroOverlay }}
      />

      {/* Decorative blobs */}
      <div className="absolute top-40 right-0 w-80 h-80 rounded-full opacity-15 blur-3xl z-10" style={{ backgroundColor: c.primary }} />
      <div className="absolute bottom-20 left-0 w-64 h-64 rounded-full opacity-10 blur-3xl z-10" style={{ backgroundColor: "#0ea5e9" }} />

      <div className="relative z-20 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 w-full">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Left: Headline */}
          <div>
            <div
              className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-sm font-medium mb-6"
              style={{
                backgroundColor: "rgba(79,209,197,0.2)",
                color: c.primaryLight,
                border: "1px solid rgba(79,209,197,0.3)",
              }}
            >
              <TrendingUp className="w-3.5 h-3.5" />
              Platform Wisata Cerdas Dieng #1
            </div>

            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-white leading-tight mb-4">
              Jelajahi{" "}
              <span
                style={{
                  background: `linear-gradient(90deg, ${c.primary}, ${c.accent})`,
                  WebkitBackgroundClip: "text",
                  WebkitTextFillColor: "transparent",
                }}
              >
                Dieng
              </span>
              <br />
              Negeri di Atas Awan
            </h1>

            <p className="text-base mb-8" style={{ color: c.primaryLight, lineHeight: "1.8" }}>
              Platform wisata berbasis AI untuk Dataran Tinggi Dieng - prediksi cuaca dingin real-time,
              itinerary adaptif, dan informasi destinasi terlengkap se-Dieng Plateau.
            </p>


            {/* Spot Chips */}
            <div className="flex flex-wrap gap-2">
              <span className="text-sm mr-1" style={{ color: c.primaryLight }}>Populer:</span>
              {activeSpots.map((s) => (
                <button
                  key={s}
                  onClick={() => {
                    const dest = destinations.find(d => d.name.toLowerCase() === s.toLowerCase());
                    if (dest) setSelectedSpot(dest);
                  }}
                  className="px-3 py-1 rounded-full text-xs font-medium transition-all hover:scale-105"
                  style={{
                    backgroundColor: "rgba(255,255,255,0.12)",
                    color: "#ffffff",
                    border: "1px solid rgba(255,255,255,0.2)",
                  }}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>

          {/* Right: Weather Card + Stats */}
          <div className="flex flex-col gap-4">
            {/* Live Weather */}
            <div
              className="rounded-2xl p-5 shadow-2xl"
              style={{
                background: "linear-gradient(135deg, rgba(14,165,233,0.25), rgba(6,182,212,0.15))",
                backdropFilter: "blur(20px)",
                border: "1px solid rgba(255,255,255,0.15)",
              }}
            >
              <div className="flex items-start justify-between mb-3">
                <div>
                  <div className="text-xs font-medium mb-1" style={{ color: "#7dd3fc" }}>
                    ● LIVE - Cuaca Sekarang
                  </div>
                  <div className="flex items-center gap-1 text-white text-sm">
                    <MapPin className="w-3.5 h-3.5" style={{ color: c.primary }} />
                    Dieng Plateau, Wonosobo
                  </div>
                </div>
                <span className="text-5xl">{displayIcon}</span>
              </div>
              <div className="text-white text-4xl font-bold mb-1">{displayTemp}°C</div>
              <div className="text-sm mb-4" style={{ color: "#bae6fd" }}>
                {displayCondition}
              </div>
              <div className="grid grid-cols-3 gap-2 sm:gap-3">
                {[
                  { label: "Kelembaban", value: displayHumidity },
                  { label: "Angin", value: displayWind },
                  { label: "Malam nanti", value: "5°C" },
                ].map((item) => (
                  <div key={item.label} className="rounded-xl p-2 sm:p-2.5 text-center" style={{ backgroundColor: "rgba(255,255,255,0.1)" }}>
                    <div className="text-white font-semibold text-xs sm:text-sm">{item.value}</div>
                    <div className="text-[10px] sm:text-xs" style={{ color: "#93c5fd" }}>{item.label}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Frost Warning */}
            <div
              className="rounded-2xl p-4 flex items-start gap-3"
              style={{
                background: "rgba(56,189,248,0.15)",
                border: "1px solid rgba(56,189,248,0.3)",
                backdropFilter: "blur(20px)",
              }}
            >
              <span className="text-2xl">🧊</span>
              <div>
                <div className="text-sm font-semibold mb-0.5" style={{ color: "#e0f2fe" }}>
                  Potensi Embun Beku (Embun Upas)
                </div>
                <div className="text-xs" style={{ color: "#bae6fd" }}>
                  Suhu malam diprediksi 2–5°C. Fenomena embun beku mungkin terjadi dini hari. Siapkan pakaian hangat berlapis.
                </div>
              </div>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-2 gap-2.5 sm:gap-3">
              {stats.map(({ icon: Icon, value, label }) => (
                <div
                  key={label}
                  className="rounded-2xl p-3 sm:p-4 flex items-center gap-2.5 sm:gap-3"
                  style={{
                    backgroundColor: "rgba(255,255,255,0.1)",
                    backdropFilter: "blur(20px)",
                    border: "1px solid rgba(255,255,255,0.15)",
                  }}
                >
                  <div className="w-8 h-8 sm:w-9 sm:h-9 rounded-lg flex items-center justify-center flex-shrink-0" style={{ backgroundColor: "rgba(79,209,197,0.2)" }}>
                    <Icon className="w-4 h-4 sm:w-5 sm:h-5" style={{ color: c.primary }} />
                  </div>
                  <div>
                    <div className="text-white font-bold text-sm sm:text-lg leading-none">{value}</div>
                    <div className="text-[10px] sm:text-xs mt-0.5" style={{ color: c.primaryLight }}>{label}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div
        className="absolute bottom-0 left-0 right-0 h-15 z-20"
        style={{ background: `linear-gradient(to bottom, transparent, ${c.bgBase})` }}
      />

      {/* Spot Detail Modal */}
      <AnimatePresence>
        {selectedSpot && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setSelectedSpot(null)}
              className="absolute inset-0 bg-black/60 backdrop-blur-sm"
            />
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              className="relative w-full max-w-lg rounded-3xl overflow-hidden shadow-2xl z-10"
              style={{ backgroundColor: c.bgSurface, border: `1px solid ${c.border}` }}
            >
              <div
                className="h-48 bg-gray-200 relative"
                style={{
                  backgroundImage: `url('${getSpotImage(selectedSpot.name)}')`,
                  backgroundSize: "cover",
                  backgroundPosition: "center",
                }}
              >
                <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent" />
                <button
                  onClick={() => setSelectedSpot(null)}
                  className="absolute top-4 right-4 w-8 h-8 flex items-center justify-center rounded-full bg-black/50 text-white hover:bg-black/70 transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
                <div className="absolute bottom-4 left-5 pr-5">
                  <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-white/20 text-white backdrop-blur-md mb-2 inline-block">
                    {selectedSpot.category || "Alam"}
                  </span>
                  <h2 className="text-2xl font-bold text-white leading-tight">{selectedSpot.name}</h2>
                </div>
              </div>

              <div className="p-6">
                <div className="flex items-center gap-2 mb-4">
                  <MapPin className="w-4 h-4 text-emerald-500" />
                  <span className="text-sm font-medium" style={{ color: c.textSecondary }}>{selectedSpot.location}</span>
                </div>
                <p className="text-sm mb-6 leading-relaxed" style={{ color: c.textPrimary }}>
                  {selectedSpot.tip || "Destinasi wisata unggulan di Dataran Tinggi Dieng."}
                </p>

                <div className="grid grid-cols-2 gap-4">
                  <div className="p-4 rounded-2xl border" style={{ backgroundColor: c.bgInput, borderColor: c.border }}>
                    <div className="text-xs mb-1" style={{ color: c.textMuted }}>Tiket Lokal</div>
                    <div className="text-lg font-bold" style={{ color: c.primary }}>{selectedSpot.priceLocal}</div>
                  </div>
                  <div className="p-4 rounded-2xl border" style={{ backgroundColor: c.bgInput, borderColor: c.border }}>
                    <div className="text-xs mb-1" style={{ color: c.textMuted }}>Tiket Asing</div>
                    <div className="text-lg font-bold" style={{ color: "#d97706" }}>{selectedSpot.priceForeign}</div>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
