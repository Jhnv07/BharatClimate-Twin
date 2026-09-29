"""
Phase 5 - BharatClimate Twin Streamlit Dashboard.

Title: BharatClimate Twin - Uttar Pradesh Pilot
Uses: Plotly (carto-positron map), st.cache_data, saved predictions + models.
No API tokens required.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config
from src.scenario import apply_scenario

st.set_page_config(
    page_title="BharatClimate Twin - Uttar Pradesh Pilot",
    page_icon="🌡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ────────────────────────────── Custom CSS ──────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.kpi-card {
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
    border-radius: 12px;
    padding: 18px 22px;
    color: white;
    text-align: center;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    margin-bottom: 8px;
}
.kpi-value { font-size: 2.1rem; font-weight: 700; line-height: 1.2; }
.kpi-label { font-size: 0.78rem; opacity: 0.85; text-transform: uppercase; letter-spacing: 0.05em; margin-top: 4px; }
.kpi-delta { font-size: 0.9rem; font-weight: 500; margin-top: 6px; }
.disclaimer-box {
    background: #fff3cd; border-left: 4px solid #ffc107;
    padding: 10px 16px; border-radius: 6px; margin: 8px 0;
    font-size: 0.82rem; color: #856404;
}
.arch-box {
    background: #f0f4ff; border-radius: 10px;
    padding: 20px; font-family: monospace; font-size: 0.85rem;
    white-space: pre; overflow-x: auto;
}
</style>
""", unsafe_allow_html=True)


# ────────────────────────────── Data loaders ──────────────────────────────
@st.cache_data
def load_predictions():
    path = config.PROCESSED_DIR / "predictions.csv"
    df = pd.read_csv(path, parse_dates=["date"])
    return df


@st.cache_data
def load_metrics():
    path = config.MODELS_DIR / "metrics.json"
    with open(path) as f:
        return json.load(f)


@st.cache_data
def load_climate():
    return pd.read_csv(config.CLIMATE_CSV, parse_dates=["date"])


# ────────────────────────────── Sidebar ──────────────────────────────
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/b/b9/Map_of_Uttar_Pradesh.svg/200px-Map_of_Uttar_Pradesh.svg.png", width=120)
st.sidebar.title("🌡️ BharatClimate Twin")
st.sidebar.caption("Uttar Pradesh Pilot · AI Climate Digital Twin")

variable    = st.sidebar.selectbox("Variable", ["Tmax (°C)", "Rainfall (mm)"], key="var_sel")
map_layer   = st.sidebar.selectbox("Map Layer", ["Observed", "AI Forecast", "Scenario", "Scenario Difference"], key="layer_sel")

pred_df = load_predictions()
test_dates = sorted(pred_df["date"].dt.strftime("%Y-%m-%d").unique())
date_sel = st.sidebar.selectbox("Date (Test Period 2024)", test_dates, index=0, key="date_sel")

st.sidebar.markdown("---")
st.sidebar.subheader("Scenario Controls")
dT     = st.sidebar.slider("Temperature offset ΔT (°C)", -2.0, 5.0, 0.0, 0.5, key="dT")
dR_pct = st.sidebar.slider("Rainfall change ΔR (%)", -50, 100, 0, 5, key="dR")
st.sidebar.markdown('<div class="disclaimer-box">⚠️ What-if sensitivity scenario, not a validated climate projection.</div>', unsafe_allow_html=True)

# ────────────────────────────── Main area ──────────────────────────────
st.title("🌡️ BharatClimate Twin — Uttar Pradesh Pilot")
st.caption("AI-powered climate digital twin · IMD data 2020-2024 · 12 one-degree cells · Next-day forecast")

# Determine variable keys
is_tmax = variable.startswith("Tmax")
obs_col   = "tmax_observed"   if is_tmax else "rain_observed"
pred_col  = "tmax_ml_pred"    if is_tmax else "rain_ml_pred"
persist_col = "tmax_persistence" if is_tmax else "rain_persistence"
unit      = "°C" if is_tmax else "mm"
var_label = "Tmax" if is_tmax else "Rainfall"
thresh    = config.HEAT_RISK_TMAX_C if is_tmax else config.HEAVY_RAIN_MM

# Filter to selected date
day_df = pred_df[pred_df["date"].dt.strftime("%Y-%m-%d") == date_sel].copy()

# Scenario
scn = apply_scenario(pred_df, dT=dT, dR_pct=dR_pct, date=date_sel)
scn_base = scn["baseline"]
scn_out  = scn["scenario"]
scn_diff = scn["difference"]
thresh_info = scn["thresholds"]

# ── KPI cards ──
scn_col = "tmax_scenario" if is_tmax else "rain_scenario"
base_col_k = "tmax_forecast" if is_tmax else "rain_forecast"

