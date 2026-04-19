"""
CYBERJOAR AI - PS1: Multi-Source Intelligence Fusion Dashboard
Author: Sujal Kumar Nayak
"""

import streamlit as st
import pandas as pd
import json
import base64
import logging
from pathlib import Path
from utils.data_loader import load_osint_csv, load_humint_json, parse_uploaded_image
from utils.map_builder import build_map_html
from utils.validators import validate_dataframe

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="StratFusion | Intelligence Dashboard",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Dark military theme */
    .stApp { background-color: #0a0f0d; color: #c8d6c8; }
    .stSidebar { background-color: #0d1a13 !important; }
    .stSidebar .stMarkdown, .stSidebar label { color: #8fbc8f !important; }
    
    /* Header */
    .main-header {
        background: linear-gradient(135deg, #0d2b1a 0%, #0a1f12 100%);
        border: 1px solid #1a4a2a;
        border-radius: 8px;
        padding: 20px 30px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 16px;
    }
    .main-header h1 { color: #39ff14; font-size: 1.8rem; margin: 0; letter-spacing: 3px; }
    .main-header p  { color: #7fbf7f; margin: 4px 0 0 0; font-size: 0.85rem; letter-spacing: 1px; }
    
    /* Stat cards */
    .stat-card {
        background: #0d2b1a;
        border: 1px solid #1a4a2a;
        border-radius: 6px;
        padding: 14px 18px;
        text-align: center;
    }
    .stat-card .val { font-size: 2rem; font-weight: 700; color: #39ff14; }
    .stat-card .lbl { font-size: 0.7rem; color: #7fbf7f; letter-spacing: 2px; text-transform: uppercase; }
    
    /* Intel type badges */
    .badge-osint  { background:#1a3a1a; color:#39ff14; border:1px solid #2a6a2a; padding:2px 8px; border-radius:3px; font-size:0.7rem; }
    .badge-humint { background:#1a2a3a; color:#39aaff; border:1px solid #2a5a7a; padding:2px 8px; border-radius:3px; font-size:0.7rem; }
    .badge-imint  { background:#3a1a1a; color:#ff6b39; border:1px solid #7a2a2a; padding:2px 8px; border-radius:3px; font-size:0.7rem; }

    /* Section headers */
    .section-header {
        color: #39ff14;
        font-size: 0.75rem;
        letter-spacing: 3px;
        text-transform: uppercase;
        border-bottom: 1px solid #1a4a2a;
        padding-bottom: 6px;
        margin: 16px 0 10px 0;
    }
    
    /* Upload zone */
    .stFileUploader { border: 1px dashed #2a6a2a !important; border-radius: 6px; }
    
    /* Buttons */
    .stButton > button {
        background: #0d2b1a;
        border: 1px solid #39ff14;
        color: #39ff14;
        border-radius: 4px;
        letter-spacing: 1px;
        font-size: 0.8rem;
    }
    .stButton > button:hover { background: #1a4a2a; }
    
    /* Map container */
    .map-wrapper {
        border: 1px solid #1a4a2a;
        border-radius: 8px;
        overflow: hidden;
    }
    
    /* Status bar */
    .status-bar {
        background: #0d1a13;
        border: 1px solid #1a3a1a;
        border-radius: 4px;
        padding: 8px 14px;
        font-size: 0.75rem;
        color: #7fbf7f;
        letter-spacing: 1px;
        font-family: monospace;
    }
    
    /* Hide Streamlit default elements */
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding-top: 1rem; }
</style>
""", unsafe_allow_html=True)


# ── Session State Init ────────────────────────────────────────────────────────
def init_session_state():
    """Initialize all session state variables."""
    defaults = {
        "osint_df": None,
        "humint_df": None,
        "imint_data": [],   # list of {lat, lon, name, b64_img}
        "all_markers": [],  # unified list for map
        "map_ready": False,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


init_session_state()


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <div>
        <h1>🛰️ STRATFUSION</h1>
        <p>MULTI-SOURCE INTELLIGENCE FUSION DASHBOARD &nbsp;|&nbsp; CYBERJOAR AI OC.41335.2026</p>
    </div>
</div>
""", unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="section-header">⬆ INGEST INTELLIGENCE</div>', unsafe_allow_html=True)

    # --- OSINT Upload ---
    st.markdown("**OSINT** — Open Source Intelligence")
    st.caption("CSV with columns: `name, lat, lon, source, summary`")
    osint_file = st.file_uploader("Upload OSINT CSV", type=["csv"], key="osint_upload", label_visibility="collapsed")

    if osint_file:
        try:
            df = load_osint_csv(osint_file)
            valid, msg = validate_dataframe(df, required_cols=["name", "lat", "lon"])
            if valid:
                st.session_state.osint_df = df
                st.success(f"✅ {len(df)} OSINT nodes loaded")
                logger.info(f"OSINT loaded: {len(df)} rows")
            else:
                st.error(f"❌ {msg}")
        except Exception as e:
            st.error(f"Parse error: {e}")
            logger.error(f"OSINT load failed: {e}", exc_info=True)

    st.divider()

    # --- HUMINT Upload ---
    st.markdown("**HUMINT** — Human Intelligence")
    st.caption("JSON or CSV with: `name, lat, lon, agent, report`")
    humint_file = st.file_uploader("Upload HUMINT", type=["json", "csv"], key="humint_upload", label_visibility="collapsed")

    if humint_file:
        try:
            df = load_humint_json(humint_file)
            valid, msg = validate_dataframe(df, required_cols=["name", "lat", "lon"])
            if valid:
                st.session_state.humint_df = df
                st.success(f"✅ {len(df)} HUMINT reports loaded")
                logger.info(f"HUMINT loaded: {len(df)} rows")
            else:
                st.error(f"❌ {msg}")
        except Exception as e:
            st.error(f"Parse error: {e}")
            logger.error(f"HUMINT load failed: {e}", exc_info=True)

    st.divider()

    # --- IMINT Upload ---
    st.markdown("**IMINT** — Imagery Intelligence")
    st.caption("JPG/JPEG images — filename format: `name_LAT_LON.jpg`")
    imint_files = st.file_uploader(
        "Upload IMINT Images",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
        key="imint_upload",
        label_visibility="collapsed"
    )

    if imint_files:
        parsed = []
        for f in imint_files:
            result = parse_uploaded_image(f)
            if result:
                parsed.append(result)
        if parsed:
            st.session_state.imint_data = parsed
            st.success(f"✅ {len(parsed)} IMINT images loaded")
            logger.info(f"IMINT loaded: {len(parsed)} images")

    st.divider()

    # --- Sample Data Button ---
    st.markdown('<div class="section-header">🔧 QUICK DEMO</div>', unsafe_allow_html=True)
    if st.button("⚡ Load Sample Intel Data", use_container_width=True):
        sample_osint = pd.DataFrame([
            {"name": "Checkpoint Alpha", "lat": 28.6139, "lon": 77.2090, "source": "Twitter/X", "summary": "Unusual vehicle movement reported near NH-44"},
            {"name": "Market Intel Node", "lat": 28.6304, "lon": 77.2177, "source": "Open Forum", "summary": "Supply disruption observed at Azadpur mandi"},
            {"name": "Broadcast Intercept",  "lat": 28.5921, "lon": 77.2291, "source": "Radio OSINT", "summary": "Encrypted radio traffic spike at 1400 hrs"},
            {"name": "Social Chatter Node", "lat": 28.6562, "lon": 77.2410, "source": "Facebook", "summary": "Mass gathering reported near Mukherjee Nagar"},
        ])
        sample_humint = pd.DataFrame([
            {"name": "Agent KILO Report", "lat": 28.6100, "lon": 77.2300, "agent": "Field Agent K-7", "report": "Subject confirmed at location, maintaining surveillance"},
            {"name": "Source DELTA Brief", "lat": 28.6440, "lon": 77.1990, "agent": "Handler D-3",   "report": "Package transfer observed at secondary location"},
        ])
        st.session_state.osint_df   = sample_osint
        st.session_state.humint_df  = sample_humint
        st.session_state.imint_data = []
        st.success("✅ Sample data loaded!")
        logger.info("Sample intel data loaded via Quick Demo button")

    st.divider()

    # --- Map Settings ---
    st.markdown('<div class="section-header">⚙ MAP SETTINGS</div>', unsafe_allow_html=True)
    map_style = st.selectbox(
        "Tile Layer",
        ["Satellite (ESRI)", "Terrain (OpenTopo)", "Dark (CartoDB)", "Standard (OSM)"],
        index=0
    )
    zoom_level = st.slider("Default Zoom", min_value=5, max_value=16, value=11)


# ── Combine all data into unified markers list ────────────────────────────────
def build_markers() -> list[dict]:
    """Merge OSINT, HUMINT, and IMINT into a single marker list for the map."""
    markers = []

    if st.session_state.osint_df is not None:
        for _, row in st.session_state.osint_df.iterrows():
            markers.append({
                "type": "OSINT",
                "name": str(row.get("name", "OSINT Node")),
                "lat":  float(row["lat"]),
                "lon":  float(row["lon"]),
                "meta": {
                    "Source":  str(row.get("source",  "—")),
                    "Summary": str(row.get("summary", "—")),
                },
                "img_b64": None,
            })

    if st.session_state.humint_df is not None:
        for _, row in st.session_state.humint_df.iterrows():
            markers.append({
                "type": "HUMINT",
                "name": str(row.get("name", "HUMINT Node")),
                "lat":  float(row["lat"]),
                "lon":  float(row["lon"]),
                "meta": {
                    "Agent":  str(row.get("agent",  "—")),
                    "Report": str(row.get("report", "—")),
                },
                "img_b64": None,
            })

    for item in st.session_state.imint_data:
        markers.append({
            "type": "IMINT",
            "name": item["name"],
            "lat":  item["lat"],
            "lon":  item["lon"],
            "meta": {"File": item["filename"]},
            "img_b64": item["b64"],
        })

    return markers


# ── Main Panel ────────────────────────────────────────────────────────────────
# Stat cards row
markers = build_markers()
osint_count  = sum(1 for m in markers if m["type"] == "OSINT")
humint_count = sum(1 for m in markers if m["type"] == "HUMINT")
imint_count  = sum(1 for m in markers if m["type"] == "IMINT")

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="stat-card"><div class="val">{len(markers)}</div><div class="lbl">Total Intel Nodes</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="stat-card"><div class="val">{osint_count}</div><div class="lbl">OSINT Nodes</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="stat-card"><div class="val">{humint_count}</div><div class="lbl">HUMINT Reports</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="stat-card"><div class="val">{imint_count}</div><div class="lbl">IMINT Images</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Map
if markers:
    map_html = build_map_html(markers, map_style=map_style, zoom=zoom_level)
    st.markdown('<div class="map-wrapper">', unsafe_allow_html=True)
    st.components.v1.html(map_html, height=560, scrolling=False)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="status-bar">● LIVE &nbsp;|&nbsp; {len(markers)} NODES PLOTTED &nbsp;|&nbsp; HOVER MARKERS FOR INTEL POPUP &nbsp;|&nbsp; MAP: {map_style.upper()}</div>',
        unsafe_allow_html=True
    )
else:
    st.markdown("""
    <div style="border:1px dashed #2a6a2a; border-radius:8px; padding:80px; text-align:center; color:#4a8a4a;">
        <div style="font-size:3rem">🛰️</div>
        <div style="font-size:1.1rem; letter-spacing:3px; margin-top:12px;">AWAITING INTELLIGENCE FEED</div>
        <div style="font-size:0.8rem; margin-top:8px; color:#3a6a3a;">Upload OSINT / HUMINT / IMINT data or click "Load Sample Intel Data"</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# Data preview table
if markers:
    st.markdown('<div class="section-header">📋 INTELLIGENCE REGISTRY</div>', unsafe_allow_html=True)
    preview_df = pd.DataFrame([
        {
            "Type":    m["type"],
            "Name":    m["name"],
            "Lat":     m["lat"],
            "Lon":     m["lon"],
            "Details": " | ".join(f"{k}: {v}" for k, v in m["meta"].items()),
        }
        for m in markers
    ])
    st.dataframe(
        preview_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Type": st.column_config.TextColumn(width="small"),
            "Lat":  st.column_config.NumberColumn(format="%.4f", width="small"),
            "Lon":  st.column_config.NumberColumn(format="%.4f", width="small"),
        }
    )
