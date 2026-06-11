import { useState, useEffect, type ReactNode } from "react";
import { Search, Star, MapPin, Clock, Wifi, Car, Bus, Bike, Ship, Phone, ExternalLink, Tag, Hotel, Ticket, Navigation } from "lucide-react";
import { useThemeColors } from "../hooks/useThemeColors";

type Tab = "tiket" | "penginapan" | "transportasi";

const tickets = [
  { name: "Kompleks Candi Arjuna", location: "Dieng Plateau, Wonosobo", priceLocal: "Rp 20.000", priceForeign: "Rp 50.000", hours: "07.00–17.00", rating: 4.8, category: "Candi Hindu", tip: "Candi tertua di Jawa, abad ke-7" },
  { name: "Kawah Sikidang", location: "Dieng Plateau, Wonosobo", priceLocal: "Rp 15.000", priceForeign: "Rp 30.000", hours: "07.00–17.00", rating: 4.6, category: "Geologi", tip: "Jangan terlalu dekat - gas belerang!" },
  { name: "Telaga Warna", location: "Dieng Plateau, Wonosobo", priceLocal: "Rp 20.000", priceForeign: "Rp 40.000", hours: "07.00–17.00", rating: 4.7, category: "Danau Vulkanik", tip: "Warna berubah tergantung cuaca & mineral" },
  { name: "Bukit Sikunir", location: "Sembungan, Wonosobo", priceLocal: "Rp 10.000", priceForeign: "Rp 20.000", hours: "03.00–10.00", rating: 4.9, category: "Sunrise Point", tip: "Naik pukul 04.00 untuk sunrise terbaik" },
  { name: "Museum Kailasa", location: "Dieng Plateau, Wonosobo", priceLocal: "Rp 10.000", priceForeign: "Rp 20.000", hours: "08.00–16.00", rating: 4.5, category: "Museum", tip: "Artefak lengkap peradaban Hindu Dieng" },
  { name: "Batu Ratapan Angin", location: "Dieng Plateau, Wonosobo", priceLocal: "Rp 5.000", priceForeign: "Rp 10.000", hours: "06.00–17.00", rating: 4.6, category: "Panorama", tip: "Spot foto terbaik Dieng" },
  { name: "Sumur Jalatunda", location: "Dieng Plateau, Wonosobo", priceLocal: "Rp 10.000", priceForeign: "Rp 20.000", hours: "07.00–17.00", rating: 4.4, category: "Religi & Sejarah", tip: "Lempar batu - legendanya tentang permohonan" },
  { name: "Gunung Prau (Trek)", location: "Dieng / Wonosobo", priceLocal: "Rp 25.000", priceForeign: "Rp 50.000", hours: "Mulai 00.00 (camping)", rating: 4.9, category: "Trekking", tip: "Camping overnight untuk golden sunrise" },
];

