# 🛰️ StratFusion — Multi-Source Intelligence Fusion Dashboard

> **CYBERJOAR AI Assignment | PS1 | OC.41335.2026.59218**  
> A centralized, web-based intelligence dashboard that fuses OSINT, HUMINT, and IMINT onto a single interactive geospatial map.

[![CI](https://github.com/SKcoder6344/stratfusion/actions/workflows/ci.yml/badge.svg)](https://github.com/SKcoder6344/stratfusion/actions)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35-red)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🔍 What It Does

Modern intelligence operations are crippled by fragmented data — OSINT lives in databases, HUMINT in spreadsheets, IMINT in image folders. Analysts waste critical time toggling between tools.

**StratFusion** solves this by providing a single-screen **Common Operating Picture**:
- Upload intelligence from three sources → all data appears as **interactive dots on a live terrain map**
- **Hover over any dot** → instantly see a popup with raw metadata or satellite imagery — no page navigation needed
- Color-coded by intel type: 🟢 OSINT | 🔵 HUMINT | 🟠 IMINT

---

## 🏗️ Architecture

```
User (Browser)
    │
    ▼
Streamlit App (app.py)
    ├── Sidebar: File Upload Panel
    │       ├── OSINT CSV Ingestor    → utils/data_loader.py
    │       ├── HUMINT JSON Ingestor  → utils/data_loader.py
    │       └── IMINT Image Parser    → utils/data_loader.py (base64 encode)
    │
    ├── Data Validation Layer         → utils/validators.py
    │
    └── Map Renderer                  → utils/map_builder.py
            └── Leaflet.js (embedded HTML)
                    └── Custom SVG markers + hover popup JS
```

---

## 🛠️ Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Frontend/App | Streamlit | Rapid deployment, live URL, no React needed |
| Map Engine | Leaflet.js (CDN) | Open-source, tile-agnostic, hover events |
| Tile Layers | ESRI Satellite, OpenTopo, CartoDB Dark, OSM | Multi-environment support |
| Data Handling | Pandas | CSV/JSON ingestion + validation |
| Image Encoding | Python base64 | Inline IMINT display without file server |
| CI/CD | GitHub Actions | Auto-test on every push |
| Containerization | Docker | One-command reproducibility |

---

## 🚀 Quick Start

### Option 1 — Streamlit Cloud (Live Demo)
```
[LIVE LINK — add after deployment]
```

### Option 2 — Run Locally
```bash
git clone https://github.com/SKcoder6344/stratfusion
cd stratfusion
pip install -r requirements.txt
streamlit run app.py
```

### Option 3 — Docker
```bash
docker build -t stratfusion .
docker run -p 8501:8501 stratfusion
# Open http://localhost:8501
```

---

## 📁 Folder Structure

```
fusion-dashboard/
├── app.py                      # Main Streamlit application
├── utils/
│   ├── data_loader.py          # OSINT/HUMINT/IMINT ingestion
│   ├── map_builder.py          # Leaflet HTML generator
│   └── validators.py           # Input validation
├── data/sample/
│   ├── sample_osint.csv        # Demo OSINT data (Delhi region)
│   └── sample_humint.json      # Demo HUMINT data
├── tests/
│   └── test_validators.py      # 8 unit tests (all passing)
├── .streamlit/config.toml      # Dark military theme
├── .github/workflows/ci.yml    # GitHub Actions CI
├── Dockerfile
├── Makefile
└── requirements.txt
```

---

## 📋 How to Upload Data

### OSINT (CSV)
| Column | Required | Description |
|---|---|---|
| `name` | ✅ | Node label |
| `lat` | ✅ | Latitude (decimal) |
| `lon` | ✅ | Longitude (decimal) |
| `source` | Optional | Data origin |
| `summary` | Optional | Intel summary |

### HUMINT (JSON or CSV)
```json
[{"name": "Agent Report", "lat": 28.61, "lon": 77.20, "agent": "K-7", "report": "..."}]
```

### IMINT (Images)
Name your files: `description_LAT_LON.jpg`  
Example: `target_building_28.6139_77.2090.jpg`

---

## 🎯 Key Logic (For Submission Email)

The dashboard solves the **fragmented intelligence problem** through three mechanisms:

1. **Unified Ingestion**: A polymorphic data loader accepts CSV (OSINT), JSON/CSV (HUMINT), and JPG/JPEG (IMINT) — normalizing column names and validating lat/lon ranges before any data touches the map.

2. **Coordinate-Anchored Rendering**: All intel sources are reduced to a `{type, lat, lon, meta, img_b64}` marker schema. Leaflet.js renders custom SVG dots color-coded by type — OSINT (green), HUMINT (blue), IMINT (orange) — providing instant visual triage.

3. **Hover-Activated Intel Popup**: A pure JavaScript event listener on each marker intercepts `mouseover` events and dynamically builds an HTML popup containing the raw metadata and — for IMINT — a base64-inline satellite image thumbnail, eliminating the need to navigate away from the map view.

---

## 📈 Demo

Click **"⚡ Load Sample Intel Data"** in the sidebar to instantly see 6 OSINT nodes and 3 HUMINT reports plotted on a live satellite map of Delhi.

---

## 🔮 Future Improvements

- MongoDB + AWS S3 live connector (currently simulated via file upload)
- Real-time OSINT feed via Twitter/X API streaming
- Temporal filtering — slider to view intel by time window
- Analyst annotation layer — add notes directly on map

---

## 👤 Author

**Sujal Kumar Nayak**  
B.Tech CSE Final Year | LPU  
GitHub: [@SKcoder6344](https://github.com/SKcoder6344)
