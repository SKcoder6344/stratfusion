"""
tests/test_validators.py
Unit tests for input validation logic.
"""

import pandas as pd
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.validators import validate_dataframe
from utils.data_loader import parse_uploaded_image
import io


# ── validate_dataframe ────────────────────────────────────────────────────────

def test_valid_dataframe_passes():
    df = pd.DataFrame([{"name": "Node A", "lat": 28.61, "lon": 77.20}])
    valid, msg = validate_dataframe(df, required_cols=["name", "lat", "lon"])
    assert valid is True


def test_missing_column_fails():
    df = pd.DataFrame([{"name": "Node A", "lat": 28.61}])  # missing lon
    valid, msg = validate_dataframe(df, required_cols=["name", "lat", "lon"])
    assert valid is False
    assert "lon" in msg


def test_invalid_latitude_fails():
    df = pd.DataFrame([{"name": "Bad Node", "lat": 999.0, "lon": 77.20}])
    valid, msg = validate_dataframe(df, required_cols=["name", "lat", "lon"])
    assert valid is False
    assert "latitude" in msg.lower()


def test_invalid_longitude_fails():
    df = pd.DataFrame([{"name": "Bad Node", "lat": 28.61, "lon": -999.0}])
    valid, msg = validate_dataframe(df, required_cols=["name", "lat", "lon"])
    assert valid is False
    assert "longitude" in msg.lower()


def test_empty_dataframe_fails():
    df = pd.DataFrame()
    valid, msg = validate_dataframe(df, required_cols=["name", "lat", "lon"])
    assert valid is False
    assert "empty" in msg.lower()


# ── parse_uploaded_image ──────────────────────────────────────────────────────

class FakeFile:
    """Minimal mock of a Streamlit UploadedFile."""
    def __init__(self, name: str, content: bytes = b"fake_image_data"):
        self.name = name
        self._content = content
    def read(self):
        return self._content


def test_image_parse_with_coords_in_filename():
    f = FakeFile("checkpoint_28.6139_77.2090.jpg")
    result = parse_uploaded_image(f)
    assert result is not None
    assert abs(result["lat"] - 28.6139) < 0.001
    assert abs(result["lon"] - 77.2090) < 0.001


def test_image_parse_no_coords_uses_default():
    f = FakeFile("random_image_nocoords.jpg")
    result = parse_uploaded_image(f)
    assert result is not None
    assert result["lat"] == 20.5937  # India default


def test_image_parse_returns_base64():
    f = FakeFile("target_28.00_77.00.jpg", b"abc123")
    result = parse_uploaded_image(f)
    assert result["b64"] is not None
    assert len(result["b64"]) > 0
