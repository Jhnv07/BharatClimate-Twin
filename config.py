"""Single source of truth for the BharatClimate Twin Uttar Pradesh pilot.

Change LAT_*/LON_* or START_YEAR/END_YEAR here; all scripts import from this file.
"""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

# Pilot region: central / eastern Uttar Pradesh (inclusive bbox, degrees).
LAT_MIN = 25.0
LAT_MAX = 28.0
LON_MIN = 79.0
LON_MAX = 83.0

# Inclusive calendar years for IMD downloads and later chronological splits.
START_YEAR = 2020
END_YEAR = 2024

PRIMARY_VAR = "tmax"
ENABLE_RAIN = True

# Common analysis grid. IMD Tmax is natively 1 degree; IMD rainfall is natively
# 0.25 degree and is averaged onto the Tmax 1-degree cells in preprocess.py.
ANALYSIS_GRID_DEG = 1.0

# Prototype operational thresholds (not official warning products).
HEAT_RISK_TMAX_C = 40.0
HEAVY_RAIN_MM = 64.5

FILL_VALUE = -999.0

RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
MODELS_DIR = PROJECT_ROOT / "models"
ASSETS_DIR = PROJECT_ROOT / "assets"

TMAX_REGION_NC = PROCESSED_DIR / "tmax_region.nc"
RAIN_REGION_NC = PROCESSED_DIR / "rain_region.nc"
CLIMATE_CSV = PROCESSED_DIR / "climate_pilot.csv"
CLIMATE_PARQUET = PROCESSED_DIR / "climate_pilot.parquet"

# IMD fill / missing markers commonly seen in GRD → xarray conversion.
MISSING_SENTINELS = (-999.0, -999, 99.9, -99.9)
