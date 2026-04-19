"""
utils/map_builder.py
Generates a self-contained Leaflet.js HTML map with hover-activated popups.
"""

import json
from typing import Optional


# Map tile layer URLs
TILE_LAYERS = {
    "Satellite (ESRI)": {
        "url": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        "attr": "Tiles &copy; Esri",
        "maxZoom": 18,
    },
    "Terrain (OpenTopo)": {
        "url": "https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
        "attr": "Map data: &copy; OpenStreetMap contributors, SRTM | Map style: &copy; OpenTopoMap",
        "maxZoom": 17,
    },
    "Dark (CartoDB)": {
        "url": "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
        "attr": "&copy; OpenStreetMap contributors &copy; CARTO",
        "maxZoom": 19,
    },
    "Standard (OSM)": {
        "url": "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        "attr": "&copy; OpenStreetMap contributors",
        "maxZoom": 19,
    },
}

# Color config per intel type
TYPE_CONFIG = {
    "OSINT":  {"color": "#39ff14", "ring": "#1a7a0a", "label": "OSINT"},
    "HUMINT": {"color": "#39aaff", "ring": "#0a4a7a", "label": "HUMINT"},
    "IMINT":  {"color": "#ff6b39", "ring": "#7a2a0a", "label": "IMINT"},
}


def _safe_json(obj) -> str:
    """Serialize to JSON safely."""
    return json.dumps(obj, ensure_ascii=False)


