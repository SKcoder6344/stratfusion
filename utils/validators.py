"""
utils/validators.py
Input validation functions for uploaded intelligence data.
"""

import logging
import pandas as pd
from typing import Tuple

logger = logging.getLogger(__name__)

VALID_LAT_RANGE = (-90.0, 90.0)
VALID_LON_RANGE = (-180.0, 180.0)


def validate_dataframe(df: pd.DataFrame, required_cols: list[str]) -> Tuple[bool, str]:
    """
    Validate that a DataFrame has required columns and valid coordinate values.

    Args:
        df:            DataFrame to validate
        required_cols: List of column names that must be present

    Returns:
        Tuple of (is_valid: bool, message: str)
    """
    if df.empty:
        return False, "Uploaded file is empty."

    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        return False, f"Missing required columns: {missing}. Found: {list(df.columns)}"

    # Validate lat/lon ranges
    if "lat" in df.columns and "lon" in df.columns:
        try:
            lats = pd.to_numeric(df["lat"], errors="coerce")
            lons = pd.to_numeric(df["lon"], errors="coerce")

            invalid_lat = lats.isna() | (lats < VALID_LAT_RANGE[0]) | (lats > VALID_LAT_RANGE[1])
            invalid_lon = lons.isna() | (lons < VALID_LON_RANGE[0]) | (lons > VALID_LON_RANGE[1])

            if invalid_lat.any():
                bad_count = invalid_lat.sum()
                logger.warning(f"[validate_dataframe] {bad_count} rows with invalid latitude")
                return False, f"{bad_count} rows have invalid latitude values (must be between -90 and 90)."

            if invalid_lon.any():
                bad_count = invalid_lon.sum()
                logger.warning(f"[validate_dataframe] {bad_count} rows with invalid longitude")
                return False, f"{bad_count} rows have invalid longitude values (must be between -180 and 180)."

        except Exception as e:
            return False, f"Coordinate validation error: {e}"

    logger.info(f"[validate_dataframe] Validation passed for {len(df)} rows")
    return True, "OK"
