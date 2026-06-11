import { useState, useEffect, useRef } from "react";
import { Menu, X, MapPin, Bell, Sun, Moon } from "lucide-react";
import { useTheme } from "next-themes";
import { useThemeColors } from "../hooks/useThemeColors";
import NotificationPanel from "./NotificationPanel";

const navLinks = [
  { id: "beranda", label: "Beranda" },
  { id: "cuaca", label: "Cuaca" },
  { id: "rute", label: "Rute" },
  { id: "asisten", label: "DITA" },
  { id: "itinerary", label: "Itinerary" },
  { id: "info", label: "Pusat Informasi" },
];

const UNREAD_INIT = 4;

export default function Navbar() {
  const [menuOpen, setMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const [active, setActive] = useState(window.location.pathname === "/" ? "beranda" : "");
  const [notifOpen, setNotifOpen] = useState(false);
  const [unreadCount, setUnreadCount] = useState(UNREAD_INIT);
  const notifRef = useRef<HTMLDivElement>(null);
  const { theme, setTheme } = useTheme();
  const c = useThemeColors();

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
      if (window.location.pathname !== "/") return;
      
      for (const { id } of [...navLinks].reverse()) {
        const el = document.getElementById(id);
        if (el && window.scrollY >= el.offsetTop - 100) {
          setActive(id);
          break;
        }
      }
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const scrollTo = (id: string) => {
    if (window.location.pathname !== "/") {
      window.location.href = "/#" + id;
      return;
    }
    document.getElementById(id)?.scrollIntoView({ behavior: "smooth" });
    setMenuOpen(false);
    setActive(id);
  };

  const handleNotifOpen = () => {
    setNotifOpen((prev) => {
      if (!prev) setUnreadCount(0);
      return !prev;
    });
  };

  const toggleTheme = () => setTheme(theme === "dark" ? "light" : "dark");

  return (
    <nav
      className="fixed top-0 left-0 right-0 z-[9999] transition-all duration-300"
      style={{
        backgroundColor: scrolled ? c.navBgScrolled : c.navBg,
        boxShadow: scrolled ? "0 4px 30px rgba(0,0,0,0.3)" : "none",
      }}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <button onClick={() => scrollTo("beranda")} className="flex items-center gap-2.5 group flex-shrink-0">
            <div
              className="w-9 h-9 rounded-xl flex items-center justify-center shadow-md transition-transform group-hover:scale-105 text-lg"
              style={{ background: c.gradientPrimary }}
            >
              🏔️
            </div>
            <div className="text-left">
              <div className="text-white font-bold text-base leading-tight">Dihyang</div>
              <div className="text-[10px] leading-tight" style={{ color: c.navText }}>
                Dataran Tinggi Dieng
              </div>
            </div>
          </button>

          {/* Desktop Nav */}
          <div className="hidden lg:flex items-center gap-0.5">
            {navLinks.map((link) => (
              <button
                key={link.id}
                onClick={() => scrollTo(link.id)}
                className="relative px-3 py-2 rounded-lg text-sm transition-all duration-200 font-medium"
                style={{
                  color: active === link.id ? "#ffffff" : c.navText,
                  backgroundColor: active === link.id ? "rgba(255,255,255,0.12)" : "transparent",
                }}
              >
                {link.label}
                {active === link.id && (
                  <span
                    className="absolute bottom-1 left-1/2 -translate-x-1/2 w-1 h-1 rounded-full"
                    style={{ backgroundColor: c.primary }}
                  />
                )}
              </button>
            ))}
          </div>

          {/* Actions */}
          <div className="flex items-center gap-2">
            {/* Location */}
            <div className="hidden md:flex items-center gap-1.5 text-sm" style={{ color: c.navText }}>
              <MapPin className="w-3.5 h-3.5" />
              <span>Dieng, Wonosobo</span>
            </div>

            {/* Theme Toggle */}
            <button
              onClick={toggleTheme}
              className="p-2 rounded-xl transition-all hover:bg-white/10"
              style={{ color: c.navText }}
              aria-label="Toggle tema"
            >
              {theme === "dark" ? <Sun className="w-[18px] h-[18px]" /> : <Moon className="w-[18px] h-[18px]" />}
            </button>

            {/* Notification Bell */}
            <div className="relative" ref={notifRef}>
              <button
                onClick={handleNotifOpen}
                className="relative p-2 rounded-xl transition-all hover:bg-white/10"
                style={{ color: c.navText }}
                aria-label="Notifikasi"
              >
                <Bell className="w-5 h-5" />
                {unreadCount > 0 && (
                  <span
                    className="absolute -top-0.5 -right-0.5 w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold text-white border-2 animate-pulse"
                    style={{ backgroundColor: "#ef4444", borderColor: scrolled ? c.navBgScrolled : c.navBg }}
                  >
                    {unreadCount}
                  </span>
                )}
              </button>

              <div className="relative">
                <NotificationPanel
                  isOpen={notifOpen}
                  onClose={() => setNotifOpen(false)}
                />
              </div>
            </div>

            {/* CTA */}
            <button
              onClick={() => scrollTo("itinerary")}
              className="hidden md:block px-4 py-2 rounded-full text-sm font-semibold text-white shadow-lg transition-all duration-200 hover:scale-105 whitespace-nowrap flex-shrink-0"
              style={{
                background: c.gradientAccent,
                boxShadow: "0 4px 15px rgba(246,173,85,0.35)",
              }}
            >
              Trip Plan
            </button>

            {/* Mobile Toggle */}
            <button
              className="lg:hidden p-2 rounded-lg"
              style={{ color: c.navText }}
              onClick={() => setMenuOpen(!menuOpen)}
            >
              {menuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      {menuOpen && (
        <div
          className="lg:hidden px-4 pb-4 border-t"
          style={{ backgroundColor: c.navMobileBg, borderColor: c.navMobileBorder }}
        >
          <div className="space-y-1 pt-3">
            {navLinks.map((link) => (
              <button
                key={link.id}
                onClick={() => scrollTo(link.id)}
                className="block w-full text-left px-3 py-2.5 rounded-lg text-sm font-medium"
                style={{
                  color: active === link.id ? "#ffffff" : c.navText,
                  backgroundColor: active === link.id ? "rgba(255,255,255,0.1)" : "transparent",
                }}
              >
                {link.label}
              </button>
            ))}
            <button
              onClick={() => scrollTo("itinerary")}
              className="w-full mt-3 py-2.5 rounded-full text-sm font-semibold text-white"
              style={{ background: c.gradientAccent }}
            >
              Trip Plan
            </button>
          </div>
        </div>
      )}
    </nav>
  );
}