def build_map_html(
    markers: list[dict],
    map_style: str = "Satellite (ESRI)",
    zoom: int = 11,
) -> str:
    """
    Build a complete Leaflet.js HTML page with interactive markers and hover popups.

    Args:
        markers:   List of marker dicts with keys: type, name, lat, lon, meta, img_b64
        map_style: Tile layer name from TILE_LAYERS dict
        zoom:      Default zoom level

    Returns:
        Full HTML string ready to be embedded via st.components.v1.html()
    """
    tile = TILE_LAYERS.get(map_style, TILE_LAYERS["Satellite (ESRI)"])

    # Calculate map center from average lat/lon
    if markers:
        center_lat = sum(m["lat"] for m in markers) / len(markers)
        center_lon = sum(m["lon"] for m in markers) / len(markers)
    else:
        center_lat, center_lon = 20.5937, 78.9629  # Default: India center

    # Serialize markers to JS-safe JSON
    markers_json = _safe_json(markers)

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  html, body {{ width: 100%; height: 100%; background: #0a0f0d; }}
  #map {{ width: 100%; height: 100vh; }}

  /* Popup overlay */
  #intel-popup {{
    display: none;
    position: fixed;
    z-index: 9999;
    background: #0d1a13;
    border: 1px solid #39ff14;
    border-radius: 8px;
    padding: 14px 16px;
    min-width: 240px;
    max-width: 320px;
    box-shadow: 0 0 24px rgba(57,255,20,0.25);
    pointer-events: none;
    font-family: 'Courier New', monospace;
    color: #c8d6c8;
    font-size: 12px;
    line-height: 1.6;
  }}
  #intel-popup .popup-header {{
    font-size: 11px;
    letter-spacing: 2px;
    font-weight: bold;
    margin-bottom: 8px;
    padding-bottom: 6px;
    border-bottom: 1px solid #1a4a2a;
  }}
  #intel-popup .popup-name {{
    font-size: 13px;
    color: #ffffff;
    font-weight: bold;
    margin-bottom: 6px;
  }}
  #intel-popup .popup-meta {{ color: #8fbc8f; }}
  #intel-popup .popup-meta span {{ color: #c8d6c8; }}
  #intel-popup .popup-img {{
    width: 100%;
    max-height: 160px;
    object-fit: cover;
    border-radius: 4px;
    margin-top: 8px;
    border: 1px solid #2a5a2a;
  }}
  #intel-popup .badge {{
    display: inline-block;
    padding: 2px 8px;
    border-radius: 3px;
    font-size: 10px;
    letter-spacing: 1px;
    font-weight: bold;
    margin-bottom: 8px;
  }}
  .badge-OSINT  {{ background:#1a3a1a; color:#39ff14; border:1px solid #2a6a2a; }}
  .badge-HUMINT {{ background:#1a2a3a; color:#39aaff; border:1px solid #2a5a7a; }}
  .badge-IMINT  {{ background:#3a1a1a; color:#ff6b39; border:1px solid #7a2a2a; }}

  /* Custom marker pulse */
  .pulse-ring {{
    border-radius: 50%;
    animation: pulse 2s ease-out infinite;
  }}
  @keyframes pulse {{
    0%   {{ opacity: 1; transform: scale(1); }}
    100% {{ opacity: 0; transform: scale(2.5); }}
  }}

  /* Leaflet dark overrides */
  .leaflet-container {{ background: #0a0f0d; }}
  .leaflet-control-zoom a {{ background:#0d2b1a; color:#39ff14; border-color:#2a6a2a; }}
  .leaflet-control-attribution {{ background: rgba(10,15,13,0.8); color:#4a8a4a; }}
</style>
</head>
<body>
<div id="map"></div>
<div id="intel-popup"></div>

<script>
// ── Data ────────────────────────────────────────────────────────────────────
const MARKERS = {markers_json};

const TYPE_CONFIG = {{
  "OSINT":  {{ color: "#39ff14", ring: "rgba(57,255,20,0.3)" }},
  "HUMINT": {{ color: "#39aaff", ring: "rgba(57,170,255,0.3)" }},
  "IMINT":  {{ color: "#ff6b39", ring: "rgba(255,107,57,0.3)" }},
}};

// ── Map Init ────────────────────────────────────────────────────────────────
const map = L.map('map', {{
  center: [{center_lat}, {center_lon}],
  zoom: {zoom},
  zoomControl: true,
  preferCanvas: true,
}});

L.tileLayer('{tile["url"]}', {{
  attribution: '{tile["attr"]}',
  maxZoom: {tile["maxZoom"]},
  subdomains: 'abcd',
}}).addTo(map);

// ── Popup Element ───────────────────────────────────────────────────────────
const popup = document.getElementById('intel-popup');
let popupTimeout;

function showPopup(e, marker) {{
  const cfg  = TYPE_CONFIG[marker.type] || TYPE_CONFIG['OSINT'];
  const meta = marker.meta || {{}};

  let metaHtml = '';
  for (const [k, v] of Object.entries(meta)) {{
    metaHtml += `<div class="popup-meta">${{k}}: <span>${{v}}</span></div>`;
  }}

  let imgHtml = '';
  if (marker.img_b64) {{
    imgHtml = `<img class="popup-img" src="data:image/jpeg;base64,${{marker.img_b64}}" alt="IMINT"/>`;
  }}

  popup.innerHTML = `
    <div class="popup-header">◈ INTEL NODE REPORT</div>
    <span class="badge badge-${{marker.type}}">${{marker.type}}</span>
    <div class="popup-name">${{marker.name}}</div>
    ${{metaHtml}}
    <div class="popup-meta">Coords: <span>${{marker.lat.toFixed(4)}}°N, ${{marker.lon.toFixed(4)}}°E</span></div>
    ${{imgHtml}}
  `;

  // Position near cursor but keep in bounds
  const x = e.originalEvent.clientX;
  const y = e.originalEvent.clientY;
  const pw = 320, ph = 260;
  const vw = window.innerWidth, vh = window.innerHeight;

  let left = x + 16;
  let top  = y + 16;
  if (left + pw > vw) left = x - pw - 8;
  if (top  + ph > vh) top  = y - ph - 8;

  popup.style.left    = left + 'px';
  popup.style.top     = top  + 'px';
  popup.style.display = 'block';
}}

function hidePopup() {{
  clearTimeout(popupTimeout);
  popupTimeout = setTimeout(() => {{ popup.style.display = 'none'; }}, 120);
}}

// ── Plot Markers ────────────────────────────────────────────────────────────
MARKERS.forEach(function(m) {{
  const cfg = TYPE_CONFIG[m.type] || TYPE_CONFIG['OSINT'];

  // Custom SVG icon — glowing dot with type color
  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 28 28">
      <circle cx="14" cy="14" r="10" fill="${{cfg.ring}}" opacity="0.5"/>
      <circle cx="14" cy="14" r="6"  fill="${{cfg.color}}" opacity="0.9"/>
      <circle cx="14" cy="14" r="3"  fill="#ffffff"        opacity="0.95"/>
    </svg>`;

  const icon = L.divIcon({{
    html: svg,
    className: '',
    iconSize:   [28, 28],
    iconAnchor: [14, 14],
  }});

  const leafletMarker = L.marker([m.lat, m.lon], {{ icon }}).addTo(map);

  // Hover events
  leafletMarker.on('mouseover', function(e) {{ showPopup(e, m); }});
  leafletMarker.on('mousemove', function(e) {{ showPopup(e, m); }});
  leafletMarker.on('mouseout',  function()  {{ hidePopup();      }});

  // Click — keep popup open
  leafletMarker.on('click', function(e) {{
    clearTimeout(popupTimeout);
    showPopup(e, m);
  }});
}});

// ── Fit Map to Markers ──────────────────────────────────────────────────────
if (MARKERS.length > 1) {{
  const latLngs = MARKERS.map(m => [m.lat, m.lon]);
  map.fitBounds(latLngs, {{ padding: [40, 40] }});
}}
</script>
</body>
</html>"""

    return html