obs_mean = day_df[obs_col].mean() if obs_col in day_df.columns else np.nan
obs_max  = day_df[obs_col].max()  if obs_col in day_df.columns else np.nan
high_risk = int((day_df[obs_col] >= thresh).sum()) if obs_col in day_df.columns else 0

scn_mean = scn_out[scn_col].mean() if scn_col in scn_out.columns else np.nan
base_mean = scn_base[base_col_k].mean() if base_col_k in scn_base.columns else np.nan
delta_mean = scn_mean - base_mean if not np.isnan(scn_mean) else 0.0

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f'<div class="kpi-card"><div class="kpi-value">{obs_mean:.1f}{unit}</div><div class="kpi-label">Regional Mean (Observed)</div></div>', unsafe_allow_html=True)
with k2:
    st.markdown(f'<div class="kpi-card"><div class="kpi-value">{obs_max:.1f}{unit}</div><div class="kpi-label">Regional Max (Observed)</div></div>', unsafe_allow_html=True)
with k3:
    st.markdown(f'<div class="kpi-card"><div class="kpi-value">{high_risk}</div><div class="kpi-label">High-Risk Cells (≥{thresh:.0f}{unit})</div></div>', unsafe_allow_html=True)
with k4:
    delta_sign = "+" if delta_mean >= 0 else ""
    st.markdown(f'<div class="kpi-card"><div class="kpi-value">{delta_sign}{delta_mean:.2f}{unit}</div><div class="kpi-label">Baseline→Scenario Change</div></div>', unsafe_allow_html=True)

st.markdown("---")

# ── Map ──
map_col, ts_col = st.columns([1.6, 1.0])

with map_col:
    st.subheader(f"📍 {var_label} Map — {date_sel} ({map_layer})")

    if map_layer == "Observed":
        plot_df = day_df[["lat", "lon", obs_col]].rename(columns={obs_col: "value"})
    elif map_layer == "AI Forecast":
        plot_df = day_df[["lat", "lon", pred_col]].rename(columns={pred_col: "value"})
    elif map_layer == "Scenario":
        tmp = scn_out[["lat", "lon", scn_col]].rename(columns={scn_col: "value"})
        plot_df = tmp
    else:
        diff_col = "tmax_diff" if is_tmax else "rain_diff"
        tmp = scn_diff[["lat", "lon", diff_col]].rename(columns={diff_col: "value"})
        plot_df = tmp

    colorscale = "RdYlBu_r" if is_tmax else "Blues"
    if map_layer == "Scenario Difference":
        colorscale = "RdBu_r"

    fig_map = go.Figure(go.Scattermap(
        lat=plot_df["lat"],
        lon=plot_df["lon"],
        mode="markers",
        marker=dict(
            size=28,
            color=plot_df["value"],
            colorscale=colorscale,
            showscale=True,
            colorbar=dict(title=unit, thickness=14),
            opacity=0.82,
        ),
        text=[
            f"Lat:{r.lat}, Lon:{r.lon}<br>{var_label}: {r.value:.2f}{unit}"
            for _, r in plot_df.iterrows()
        ],
        hoverinfo="text",
    ))
    fig_map.update_layout(
        map=dict(style="carto-positron", zoom=5.5,
                 center=dict(lat=26.5, lon=81.0)),
        margin=dict(l=0, r=0, t=0, b=0),
        height=420,
    )
    st.plotly_chart(fig_map, use_container_width='stretch')

    # Threshold info
    if dT != 0 or dR_pct != 0:
        if is_tmax and "heat_cells_scenario" in thresh_info:
            st.info(f"🌡️ Heat-risk cells (≥{config.HEAT_RISK_TMAX_C}°C): Baseline **{thresh_info['heat_cells_baseline']}** → Scenario **{thresh_info['heat_cells_scenario']}**")
        elif not is_tmax and "heavy_rain_cells_scenario" in thresh_info:
            st.info(f"🌧️ Heavy-rain cells (≥{config.HEAVY_RAIN_MM}mm): Baseline **{thresh_info['heavy_rain_cells_baseline']}** → Scenario **{thresh_info['heavy_rain_cells_scenario']}**")

