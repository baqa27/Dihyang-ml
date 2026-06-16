import { useState, type ReactNode } from "react";
import {
  MapPin, Calendar, Users, Sparkles, Clock, ChevronRight, CloudRain,
  Sun, Cloud, AlertCircle, Plus, CheckCircle2, Navigation, Utensils, Camera, Bed,
} from "lucide-react";
import { useThemeColors } from "../hooks/useThemeColors";
import { apiService } from "../../services/api.service";
import { APIError } from "../../config/api";

const destinations = ["Dieng Plateau", "Sikunir", "Kawah Sikidang", "Telaga Warna", "Gunung Prau", "Batu Ratapan Angin", "Wonosobo", "Sumur Jalatunda"];
const interests = ["Sunrise 🌄", "Budaya 🏛️", "Kuliner 🍜", "Alam 🌿", "Fotografi 📸", "Trekking 🥾", "Kawah 🌋", "Sejarah 📜"];
const durations = ["2 Hari", "3 Hari", "5 Hari", "7 Hari", "10 Hari"];
const budgets = ["< Rp 500rb/hari", "Rp 500rb–1jt/hari", "Rp 1–2jt/hari", "> Rp 2jt/hari"];

type Activity = {
  time: string;
  name: string;
  location: string;
  duration: string;
  type: "attraction" | "food" | "transport" | "hotel";
  note?: string;
  weatherOk: boolean;
};

type Day = {
  day: number;
  date: string;
  weather: { icon: string; condition: string; temp: string; rain: number };
  activities: Activity[];
  warning?: string;
};

type GenerationMeta = {
  source: "gemini" | "nvidia" | "fallback";
  requestedDays: number;
  message?: string;
};

const activityIcons: Record<string, ReactNode> = {
  attraction: <Camera className="w-4 h-4" />,
  food: <Utensils className="w-4 h-4" />,
  transport: <Navigation className="w-4 h-4" />,
  hotel: <Bed className="w-4 h-4" />,
};

const activityColors: Record<string, { bg: string; color: string }> = {
  attraction: { bg: "#d1fae5", color: "#065f46" },
  food: { bg: "#fef3c7", color: "#92400e" },
  transport: { bg: "#dbeafe", color: "#1e40af" },
  hotel: { bg: "#ede9fe", color: "#5b21b6" },
};

