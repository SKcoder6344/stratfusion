"""
utils/data_loader.py
Handles ingestion of OSINT (CSV), HUMINT (JSON/CSV), and IMINT (images).
"""

import base64
import io
import json
import logging
import re
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)


def load_osint_csv(file_obj) -> pd.DataFrame:
    """
    Load OSINT data from an uploaded CSV file.

    Args:
        file_obj: Streamlit UploadedFile object

    Returns:
        DataFrame with at least columns: name, lat, lon
    """
    df = pd.read_csv(file_obj)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    logger.info(f"[load_osint_csv] Loaded {len(df)} rows, columns: {list(df.columns)}")
    return df


def load_humint_json(file_obj) -> pd.DataFrame:
    """
    Load HUMINT data from an uploaded JSON or CSV file.

    Args:
        file_obj: Streamlit UploadedFile object (json or csv)

    Returns:
        DataFrame with at least columns: name, lat, lon
    """
    filename = file_obj.name.lower()

    if filename.endswith(".json"):
        content = file_obj.read()
        data = json.loads(content)
        # Support both list-of-dicts and {reports: [...]} formats
        if isinstance(data, list):
            df = pd.DataFrame(data)
        elif isinstance(data, dict):
            # Try common wrapper keys
            for key in ["reports", "data", "humint", "records", "items"]:
                if key in data:
                    df = pd.DataFrame(data[key])
                    break
            else:
                df = pd.DataFrame([data])
        else:
            raise ValueError("Unsupported JSON structure")
    else:
        df = pd.read_csv(file_obj)

    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    logger.info(f"[load_humint_json] Loaded {len(df)} rows from {filename}")
    return df


def parse_uploaded_image(file_obj) -> Optional[dict]:
    """
    Parse an uploaded image file and extract lat/lon from filename.

    Expected filename formats:
      - name_28.6139_77.2090.jpg
      - checkpoint_28.6139_77.2090.jpeg
      - Any name with two decimal numbers anywhere in it

    Args:
        file_obj: Streamlit UploadedFile (jpg/jpeg/png)

    Returns:
        Dict with keys: name, lat, lon, b64, filename
        Returns None if lat/lon cannot be parsed.
    """
    filename = file_obj.name
    stem     = filename.rsplit(".", 1)[0]  # remove extension

    # Find all decimal numbers in filename
    coords = re.findall(r"[-+]?\d+\.\d+", stem)

    if len(coords) >= 2:
        lat = float(coords[0])
        lon = float(coords[1])
    else:
        # Fall back: try to split on underscore and grab last two numeric parts
        parts = stem.split("_")
        numeric = []
        for p in parts:
            try:
                numeric.append(float(p))
            except ValueError:
                pass
        if len(numeric) >= 2:
            lat = numeric[-2]
            lon = numeric[-1]
        else:
            logger.warning(
                f"[parse_uploaded_image] Cannot extract lat/lon from filename: {filename}. "
                "Use format: name_LAT_LON.jpg (e.g. target_28.6139_77.2090.jpg)"
            )
            # Default to India center so it still shows on map
            lat, lon = 20.5937, 78.9629

    # Derive a readable name from filename stem
    name_parts = re.split(r"[_\-\s]+", stem)
    name_parts = [p for p in name_parts if not re.match(r"^[-+]?\d+\.?\d*$", p)]
    name = " ".join(name_parts).title() if name_parts else stem

    # Encode image to base64
    image_bytes = file_obj.read()
    b64 = base64.b64encode(image_bytes).decode("utf-8")

    logger.info(f"[parse_uploaded_image] Parsed '{filename}' → name='{name}', lat={lat}, lon={lon}")

    return {
        "name":     name or filename,
        "lat":      lat,
        "lon":      lon,
        "b64":      b64,
        "filename": filename,
    }