const hotels = [
  { name: "Villa Dieng Permai", location: "Dieng Plateau, Wonosobo", price: "Rp 450.000", category: "Resort", rating: 4.7, amenities: ["Sarapan", "WiFi", "Air Panas", "View Gunung"], image: "https://static.promediateknologi.id/crop/0x0:0x0/1200x0/webp/photo/p1/1001/2025/07/30/Villa-di-Dieng-2511235700.jpg?w=400&q=80", availability: true },
  { name: "Rumah Tamu Bu Jono", location: "Dieng Plateau, Wonosobo", price: "Rp 120.000", category: "Homestay", rating: 4.5, amenities: ["Sarapan", "Selimut Tebal", "Teh Panas"], image: "https://i0.wp.com/penginapan.net/wp-content/uploads/losmen-restaurant-bu-jono.jpg?fit=460%2C300&ssl=1?w=400&q=80", availability: true },
  { name: "Hotel Kresna Wonosobo", location: "Wonosobo, Jawa Tengah", price: "Rp 350.000", category: "Hotel", rating: 4.3, amenities: ["AC", "WiFi", "Restoran", "Parkir"], image: "https://cf.bstatic.com/xdata/images/hotel/max1024x768/590121889.jpg?k=d279d320dd30f1a4a870f0c14bfb93b7fc7c5f31c446c2d9827c3b3e44bd342d&o=?w=400&q=80", availability: true },
  { name: "Penginapan HD Dieng Resto", location: "Dieng Plateau, Wonosobo", price: "Rp 150.000", category: "Budget", rating: 4.2, amenities: ["Sarapan", "WiFi", "Teh Purwaceng"], image: "https://phinemo.com/wp-content/uploads/2021/01/EqKvy_WVoAEc9RF-min.jpg?w=400&q=80", availability: false },
  { name: "Dian Hotel Wonosobo", location: "Wonosobo, Jawa Tengah", price: "Rp 250.000", category: "Hotel", rating: 4.1, amenities: ["AC", "WiFi", "Sarapan", "Kamar Mandi Dalam"], image: "https://www.indonesia.travel/contentassets/b1999b9de3e445ad8bfe80a25c3dce24/grand-dian-hotel-guci.jpeg?w=400&q=80", availability: true },
  { name: "Camp Gunung Prau", location: "Jalur Pendakian Prau", price: "Rp 50.000", category: "Camping", rating: 4.8, amenities: ["Area Camping", "Toilet", "Air Bersih"], image: "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgPcgMBL4toOECsSz9MVKfYpWReoJ4War9jEkQM_v_dx0KOsT8RCXc0oi1Ev8b4fChcqt342n11FNaSKwz1A89--MH4t5NnQ7_8pK3pctL22-vmGqw0rD33hKhePzxqfYRgMSmrCSJdVZb_wy6Rj_CYvfS1aUlAqxf9Kf6FwQN9mcSkQFGuFPdd5nnKVw/w400-h221/Screenshot_20220809-110400_WhatsAppBusiness.jpg?w=400&q=80", availability: true },
];

const transports = [
  {
    category: "Menuju Dieng",
    icon: Bus,
    color: "#059669",
    bg: "#d1fae5",
    options: [
      { name: "Bus Efisiensi (Jogja–Wonosobo)", detail: "AC ekonomi & eksekutif", price: "Rp 45.000–80.000", note: "Berangkat dari Terminal Giwangan Yogyakarta" },
      { name: "Elf/Angkot (Wonosobo–Dieng)", detail: "Angkot pedesaan reguler", price: "Rp 15.000–20.000", note: "Dari Terminal Wonosobo, jam 05.00–17.00" },
      { name: "Travel Shuttle Langsung", detail: "Jogja / Semarang / Solo → Dieng", price: "Rp 100.000–150.000", note: "Booking via Traveloka, RedBus, WhatsApp agen" },
    ],
  },
  {
    category: "Transportasi di Dieng",
    icon: Bike,
    color: "#0ea5e9",
    bg: "#dbeafe",
    options: [
      { name: "Sewa Motor", detail: "Matic/Trail untuk medan pegunungan", price: "Rp 75.000–100.000/hari", note: "Bawa SIM & KTP. Helm wajib!" },
      { name: "Sewa Mobil + Driver", detail: "Paket wisata full day Dieng", price: "Rp 400.000–600.000/hari", note: "Termasuk semua destinasi utama Dieng" },
      { name: "Ojek Lokal", detail: "Antar jemput spot wisata", price: "Rp 10.000–25.000/trip", note: "Tersedia di pusat Desa Dieng" },
    ],
  },
  {
    category: "Paket Wisata Dieng",
    icon: Car,
    color: "#7c3aed",
    bg: "#ede9fe",
    options: [
      { name: "Paket Sunrise Sikunir", detail: "Antar jemput + guide lokal", price: "Rp 50.000–100.000/orang", note: "Berangkat 03.00–03.30 dari penginapan" },
      { name: "Paket One Day Trip Dieng", detail: "7–9 destinasi + makan siang", price: "Rp 150.000–250.000/orang", note: "Tersedia dari Wonosobo & Yogyakarta" },
      { name: "Paket Trekking Gunung Prau", detail: "Include porter, tenda & konsumsi", price: "Rp 350.000–600.000/orang", note: "2D1N - berangkat sore, sunrise esok hari" },
    ],
  },
  {
    category: "Tips Transportasi Dieng",
    icon: Ship,
    color: "#d97706",
    bg: "#fef3c7",
    options: [
      { name: "Kondisi Jalan", detail: "Berliku, sempit & terjal", price: "Perhatian ekstra", note: "Hindari berkendara saat kabut tebal & malam hari" },
      { name: "BBM & Bengkel", detail: "Terbatas di Dieng", price: "Isi penuh di Wonosobo", note: "SPBU terdekat ada di Wonosobo kota" },
      { name: "Parkir Wisata", detail: "Area parkir tersedia di tiap destinasi", price: "Rp 2.000–5.000/kendaraan", note: "Patuhi rambu - jalan sempit!" },
    ],
  },
];

