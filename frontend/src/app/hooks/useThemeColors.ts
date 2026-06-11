import { useTheme } from "next-themes";

export function useThemeColors() {
  const { resolvedTheme } = useTheme();
  const d = resolvedTheme === "dark";

  return {
    d,
    // ── Navigation ──────────────────────────────────────────
    navBg: d ? "#0f2726" : "#1b3f3e",
    navBgScrolled: d ? "#080f0f" : "#0d2a29",
    navMobileBg: d ? "#0f2422" : "#1f4f4c",
    navMobileBorder: d ? "#1e3735" : "#2a5e5b",
    navText: d ? "#89c7c1" : "#9dd4cf",
    navActiveIndicator: "#4fd1c5",

    // ── Section backgrounds ───────────────────────────────────
    bgBase: d ? "#0d1e1c" : "#f4fffe",
    bgAlt: d ? "#111f1e" : "#edfafa",
    bgSurface: d ? "#152d2b" : "#ffffff",
    bgCard: d ? "#1a3230" : "#ffffff",
    bgTint: d ? "#1c3836" : "#edfafa",
    bgInput: d ? "#1c3836" : "#f0fafa",
    bgInputBorder: d ? "#2a4540" : "#c8e0de",

    // ── Brand ────────────────────────────────────────────────
    primary: "#4fd1c5",
    primaryHover: "#38b2ac",
    primaryDark: d ? "#3dbdb2" : "#2a8a84",
    primaryLight: d ? "#81e6d9" : "#a3e8e3",
    primaryGlow: "rgba(79,209,197,0.22)",
    secondary: "#a3bfbc",
    secondaryDark: d ? "#a3bfbc" : "#7a9e9a",

    // ── Text ──────────────────────────────────────────────────
    textPrimary: d ? "#dff5f2" : "#1a3737",
    textSecondary: d ? "#a3bfbc" : "#4a7070",
    textMuted: d ? "#6e9490" : "#7a9e9a",
    textOnDark: d ? "#dff5f2" : "#ffffff",
    textOnPrimary: "#ffffff",

    // ── Borders ───────────────────────────────────────────────
    border: d ? "#2a4540" : "#c0ddd9",
    borderLight: d ? "#1e3533" : "#d8eeeb",

    // ── CTA / Accent ──────────────────────────────────────────
    accent: "#f6ad55",
    accentDark: "#e8931e",
    accentGlow: "rgba(246,173,85,0.38)",

    // ── Gradients ─────────────────────────────────────────────
    gradientPrimary: "linear-gradient(135deg, #4fd1c5, #38b2ac)",
    gradientAccent: "linear-gradient(135deg, #f6ad55, #e8931e)",
    gradientNav: d
      ? "linear-gradient(135deg, #0f2726, #1a4240)"
      : "linear-gradient(135deg, #1b3f3e, #2a7a74)",
    gradientNavScrolled: d ? "#080f0f" : "#0d2a29",
    gradientHeroOverlay: d
      ? "linear-gradient(135deg, rgba(8,18,18,0.95) 0%, rgba(15,35,33,0.87) 40%, rgba(5,15,14,0.68) 100%)"
      : "linear-gradient(135deg, rgba(20,48,47,0.92) 0%, rgba(26,60,58,0.78) 40%, rgba(10,28,26,0.60) 100%)",
    gradientWeatherCard: d
      ? "linear-gradient(135deg, #1a4240, #1c3f60)"
      : "linear-gradient(135deg, #2a8a84, #2b6cb0)",
    gradientChatHeader: d
      ? "linear-gradient(135deg, #0f2726, #1a4240)"
      : "linear-gradient(135deg, #1b3f3e, #2a8a84)",
    gradientItinerary: d
      ? "linear-gradient(135deg, #0f2726, #1a4240)"
      : "linear-gradient(135deg, #1b3f3e, #2a8a84)",
    gradientFooter: d ? "#091817" : "#091817",
    gradientCtaBanner: d
      ? "linear-gradient(135deg, #1a4240, #2a7a74, #1c6060)"
      : "linear-gradient(135deg, #1b3f3e, #2a8a84, #1a6a6a)",

    // ── Status: Danger ────────────────────────────────────────
    dangerBg: d ? "#2d1010" : "#fef2f2",
    dangerBorder: d ? "#5c2020" : "#fecaca",
    dangerBadge: "#ef4444",
    dangerText: d ? "#fca5a5" : "#dc2626",

    // ── Status: Warning ───────────────────────────────────────
    warningBg: d ? "#2d2010" : "#fffbeb",
    warningBorder: d ? "#5c4010" : "#fde68a",
    warningBadge: "#f59e0b",
    warningText: d ? "#fcd34d" : "#d97706",

    // ── Status: Success ───────────────────────────────────────
    successBg: d ? "#0f2e2c" : "#edfafa",
    successBorder: d ? "#2a5c58" : "#b2e8e5",
    successBadge: "#4fd1c5",
    successText: d ? "#4fd1c5" : "#2a8a84",

    // ── Status: Info ──────────────────────────────────────────
    infoBg: d ? "#0f1e30" : "#eff6ff",
    infoBorder: d ? "#1e3c58" : "#bfdbfe",
    infoBadge: "#3b82f6",
    infoText: d ? "#93c5fd" : "#2563eb",
  };
}