export default function SmartItinerary() {
  const [step, setStep] = useState<"form" | "result">("form");
  const [destination, setDestination] = useState("Dieng Plateau");
  const [duration, setDuration] = useState("3 Hari");
  const [budget, setBudget] = useState("Rp 500rb–1jt/hari");
  const [selectedInterests, setSelectedInterests] = useState<string[]>(["Sunrise 🌄", "Budaya 🏛️"]);
  const [guests, setGuests] = useState(2);
  const [activeDay, setActiveDay] = useState(0);
  const [loading, setLoading] = useState(false);
  const [itinerary, setItinerary] = useState<Day[] | null>(null);
  const [generationMeta, setGenerationMeta] = useState<GenerationMeta | null>(null);
  const [error, setError] = useState<string | null>(null);
  const c = useThemeColors();

  const toggleInterest = (interest: string) => {
    setSelectedInterests((prev) =>
      prev.includes(interest) ? prev.filter((i) => i !== interest) : [...prev, interest]
    );
  };

  const mapBackendItinerary = (data: any, expectedDays: number): Day[] => {
    if (!data || !Array.isArray(data.days)) {
      throw new Error("Format itinerary dari backend tidak valid.");
    }
    if (data.days.length !== expectedDays) {
      throw new Error(`Backend mengembalikan ${data.days.length} hari, seharusnya ${expectedDays} hari.`);
    }

    return data.days.map((d: any, idx: number) => {
      const rawActivities = d.activities || d.items || [];
      if (!Array.isArray(rawActivities) || rawActivities.length === 0) {
        throw new Error(`Hari ke-${idx + 1} tidak memiliki aktivitas.`);
      }

      const activities: Activity[] = rawActivities.map((item: any) => {
        let type: Activity["type"] = "attraction";
        if (item.type === "food") type = "food";
        else if (item.type === "stay" || item.type === "hotel" || item.type === "accommodation") type = "hotel";
        else if (item.type === "transport" || item.type === "transportation") type = "transport";

        return {
          time: item.time || "08:00",
          name: item.name || item.title || "Aktivitas Wisata",
          location: item.location || destination,
          duration: item.duration || ((item.type === "stay" || item.type === "hotel") ? "-" : "1.5 jam"),
          type,
          note: item.note || item.desc || undefined,
          weatherOk: item.weatherOk ?? true,
        };
      });

      const weather = d.weather || {};
      return {
        day: idx + 1,
        date: d.date || d.day || `Hari ke-${idx + 1}`,
        weather: {
          icon: weather.icon || "🌫️",
          condition: weather.condition || "Cuaca berubah-ubah",
          temp: weather.temp || "14°C",
          rain: Number(weather.rain) || 0,
        },
        activities,
        warning: d.warning || undefined,
      };
    });
  };

  const handleGenerate = async () => {
    setLoading(true);
    setError(null);
    const requestedDays = Number.parseInt(duration, 10);

    let style = "couple";
    if (guests === 1) style = "solo";
    else if (guests === 2) style = "couple";
    else if (guests <= 4) style = "family";
    else style = "group";

    let budgetVal = 750000;
    if (budget.includes("<")) budgetVal = 300000;
    else if (budget.includes("500")) budgetVal = 750000;
    else if (budget.includes("1–2")) budgetVal = 1500000;
    else budgetVal = 2500000;

    try {
      const data = await apiService.generateItinerary({
        destination,
        duration: requestedDays,
        travelStyle: style,
        budget: budgetVal,
        guests,
        interests: selectedInterests,
        vehicle: "Mobil",
      });
      
      const mapped = mapBackendItinerary(data, requestedDays);
      setItinerary(mapped);
      setGenerationMeta(data.meta || {
        source: "fallback",
        requestedDays,
        message: "Backend tidak mengirim informasi sumber itinerary.",
      });
      setActiveDay(0);
      setStep("result");
    } catch (err) {
      console.error("Error generating itinerary:", err);
      setItinerary(null);
      setGenerationMeta(null);
      
      let errorMessage = "Itinerary gagal dibuat. Pastikan backend berjalan lalu coba lagi.";
      
      if (err instanceof APIError) {
        if (err.errorType === 'network_error') {
          errorMessage = "Tidak dapat terhubung ke server. Pastikan backend berjalan.";
        } else if (err.statusCode === 422) {
          errorMessage = `Data tidak valid: ${err.message}`;
        } else if (err.statusCode === 503) {
          errorMessage = "Layanan AI sedang sibuk. Silakan coba lagi dalam beberapa saat.";
        } else {
          errorMessage = err.message;
        }
      } else if (err instanceof Error) {
        errorMessage = err.message;
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const currentItinerary = itinerary || [];

  return (
    <section className="py-20 px-4" style={{ backgroundColor: c.bgBase }}>
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold mb-3" style={{ color: c.textPrimary }}>
            Smart Itinerary Wisata Dieng
          </h2>
          <p className="max-w-xl mx-auto text-sm" style={{ color: c.textSecondary }}>
            Rencanakan perjalanan ke Dieng yang adaptif terhadap cuaca dingin & kabut. AI kami menyesuaikan aktivitas
            secara otomatis - termasuk potensi embun beku malam hari.
          </p>
        </div>

        {step === "form" ? (
          <div className="max-w-3xl mx-auto">
            <div
              className="rounded-3xl shadow-xl border overflow-hidden"
              style={{ backgroundColor: c.bgSurface, borderColor: c.border }}
            >
              {/* Form Header */}
              <div
                className="px-8 py-6"
                style={{ background: c.gradientItinerary }}
              >
                <h3 className="text-white font-bold text-lg mb-1">Rancang Perjalanan Impianmu</h3>
                <p style={{ color: c.primaryLight, fontSize: "13px" }}>
                  Isi preferensi dan biarkan AI menyusun itinerary terbaik untukmu
                </p>
              </div>

              <div className="p-8 space-y-7">
                {/* Destination */}
                <div>
                  <label className="block text-sm font-semibold mb-3" style={{ color: c.textPrimary }}>
                    <MapPin className="w-4 h-4 inline mr-1.5" style={{ color: c.primary }} />
                    Destinasi Wisata
                  </label>
                  <div className="flex flex-wrap gap-2">
                    {destinations.map((d) => (
                      <button
                        key={d}
                        onClick={() => setDestination(d)}
                        className="py-2 px-3 rounded-xl text-sm font-medium transition-all hover:scale-105"
                        style={{
                          backgroundColor: destination === d ? c.navBg : c.bgTint,
                          color: destination === d ? "#ffffff" : c.successText,
                          border: destination === d ? "none" : `1px solid ${c.successBorder}`,
                        }}
                      >
                        {d}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Duration + Budget + Guests */}
                <div className="grid md:grid-cols-3 gap-5">
                  <div>
                    <label className="block text-sm font-semibold mb-2" style={{ color: c.textPrimary }}>
                      <Calendar className="w-4 h-4 inline mr-1.5" style={{ color: c.primary }} />
                      Durasi
                    </label>
                    <div className="flex flex-col gap-2">
                      {durations.map((d) => (
                        <button
                          key={d}
                          onClick={() => setDuration(d)}
                          className="py-2 px-3 rounded-xl text-sm text-left transition-all"
                          style={{
                            backgroundColor: duration === d ? c.navBg : c.bgInput,
                            color: duration === d ? "#ffffff" : c.textPrimary,
                            border: duration === d ? "none" : `1px solid ${c.border}`,
                          }}
                        >
                          {d}
                        </button>
                      ))}
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-semibold mb-2" style={{ color: c.textPrimary }}>
                      💰 Anggaran/Hari
                    </label>
                    <div className="flex flex-col gap-2">
                      {budgets.map((b) => (
                        <button
                          key={b}
                          onClick={() => setBudget(b)}
                          className="py-2 px-3 rounded-xl text-xs text-left transition-all"
                          style={{
                            backgroundColor: budget === b ? c.navBg : c.bgInput,
                            color: budget === b ? "#ffffff" : c.textPrimary,
                            border: budget === b ? "none" : `1px solid ${c.border}`,
                          }}
                        >
                          {b}
                        </button>
                      ))}
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-semibold mb-2" style={{ color: c.textPrimary }}>
                      <Users className="w-4 h-4 inline mr-1.5" style={{ color: c.primary }} />
                      Jumlah Tamu
                    </label>
                    <div className="flex items-center gap-3 mt-3">
                      <button
                        onClick={() => setGuests(Math.max(1, guests - 1))}
                        className="w-10 h-10 rounded-xl border text-lg font-bold transition-all"
                        style={{ borderColor: c.successBorder, color: c.primary }}
                      >−</button>
                      <span className="text-2xl font-bold w-8 text-center" style={{ color: c.textPrimary }}>{guests}</span>
                      <button
                        onClick={() => setGuests(Math.min(20, guests + 1))}
                        className="w-10 h-10 rounded-xl border text-lg font-bold transition-all"
                        style={{ borderColor: c.successBorder, color: c.primary }}
                      >+</button>
                    </div>
                    <div className="text-xs mt-2" style={{ color: c.textMuted }}>Orang</div>
                  </div>
                </div>

                {/* Interests */}
                <div>
                  <label className="block text-sm font-semibold mb-3" style={{ color: c.textPrimary }}>
                    ✨ Minat & Aktivitas (pilih beberapa)
                  </label>
                  <div className="flex flex-wrap gap-2">
                    {interests.map((interest) => (
                      <button
                        key={interest}
                        onClick={() => toggleInterest(interest)}
                        className="px-4 py-2 rounded-full text-sm font-medium transition-all hover:scale-105"
                        style={{
                          backgroundColor: selectedInterests.includes(interest) ? c.navBg : c.bgTint,
                          color: selectedInterests.includes(interest) ? "#ffffff" : c.successText,
                          border: selectedInterests.includes(interest) ? "none" : `1px solid ${c.successBorder}`,
                        }}
                      >
                        {selectedInterests.includes(interest) && <CheckCircle2 className="w-3.5 h-3.5 inline mr-1.5" />}
                        {interest}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Generate Button */}
                <button
                  onClick={handleGenerate}
                  disabled={loading}
                  className="w-full py-4 rounded-2xl text-white font-bold text-base shadow-xl transition-all hover:scale-[1.02] disabled:opacity-60"
                  style={{
                    background: c.gradientAccent,
                    boxShadow: "0 6px 20px rgba(246,173,85,0.4)",
                  }}
                >
                  {loading ? (
                    <span className="flex items-center justify-center gap-2">
                      <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      AI sedang menyusun itinerary...
                    </span>
                  ) : (
                    <span className="flex items-center justify-center gap-2">
                      <Sparkles className="w-5 h-5" />
                      Generate Smart Itinerary
                    </span>
                  )}
                </button>
                {error && (
                  <div
                    role="alert"
                    className="rounded-xl border px-4 py-3 text-sm"
                    style={{ backgroundColor: c.dangerBg, borderColor: c.dangerBorder, color: c.dangerText }}
                  >
                    <div className="font-semibold mb-1">Itinerary belum berhasil dibuat</div>
                    <div>{error}</div>
                  </div>
                )}
              </div>
            </div>
          </div>
        ) : (
          <div>
            {/* Back Button */}
            <button
              onClick={() => setStep("form")}
              className="mb-6 flex items-center gap-2 text-sm font-medium transition-colors"
              style={{ color: c.primary }}
            >
              ← Ubah Preferensi
            </button>

            {/* Summary Bar */}
            <div
              className="rounded-2xl p-4 mb-8 flex flex-wrap gap-4 items-center border"
              style={{ backgroundColor: c.bgSurface, borderColor: c.successBorder }}
            >
              {[
                { icon: MapPin, label: destination },
                { icon: Calendar, label: duration },
                { icon: Users, label: `${guests} orang` },
                { icon: null, label: `💰 ${budget}` },
              ].map(({ icon: Icon, label }) => (
                <div key={label} className="flex items-center gap-1.5">
                  {Icon && <Icon className="w-4 h-4" style={{ color: c.primary }} />}
                  <span className="text-sm font-medium" style={{ color: c.textPrimary }}>{label}</span>
                </div>
              ))}
              <div className="ml-auto">
                <span
                  className="px-3 py-1 rounded-full text-xs font-semibold"
                  style={{
                    backgroundColor: generationMeta?.source === "fallback" ? "#fef3c7" : c.bgTint,
                    color: generationMeta?.source === "fallback" ? "#92400e" : c.successText,
                  }}
                >
                  {generationMeta?.source === "fallback" ? "Rencana lokal adaptif" : "✅ AI Dioptimalkan"}
                </span>
              </div>
            </div>

            {generationMeta?.message && (
              <div
                className="rounded-2xl px-4 py-3 mb-6 border text-sm"
                style={{ backgroundColor: "#fffbeb", borderColor: "#fcd34d", color: "#92400e" }}
              >
                {generationMeta.message}
              </div>
            )}

            <div className="grid lg:grid-cols-4 gap-6">
              {/* Day Selector */}
              <div className="lg:col-span-1">
                <h3 className="font-bold text-sm mb-3" style={{ color: c.textPrimary }}>
                  Pilih Hari
                </h3>
                <div className="space-y-2">
                  {currentItinerary.map((day, i) => (
                    <button
                      key={i}
                      onClick={() => setActiveDay(i)}
                      className="w-full flex items-center gap-3 p-3 rounded-2xl text-left transition-all hover:scale-[1.02] border"
                      style={{
                        backgroundColor: activeDay === i ? c.navBg : c.bgSurface,
                        borderColor: activeDay === i ? "transparent" : day.warning ? c.dangerBorder : c.border,
                      }}
                    >
                      <span className="text-2xl">{day.weather.icon}</span>
                      <div>
                        <div className="text-sm font-bold" style={{ color: activeDay === i ? "#ffffff" : c.textPrimary }}>
                          Hari {day.day}
                        </div>
                        <div className="text-xs" style={{ color: activeDay === i ? c.primaryLight : c.textMuted }}>
                          {day.weather.condition} • {day.weather.temp}
                        </div>
                      </div>
                      {day.warning && (
                        <AlertCircle className="w-4 h-4 ml-auto flex-shrink-0" style={{ color: activeDay === i ? "#fca5a5" : "#ef4444" }} />
                      )}
                    </button>
                  ))}
                </div>
              </div>

              {/* Timeline */}
              <div className="lg:col-span-3">
                {currentItinerary[activeDay]?.warning && (
                  <div
                    className="rounded-2xl p-4 mb-4 flex items-start gap-3 border"
                    style={{ backgroundColor: c.dangerBg, borderColor: c.dangerBorder }}
                  >
                    <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
                    <div>
                      <div className="text-sm font-semibold text-red-700 mb-0.5">Penyesuaian Cuaca Otomatis</div>
                      <div className="text-sm text-red-600">{currentItinerary[activeDay].warning}</div>
                    </div>
                  </div>
                )}

                <div
                  className="rounded-3xl overflow-hidden border shadow-sm"
                  style={{ backgroundColor: c.bgSurface, borderColor: c.border }}
                >
                  <div
                    className="px-6 py-4 flex items-center justify-between border-b"
                    style={{ borderColor: c.borderLight, backgroundColor: c.bgTint }}
                  >
                    <div>
                      <div className="font-bold text-sm" style={{ color: c.textPrimary }}>
                        {currentItinerary[activeDay]?.date}
                      </div>
                      <div className="text-xs mt-0.5" style={{ color: c.textSecondary }}>
                        {currentItinerary[activeDay]?.activities.length} aktivitas •{" "}
                        {currentItinerary[activeDay]?.weather.icon} {currentItinerary[activeDay]?.weather.condition}
                      </div>
                    </div>
                    <div
                      className="px-3 py-1 rounded-full text-xs font-semibold"
                      style={{
                        backgroundColor: currentItinerary[activeDay]?.weather.rain >= 50 ? c.dangerBg : c.bgTint,
                        color: currentItinerary[activeDay]?.weather.rain >= 50 ? c.dangerText : c.successText,
                      }}
                    >
                      {currentItinerary[activeDay]?.weather.rain >= 50 ? "⚠️ Cuaca Buruk" : "✅ Cuaca Baik"}
                    </div>
                  </div>

                  <div className="p-6">
                    <div className="relative">
                      {/* Timeline line */}
                      <div
                        className="absolute left-10 top-0 bottom-0 w-0.5"
                        style={{ backgroundColor: c.border }}
                      />

                      <div className="space-y-5">
                        {currentItinerary[activeDay]?.activities.map((activity, i) => {
                          const actColors = activityColors[activity.type];
                          return (
                            <div key={i} className="flex gap-5 relative">
                              {/* Time */}
                              <div className="w-14 text-right flex-shrink-0 pt-3">
                                <span className="text-xs font-semibold" style={{ color: c.textMuted }}>
                                  {activity.time}
                                </span>
                              </div>

                              {/* Dot */}
                              <div className="relative flex-shrink-0 mt-3">
                                <div
                                  className="w-4 h-4 rounded-full border-2 border-white shadow-md"
                                  style={{ backgroundColor: actColors.color }}
                                />
                              </div>

                              {/* Activity Card */}
                              <div
                                className="flex-1 p-4 rounded-2xl border transition-all hover:shadow-md"
                                style={{ backgroundColor: c.bgInput, borderColor: c.borderLight }}
                              >
                                <div className="flex items-start justify-between gap-2">
                                  <div className="flex-1">
                                    <div className="flex items-center gap-2 flex-wrap mb-1">
                                      <span
                                        className="flex items-center gap-1 px-2 py-0.5 rounded-lg text-xs font-medium"
                                        style={{ backgroundColor: actColors.bg, color: actColors.color }}
                                      >
                                        {activityIcons[activity.type]}
                                        {activity.type === "attraction"
                                          ? "Wisata"
                                          : activity.type === "food"
                                          ? "Kuliner"
                                          : activity.type === "hotel"
                                          ? "Penginapan"
                                          : "Transportasi"}
                                      </span>
                                    </div>
                                    <div className="font-semibold text-sm" style={{ color: c.textPrimary }}>
                                      {activity.name}
                                    </div>
                                    <div className="flex items-center gap-1 mt-1">
                                      <MapPin className="w-3 h-3" style={{ color: c.textMuted }} />
                                      <span className="text-xs" style={{ color: c.textSecondary }}>
                                        {activity.location}
                                      </span>
                                      <span className="mx-1" style={{ color: c.border }}>·</span>
                                      <Clock className="w-3 h-3" style={{ color: c.textMuted }} />
                                      <span className="text-xs" style={{ color: c.textSecondary }}>
                                        {activity.duration}
                                      </span>
                                    </div>
                                    {activity.note && (
                                      <div
                                        className="mt-2 text-xs px-2 py-1 rounded-lg"
                                        style={{ backgroundColor: c.bgTint, color: c.successText }}
                                      >
                                        💡 {activity.note}
                                      </div>
                                    )}
                                  </div>
                                </div>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
