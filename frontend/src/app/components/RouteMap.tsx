import { useEffect, Fragment } from "react";
import { MapContainer, TileLayer, Polyline, Marker, Popup, useMap } from "react-leaflet";
import L from "leaflet";
import { useThemeColors } from "../hooks/useThemeColors";

type RouteStatus = "aman" | "waspada" | "bahaya";

const DIENG: [number, number] = [-7.2091, 109.9131];

const routeData = [
  {
    id: "wonosobo",
    label: "Wonosobo → Dieng",
    status: "waspada" as RouteStatus,
    color: "#f59e0b",
    start: [-7.3601, 109.9040] as [number, number],
    startLabel: "Terminal Wonosobo",
    path: [
      [-7.3601, 109.9040],
      [-7.3215, 109.9062],
      [-7.2883, 109.9087],
      [-7.2582, 109.9094],
      [-7.2319, 109.9092],
      [-7.2091, 109.9131],
    ] as [number, number][],
    incidents: [
      { pos: [-7.2950, 109.9080] as [number, number], label: "Tikungan Tajam km 8", level: "waspada" as RouteStatus },
      { pos: [-7.2430, 109.9090] as [number, number], label: "Kabut Tebal km 20–26", level: "waspada" as RouteStatus },
    ],
    distance: "26 km",
    time: "~70 mnt",
    blocked: false,
  },
  {
    id: "banjarnegara",
    label: "Banjarnegara → Dieng",
    status: "aman" as RouteStatus,
    color: "#10b981",
    start: [-7.3884, 109.6963] as [number, number],
    startLabel: "Kota Banjarnegara",
    path: [
      [-7.3884, 109.6963],
      [-7.3502, 109.7482],
      [-7.2811, 109.8185],
      [-7.2601, 109.8756],
      [-7.2350, 109.9020],
      [-7.2091, 109.9131],
    ] as [number, number][],
    incidents: [],
    distance: "44 km",
    time: "~80 mnt",
    blocked: false,
  },
  {
    id: "temanggung",
    label: "Temanggung → Dieng",
    status: "bahaya" as RouteStatus,
    color: "#ef4444",
    start: [-7.3176, 110.1703] as [number, number],
    startLabel: "Parakan, Temanggung",
    path: [
      [-7.3176, 110.1703],
      [-7.2912, 110.1241],
      [-7.2651, 110.0652],
      [-7.2319, 110.0052],
    ] as [number, number][],
    incidents: [
      { pos: [-7.2500, 110.0312] as [number, number], label: "Jalan Rusak km 15–22", level: "waspada" as RouteStatus },
      { pos: [-7.2319, 110.0052] as [number, number], label: "LONGSOR km 18 - JALUR DITUTUP", level: "bahaya" as RouteStatus },
    ],
    distance: "58 km",
    time: "DITUTUP",
    blocked: true,
  },
];

const statusColors: Record<RouteStatus, string> = {
  aman: "#10b981",
  waspada: "#f59e0b",
  bahaya: "#ef4444",
};

const statusLabels: Record<RouteStatus, string> = {
  aman: "AMAN",
  waspada: "WASPADA",
  bahaya: "BAHAYA",
};

function makeDivIcon(color: string, size = 14): L.DivIcon {
  return L.divIcon({
    className: "",
    html: `<div style="width:${size}px;height:${size}px;border-radius:50%;background:${color};border:2.5px solid white;box-shadow:0 2px 6px rgba(0,0,0,0.35);"></div>`,
    iconSize: [size, size],
    iconAnchor: [size / 2, size / 2],
  });
}

function makeIncidentIcon(level: RouteStatus): L.DivIcon {
  const color = statusColors[level];
  return L.divIcon({
    className: "",
    html: `<div style="width:24px;height:24px;border-radius:50%;background:${color};border:2.5px solid white;display:flex;align-items:center;justify-content:center;box-shadow:0 2px 8px rgba(0,0,0,0.4);font-size:12px;line-height:24px;text-align:center;">⚠</div>`,
    iconSize: [24, 24],
    iconAnchor: [12, 12],
  });
}

function makeDestIcon(): L.DivIcon {
  return L.divIcon({
    className: "",
    html: `<div style="width:36px;height:36px;border-radius:50%;background:linear-gradient(135deg,#4fd1c5,#38b2ac);border:3px solid white;display:flex;align-items:center;justify-content:center;box-shadow:0 3px 12px rgba(79,209,197,0.55);font-size:18px;line-height:30px;text-align:center;">🏔</div>`,
    iconSize: [36, 36],
    iconAnchor: [18, 18],
  });
}

function FitBounds() {
  const map = useMap();
  useEffect(() => {
    const allPoints: [number, number][] = [
      DIENG,
      ...routeData.flatMap((r) => r.path),
    ];
    const bounds = L.latLngBounds(allPoints);
    map.fitBounds(bounds, { padding: [40, 40] });
  }, [map]);
  return null;
}

interface Props {
  activeRouteId: string | null;
  onRouteClick: (id: string) => void;
  height?: number;
}