const categoryColors: Record<string, { bg: string; color: string }> = {
  Luxury: { bg: "#fef3c7", color: "#92400e" },
  Resort: { bg: "#dbeafe", color: "#1e40af" },
  Boutique: { bg: "#ede9fe", color: "#5b21b6" },
  Budget: { bg: "#d1fae5", color: "#065f46" },
  "Eco Lodge": { bg: "#d1fae5", color: "#065f46" },
};

export default function InfoCenter() {
  const [activeTab, setActiveTab] = useState<Tab>("tiket");
  const [search, setSearch] = useState("");
  const [ticketData, setTicketData] = useState<any[]>(tickets);
  const c = useThemeColors();

  useEffect(() => {
    const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";
    fetch(`${apiUrl}/api/destinations`)
      .then((res) => res.json())
      .then((data) => {
        if (data && data.length > 0) {
          setTicketData(data);
        }
      })
      .catch((err) => console.error("Error fetching destinations:", err));
  }, []);

  const tabs: { id: Tab; label: string; icon: ReactNode }[] = [
    { id: "tiket", label: "Tiket & Retribusi", icon: <Ticket className="w-4 h-4" /> },
    { id: "penginapan", label: "Penginapan", icon: <Hotel className="w-4 h-4" /> },
    { id: "transportasi", label: "Transportasi", icon: <Navigation className="w-4 h-4" /> },
  ];

  const filteredTickets = ticketData.filter(
    (t) =>
      t.name.toLowerCase().includes(search.toLowerCase()) ||
      (t.location && t.location.toLowerCase().includes(search.toLowerCase())) ||
      (t.category && t.category.toLowerCase().includes(search.toLowerCase()))
  );

  const filteredHotels = hotels.filter(
    (h) =>
      h.name.toLowerCase().includes(search.toLowerCase()) ||
      h.location.toLowerCase().includes(search.toLowerCase()) ||
      h.category.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <section className="py-20 px-4" style={{ backgroundColor: c.bgSurface }}>
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <div
            className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-sm font-medium mb-4"
            style={{ backgroundColor: c.infoBg, color: c.infoText }}
          >
            <Tag className="w-3.5 h-3.5" />
            Data Terverifikasi & Terpusat
          </div>
          <h2 className="text-3xl font-bold mb-3" style={{ color: c.textPrimary }}>
            Pusat Informasi Wisata Dieng
          </h2>
          <p className="max-w-xl mx-auto text-sm" style={{ color: c.textSecondary }}>
            Data terpusat dan terverifikasi - harga tiket retribusi resmi, daftar penginapan,
            dan panduan transportasi lengkap menuju & di Dataran Tinggi Dieng.
          </p>
        </div>

        {/* Tabs */}
        <div className="flex flex-col sm:flex-row sm:items-center gap-4 mb-8">
          <div
            className="flex p-1 rounded-2xl gap-1"
            style={{ backgroundColor: c.bgInput }}
          >
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => { setActiveTab(tab.id); setSearch(""); }}
                className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold transition-all"
                style={{
                  backgroundColor: activeTab === tab.id ? c.navBg : "transparent",
                  color: activeTab === tab.id ? "#ffffff" : c.textSecondary,
                  boxShadow: activeTab === tab.id ? "0 2px 8px rgba(0,0,0,0.2)" : "none",
                }}
              >
                {tab.icon}
                {tab.label}
              </button>
            ))}
          </div>

          {/* Search */}
          {activeTab !== "transportasi" && (
            <div
              className="flex items-center gap-2 px-4 py-2.5 rounded-2xl border flex-1 max-w-xs"
              style={{ borderColor: c.border, backgroundColor: c.bgInput }}
            >
              <Search className="w-4 h-4 flex-shrink-0" style={{ color: c.textMuted }} />
              <input
                type="text"
                placeholder={`Cari ${activeTab === "tiket" ? "destinasi atau kategori" : "hotel atau lokasi"}...`}
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="bg-transparent outline-none text-sm flex-1"
                style={{ color: c.textPrimary }}
              />
            </div>
          )}
        </div>

        {/* Tiket Tab */}
        {activeTab === "tiket" && (
          <div className="grid md:grid-cols-2 xl:grid-cols-4 gap-4">
            {filteredTickets.map((ticket) => (
              <div
                key={ticket.name}
                className="rounded-2xl p-5 border shadow-sm hover:shadow-lg transition-all hover:scale-[1.02] cursor-pointer"
                style={{ backgroundColor: c.bgSurface, borderColor: c.border }}
              >
                <div className="flex items-start justify-between mb-3">
                  <span
                    className="px-2.5 py-1 rounded-full text-xs font-semibold"
                    style={{ backgroundColor: c.bgTint, color: c.successText }}
                  >
                    {ticket.category}
                  </span>
                  <div className="flex items-center gap-1">
                    <Star className="w-3.5 h-3.5 text-amber-400 fill-amber-400" />
                    <span className="text-xs font-semibold" style={{ color: "#92400e" }}>
                      {ticket.rating}
                    </span>
                  </div>
                </div>

                <h3 className="font-bold text-sm mb-1" style={{ color: c.textPrimary }}>{ticket.name}</h3>

                <div className="flex items-center gap-1 mb-3">
                  <MapPin className="w-3 h-3" style={{ color: c.textMuted }} />
                  <span className="text-xs" style={{ color: c.textSecondary }}>{ticket.location}</span>
                </div>

                <div className="space-y-2 mb-4">
                  <div className="flex justify-between items-center">
                    <span className="text-xs" style={{ color: c.textMuted }}>Lokal</span>
                    <span className="text-sm font-bold" style={{ color: c.primary }}>{ticket.priceLocal}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-xs" style={{ color: c.textMuted }}>Asing</span>
                    <span className="text-sm font-bold" style={{ color: "#d97706" }}>{ticket.priceForeign}</span>
                  </div>
                </div>

                <div className="border-t pt-3 space-y-1.5" style={{ borderColor: c.borderLight }}>
                  <div className="flex items-center gap-1.5">
                    <Clock className="w-3 h-3" style={{ color: c.textMuted }} />
                    <span className="text-xs" style={{ color: c.textSecondary }}>{ticket.hours}</span>
                  </div>
                  <div
                    className="text-xs px-2 py-1 rounded-lg"
                    style={{ backgroundColor: c.warningBg, color: "#92400e" }}
                  >
                    💡 {ticket.tip}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Penginapan Tab */}
        {activeTab === "penginapan" && (
          <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-5">
            {filteredHotels.map((hotel) => {
              const catColor = categoryColors[hotel.category] || { bg: c.bgInput, color: c.textPrimary };
              return (
                <div
                  key={hotel.name}
                  className="rounded-3xl border overflow-hidden shadow-sm hover:shadow-xl transition-all hover:scale-[1.02]"
                  style={{ backgroundColor: c.bgSurface, borderColor: c.border }}
                >
                  <div
                    className="h-44 relative bg-gray-100"
                    style={{
                      backgroundImage: `url('${hotel.image}')`,
                      backgroundSize: "cover",
                      backgroundPosition: "center",
                    }}
                  >
                    <div className="absolute inset-0" style={{ background: "linear-gradient(to top, rgba(0,0,0,0.4), transparent)" }} />
                    <div className="absolute top-3 left-3">
                      <span
                        className="px-2.5 py-1 rounded-full text-xs font-bold"
                        style={{ backgroundColor: catColor.bg, color: catColor.color }}
                      >
                        {hotel.category}
                      </span>
                    </div>
                    {!hotel.availability && (
                      <div className="absolute top-3 right-3">
                        <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-red-100 text-red-600">
                          Penuh
                        </span>
                      </div>
                    )}
                    <div className="absolute bottom-3 left-3 flex items-center gap-1">
                      <Star className="w-3.5 h-3.5 text-amber-400 fill-amber-400" />
                      <span className="text-white text-sm font-bold">{hotel.rating}</span>
                    </div>
                  </div>

                  <div className="p-4">
                    <h3 className="font-bold text-base mb-1" style={{ color: c.textPrimary }}>{hotel.name}</h3>
                    <div className="flex items-center gap-1 mb-3">
                      <MapPin className="w-3 h-3" style={{ color: c.textMuted }} />
                      <span className="text-xs" style={{ color: c.textSecondary }}>{hotel.location}</span>
                    </div>

                    <div className="flex flex-wrap gap-1.5 mb-4">
                      {hotel.amenities.map((a) => (
                        <span
                          key={a}
                          className="px-2 py-0.5 rounded-lg text-xs"
                          style={{ backgroundColor: c.bgTint, color: c.successText }}
                        >
                          {a}
                        </span>
                      ))}
                    </div>

                    <div className="flex items-center justify-between">
                      <div>
                        <span className="text-xs" style={{ color: c.textMuted }}>Mulai dari</span>
                        <div className="font-bold text-base" style={{ color: c.textPrimary }}>{hotel.price}</div>
                        <span className="text-xs" style={{ color: c.textMuted }}>/malam</span>
                      </div>

                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Transportasi Tab */}
        {activeTab === "transportasi" && (
          <div className="grid md:grid-cols-2 gap-6">
            {transports.map((category) => {
              const Icon = category.icon;
              return (
                <div
                  key={category.category}
                  className="rounded-3xl border shadow-sm overflow-hidden"
                  style={{ backgroundColor: c.bgSurface, borderColor: c.border }}
                >
                  <div
                    className="px-5 py-4 flex items-center gap-3 border-b"
                    style={{ backgroundColor: category.bg, borderColor: c.border }}
                  >
                    <div
                      className="w-10 h-10 rounded-xl flex items-center justify-center"
                      style={{ backgroundColor: category.color }}
                    >
                      <Icon className="w-5 h-5 text-white" />
                    </div>
                    <h3 className="font-bold text-base" style={{ color: "#1f2937" }}>
                      {category.category}
                    </h3>
                  </div>
                  <div className="divide-y" style={{ borderColor: c.borderLight }}>
                    {category.options.map((opt) => (
                      <div key={opt.name} className="px-5 py-4 transition-colors">
                        <div className="flex items-start justify-between gap-4">
                          <div className="flex-1">
                            <div className="font-semibold text-sm mb-0.5" style={{ color: c.textPrimary }}>
                              {opt.name}
                            </div>
                            <div className="text-xs mb-1" style={{ color: c.textSecondary }}>{opt.detail}</div>
                            <div className="text-xs" style={{ color: c.textMuted }}>ℹ️ {opt.note}</div>
                          </div>
                          <div className="text-right flex-shrink-0">
                            <div className="font-bold text-sm" style={{ color: category.color }}>{opt.price}</div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Footer Note */}
        <div
          className="mt-10 p-4 rounded-2xl text-center text-sm border"
          style={{ backgroundColor: c.bgTint, borderColor: c.successBorder, color: c.successText }}
        >
          ✅ Data diverifikasi dari Dinas Pariwisata Wonosobo & pengelola wisata Dieng Plateau. Harga dapat berubah sewaktu-waktu.
          Terakhir diperbarui: 31 Mei 2026.
        </div>
      </div>
    </section>
  );
}