with ts_col:
    st.subheader("📈 Selected Cell Time Series")
    # Pick cell closest to centre
    centre_lat, centre_lon = 26.5, 81.0
    cells = pred_df[["lat", "lon"]].drop_duplicates()
    cells["dist"] = ((cells["lat"] - centre_lat)**2 + (cells["lon"] - centre_lon)**2)**0.5
    best = cells.loc[cells["dist"].idxmin()]
    cell_df = pred_df[(pred_df["lat"] == best["lat"]) & (pred_df["lon"] == best["lon"])].copy()
    cell_df = cell_df.sort_values("date")

    fig_ts = go.Figure()
    if obs_col in cell_df.columns:
        fig_ts.add_trace(go.Scatter(x=cell_df["date"], y=cell_df[obs_col], mode="lines",
                                    name="Observed", line=dict(color="black", width=1.5)))
    if pred_col in cell_df.columns:
        fig_ts.add_trace(go.Scatter(x=cell_df["date"], y=cell_df[pred_col], mode="lines",
                                    name="AI Forecast", line=dict(color="#2196F3", width=1.5)))
    if persist_col in cell_df.columns:
        fig_ts.add_trace(go.Scatter(x=cell_df["date"], y=cell_df[persist_col], mode="lines",
                                    name="Persistence", line=dict(color="orange", dash="dot", width=1.2)))
    fig_ts.update_layout(
        height=420, template="plotly_white",
        font=dict(family="Inter, sans-serif", size=11),
        legend=dict(orientation="h", y=1.08),
        xaxis_title="Date", yaxis_title=f"{var_label} ({unit})",
        margin=dict(l=10, r=10, t=30, b=10),
    )
    st.plotly_chart(fig_ts, use_container_width='stretch')
    st.caption(f"Cell: Lat {best['lat']}, Lon {best['lon']} (closest to region centre)")

st.markdown("---")

# ── Tabs ──
tab1, tab2 = st.tabs(["📊 Model Performance", "ℹ️ About"])

with tab1:
    metrics = load_metrics()
    st.subheader("Test-Set Metrics (2024)")
    rows = []
    for var_key, m in metrics.items():
        rows.append({
            "Variable": var_key.upper(),
            "MAE": m.get("mae"),
            "RMSE": m.get("rmse"),
            "Correlation": m.get("corr"),
            "Persistence MAE": m.get("persistence_mae"),
            "% Improvement vs Persistence": m.get("pct_improvement_over_persistence"),
            "Rain/No-Rain Acc.": m.get("rain_nrain_accuracy", "—"),
        })
    st.dataframe(pd.DataFrame(rows), use_container_width='stretch', hide_index=True)

    st.subheader("Evaluation Plots")
    plot_files = sorted(config.ASSETS_DIR.glob("*.png"))
    if plot_files:
        cols = st.columns(min(3, len(plot_files)))
        for i, pf in enumerate(plot_files):
            cols[i % 3].image(str(pf), caption=pf.stem.replace("_", " ").title(), use_container_width='stretch')
    else:
        plot_files_html = sorted(config.ASSETS_DIR.glob("*.html"))
        if plot_files_html:
            for pf in plot_files_html:
                st.markdown(f"[{pf.stem}]({pf})")
        else:
            st.info("Run evaluate.py to generate plots, then refresh.")

with tab2:
    st.subheader("About BharatClimate Twin — UP Pilot")
    st.markdown("""
    **Digital Twin Loop:**

    `
    Observations (IMD)
         │
         ▼
    Climate State (grid cells, tmax/rain)
         │
         ▼
    ML Forecast (XGBRegressor, global model, lag + rolling features)
         │
         ▼
    Scenario Engine (what-if perturbations: +ΔT, +ΔR%)
         │
         ▼
    Risk Insight (heat-stress cells ≥40°C, heavy rain ≥64.5 mm/day)
    `
    """)

    st.markdown("""
    **Data Sources and Resolutions**
    | Source | Variable | Native Resolution | Grid Used |
    |--------|----------|------------------|-----------|
    | IMD GRD | Tmax | 1° × 1° | 1° (native) |
    | IMD GRD | Rainfall | 0.25° × 0.25° | Aggregated to 1° |

    **Pilot Region:** Central–Eastern Uttar Pradesh  
    Lat 25–28°N, Lon 79–83°E · 12 one-degree grid cells · 2020–2024

    ---
    **Architecture (simplified)**
    """)

    st.markdown("""
    <div class="arch-box">
    [IMD Raw Data (GRD)]
          |
    [preprocess.py]  ──>  climate_pilot.csv  (12 cells, 5 yr)
          |
    [features.py]   ──>  features.parquet   (lags, rolling, cyclic)
          |
    [train.py]      ──>  tmax_model.joblib / rain_model.joblib
                         metrics.json / predictions.csv
          |
    [scenario.py]   ──>  what-if perturbations + threshold counts
          |
    [app.py]        ──>  Streamlit dashboard (this UI)
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    ---
    **⚠️ Limitations**
    - Small 12-cell pilot region (does not cover all of UP)
    - Next-day forecast only (no multi-day outlook)
    - Statistical ML model — no physical equations
    - No satellite data integrated yet (INSAT/MOSDAC LST, SST, rainfall — roadmap item)
    - Training data 2020–2024 only

    **🚀 Roadmap**
    - INSAT-3D/3DR MOSDAC LST, SST, and IR-derived rainfall integration *(not yet integrated)*
    - ConvLSTM / spatiotemporal deep learning
    - Ensemble-based uncertainty quantification
    - Real-time IMD API ingestion and data assimilation
    - National scaling to all-India 1° grid
    - Multi-day probabilistic forecasts

    ---
    *INSAT/MOSDAC satellite data is NOT integrated in this prototype.*
    """)