export default function RouteMap({ activeRouteId, onRouteClick, height = 400 }: Props) {
  const c = useThemeColors();

  const tileUrl = c.d
    ? "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
    : "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png";

  return (
    <div
      className="overflow-hidden"
      style={{ height: `${height}px`, width: "100%" }}
    >
      {/* Legend overlay */}
      <div style={{ position: "relative", height: "100%" }}>
        <MapContainer
          center={DIENG}
          zoom={11}
          style={{ height: "100%", width: "100%" }}
          scrollWheelZoom={false}
        >
          <TileLayer
            url={tileUrl}
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/">CARTO</a>'
          />
          <FitBounds />

          {/* Dieng destination */}
          <Marker position={DIENG} icon={makeDestIcon()}>
            <Popup>
              <strong>🏔️ Dieng Plateau</strong><br />
              Dataran Tinggi Dieng, Wonosobo<br />
              <small>Ketinggian ±2.093 mdpl</small>
            </Popup>
          </Marker>

          {routeData.map((route) => {
            const isActive = activeRouteId === route.id;
            return (
              <Fragment key={route.id}>
                {/* Route line */}
                <Polyline
                  key={`line-${route.id}`}
                  positions={route.path}
                  pathOptions={{
                    color: route.color,
                    weight: isActive ? 7 : 4,
                    opacity: route.blocked && !isActive ? 0.45 : 0.9,
                    dashArray: route.blocked ? "10 7" : undefined,
                  }}
                  eventHandlers={{ click: () => onRouteClick(route.id) }}
                />

                {/* Start marker */}
                <Marker
                  key={`start-${route.id}`}
                  position={route.start}
                  icon={makeDivIcon(route.color, 16)}
                >
                  <Popup>
                    <strong>{route.startLabel}</strong><br />
                    <span
                      style={{
                        display: "inline-block",
                        padding: "1px 6px",
                        borderRadius: "9999px",
                        backgroundColor: route.color,
                        color: "#fff",
                        fontSize: "10px",
                        fontWeight: 700,
                        marginTop: "3px",
                        marginBottom: "3px",
                      }}
                    >
                      {statusLabels[route.status]}
                    </span>
                    <br />
                    <small>{route.distance} · {route.time}</small>
                  </Popup>
                </Marker>

                {/* Incident markers */}
                {route.incidents.map((inc, i) => (
                  <Marker
                    key={`inc-${route.id}-${i}`}
                    position={inc.pos}
                    icon={makeIncidentIcon(inc.level)}
                  >
                    <Popup>
                      <span
                        style={{
                          display: "inline-block",
                          padding: "1px 6px",
                          borderRadius: "9999px",
                          backgroundColor: statusColors[inc.level],
                          color: "#fff",
                          fontSize: "10px",
                          fontWeight: 700,
                          marginBottom: "3px",
                        }}
                      >
                        {statusLabels[inc.level]}
                      </span>
                      <br />
                      <strong style={{ fontSize: "12px" }}>{inc.label}</strong><br />
                      <small style={{ color: "#888" }}>{route.label}</small>
                    </Popup>
                  </Marker>
                ))}
              </Fragment>
            );
          })}
        </MapContainer>

        {/* Map legend - absolute overlay */}
        <div
          style={{
            position: "absolute",
            bottom: "16px",
            left: "16px",
            zIndex: 1000,
            backgroundColor: c.bgSurface,
            border: `1px solid ${c.border}`,
            borderRadius: "12px",
            padding: "10px 14px",
            boxShadow: "0 4px 16px rgba(0,0,0,0.15)",
            pointerEvents: "none",
          }}
        >
          <div style={{ fontSize: "10px", fontWeight: 700, color: c.textMuted, marginBottom: "6px", letterSpacing: "0.05em" }}>
            LEGENDA
          </div>
          {[
            { color: "#10b981", label: "Jalur Aman" },
            { color: "#f59e0b", label: "Jalur Waspada" },
            { color: "#ef4444", label: "Jalur Bahaya / Ditutup", dash: true },
          ].map((item) => (
            <div key={item.label} style={{ display: "flex", alignItems: "center", gap: "6px", marginBottom: "4px" }}>
              <div style={{
                width: "24px",
                height: "4px",
                borderRadius: "2px",
                backgroundColor: item.color,
                opacity: item.dash ? 0.6 : 1,
                backgroundImage: item.dash ? `repeating-linear-gradient(90deg, ${item.color} 0, ${item.color} 6px, transparent 6px, transparent 10px)` : undefined,
                backgroundSize: "10px 4px",
              }} />
              <span style={{ fontSize: "11px", color: c.textPrimary }}>{item.label}</span>
            </div>
          ))}
          <div style={{ display: "flex", alignItems: "center", gap: "6px", marginTop: "2px" }}>
            <div style={{ width: "16px", height: "16px", borderRadius: "50%", backgroundColor: "#f59e0b", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "9px" }}>⚠</div>
            <span style={{ fontSize: "11px", color: c.textPrimary }}>Titik Insiden</span>
          </div>
        </div>

        {/* Tip overlay top-right */}
        <div
          style={{
            position: "absolute",
            top: "12px",
            right: "50px",
            zIndex: 1000,
            backgroundColor: c.bgSurface,
            border: `1px solid ${c.border}`,
            borderRadius: "8px",
            padding: "5px 10px",
            boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
            pointerEvents: "none",
          }}
        >
          <span style={{ fontSize: "11px", color: c.textSecondary }}>
            Klik jalur untuk memilih rute
          </span>
        </div>
      </div>
    </div>
  );
}
