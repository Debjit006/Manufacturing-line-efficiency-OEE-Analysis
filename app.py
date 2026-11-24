from io import BytesIO
from pathlib import Path
import re

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st


# ============================================================
# MANUFACTURING OEE ANALYTICS - UPLOAD YOUR OWN CSV / EXCEL FILE
# ============================================================

st.set_page_config(
    page_title="Manufacturing OEE Analytics",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)

NAVY = "#12284C"
BLUE = "#2463A5"
TEAL = "#0F766E"
AMBER = "#C98A00"
RED = "#B13F2E"
SLATE = "#64748B"
BG = "#F4F7FB"
WHITE = "#FFFFFF"
INK = "#172B4D"
MUTED = "#66758A"
BORDER = "#E3EAF2"

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: Inter, 'Segoe UI', sans-serif; }
    .stApp { background: #F3F6FA; }
    .block-container { max-width: 1450px; padding-top: 2rem; padding-bottom: 3rem; }
    #MainMenu, footer { visibility: hidden; }
    [data-testid="stSidebar"] { background: #0E1B33; }
    [data-testid="stSidebar"] * { color: #E6EDF7; }
    [data-testid="stSidebar"] hr { border-color: rgba(255,255,255,.15); }
    .brand { font-size: 20px; font-weight: 800; letter-spacing: .3px; }
    .brand-sub { color: #B8C7DB; font-size: 12px; margin-top: 3px; }
    .page-title { color: #12284C; font-size: 30px; font-weight: 800; margin-bottom: 3px; }
    .page-sub { color: #64748B; font-size: 14px; margin-bottom: 18px; }
    .rule { height: 1px; background: #DDE4EE; margin: 15px 0 25px; }
    .hero { background: linear-gradient(120deg,#0E2347,#2463A5); color: white;
            padding: 30px 32px; border-radius: 14px; margin-bottom: 24px; }
    .hero h2 { color: white; font-size: 25px; margin: 0 0 8px; }
    .hero p { color: #D6E6F8; margin: 0 0 14px; }
    .chip { display: inline-block; background: rgba(255,255,255,.15); color: white;
            padding: 5px 11px; border-radius: 20px; margin: 3px 6px 0 0; font-size: 12px; }
    .kpi { background: white; border: 1px solid #E2E8F0; border-left: 5px solid var(--accent);
           border-radius: 12px; padding: 16px 18px; min-height: 112px;
           box-shadow: 0 2px 8px rgba(15,30,60,.04); }
    .kpi-label { color: #64748B; font-size: 12px; font-weight: 600; }
    .kpi-value { color: #12284C; font-size: 29px; font-weight: 800; margin: 5px 0; }
    .kpi-note { color: #64748B; font-size: 11px; }
    .section-title { color: #12284C; font-size: 18px; font-weight: 750; margin: 25px 0 3px; }
    .section-sub { color: #64748B; font-size: 12px; margin-bottom: 12px; }
    .white-card { background: white; border: 1px solid #E2E8F0; border-radius: 12px; padding: 16px; }
    .footer { color: #8492A6; font-size: 12px; border-top: 1px solid #DDE4EE;
              padding-top: 16px; margin-top: 42px; line-height: 1.6; }
    [data-testid="stDataFrame"] { background: #FFFFFF; }
    [data-testid="stAlert"] { border-radius: 12px; }
    .stCaption { color: #718096; }
    h1, h2, h3 { letter-spacing: -.35px; }

    /* Professional sidebar and navigation */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #101F38 0%, #172F52 100%);
        border-right: 1px solid rgba(255,255,255,.08);
    }
    [data-testid="stSidebar"] .brand {
        font-size: 21px; font-weight: 800; letter-spacing: .8px;
        padding: 8px 0 2px; color: #FFFFFF;
    }
    [data-testid="stSidebar"] .brand-sub {
        color: #B7C7DC; font-size: 13px; letter-spacing: .2px;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        font-size: 15px !important; font-weight: 600 !important;
        padding: 7px 9px !important; border-radius: 9px;
        margin: 3px 0 !important;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
        background: rgba(255,255,255,.10);
    }
    [data-testid="stSidebar"] [data-testid="stFileUploader"] {
        background: rgba(255,255,255,.08); padding: 10px;
        border: 1px solid rgba(255,255,255,.16); border-radius: 12px;
    }
    [data-testid="stSidebar"] .stButton button {
        border-radius: 9px; font-weight: 650;
    }

    /* Larger, clearer typography and controls */
    .block-container { max-width: 1500px; padding-top: 2.2rem; padding-bottom: 3.5rem; }
    .page-title { font-size: 34px; letter-spacing: -.7px; }
    .page-sub { font-size: 15px; line-height: 1.55; }
    .section-title { font-size: 20px; letter-spacing: -.2px; margin-top: 30px; }
    .section-sub { font-size: 13px; line-height: 1.5; }
    [data-testid="stMetric"] {
        background: #FFFFFF; border: 1px solid #E3EAF2;
        border-radius: 13px; padding: 17px 18px !important;
        box-shadow: 0 3px 12px rgba(20,42,75,.055);
    }
    [data-testid="stMetricLabel"] { font-size: 13px !important; color: #66758A !important; }
    [data-testid="stMetricValue"] { font-size: 29px !important; font-weight: 750 !important; color: #172B4D; }
    [data-testid="stMetricDelta"] { font-size: 12px !important; }
    div[data-testid="stPlotlyChart"] {
        background: white; border: 1px solid #E3EAF2;
        border-radius: 14px; padding: 10px;
        box-shadow: 0 3px 12px rgba(20,42,75,.04);
    }
    div[data-testid="stDataFrame"], div[data-testid="stTable"] {
        border: 1px solid #E3EAF2; border-radius: 12px; overflow: hidden;
    }
    div[data-testid="stExpander"] {
        background: #FFFFFF; border: 1px solid #E3EAF2; border-radius: 12px;
    }
    .stButton > button, [data-testid="stDownloadButton"] button {
        border-radius: 10px; font-weight: 650; min-height: 42px;
        border: 1px solid #CBD7E6;
    }
    .stButton > button[kind="primary"] {
        background: #1D5C91; border-color: #1D5C91; color: white;
    }
    input, textarea, [data-baseweb="select"] > div {
        border-radius: 9px !important;
    }
    @media (max-width: 900px) {
        .page-title { font-size: 27px; }
        .kpi-value { font-size: 24px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# -------------------------- HELPERS --------------------------

def header(title, subtitle):
    st.markdown(
        f'<div class="page-title">{title}</div><div class="page-sub">{subtitle}</div><div class="rule"></div>',
        unsafe_allow_html=True,
    )


def section(title, subtitle=""):
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="section-sub">{subtitle}</div>', unsafe_allow_html=True)


def kpi(col, label, value, note="", accent=BLUE):
    with col:
        st.markdown(
            f"""
            <div class="kpi" style="--accent:{accent}">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{value}</div>
                <div class="kpi-note">{note}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def tidy(fig, height=350):
    fig.update_layout(
        height=height,
        margin=dict(l=12, r=12, t=45, b=12),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family="Inter, sans-serif", color="#334155", size=12),
        colorway=[BLUE, TEAL, AMBER, RED, SLATE],
        legend=dict(orientation="h", y=1.12),
    )
    fig.update_xaxes(showgrid=False, linecolor="#CBD5E1")
    fig.update_yaxes(gridcolor="#EEF2F7", zeroline=False)
    return fig


def norm(text):
    return re.sub(r"[^a-z0-9]+", "", str(text).lower())


def find_column(columns, keywords):
    """Find a likely column using flexible name matching."""
    normalized = {col: norm(col) for col in columns}
    for keyword in keywords:
        key = norm(keyword)
        for col, value in normalized.items():
            if value == key:
                return col
    for keyword in keywords:
        key = norm(keyword)
        for col, value in normalized.items():
            if key in value or value in key:
                return col
    return None


def numeric_series(series):
    """Parse numbers conservatively; reject text that merely contains digits.

    Accepts 1200, 1,200, -5, 15 min and 950 units.
    Rejects 'one thousand', '?', 'approx. 20' and '15 min extra'.
    """
    values = series.astype("string").str.strip()
    values = values.str.replace(",", "", regex=False)
    missing_tokens = {"", "na", "n/a", "nan", "none", "null", "-"}
    values = values.mask(values.str.lower().isin(missing_tokens))

    pattern = r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:\s*[a-zA-Z%]+)?$"
    valid_format = values.str.fullmatch(pattern, na=False)
    numeric_text = values.where(valid_format).str.extract(
        r"^([+-]?(?:\d+(?:\.\d*)?|\.\d+))", expand=False
    )
    return pd.to_numeric(numeric_text, errors="coerce")



def read_upload(uploaded_file, sheet_name=None):
    name = uploaded_file.name.lower()
    if name.endswith(".csv"):
        try:
            return pd.read_csv(uploaded_file, sep=None, engine="python")
        except Exception:
            uploaded_file.seek(0)
            return pd.read_csv(uploaded_file)
    if name.endswith((".xlsx", ".xls")):
        return pd.read_excel(uploaded_file, sheet_name=sheet_name)
    raise ValueError("Please upload a CSV or Excel file.")


def excel_download(sheets):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for sheet_name, frame in sheets.items():
            safe_name = str(sheet_name)[:31]
            frame.to_excel(writer, sheet_name=safe_name, index=False)
    output.seek(0)
    return output.getvalue()


def footer(row_count, file_name):
    st.markdown(
        f'<div class="footer">Manufacturing OEE Analytics | {file_name} | {row_count:,} retained records | OEE = Availability × Performance × Quality</div>',
        unsafe_allow_html=True,
    )


# -------------------------- SIDEBAR --------------------------

st.sidebar.markdown(
    '<div class="brand">◈ MANUFACTURING</div>'
    '<div class="brand-sub">OEE &amp; Production Intelligence</div>',
    unsafe_allow_html=True,
)
st.sidebar.divider()
st.sidebar.markdown("### 1. Upload your data")
uploaded = st.sidebar.file_uploader(
    "Choose CSV or Excel file",
    type=["csv", "xlsx", "xls"],
    help="Upload your manufacturing production dataset. No sample data folder is required.",
)

if uploaded is None:
    st.title("Manufacturing OEE Analytics")
    st.markdown(
        """
        Upload your own **CSV or Excel file** to create an interactive manufacturing
        analytics dashboard.

        **How it works**
        1. Upload your production data.
        2. Select the columns that represent time, production, machine, product and downtime.
        3. View OEE, machine, production and downtime analysis.
        4. Download the analysed results as CSV or Excel.
        """
    )
    st.info("Start by uploading your CSV or Excel file using the button in the left sidebar.")
    st.markdown("**Recommended raw-data columns**")
    st.code(
        "production_date, machine_id, planned_time, run_time, ideal_cycle_time, "
        "total_count, good_count, downtime_reason, downtime_minutes, product_id, shift"
    )
    st.caption(
        "If your file already contains OEE / Availability / Performance / Quality percentages, "
        "you can map those columns instead."
    )
    st.stop()


# -------------------------- LOAD FILE --------------------------

try:
    if uploaded.name.lower().endswith((".xlsx", ".xls")):
        excel_file = pd.ExcelFile(uploaded)
        sheet = st.sidebar.selectbox("Select Excel sheet", excel_file.sheet_names)
        uploaded.seek(0)
        raw = read_upload(uploaded, sheet)
    else:
        raw = read_upload(uploaded)
except Exception as exc:
    st.error(f"Could not read this file: {exc}")
    st.stop()

if raw.empty:
    st.error("The uploaded file is empty. Please upload a file containing data.")
    st.stop()

raw_original = raw.copy(deep=True)
raw.columns = [str(c).strip() for c in raw.columns]
raw = raw.dropna(how="all").copy()
columns = list(raw.columns)

st.sidebar.success(f"Loaded {len(raw):,} rows and {len(columns)} columns")
st.sidebar.divider()
page = st.sidebar.radio(
    "NAVIGATION",
    ["Home", "Data Quality", "OEE Analysis", "Machine Analysis", "Line Analysis", "Production Analysis", "Quality Analysis", "Downtime Analysis", "Loss Analysis", "Reports"],
    format_func=lambda item: {
        "Home": "⌂   Home",
        "Data Quality": "✓   Data Quality",
        "OEE Analysis": "◉   OEE Analysis",
        "Machine Analysis": "▣   Machine Analysis",
        "Line Analysis": "▤   Production Line Analysis",
        "Production Analysis": "▥   Production Analysis",
        "Quality Analysis": "✓   Quality Analysis",
        "Downtime Analysis": "◷   Downtime Analysis",
        "Loss Analysis": "▰   Loss Analysis",
        "Reports": "⇩   Reports & Downloads",
    }.get(item, item),
)
st.sidebar.divider()
st.sidebar.caption("Manufacturing Analytics Project")
st.sidebar.caption("Manufacturing OEE Analytics · Version 6.0")


# -------------------------- COLUMN MAPPING --------------------------

# Keep configuration in the sidebar so analytical pages stay uncluttered.
with st.sidebar.expander("⚙️ Configure data columns", expanded=False):
    st.caption("Auto-detected fields are preselected. Change them only if needed.")
    date_guess = find_column(columns, ["production_date", "date", "timestamp", "datetime"])
    machine_guess = find_column(columns, ["machine_id", "machine", "equipment", "asset"])
    product_guess = find_column(columns, ["product_id", "product", "item", "sku"])
    shift_guess = find_column(columns, ["shift", "shift_name"])
    line_guess = find_column(columns, ["production_line", "line", "work_centre", "work_center"])
    downtime_reason_guess = find_column(columns, ["downtime_reason", "reason", "stop_reason", "failure_reason"])
    downtime_type_guess = find_column(columns, ["downtime_type", "planned_unplanned", "downtime_class"])
    defect_reason_guess = find_column(columns, ["defect_reason", "defect_category", "reject_reason"])
    minor_stop_guess = find_column(columns, ["minor_stop_minutes", "minor_stop_minutes", "minor_stop_duration"])

    date_col = st.selectbox("Date column", [None] + columns, index=([None] + columns).index(date_guess) if date_guess in columns else 0, key="map_date")
    machine_col = st.selectbox("Machine column", [None] + columns, index=([None] + columns).index(machine_guess) if machine_guess in columns else 0, key="map_machine")
    product_col = st.selectbox("Product column", [None] + columns, index=([None] + columns).index(product_guess) if product_guess in columns else 0, key="map_product")
    shift_col = st.selectbox("Shift column", [None] + columns, index=([None] + columns).index(shift_guess) if shift_guess in columns else 0, key="map_shift")
    line_col = st.selectbox("Production line", [None] + columns, index=([None] + columns).index(line_guess) if line_guess in columns else 0, key="map_line")
    downtime_reason_col = st.selectbox("Downtime reason", [None] + columns, index=([None] + columns).index(downtime_reason_guess) if downtime_reason_guess in columns else 0, key="map_downtime_reason")
    downtime_type_col = st.selectbox("Downtime type (planned/unplanned)", [None] + columns, index=([None] + columns).index(downtime_type_guess) if downtime_type_guess in columns else 0, key="map_downtime_type")
    defect_reason_col = st.selectbox("Defect category / reason", [None] + columns, index=([None] + columns).index(defect_reason_guess) if defect_reason_guess in columns else 0, key="map_defect_reason")
    minor_stop_col = st.selectbox("Minor-stop minutes (optional)", [None] + columns, index=([None] + columns).index(minor_stop_guess) if minor_stop_guess in columns else 0, key="map_minor_stop")

    st.markdown("**Raw OEE inputs**")
    st.caption("Use consistent time units. This app expects planned/run time in minutes and ideal cycle time in seconds per unit.")
    planned_guess = find_column(columns, ["planned_time", "planned_production_time", "planned_minutes"])
    run_guess = find_column(columns, ["run_time", "operating_time", "runtime", "actual_run_time"])
    cycle_guess = find_column(columns, ["ideal_cycle_time", "ideal_cycle", "cycle_time"])
    total_guess = find_column(columns, ["total_count", "total_production", "total_units", "produced"])
    good_guess = find_column(columns, ["good_count", "good_production", "good_units", "accepted_count"])
    reject_guess = find_column(columns, ["reject_count", "rejected_count", "rejects"])
    downtime_guess = find_column(columns, ["downtime_minutes", "downtime (minutes)", "total_downtime", "downtime"])

    planned_col = st.selectbox("Planned time", [None] + columns, index=([None] + columns).index(planned_guess) if planned_guess in columns else 0, key="map_planned")
    run_col = st.selectbox("Run / operating time", [None] + columns, index=([None] + columns).index(run_guess) if run_guess in columns else 0, key="map_run")
    cycle_col = st.selectbox("Ideal cycle time", [None] + columns, index=([None] + columns).index(cycle_guess) if cycle_guess in columns else 0, key="map_cycle")
    total_col = st.selectbox("Total production count", [None] + columns, index=([None] + columns).index(total_guess) if total_guess in columns else 0, key="map_total")
    good_col = st.selectbox("Good production count", [None] + columns, index=([None] + columns).index(good_guess) if good_guess in columns else 0, key="map_good")
    reject_col = st.selectbox("Rejected production count", [None] + columns, index=([None] + columns).index(reject_guess) if reject_guess in columns else 0, key="map_reject")
    downtime_col = st.selectbox("Downtime minutes", [None] + columns, index=([None] + columns).index(downtime_guess) if downtime_guess in columns else 0, key="map_downtime")

    st.markdown("**Existing percentage fields (optional)**")
    oee_guess = find_column(columns, ["oee (%)", "oee", "oee_percent"])
    avail_guess = find_column(columns, ["availability (%)", "availability", "availability_percent"])
    perf_guess = find_column(columns, ["performance (%)", "performance", "performance_percent"])
    quality_guess = find_column(columns, ["quality (%)", "quality", "quality_percent"])
    oee_col = st.selectbox("OEE (%)", [None] + columns, index=([None] + columns).index(oee_guess) if oee_guess in columns else 0, key="map_oee")
    availability_col = st.selectbox("Availability (%)", [None] + columns, index=([None] + columns).index(avail_guess) if avail_guess in columns else 0, key="map_availability")
    performance_col = st.selectbox("Performance (%)", [None] + columns, index=([None] + columns).index(perf_guess) if perf_guess in columns else 0, key="map_performance")
    quality_col = st.selectbox("Quality (%)", [None] + columns, index=([None] + columns).index(quality_guess) if quality_guess in columns else 0, key="map_quality")


# User-defined benchmark for comparison (not an assumed universal standard).
target_oee = st.sidebar.slider(
    "User-defined OEE target (%)",
    min_value=30, max_value=100, value=85, step=1,
    help="Choose the OEE benchmark you want to compare against."
)

# -------------------------- PREPARE ANALYSIS DATA --------------------------

df = raw.copy()
# Safe formatting cleanup: trim text and convert whitespace-only cells to missing.
for _col in df.select_dtypes(include=["object", "string"]).columns:
    df[_col] = df[_col].astype("string").str.strip()
df = df.replace(r"^\s*$", pd.NA, regex=True)

# Standardise common category labels without inventing missing values.
for _category_col in [machine_col, product_col, shift_col, line_col, downtime_type_col, defect_reason_col]:
    if _category_col and _category_col in df.columns:
        df[_category_col] = df[_category_col].astype("string").str.strip().str.upper()
if downtime_reason_col and downtime_reason_col in df.columns:
    df[downtime_reason_col] = (
        df[downtime_reason_col].astype("string").str.strip()
        .str.replace(r"\s+", " ", regex=True).str.title()
    )

# ---------------- DUPLICATE DATA CLEANING ----------------
original_rows = len(df)
record_id_col = find_column(df.columns, ["record_id", "record id", "recordid", "id"])
duplicate_id = pd.Series(False, index=df.index, dtype=bool)
if record_id_col:
    ids = df[record_id_col].astype("string").str.strip()
    duplicate_id = (ids.notna() & ids.ne("") & ids.duplicated(keep="first")).fillna(False)

# Compare canonical values so formatting differences do not hide duplicates.
# The duplicate comparison deliberately excludes record_id.
comparison = df.drop(columns=[record_id_col], errors="ignore").copy()

def _canonical_date(series):
    """Parse ISO dates first, then common day-first spreadsheet dates."""
    values = series.astype("string").str.strip()
    iso = pd.to_datetime(values, format="%Y-%m-%d", errors="coerce")
    try:
        other = pd.to_datetime(values.where(iso.isna()), errors="coerce",
                               dayfirst=True, format="mixed")
    except (TypeError, ValueError):
        other = pd.to_datetime(values.where(iso.isna()), errors="coerce",
                                dayfirst=True)
    parsed = iso.fillna(other)
    return parsed.dt.strftime("%Y-%m-%d").fillna(
        values.str.casefold().replace({"<na>": "<MISSING>", "": "<MISSING>"})
    )

def _canonical_numeric(series):
    parsed = numeric_series(series)
    fallback = (series.astype("string").str.strip().str.casefold()
                .replace({"<na>": "<MISSING>", "": "<MISSING>"}))
    # Format numeric values consistently (18 and 18.0 become the same value).
    return parsed.map(lambda x: "<MISSING>" if pd.isna(x) else format(float(x), ".12g")).astype("string").fillna(fallback)

for _col in comparison.columns:
    _name = norm(_col)
    if _col == date_col or _name in {"date", "productiondate", "datetime", "timestamp"}:
        comparison[_col] = _canonical_date(comparison[_col])
    elif any(token in _name for token in (
        "planned", "runtime", "operatingtime", "downtime", "cycletime",
        "totalcount", "goodcount", "rejectcount", "productioncount",
        "totalproduction", "goodproduction", "rejectedproduction"
    )):
        comparison[_col] = _canonical_numeric(comparison[_col])
    else:
        comparison[_col] = (
            comparison[_col].astype("string").str.strip().str.casefold()
            .str.replace(r"\s+", " ", regex=True)
            .replace({"<na>": "<MISSING>", "": "<MISSING>"})
        )

duplicate_exact = df.duplicated(keep="first").fillna(False)
normalized_duplicate = comparison.duplicated(keep="first").fillna(False)
# Remove repeated IDs, exact rows, and normalized copies of the same full
# production record. Less-complete matches are only flagged for manual review.
duplicate_rows = (duplicate_id | duplicate_exact | normalized_duplicate).fillna(False)

business_columns = [c for c in df.columns if c != record_id_col]
duplicate_business = (
    df.duplicated(subset=business_columns, keep="first")
    if business_columns else pd.Series(False, index=df.index, dtype=bool)
)
potential_duplicate = (duplicate_business & ~duplicate_rows).fillna(False)
duplicates_removed = int(duplicate_rows.sum())
potential_duplicates_count = int(potential_duplicate.sum())

# Preserve removed rows so users can inspect exactly what was detected.
duplicate_report = df.loc[duplicate_rows].copy()
if not duplicate_report.empty:
    duplicate_reasons = []
    for idx in duplicate_report.index:
        reasons = []
        if bool(duplicate_id.loc[idx]):
            reasons.append("Repeated record ID")
        if bool(duplicate_exact.loc[idx]):
            reasons.append("Exact duplicate row")
        if bool(normalized_duplicate.loc[idx]) and not bool(duplicate_exact.loc[idx]):
            reasons.append("Same production record after date / text / numeric standardisation")
        duplicate_reasons.append("; ".join(reasons) or "Duplicate")
    duplicate_report.insert(0, "duplicate_reason", duplicate_reasons)
    duplicate_report.insert(1, "duplicate_source_index", duplicate_report.index.astype(str))

# Keep similar business records separately for human review; do not auto-delete them.
potential_duplicate_report = df.loc[potential_duplicate].copy()
if not potential_duplicate_report.empty:
    potential_duplicate_report.insert(
        0, "duplicate_review_reason",
        "Possible matching production details (different record ID)"
    )

df = df.loc[~duplicate_rows].copy()
potential_duplicate = potential_duplicate.reindex(df.index).fillna(False)

# ---------------- DATE STANDARDISATION ----------------
date_invalid = pd.Series(False, index=df.index, dtype=bool)
if date_col:
    original_dates = df[date_col].copy()
    try:
        parsed_dates = pd.to_datetime(original_dates, errors="coerce", dayfirst=True, format="mixed")
    except (TypeError, ValueError):
        parsed_dates = pd.to_datetime(original_dates, errors="coerce", dayfirst=True)
    date_invalid = (original_dates.notna() & parsed_dates.isna()).fillna(False).astype(bool)
    df[date_col] = parsed_dates

# ---------------- NUMERIC VALIDATION ----------------
numeric_columns = {
    "Planned time": planned_col, "Run time": run_col, "Ideal cycle time": cycle_col,
    "Total count": total_col, "Good count": good_col, "Reject count": reject_col,
    "Downtime": downtime_col, "Minor-stop minutes": minor_stop_col,
}
numeric_columns = {label: col for label, col in numeric_columns.items() if col}
numeric_invalid = pd.Series(False, index=df.index, dtype=bool)
negative_invalid = pd.Series(False, index=df.index, dtype=bool)
for label, col in numeric_columns.items():
    original_values = df[col].copy()
    parsed_values = numeric_series(original_values)
    invalid_here = (original_values.notna() & parsed_values.isna()).fillna(False).astype(bool)
    negative_here = (parsed_values < 0).fillna(False).astype(bool)
    numeric_invalid = (numeric_invalid | invalid_here).fillna(False).astype(bool)
    negative_invalid = (negative_invalid | negative_here).fillna(False).astype(bool)
    df[col] = parsed_values.mask(negative_here)

runtime_exceeds_planned = pd.Series(False, index=df.index, dtype=bool)
if planned_col and run_col:
    runtime_exceeds_planned = (
        numeric_series(df[run_col]) > numeric_series(df[planned_col])
    ).fillna(False).astype(bool)

count_inconsistent = pd.Series(False, index=df.index, dtype=bool)
if total_col and good_col and reject_col:
    total_values, good_values, reject_values = (
        numeric_series(df[total_col]), numeric_series(df[good_col]), numeric_series(df[reject_col])
    )
    count_inconsistent = (
        total_values.notna() & good_values.notna() & reject_values.notna()
        & ((good_values + reject_values) != total_values)
    ).fillna(False).astype(bool)

# Flag physically implausible production rates instead of silently hiding them.
performance_invalid = pd.Series(False, index=df.index, dtype=bool)
if planned_col and cycle_col and total_col:
    _planned_for_check = numeric_series(df[planned_col])
    _cycle_for_check = numeric_series(df[cycle_col])
    _total_for_check = numeric_series(df[total_col])
    if run_col:
        _runtime_for_check = numeric_series(df[run_col])
    elif downtime_col:
        _runtime_for_check = _planned_for_check - numeric_series(df[downtime_col])
    else:
        _runtime_for_check = pd.Series(pd.NA, index=df.index, dtype="Float64")
    _candidate_performance = (
        _cycle_for_check * _total_for_check /
        (_runtime_for_check * 60).replace(0, pd.NA) * 100
    )
    performance_invalid = (_candidate_performance > 100).fillna(False).astype(bool)

reason_was_missing = pd.Series(False, index=df.index, dtype=bool)
if downtime_reason_col:
    reason_was_missing = df[downtime_reason_col].isna().fillna(False).astype(bool)
    df[downtime_reason_col] = df[downtime_reason_col].fillna("Unknown")

# ---------------- MISSING VALUE / DATA QUALITY REPORT ----------------
missing_summary = df.isna().sum()
rows_with_missing = int(df.isna().any(axis=1).sum())
issue_lists = {idx: [] for idx in df.index}
for idx in df.index:
    if df.loc[idx].isna().any():
        issue_lists[idx].append("Missing value")
    if bool(date_invalid.reindex(df.index).fillna(False).loc[idx]):
        issue_lists[idx].append("Invalid date")
    if bool(numeric_invalid.reindex(df.index).fillna(False).loc[idx]):
        issue_lists[idx].append("Invalid numeric value")
    if bool(negative_invalid.reindex(df.index).fillna(False).loc[idx]):
        issue_lists[idx].append("Negative numeric value")
    if bool(count_inconsistent.reindex(df.index).fillna(False).loc[idx]):
        issue_lists[idx].append("Good + reject count does not equal total count")
    if bool(runtime_exceeds_planned.reindex(df.index).fillna(False).loc[idx]):
        issue_lists[idx].append("Run time exceeds planned production time")
    if bool(performance_invalid.reindex(df.index).fillna(False).loc[idx]):
        issue_lists[idx].append("Calculated performance exceeds 100% - verify cycle time or production inputs")
    if bool(reason_was_missing.reindex(df.index).fillna(False).loc[idx]):
        issue_lists[idx].append("Missing downtime reason (labelled Unknown)")
    if bool(potential_duplicate.reindex(df.index).fillna(False).loc[idx]):
        issue_lists[idx].append("Possible duplicate business record - review before removal")

df["quality_issues"] = ["; ".join(issue_lists[idx]) for idx in df.index]
df["data_quality_status"] = df["quality_issues"].map(
    lambda value: "Needs Review" if value else "Valid"
)

row_has_missing_required = pd.Series(False, index=df.index, dtype=bool)
required_cols = [planned_col, cycle_col, total_col, good_col]
if run_col:
    required_cols.append(run_col)
elif planned_col and downtime_col:
    required_cols.append(downtime_col)
if reject_col:
    required_cols.append(reject_col)
for col in [c for c in required_cols if c and c in df.columns]:
    row_has_missing_required |= df[col].isna()

oee_invalid_rows = (
    row_has_missing_required
    | date_invalid.reindex(df.index).fillna(False)
    | numeric_invalid.reindex(df.index).fillna(False)
    | negative_invalid.reindex(df.index).fillna(False)
    | count_inconsistent.reindex(df.index).fillna(False)
    | runtime_exceeds_planned.reindex(df.index).fillna(False)
).fillna(True).astype(bool)

# Detailed cleaning results are intentionally shown only on the Data Quality page.
# Keeping this report off the analytics pages gives charts and KPIs a clean layout.

# Convert percentages to a 0-100 scale when users entered fractions (0-1).
def as_percent(series):
    values = numeric_series(series)
    if values.dropna().empty:
        return values
    if values.dropna().between(0, 1).all():
        values = values * 100
    # Impossible percentages become missing; never silently clip them to 0 or 100.
    return values.where(values.between(0, 100))


analysis = df.copy()
if downtime_col:
    analysis["Downtime (Minutes)"] = numeric_series(analysis[downtime_col])
if minor_stop_col:
    analysis["Minor Stop (Minutes)"] = numeric_series(analysis[minor_stop_col])
if defect_reason_col:
    analysis["Defect Category"] = analysis[defect_reason_col].astype("string").fillna("Unknown")
if downtime_type_col:
    analysis["Downtime Type"] = analysis[downtime_type_col].astype("string").fillna("Unclassified")

inferred_runtime = bool(planned_col and not run_col and downtime_col)
if inferred_runtime:
    analysis["Run Time (Minutes)"] = (
        numeric_series(analysis[planned_col]) - analysis["Downtime (Minutes)"]
    )
    run_col = "Run Time (Minutes)"

inferred_good_count = bool(total_col and not good_col and reject_col)
if inferred_good_count:
    analysis["Good Production"] = (
        numeric_series(analysis[total_col]) - numeric_series(analysis[reject_col])
    )
    good_col = "Good Production"

raw_oee_available = bool(planned_col and run_col and cycle_col and total_col and good_col)
direct_oee_available = any([oee_col, availability_col, performance_col, quality_col])

if raw_oee_available:
    planned = numeric_series(analysis[planned_col])
    runtime = numeric_series(analysis[run_col])
    cycle_seconds = numeric_series(analysis[cycle_col])
    total_count = numeric_series(analysis[total_col])
    good_count = numeric_series(analysis[good_col])

    valid_inputs = (
        planned.gt(0) & runtime.ge(0) & runtime.le(planned)
        & cycle_seconds.gt(0) & total_count.gt(0)
        & good_count.ge(0) & good_count.le(total_count)
    ).fillna(False)
    if downtime_col and downtime_col in analysis.columns:
        downtime_values = numeric_series(analysis[downtime_col])
        valid_inputs &= (downtime_values.ge(0) & downtime_values.le(planned)).fillna(False)

    if reject_col and reject_col in analysis.columns:
        reject_count = numeric_series(analysis[reject_col])
        valid_inputs &= (
            reject_count.ge(0) & (good_count + reject_count).eq(total_count)
        ).fillna(False)

    if date_col:
        valid_inputs &= analysis[date_col].notna()
    valid_inputs &= ~oee_invalid_rows

    # Ideal cycle time is seconds/unit; runtime is minutes.
    performance_candidate = (
        cycle_seconds * total_count / (runtime * 60).replace(0, pd.NA) * 100
    )
    # Performance above 100% is retained and flagged for investigation.
    # Do not silently cap or discard it: verify ideal cycle time and time units.
    availability = (runtime / planned * 100).where(valid_inputs)
    performance = performance_candidate.where(valid_inputs)
    quality = (good_count / total_count * 100).where(valid_inputs)
    analysis["Availability (%)"] = availability
    analysis["Performance (%)"] = performance
    analysis["Quality (%)"] = quality
    analysis["OEE (%)"] = availability * performance * quality / 10000
    analysis["Total Production"] = total_count.where(valid_inputs)
    analysis["Good Production"] = good_count.where(valid_inputs)
    analysis["Rejected Production"] = (total_count - good_count).where(valid_inputs)

    analysis["_OEE_Planned_Minutes"] = planned.where(valid_inputs)
    analysis["_OEE_Run_Minutes"] = runtime.where(valid_inputs)
    analysis["_OEE_Cycle_Seconds"] = cycle_seconds.where(valid_inputs)
    analysis["_OEE_Ideal_Seconds"] = (cycle_seconds * total_count).where(valid_inputs)
    analysis["_OEE_Total_Count"] = total_count.where(valid_inputs)
    analysis["_OEE_Good_Count"] = good_count.where(valid_inputs)

    result_cols = [
        "Availability (%)", "Performance (%)", "Quality (%)", "OEE (%)",
        "Total Production", "Good Production", "Rejected Production",
    ]
    analysis.loc[~valid_inputs, result_cols] = pd.NA

elif direct_oee_available:
    for source, target in [
        (oee_col, "OEE (%)"), (availability_col, "Availability (%)"),
        (performance_col, "Performance (%)"), (quality_col, "Quality (%)"),
    ]:
        if source:
            analysis[target] = as_percent(analysis[source])
    if all(x in analysis for x in ["Availability (%)", "Performance (%)", "Quality (%)"]):
        calculated_oee = (
            analysis["Availability (%)"] * analysis["Performance (%)"]
            * analysis["Quality (%)"] / 10000
        )
        if "OEE (%)" in analysis:
            mismatch = (
                analysis["OEE (%)"].notna() & calculated_oee.notna()
                & ((analysis["OEE (%)"] - calculated_oee).abs() > 1.0)
            )
            analysis.loc[mismatch, "OEE (%)"] = pd.NA
            if mismatch.any():
                st.warning(
                    f"{int(mismatch.sum())} uploaded OEE value(s) did not match "
                    "Availability × Performance × Quality (tolerance 1 percentage point); "
                    "those OEE values are flagged unavailable."
                )
        else:
            analysis["OEE (%)"] = calculated_oee
    if total_col:
        analysis["Total Production"] = numeric_series(analysis[total_col])
    if good_col:
        analysis["Good Production"] = numeric_series(analysis[good_col])
    if "Total Production" in analysis and "Good Production" in analysis:
        analysis["Rejected Production"] = (
            analysis["Total Production"] - analysis["Good Production"]
        ).where(lambda series: series >= 0)

if downtime_col:
    analysis["Downtime (Minutes)"] = numeric_series(analysis[downtime_col])

overall_oee_metrics = {}
if raw_oee_available and "_OEE_Planned_Minutes" in analysis:
    valid_calc = analysis["_OEE_Planned_Minutes"].notna()
    p_sum = analysis.loc[valid_calc, "_OEE_Planned_Minutes"].sum()
    r_sum = analysis.loc[valid_calc, "_OEE_Run_Minutes"].sum()
    t_sum = analysis.loc[valid_calc, "_OEE_Total_Count"].sum()
    g_sum = analysis.loc[valid_calc, "_OEE_Good_Count"].sum()
    ideal_seconds = analysis.loc[valid_calc, "_OEE_Ideal_Seconds"].sum()
    if p_sum > 0 and t_sum > 0 and r_sum > 0:
        overall_a = r_sum / p_sum * 100
        overall_p = ideal_seconds / (r_sum * 60) * 100
        overall_q = g_sum / t_sum * 100
        if overall_p <= 100:
            overall_oee_metrics = {
                "Availability (%)": overall_a, "Performance (%)": overall_p,
                "Quality (%)": overall_q,
                "OEE (%)": overall_a * overall_p * overall_q / 10000,
            }

has_oee = "OEE (%)" in analysis.columns and analysis["OEE (%)"].notna().any()
has_machine = bool(machine_col and machine_col in analysis.columns)
has_date = bool(date_col and analysis[date_col].notna().any())

# -------------------------- REPORT DATA --------------------------

def group_average(data, group_col, metrics):
    usable = [m for m in metrics if m in data.columns]
    if not group_col or not usable:
        return pd.DataFrame()
    return data.groupby(group_col, dropna=False)[usable].mean(numeric_only=True).reset_index()


def group_oee_summary(data, group_col):
    """Calculate grouped OEE from aggregated inputs where available."""
    if not group_col or group_col not in data.columns:
        return pd.DataFrame()
    hidden = [
        "_OEE_Planned_Minutes", "_OEE_Run_Minutes", "_OEE_Ideal_Seconds",
        "_OEE_Total_Count", "_OEE_Good_Count"
    ]
    if all(c in data.columns for c in hidden):
        out = data.groupby(group_col, dropna=False)[hidden].sum(min_count=1).reset_index()
        p, r = out["_OEE_Planned_Minutes"], out["_OEE_Run_Minutes"]
        total, good = out["_OEE_Total_Count"], out["_OEE_Good_Count"]
        ideal_seconds = out["_OEE_Ideal_Seconds"]
        out["Availability (%)"] = (r / p * 100).where(p > 0)
        out["Performance (%)"] = (ideal_seconds / (r * 60) * 100).where(r > 0)
        out["Quality (%)"] = (good / total * 100).where(total > 0)
        out["OEE (%)"] = out["Availability (%)"] * out["Performance (%)"] * out["Quality (%)"] / 10000
        out["Total Production"] = total
        out["Good Production"] = good
        out["Rejected Production"] = total - good
        return out.drop(columns=hidden)
    # Percentage-only files cannot be reweighted without the underlying inputs.
    return group_average(data, group_col, [
        "Availability (%)", "Performance (%)", "Quality (%)", "OEE (%)"
    ])


machine_summary = group_oee_summary(analysis, machine_col)
product_summary = group_oee_summary(analysis, product_col)
shift_summary = group_oee_summary(analysis, shift_col)

line_summary = group_oee_summary(analysis, line_col)

def grouped_sum(data, group_col, value_col):
    if not group_col or group_col not in data.columns or value_col not in data.columns:
        return pd.DataFrame()
    return (data.groupby(group_col, dropna=False)[value_col]
            .sum(min_count=1).reset_index().sort_values(value_col, ascending=False))

downtime_type_summary = grouped_sum(analysis, "Downtime Type", "Downtime (Minutes)")
defect_summary = grouped_sum(analysis, "Defect Category", "Rejected Production")

if machine_col and "Total Production" in analysis and not machine_summary.empty:
    production_cols = [
        c for c in ["Total Production", "Good Production", "Rejected Production",
                    "Downtime (Minutes)"] if c in analysis
    ]
    machine_prod = analysis.groupby(machine_col, dropna=False)[production_cols].sum(
        numeric_only=True, min_count=1
    ).reset_index()
    extra_cols = [c for c in production_cols if c not in machine_summary.columns]
    if extra_cols:
        machine_summary = machine_summary.merge(
            machine_prod[[machine_col] + extra_cols], on=machine_col, how="left"
        )
elif machine_col and "Total Production" in analysis and machine_summary.empty:
    machine_summary = analysis.groupby(machine_col, dropna=False)[
        [c for c in ["Total Production", "Good Production", "Rejected Production",
                     "Downtime (Minutes)"] if c in analysis]
    ].sum(numeric_only=True, min_count=1).reset_index()

if downtime_reason_col and "Downtime (Minutes)" in analysis:
    downtime_summary = (
        analysis.groupby(downtime_reason_col, dropna=False)["Downtime (Minutes)"]
        .sum().sort_values(ascending=False).reset_index()
    )
    downtime_summary["Contribution (%)"] = (
        downtime_summary["Downtime (Minutes)"] /
        max(downtime_summary["Downtime (Minutes)"].sum(), 1) * 100
    )
    downtime_summary["Cumulative Contribution (%)"] = downtime_summary["Contribution (%)"].cumsum()
else:
    downtime_summary = pd.DataFrame()


# -------------------------- LOSS WATERFALL DATA --------------------------

loss_waterfall = None
if raw_oee_available and all(
    c in analysis.columns for c in [
        "_OEE_Planned_Minutes", "_OEE_Run_Minutes", "_OEE_Ideal_Seconds",
        "_OEE_Total_Count", "_OEE_Good_Count"
    ]
):
    valid_loss_rows = analysis["_OEE_Planned_Minutes"].notna()
    if valid_loss_rows.any():
        planned_total = analysis.loc[valid_loss_rows, "_OEE_Planned_Minutes"].sum()
        run_total = analysis.loc[valid_loss_rows, "_OEE_Run_Minutes"].sum()
        ideal_total_minutes = analysis.loc[valid_loss_rows, "_OEE_Ideal_Seconds"].sum() / 60
        good_ideal_minutes = (
            analysis.loc[valid_loss_rows, "_OEE_Cycle_Seconds"]
            * analysis.loc[valid_loss_rows, "_OEE_Good_Count"]
        ).sum() / 60
        availability_loss = planned_total - run_total
        performance_loss = run_total - ideal_total_minutes
        quality_loss = ideal_total_minutes - good_ideal_minutes
        # Small floating-point differences are rounded to zero; material negative
        # losses indicate inconsistent inputs and are not silently hidden.
        loss_waterfall = {
            "Planned Production Time": float(planned_total),
            "Availability Loss": float(availability_loss),
            "Run Time": float(run_total),
            "Performance Loss": float(performance_loss),
            "Net Operating Time": float(ideal_total_minutes),
            "Quality Loss": float(quality_loss),
            "Fully Productive Time": float(good_ideal_minutes),
        }
        loss_waterfall["Reconciliation Difference"] = float(
            planned_total - availability_loss - performance_loss - quality_loss - good_ideal_minutes
        )




# -------------------------- GLOBAL ANALYSIS FILTERS --------------------------
# Shared filters are applied to every analytical page and analysis export.
with st.sidebar.expander("🔎 Global analysis filters", expanded=True):
    filtered_analysis = analysis.copy()
    if date_col and date_col in filtered_analysis.columns:
        _valid_dates = pd.to_datetime(filtered_analysis[date_col], errors="coerce").dropna()
        if not _valid_dates.empty:
            _date_min, _date_max = _valid_dates.min().date(), _valid_dates.max().date()
            _date_range = st.date_input(
                "Production date range", value=(_date_min, _date_max),
                min_value=_date_min, max_value=_date_max, key="global_date_range"
            )
            if isinstance(_date_range, (tuple, list)) and len(_date_range) == 2:
                _dates = pd.to_datetime(filtered_analysis[date_col], errors="coerce")
                filtered_analysis = filtered_analysis.loc[
                    _dates.dt.date.between(_date_range[0], _date_range[1])
                ]
    for _label, _col in [
        ("Production line", line_col), ("Machine", machine_col),
        ("Shift", shift_col), ("Product", product_col)
    ]:
        if _col and _col in filtered_analysis.columns:
            _choices = sorted(filtered_analysis[_col].dropna().astype(str).unique().tolist())
            _selected = st.multiselect(
                _label, _choices, default=_choices, key=f"global_filter_{norm(_label)}"
            )
            if _choices and not _selected:
                filtered_analysis = filtered_analysis.iloc[0:0]
            elif _selected:
                filtered_analysis = filtered_analysis[filtered_analysis[_col].astype(str).isin(_selected)]

st.sidebar.caption(f"{len(filtered_analysis):,} records match the selected filters")
analysis = filtered_analysis.copy()
has_oee = "OEE (%)" in analysis.columns and analysis["OEE (%)"].notna().any()
has_machine = bool(machine_col and machine_col in analysis.columns)
has_date = bool(date_col and analysis[date_col].notna().any())

# Recalculate grouped summaries in the selected filter context.
machine_summary = group_oee_summary(analysis, machine_col)
product_summary = group_oee_summary(analysis, product_col)
shift_summary = group_oee_summary(analysis, shift_col)
line_summary = group_oee_summary(analysis, line_col)
if downtime_reason_col and "Downtime (Minutes)" in analysis.columns:
    downtime_summary = (
        analysis.groupby(downtime_reason_col, dropna=False)["Downtime (Minutes)"]
        .sum().sort_values(ascending=False).reset_index()
    )
    _down_total = downtime_summary["Downtime (Minutes)"].sum()
    downtime_summary["Contribution (%)"] = (
        downtime_summary["Downtime (Minutes)"] / _down_total * 100 if _down_total else 0
    )
    downtime_summary["Cumulative Contribution (%)"] = downtime_summary["Contribution (%)"].cumsum()
else:
    downtime_summary = pd.DataFrame()
downtime_type_summary = grouped_sum(analysis, "Downtime Type", "Downtime (Minutes)")
defect_summary = grouped_sum(analysis, "Defect Category", "Rejected Production")

# Recalculate weighted KPI totals for the selected filter context.
overall_oee_metrics = {}
if raw_oee_available and all(x in analysis.columns for x in [
    "_OEE_Planned_Minutes", "_OEE_Run_Minutes", "_OEE_Ideal_Seconds",
    "_OEE_Total_Count", "_OEE_Good_Count"
]):
    _valid = analysis["_OEE_Planned_Minutes"].notna()
    _p = analysis.loc[_valid, "_OEE_Planned_Minutes"].sum()
    _r = analysis.loc[_valid, "_OEE_Run_Minutes"].sum()
    _ideal = analysis.loc[_valid, "_OEE_Ideal_Seconds"].sum()
    _total = analysis.loc[_valid, "_OEE_Total_Count"].sum()
    _good = analysis.loc[_valid, "_OEE_Good_Count"].sum()
    if _p > 0 and _r > 0 and _total > 0:
        _a, _perf, _q = _r / _p * 100, _ideal / (_r * 60) * 100, _good / _total * 100
        overall_oee_metrics = {
            "Availability (%)": _a, "Performance (%)": _perf,
            "Quality (%)": _q, "OEE (%)": _a * _perf * _q / 10000
        }

# The loss waterfall uses exactly the same filtered rows as the KPI cards.
loss_waterfall = None
_loss_fields = ["_OEE_Planned_Minutes", "_OEE_Run_Minutes", "_OEE_Ideal_Seconds",
                "_OEE_Total_Count", "_OEE_Good_Count", "_OEE_Cycle_Seconds"]
if raw_oee_available and all(x in analysis.columns for x in _loss_fields):
    _valid_loss = analysis["_OEE_Planned_Minutes"].notna()
    if _valid_loss.any():
        _planned = analysis.loc[_valid_loss, "_OEE_Planned_Minutes"].sum()
        _runtime = analysis.loc[_valid_loss, "_OEE_Run_Minutes"].sum()
        _net = analysis.loc[_valid_loss, "_OEE_Ideal_Seconds"].sum() / 60
        _fully = (analysis.loc[_valid_loss, "_OEE_Cycle_Seconds"] *
                  analysis.loc[_valid_loss, "_OEE_Good_Count"]).sum() / 60
        _av_loss, _perf_loss, _qual_loss = _planned-_runtime, _runtime-_net, _net-_fully
        loss_waterfall = {
            "Planned Production Time": float(_planned),
            "Availability Loss": float(_av_loss), "Run Time": float(_runtime),
            "Performance Loss": float(_perf_loss), "Net Operating Time": float(_net),
            "Quality Loss": float(_qual_loss), "Fully Productive Time": float(_fully),
            "Reconciliation Difference": float(_planned-_av_loss-_perf_loss-_qual_loss-_fully)
        }

daily_oee_summary = pd.DataFrame()
if date_col and raw_oee_available and all(x in analysis.columns for x in _loss_fields[:5]):
    _daily = analysis.dropna(subset=[date_col]).groupby(date_col)[_loss_fields[:5]].sum(min_count=1).reset_index()
    if not _daily.empty:
        _daily["Availability (%)"] = _daily["_OEE_Run_Minutes"] / _daily["_OEE_Planned_Minutes"] * 100
        _daily["Performance (%)"] = _daily["_OEE_Ideal_Seconds"] / (_daily["_OEE_Run_Minutes"] * 60) * 100
        _daily["Quality (%)"] = _daily["_OEE_Good_Count"] / _daily["_OEE_Total_Count"] * 100
        _daily["OEE (%)"] = _daily["Availability (%)"] * _daily["Performance (%)"] * _daily["Quality (%)"] / 10000
        daily_oee_summary = _daily[[date_col, "Availability (%)", "Performance (%)", "Quality (%)", "OEE (%)"]]


# -------------------------- HOME --------------------------

if page == "Home":
    header("Manufacturing Line Efficiency", "Upload-based Overall Equipment Effectiveness analytics dashboard")
    st.markdown(
        f"""
        <div class="hero">
            <h2>Production performance at a glance</h2>
            <p>Explore your uploaded manufacturing data, identify losses and download the analysis.</p>
            <span class="chip">{len(analysis):,} records</span>
            <span class="chip">{len(columns)} columns</span>
            <span class="chip">{'OEE ready' if has_oee else 'General data analysis'}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    section("Uploaded file", uploaded.name)
    st.caption(f"Current analysis filter context: {len(analysis):,} of {len(df):,} retained records.")
    st.dataframe(raw.head(15), hide_index=True, use_container_width=True)
    section("Performance overview", "Calculated from your uploaded file.")
    if has_oee:
        metrics = [("Overall OEE", "OEE (%)", NAVY), ("Availability", "Availability (%)", BLUE),
                   ("Performance", "Performance (%)", TEAL), ("Quality", "Quality (%)", AMBER)]
        cols = st.columns(4)
        for col, (label, metric, accent) in zip(cols, metrics):
            value = overall_oee_metrics.get(metric, analysis[metric].mean())
            note = "Weighted across valid production" if metric in overall_oee_metrics else "Average across valid records"
            kpi(col, label, f"{value:.1f}%" if pd.notna(value) else "N/A",
                note, accent)
        current_oee = overall_oee_metrics.get("OEE (%)", analysis["OEE (%)"].mean())
        if pd.notna(current_oee):
            gap = current_oee - target_oee
            st.metric("OEE vs user-defined target", f"{current_oee:.1f}%", f"{gap:+.1f} percentage points")
        section("Key findings")
        if has_machine and not machine_summary.empty and "OEE (%)" in machine_summary:
            valid = machine_summary.dropna(subset=["OEE (%)"])
            if not valid.empty:
                best = valid.loc[valid["OEE (%)"].idxmax()]
                worst = valid.loc[valid["OEE (%)"].idxmin()]
                x, y = st.columns(2)
                x.metric("Best machine", str(best[machine_col]), f"{best['OEE (%)']:.1f}% OEE")
                y.metric("Lowest machine", str(worst[machine_col]), f"{worst['OEE (%)']:.1f}% OEE")
        if not downtime_summary.empty:
            st.metric("Main downtime reason", str(downtime_summary.iloc[0][downtime_reason_col]),
                      f"{downtime_summary.iloc[0]['Contribution (%)']:.1f}% of downtime")
    else:
        st.info(
            "Your file is loaded. To calculate OEE, open **Configure data columns** in the left sidebar and map either "
            "the five raw fields (planned time, run time, ideal cycle time, total count and good count), "
            "or existing OEE / Availability / Performance / Quality columns."
        )
        numeric_cols = analysis.select_dtypes(include="number").columns.tolist()
        if numeric_cols:
            st.write("Numeric columns detected:", ", ".join(numeric_cols))
            st.dataframe(analysis[numeric_cols].describe().T, use_container_width=True)
    footer(len(analysis), uploaded.name)


# -------------------------- DATA QUALITY --------------------------

elif page == "Data Quality":
    header("Data Cleaning & Quality", "Review what was standardised, removed, corrected or flagged.")
    review_df = df[df["data_quality_status"] == "Needs Review"].copy()
    q1, q2, q3, q4 = st.columns(4)
    q1.metric("Uploaded rows", f"{original_rows:,}")
    q2.metric("Duplicates removed", f"{duplicates_removed:,}")
    q3.metric("Cleaned rows", f"{len(df):,}")
    q4.metric("Needs review", f"{len(review_df):,}")

    st.markdown("#### Cleaning rules applied")
    st.info(
        "Missing or suspicious production inputs are not guessed or replaced with invented numbers. "
        "They remain visible for review and are excluded from OEE calculations when they affect a required input."
    )
    st.markdown(
        "- Trimmed surrounding whitespace and standardised machine, product and shift labels.\\n"
        "- Removed exact duplicate rows, repeated record IDs, and duplicate production rows after standardising date, text, and numeric formats.\\n"
        "- Flagged similar business records for review instead of deleting them automatically.\\n"
        "- Parsed dates and numeric values; invalid or negative numeric values are flagged.\\n"
        "- Missing or uncertain values are not guessed; they remain missing or are clearly labelled."
    )
    st.markdown("#### Duplicate records detected")
    if duplicate_report.empty:
        st.success("No exact duplicates or repeated record IDs were removed.")
    else:
        st.warning(f"{duplicates_removed:,} duplicate record(s) were removed from the analysis dataset.")
        st.dataframe(duplicate_report, hide_index=True, use_container_width=True)
        st.download_button(
            "Download removed duplicate records (CSV)",
            data=duplicate_report.to_csv(index=False).encode("utf-8-sig"),
            file_name="removed_duplicate_records.csv",
            mime="text/csv",
            key="download_duplicates_page",
            use_container_width=True,
        )
    st.markdown("#### Possible duplicates requiring review")
    if potential_duplicate_report.empty:
        st.success("No possible business duplicates flagged.")
    else:
        st.dataframe(potential_duplicate_report, hide_index=True, use_container_width=True)
    st.markdown("#### Missing values by column")
    missing_report = df.isna().sum()
    missing_report = missing_report[missing_report > 0].rename("Missing values").rename_axis("Column").reset_index()
    if missing_report.empty:
        st.success("No missing values remain in the cleaned table.")
    else:
        st.dataframe(missing_report, hide_index=True, use_container_width=True)

    st.markdown("#### Records requiring review")
    if review_df.empty:
        st.success("All retained records passed the configured quality checks.")
    else:
        st.warning(f"{len(review_df):,} retained record(s) need human review before operational use.")
        st.dataframe(review_df, hide_index=True, use_container_width=True)
        st.download_button(
            "Download review records (CSV)",
            data=review_df.to_csv(index=False).encode("utf-8-sig"),
            file_name="records_needing_review.csv",
            mime="text/csv",
            use_container_width=True,
        )
    st.markdown("#### Cleaned dataset preview")
    st.dataframe(df, hide_index=True, use_container_width=True)
    st.download_button(
        "Download cleaned dataset (CSV)",
        data=df.to_csv(index=False).encode("utf-8-sig"),
        file_name="cleaned_manufacturing_data.csv",
        mime="text/csv",
        use_container_width=True,
    )
    footer(len(df), uploaded.name)


# -------------------------- OEE ANALYSIS --------------------------

elif page == "OEE Analysis":
    header("OEE Analysis", "Availability, performance and quality combine to produce OEE")
    if not has_oee:
        st.warning("OEE columns are not mapped yet. open 'Configure data columns' in the left sidebar and map the required fields.")
    else:
        metric_options = [m for m in ["OEE (%)", "Availability (%)", "Performance (%)", "Quality (%)"] if m in analysis]
        chosen_metric = st.radio("Trend metric", metric_options, horizontal=True)
        view = analysis.copy()
        if has_date:
            st.caption("The production date range is controlled by the shared Global analysis filters in the sidebar.")
        if view.empty:
            st.warning("No records are available for this date range.")
        else:
            # Use weighted OEE components for raw production data so this page
            # agrees with the overall and grouped summaries. Percentage-only
            # uploads fall back to the mean of available record percentages.
            weighted_view_metrics = {}
            hidden_oee_cols = [
                "_OEE_Planned_Minutes", "_OEE_Run_Minutes",
                "_OEE_Ideal_Seconds", "_OEE_Total_Count", "_OEE_Good_Count",
            ]
            if all(c in view.columns for c in hidden_oee_cols):
                totals = view[hidden_oee_cols].sum(min_count=1)
                p_total, r_total = totals["_OEE_Planned_Minutes"], totals["_OEE_Run_Minutes"]
                ideal_total = totals["_OEE_Ideal_Seconds"]
                total_count = totals["_OEE_Total_Count"]
                good_count = totals["_OEE_Good_Count"]
                if pd.notna(p_total) and p_total > 0:
                    weighted_view_metrics["Availability (%)"] = r_total / p_total * 100
                if pd.notna(r_total) and r_total > 0:
                    weighted_view_metrics["Performance (%)"] = ideal_total / (r_total * 60) * 100
                if pd.notna(total_count) and total_count > 0:
                    weighted_view_metrics["Quality (%)"] = good_count / total_count * 100
                if all(k in weighted_view_metrics for k in [
                    "Availability (%)", "Performance (%)", "Quality (%)"
                ]):
                    weighted_view_metrics["OEE (%)"] = (
                        weighted_view_metrics["Availability (%)"]
                        * weighted_view_metrics["Performance (%)"]
                        * weighted_view_metrics["Quality (%)"] / 10000
                    )
            cards = st.columns(4)
            for col, metric in zip(cards, metric_options):
                value = weighted_view_metrics.get(metric, view[metric].mean())
                col.metric(metric.replace(" (%)", ""), f"{value:.1f}%")
            if raw_oee_available and "_OEE_Planned_Minutes" in view:
                valid_oee_rows = int(view["_OEE_Planned_Minutes"].notna().sum())
                excluded_oee_rows = int(len(view) - valid_oee_rows)
                st.caption(
                    f"Calculation coverage: {valid_oee_rows:,} of {len(view):,} retained records "
                    f"included · {excluded_oee_rows:,} excluded because required inputs failed validation. "
                    "Only validated production records contribute to these OEE results."
                )
            else:
                st.caption(
                    "Percentage-only mode: values are summarised from the available uploaded percentage columns."
                )
            section("OEE trend")
            if has_date:
                # Keep a true date axis (so real gaps remain visible), but
                # automatically roll large datasets up to weekly/monthly points.
                trend_source = view.dropna(subset=[date_col, chosen_metric]).copy()
                trend_source["_Trend_Date"] = pd.to_datetime(
                    trend_source[date_col], errors="coerce"
                ).dt.floor("D")
                trend_source = trend_source.dropna(subset=["_Trend_Date"])
                distinct_days = trend_source["_Trend_Date"].nunique()
                suggested = "Daily" if distinct_days <= 90 else ("Weekly" if distinct_days <= 730 else "Monthly")
                granularity = st.selectbox(
                    "Trend detail",
                    ["Auto", "Daily", "Weekly", "Monthly"],
                    index=0,
                    help="Auto keeps daily detail for small files and groups larger files to keep the chart readable. The x-axis always preserves real calendar time gaps.",
                    key="oee_trend_granularity",
                )
                bucket = suggested if granularity == "Auto" else granularity
                if bucket == "Daily":
                    trend_source["_Trend_Period"] = trend_source["_Trend_Date"]
                    period_label = "day"
                    date_format = "%d %b %Y"
                elif bucket == "Weekly":
                    trend_source["_Trend_Period"] = trend_source["_Trend_Date"].dt.to_period("W").dt.start_time
                    period_label = "week"
                    date_format = "%d %b %Y"
                else:
                    trend_source["_Trend_Period"] = trend_source["_Trend_Date"].dt.to_period("M").dt.start_time
                    period_label = "month"
                    date_format = "%b %Y"
                if all(c in trend_source.columns for c in hidden_oee_cols):
                    trend = (
                        trend_source.groupby("_Trend_Period", as_index=False)[hidden_oee_cols]
                        .sum(min_count=1)
                        .sort_values("_Trend_Period")
                    )
                    p = trend["_OEE_Planned_Minutes"]
                    r = trend["_OEE_Run_Minutes"]
                    ideal = trend["_OEE_Ideal_Seconds"]
                    total = trend["_OEE_Total_Count"]
                    good = trend["_OEE_Good_Count"]
                    trend["Availability (%)"] = (r / p * 100).where(p > 0)
                    trend["Performance (%)"] = (ideal / (r * 60) * 100).where(r > 0)
                    trend["Quality (%)"] = (good / total * 100).where(total > 0)
                    trend["OEE (%)"] = (
                        trend["Availability (%)"] * trend["Performance (%)"]
                        * trend["Quality (%)"] / 10000
                    )
                    trend["Records"] = trend_source.groupby("_Trend_Period")[chosen_metric].count().values
                else:
                    trend = (
                        trend_source.groupby("_Trend_Period", as_index=False)
                        .agg(**{chosen_metric: (chosen_metric, "mean"), "Records": (chosen_metric, "size")})
                        .sort_values("_Trend_Period")
                    )

                if trend.empty:
                    st.info("There are no valid values for this metric in the selected date range.")
                else:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=trend["_Trend_Period"],
                        y=trend[chosen_metric],
                        mode="lines+markers",
                        name=chosen_metric,
                        line=dict(color=BLUE, width=3),
                        marker=dict(size=8 if bucket != "Daily" else 7, color=BLUE, line=dict(width=1.2, color="white")),
                        connectgaps=False,
                        customdata=trend[["Records"]],
                        hovertemplate="%{x|" + date_format + "}<br>" + chosen_metric + ": %{y:.1f}%<br>Records: %{customdata[0]}<extra></extra>",
                    ))
                    # The reference line represents the weighted result for the
                    # entire selected date range, not an unweighted mean of buckets.
                    average_value = float(
                        weighted_view_metrics.get(chosen_metric, view[chosen_metric].mean())
                    )
                    fig.add_hline(
                        y=average_value, line_dash="dash", line_color=SLATE,
                        annotation_text=f"Selected-period result: {average_value:.1f}%",
                        annotation_position="top left",
                    )
                    fig.add_hline(
                        y=target_oee, line_dash="dot", line_color=AMBER,
                        annotation_text=f"User target: {target_oee}%",
                        annotation_position="bottom right",
                    )
                    span_days = (trend["_Trend_Period"].max() - trend["_Trend_Period"].min()).days
                    tick_format = "%b %Y" if span_days > 90 else "%d %b"
                    fig.update_xaxes(
                        title="Production date", type="date", tickformat=tick_format,
                        tickangle=-25, automargin=True, nticks=8,
                    )
                    fig.update_yaxes(
                        title=chosen_metric, range=[0, 100], ticksuffix="%",
                        dtick=20, rangemode="tozero",
                    )
                    fig.update_layout(hovermode="closest", showlegend=False)
                    st.caption(
                        f"{bucket} average · {len(trend):,} plotted {period_label}(s) from "
                        f"{trend['_Trend_Period'].min():%d %b %Y} to "
                        f"{trend['_Trend_Period'].max():%d %b %Y} · actual calendar spacing retained"
                    )
                    st.plotly_chart(tidy(fig, 430), use_container_width=True)
                    st.caption("The chart shows one trend view to avoid duplicate visualisations.")
            else:
                st.info("Add/map a date column to display a time trend.")
            if "Performance (%)" in view:
                over_perf = int((view["Performance (%)"] > 100).sum())
                if over_perf:
                    st.warning(f"{over_perf:,} selected record(s) have Performance above 100%. They are retained and flagged; verify ideal cycle time and source time units.")
            if "OEE (%)" in view:
                st.caption(f"Benchmark comparison uses the user-defined target of {target_oee}% (set in the sidebar).")
            section("OEE components")
            component_cols = [m for m in ["Availability (%)", "Performance (%)", "Quality (%)"] if m in view]
            if component_cols:
                component_values = pd.DataFrame({
                    "Component": component_cols,
                    "Average (%)": [
                        weighted_view_metrics.get(m, view[m].mean()) for m in component_cols
                    ],
                })
                fig = px.bar(component_values, x="Component", y="Average (%)",
                             text_auto=".1f", color="Component",
                             color_discrete_sequence=[BLUE, TEAL, AMBER])
                st.plotly_chart(tidy(fig, 280), use_container_width=True)
            st.dataframe(view[[c for c in [date_col, machine_col, "Availability (%)", "Performance (%)",
                                          "Quality (%)", "OEE (%)"] if c and c in view]],
                         hide_index=True, use_container_width=True)
    footer(len(analysis), uploaded.name)


# -------------------------- MACHINE ANALYSIS --------------------------

elif page == "Machine Analysis":
    header("Machine Analysis", "Compare machine efficiency and identify machines that need attention")
    if not has_machine:
        st.warning("No machine column detected. Map your machine identifier in Configure data columns.")
    elif machine_summary.empty:
        st.info("Map OEE percentage fields or production-time fields to calculate machine OEE.")
    else:
        if "OEE (%)" in machine_summary:
            # Convert nullable values (pd.NA) safely before sending data to Matplotlib.
            ranked = machine_summary.copy()
            ranked["OEE (%)"] = pd.to_numeric(ranked["OEE (%)"], errors="coerce")
            ranked = ranked.dropna(subset=["OEE (%)"])
            ranked = ranked[np.isfinite(ranked["OEE (%)"].astype(float))]
            ranked = ranked.sort_values("OEE (%)", ascending=False)

            if ranked.empty:
                st.info("No valid OEE values are available for the selected machines.")
            else:
                fig, ax = plt.subplots(figsize=(10, 4.5))
                ax.bar(ranked[machine_col].astype(str), ranked["OEE (%)"].astype(float), color=BLUE)
                ax.axhline(float(target_oee), linestyle="--", color=AMBER,
                           label=f"User target {target_oee}%")
                ax.set_ylabel("OEE (%)")
                ax.set_title("OEE by Machine")
                ax.tick_params(axis="x", rotation=30)
                ax.grid(axis="y", alpha=.2)
                ax.legend()
                fig.tight_layout()
                st.pyplot(fig, use_container_width=True)
                plt.close(fig)

                machine_pick = st.selectbox("Select machine", ranked[machine_col].astype(str).tolist())
                selected_machine = ranked[ranked[machine_col].astype(str) == machine_pick].iloc[0]
                st.subheader(f"Machine: {machine_pick}")
                metric_names = [m for m in ["OEE (%)", "Availability (%)", "Performance (%)", "Quality (%)"]
                                if m in ranked]
                metric_cols = st.columns(len(metric_names))
                for col, metric in zip(metric_cols, metric_names):
                    value = pd.to_numeric(pd.Series([selected_machine[metric]]), errors="coerce").iloc[0]
                    col.metric(metric.replace(" (%)", ""),
                               f"{value:.1f}%" if pd.notna(value) else "N/A")
        st.subheader("Machine summary")
        st.dataframe(machine_summary, hide_index=True, use_container_width=True)
    footer(len(analysis), uploaded.name)



# -------------------------- PRODUCTION LINE ANALYSIS --------------------------
elif page == "Line Analysis":
    header("Production Line Analysis", "Compare OEE and output across production lines")
    if not line_col:
        st.info("Map a production-line / work-centre column in Configure data columns.")
    elif line_summary.empty:
        st.info("No line-level results are available for the selected filters.")
    else:
        st.dataframe(line_summary, hide_index=True, use_container_width=True)
        if "OEE (%)" in line_summary:
            _line_plot = line_summary.dropna(subset=["OEE (%)"]).sort_values("OEE (%)")
            if not _line_plot.empty:
                fig, ax = plt.subplots(figsize=(10, 4))
                ax.barh(_line_plot[line_col].astype(str), _line_plot["OEE (%)"], color=TEAL)
                ax.axvline(target_oee, color=AMBER, linestyle="--", label=f"User target {target_oee}%")
                ax.set_xlabel("OEE (%)")
                ax.set_title("OEE by Production Line")
                ax.grid(axis="x", alpha=.2)
                ax.legend()
                fig.tight_layout()
                st.pyplot(fig, use_container_width=True)
                plt.close(fig)
    footer(len(analysis), uploaded.name)


# -------------------------- PRODUCTION ANALYSIS --------------------------

elif page == "Production Analysis":
    header("Production Analysis", "Review total output, good units, rejects, products and shifts")
    production_metrics = [m for m in ["Total Production", "Good Production", "Rejected Production"] if m in analysis]
    if production_metrics:
        totals = analysis[production_metrics].sum(numeric_only=True)
        cols = st.columns(len(production_metrics))
        for col, metric in zip(cols, production_metrics):
            col.metric(metric, f"{totals[metric]:,.0f}")
    else:
        st.info("Map Total production count and Good production count in Configure data columns to show production KPIs.")
    if has_date and "Total Production" in analysis:
        section("Production over time")
        production_columns = [
            m for m in ["Good Production", "Rejected Production"] if m in analysis.columns
        ]
        daily_prod = (
            analysis.dropna(subset=[date_col])
            .groupby(date_col, as_index=False)[production_columns]
            .sum()
            .sort_values(date_col)
        )
        if not daily_prod.empty and production_columns:
            # Use categorical date labels: this prevents long gaps between dates
            # from making bars appear extremely thin on a continuous date axis.
            daily_prod["_date_label"] = pd.to_datetime(
                daily_prod[date_col], errors="coerce"
            ).dt.strftime("%d %b %Y")
            daily_prod = daily_prod.dropna(subset=["_date_label"])

            fig = px.bar(
                daily_prod,
                x="_date_label",
                y=production_columns,
                barmode="stack",
                text_auto=".0f",
                color_discrete_sequence=[TEAL, RED],
                labels={
                    "_date_label": "Production Date",
                    "value": "Units Produced",
                    "variable": "Production Type",
                },
            )
            fig.update_layout(
                height=460,
                bargap=0.22,
                bargroupgap=0.05,
                xaxis_title="Production Date",
                yaxis_title="Units Produced",
                legend_title_text="",
                margin=dict(l=20, r=20, t=35, b=70),
            )
            fig.update_xaxes(
                type="category",
                tickangle=-35,
                categoryorder="array",
                categoryarray=daily_prod["_date_label"].tolist(),
            )
            fig.update_traces(
                width=0.72,
                marker_line_width=0,
                textposition="inside",
                insidetextanchor="middle",
                cliponaxis=False,
            )
            st.plotly_chart(fig, use_container_width=True)
    if not product_summary.empty:
        section("Product performance")
        st.dataframe(product_summary, hide_index=True, use_container_width=True)
        if "OEE (%)" in product_summary:
            _product_chart = product_summary.dropna(subset=["OEE (%)"]).sort_values("OEE (%)")
            if not _product_chart.empty:
                fig, ax = plt.subplots(figsize=(10, 4))
                ax.barh(_product_chart[product_col].astype(str), _product_chart["OEE (%)"], color=TEAL)
                ax.axvline(target_oee, linestyle="--", color=AMBER, label=f"User target {target_oee}%")
                ax.set_xlabel("OEE (%)")
                ax.set_title("OEE by Product")
                ax.grid(axis="x", alpha=.2)
                ax.legend()
                fig.tight_layout()
                st.pyplot(fig, use_container_width=True)
                plt.close(fig)
    if not shift_summary.empty:
        section("Shift performance")
        st.dataframe(shift_summary, hide_index=True, use_container_width=True)
        if "OEE (%)" in shift_summary:
            _shift_chart = shift_summary.dropna(subset=["OEE (%)"]).sort_values("OEE (%)")
            if not _shift_chart.empty:
                fig, ax = plt.subplots(figsize=(8, 3.5))
                ax.bar(_shift_chart[shift_col].astype(str), _shift_chart["OEE (%)"], color=BLUE)
                ax.axhline(target_oee, linestyle="--", color=AMBER, label=f"User target {target_oee}%")
                ax.set_ylabel("OEE (%)")
                ax.set_title("OEE by Shift")
                ax.grid(axis="y", alpha=.2)
                ax.legend()
                fig.tight_layout()
                st.pyplot(fig, use_container_width=True)
                plt.close(fig)
    footer(len(analysis), uploaded.name)



# -------------------------- QUALITY ANALYSIS --------------------------
elif page == "Quality Analysis":
    header("Quality & Rejection Analysis", "Review rejected units, rejection rates and defect categories")
    if "Total Production" not in analysis or "Rejected Production" not in analysis:
        st.info("Map total count and reject count (or good count) to enable quality analysis.")
    else:
        _total_units = analysis["Total Production"].sum(min_count=1)
        _reject_units = analysis["Rejected Production"].sum(min_count=1)
        _good_units = analysis["Good Production"].sum(min_count=1) if "Good Production" in analysis else _total_units-_reject_units
        _reject_rate = _reject_units/_total_units*100 if pd.notna(_total_units) and _total_units else np.nan
        _c1, _c2, _c3 = st.columns(3)
        _c1.metric("Total units", f"{_total_units:,.0f}" if pd.notna(_total_units) else "N/A")
        _c2.metric("Rejected units", f"{_reject_units:,.0f}" if pd.notna(_reject_units) else "N/A")
        _c3.metric("Rejection rate", f"{_reject_rate:.2f}%" if pd.notna(_reject_rate) else "N/A")
        if defect_reason_col and not defect_summary.empty:
            section("Rejected units by defect category")
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.barh(defect_summary["Defect Category"].astype(str), defect_summary["Rejected Production"], color=RED)
            ax.set_xlabel("Rejected units")
            ax.set_title("Rejects by Defect Category")
            ax.grid(axis="x", alpha=.2)
            fig.tight_layout()
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)
            st.dataframe(defect_summary, hide_index=True, use_container_width=True)
        for _label, _group_col in [("Machine", machine_col), ("Shift", shift_col), ("Product", product_col)]:
            if _group_col and _group_col in analysis.columns:
                section(f"Rejection by {_label}")
                _grp = analysis.groupby(_group_col, dropna=False).agg(
                    Total_Units=("Total Production", "sum"),
                    Rejected_Units=("Rejected Production", "sum")
                ).reset_index()
                _grp["Rejection Rate (%)"] = np.where(
                    _grp["Total_Units"] > 0, _grp["Rejected_Units"]/_grp["Total_Units"]*100, np.nan
                )
                st.dataframe(_grp.sort_values("Rejection Rate (%)", ascending=False),
                             hide_index=True, use_container_width=True)
        if all(x in analysis.columns for x in ["_OEE_Cycle_Seconds", "_OEE_Total_Count", "_OEE_Good_Count"]):
            _quality_loss = (
                analysis["_OEE_Cycle_Seconds"] *
                (analysis["_OEE_Total_Count"] - analysis["_OEE_Good_Count"])
            ).sum(min_count=1) / 60
            st.metric("Quality loss (ideal-time equivalent)", f"{_quality_loss:,.1f} minutes" if pd.notna(_quality_loss) else "N/A")
        else:
            st.caption("Time-equivalent quality loss requires ideal cycle time and validated production counts.")
    footer(len(analysis), uploaded.name)


# -------------------------- DOWNTIME ANALYSIS --------------------------

elif page == "Downtime Analysis":
    header("Downtime Analysis", "Understand why machines stop and how much time is lost")
    if "Downtime (Minutes)" not in analysis:
        st.warning("Map a downtime-minutes column in Configure data columns to analyse downtime.")
    else:
        total_down = analysis["Downtime (Minutes)"].sum()
        c1, c2 = st.columns(2)
        c1.metric("Total downtime", f"{total_down:,.1f} minutes")
        c2.metric("Average downtime per record", f"{analysis['Downtime (Minutes)'].mean():,.1f} minutes")
        if not downtime_summary.empty:
            section("Downtime by reason")
            pareto = downtime_summary.sort_values("Downtime (Minutes)", ascending=False).copy()
            fig, ax = plt.subplots(figsize=(11, 5))
            ax.bar(pareto[downtime_reason_col].astype(str), pareto["Downtime (Minutes)"], color=AMBER)
            ax.set_ylabel("Downtime (minutes)")
            ax.set_title("Downtime Pareto by Reason")
            ax.tick_params(axis="x", rotation=35)
            ax.grid(axis="y", alpha=.2)
            ax2 = ax.twinx()
            ax2.plot(range(len(pareto)), pareto["Cumulative Contribution (%)"], color=RED, marker="o")
            ax2.set_ylabel("Cumulative contribution (%)")
            ax2.set_ylim(0, 110)
            fig.tight_layout()
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)
            st.dataframe(pareto, hide_index=True, use_container_width=True)
        elif downtime_reason_col:
            st.info("No downtime reason summary could be calculated.")
        if not downtime_type_summary.empty:
            section("Planned vs unplanned downtime")
            st.dataframe(downtime_type_summary, hide_index=True, use_container_width=True)
        for label, group_col in [("Machine", machine_col), ("Shift", shift_col), ("Product", product_col)]:
            if group_col and group_col in analysis:
                section(f"Downtime by {label.lower()}")
                st.dataframe(grouped_sum(analysis, group_col, "Downtime (Minutes)"), hide_index=True, use_container_width=True)
        if "Minor Stop (Minutes)" in analysis:
            section("Minor-stop analysis")
            st.metric("Total minor-stop time", f"{analysis['Minor Stop (Minutes)'].sum():,.1f} minutes")
            st.caption("Minor stops are shown only when the uploaded source contains a dedicated minor-stop duration field.")
        if has_date:
            daily_down = analysis.dropna(subset=[date_col]).groupby(date_col)["Downtime (Minutes)"].sum().reset_index()
            section("Downtime over time")
            fig = px.line(daily_down, x=date_col, y="Downtime (Minutes)", markers=True,
                          color_discrete_sequence=[AMBER])
            st.plotly_chart(tidy(fig, 300), use_container_width=True)
    footer(len(analysis), uploaded.name)


# -------------------------- LOSS ANALYSIS --------------------------

elif page == "Loss Analysis":
    header("Production Loss Waterfall", "Trace planned production time through availability, performance and quality losses")
    if loss_waterfall is None:
        st.warning(
            "A time-based loss waterfall requires mapped raw inputs: planned time, "
            "run time (or downtime), ideal cycle time, total count and good count. "
            "Percentage-only uploads cannot produce a reliable time waterfall."
        )
    else:
        labels = [
            "Planned\nTime", "Availability\nLoss", "Run\nTime",
            "Performance\nLoss", "Net Operating\nTime", "Quality\nLoss",
            "Fully Productive\nTime",
        ]
        values = [
            loss_waterfall["Planned Production Time"],
            loss_waterfall["Availability Loss"],
            loss_waterfall["Run Time"],
            loss_waterfall["Performance Loss"],
            loss_waterfall["Net Operating Time"],
            loss_waterfall["Quality Loss"],
            loss_waterfall["Fully Productive Time"],
        ]
        # A waterfall chart: total bars start at zero; loss bars float between
        # the preceding and following production-time levels.
        starts = [
            0,
            values[0] - values[1],
            0,
            values[2] - values[3],
            0,
            values[4] - values[5],
            0,
        ]
        heights = [values[0], values[1], values[2], values[3], values[4], values[5], values[6]]
        colors = [NAVY, RED, BLUE, AMBER, TEAL, RED, TEAL]
        fig, ax = plt.subplots(figsize=(12, 5.5))
        for i, (start, height, color) in enumerate(zip(starts, heights, colors)):
            ax.bar(i, height, bottom=start if i in [1, 3, 5] else 0, color=color, width=0.68)
            display_value = height
            y_pos = (start if i in [1, 3, 5] else 0) + height
            ax.text(i, y_pos, f"{display_value:,.1f}", ha="center", va="bottom", fontsize=9)
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, fontsize=9)
        ax.set_ylabel("Time (minutes)")
        ax.set_title("Planned Time → Fully Productive Time", fontsize=14, weight="bold")
        ax.grid(axis="y", alpha=0.25)
        ax.set_axisbelow(True)
        for spine in ["top", "right"]:
            ax.spines[spine].set_visible(False)
        fig.tight_layout()
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

        if min(values[1], values[3], values[5]) < -0.01:
            st.warning("One or more calculated loss components are negative. This usually indicates inconsistent source values or an ideal cycle time that needs review. Interpret the waterfall cautiously.")
        c1, c2, c3 = st.columns(3)
        c1.metric("Planned production time", f"{values[0]:,.1f} min")
        c2.metric("Fully productive time", f"{values[6]:,.1f} min")
        c3.metric("Time converted to good output", f"{(values[6] / values[0] * 100):.1f}%" if values[0] else "N/A")

        reconciliation = loss_waterfall["Reconciliation Difference"]
        if abs(reconciliation) <= max(0.01, values[0] * 0.000001):
            st.success(f"Waterfall reconciles. Difference: {reconciliation:.6f} minutes.")
        else:
            st.error(
                f"Waterfall does not reconcile. Difference: {reconciliation:,.3f} minutes. "
                "Review the uploaded time and production inputs."
            )
        loss_table = pd.DataFrame({
            "Stage": ["Planned Production Time", "Availability Loss", "Run Time", "Performance Loss", "Net Operating Time", "Quality Loss", "Fully Productive Time"],
            "Minutes": values,
        })
        st.dataframe(loss_table, hide_index=True, use_container_width=True)
        st.caption(
            "Net Operating Time is calculated as ideal cycle time × total count. "
            "Fully Productive Time is ideal cycle time × good count. "
            "This time-based waterfall is available only when validated raw production inputs are present."
        )
    footer(len(analysis), uploaded.name)


# -------------------------- REPORTS & DOWNLOADS --------------------------

elif page == "Reports":
    header("Reports & Downloads", "Preview and download your cleaned data and analysis results")
    report_options = {
        "Original uploaded data": raw_original,
        "Cleaned data": df,
        "Analysed data": analysis,
        "Removed duplicate records": duplicate_report,
        "Possible duplicates for review": potential_duplicate_report,
    }
    if not machine_summary.empty:
        report_options["Machine summary"] = machine_summary
    if not product_summary.empty:
        report_options["Product summary"] = product_summary
    if not shift_summary.empty:
        report_options["Shift summary"] = shift_summary
    if not line_summary.empty:
        report_options["Production line summary"] = line_summary
    if not defect_summary.empty:
        report_options["Defect category summary"] = defect_summary
    if not downtime_type_summary.empty:
        report_options["Downtime type summary"] = downtime_type_summary
    if not downtime_summary.empty:
        report_options["Downtime summary"] = downtime_summary

    st.info("Exact duplicates, repeated record IDs, and fully matching production rows after standardisation are removed. Partial business-key matches are flagged for human review.")
    with st.expander("OEE methodology, assumptions and limitations", expanded=False):
        st.markdown("""
        **Formulas**
        - Availability = Run Time ÷ Planned Production Time × 100
        - Performance = (Ideal Cycle Time × Total Count) ÷ Run Time × 100
        - Quality = Good Count ÷ Total Count × 100
        - OEE = Availability × Performance × Quality ÷ 10,000

        **Units:** planned/run/downtime are minutes; ideal cycle time is seconds per unit.

        **Limitations and safeguards**
        - Critical missing values are not invented. Rows with invalid required fields are excluded from raw-input OEE calculations and remain in the review report.
        - Performance above 100% is retained and flagged for investigation; check cycle time, runtime units and count definitions.
        - Percentage-only data cannot be correctly reweighted without underlying numerators and denominators; group summaries use record averages and are labelled accordingly.
        - Planned/unplanned downtime and defect-category results require those fields in the uploaded data.
        - Minor-stop analysis requires a dedicated minor-stop duration field. Timestamp-based micro-stop analysis is not inferred.
        - The OEE target is a user-selected comparison benchmark, not a universal or automatically assumed standard.
        """)
    if raw_oee_available and overall_oee_metrics:
        with st.expander("KPI numerator / denominator audit", expanded=False):
            _valid_audit = analysis["_OEE_Planned_Minutes"].notna()
            _audit = pd.DataFrame([
                ["Availability", analysis.loc[_valid_audit, "_OEE_Run_Minutes"].sum(),
                 analysis.loc[_valid_audit, "_OEE_Planned_Minutes"].sum(),
                 overall_oee_metrics["Availability (%)"]],
                ["Performance", analysis.loc[_valid_audit, "_OEE_Ideal_Seconds"].sum(),
                 analysis.loc[_valid_audit, "_OEE_Run_Minutes"].sum()*60,
                 overall_oee_metrics["Performance (%)"]],
                ["Quality", analysis.loc[_valid_audit, "_OEE_Good_Count"].sum(),
                 analysis.loc[_valid_audit, "_OEE_Total_Count"].sum(),
                 overall_oee_metrics["Quality (%)"]],
            ], columns=["KPI", "Numerator", "Denominator", "Result (%)"])
            st.dataframe(_audit, hide_index=True, use_container_width=True)

    with st.expander("OEE methodology, assumptions and calculation audit", expanded=False):
        st.markdown(
            """
            **Formulas**
            - Availability = Run Time ÷ Planned Production Time × 100
            - Performance = (Ideal Cycle Time × Total Count) ÷ Run Time × 100
            - Quality = Good Count ÷ Total Count × 100
            - OEE = Availability × Performance × Quality ÷ 10,000

            **Time units used by this application:** planned/run/downtime in minutes; ideal cycle time in seconds per unit.

            **Important limitations**
            - Percentage-only input files cannot be correctly reweighted without underlying time and count numerators/denominators; group values are shown as record averages.
            - Missing critical inputs are not invented. Rows with invalid required inputs are excluded from raw-input OEE calculations and remain visible in Data Quality.
            - Performance above 100% is retained and flagged for investigation; verify ideal cycle time, runtime units and count definitions.
            - Planned/unplanned downtime and defect-category analysis appear only when the corresponding source fields are mapped.
            - Minor-stop analysis requires a dedicated minor-stop duration field. Timestamp-level micro-stop analysis is not inferred.
            - The user-defined OEE target is a comparison benchmark chosen in the sidebar, not a claim that the dataset or industry standard has that target.
            """
        )
    if raw_oee_available and overall_oee_metrics:
        with st.expander("Selected-filter KPI numerator / denominator audit", expanded=False):
            valid_audit = analysis["_OEE_Planned_Minutes"].notna()
            audit = pd.DataFrame([
                ["Availability", analysis.loc[valid_audit, "_OEE_Run_Minutes"].sum(), analysis.loc[valid_audit, "_OEE_Planned_Minutes"].sum(), overall_oee_metrics["Availability (%)"]],
                ["Performance", analysis.loc[valid_audit, "_OEE_Ideal_Seconds"].sum(), analysis.loc[valid_audit, "_OEE_Run_Minutes"].sum()*60, overall_oee_metrics["Performance (%)"]],
                ["Quality", analysis.loc[valid_audit, "_OEE_Good_Count"].sum(), analysis.loc[valid_audit, "_OEE_Total_Count"].sum(), overall_oee_metrics["Quality (%)"]],
            ], columns=["KPI", "Numerator", "Denominator", "Result (%)"])
            st.dataframe(audit, hide_index=True, use_container_width=True)
    report_name = st.selectbox("Choose report to preview", list(report_options))
    report_df = report_options[report_name]
    st.caption(f"{len(report_df):,} rows | {len(report_df.columns)} columns")
    st.dataframe(report_df, hide_index=True, use_container_width=True)

    csv_data = report_df.copy()
    if date_col and date_col in csv_data:
        csv_data[date_col] = pd.to_datetime(csv_data[date_col], errors="coerce").dt.strftime("%d-%m-%Y")
    review_df = df[df["data_quality_status"] == "Needs Review"].copy()
    st.caption(
        f"Valid records: {len(df) - len(review_df):,} | "
        f"Records requiring review: {len(review_df):,}"
    )
    st.download_button(
        "⬇️ Download records needing review (CSV)",
        data=review_df.to_csv(index=False).encode("utf-8-sig"),
        file_name="records_needing_review.csv",
        mime="text/csv",
        use_container_width=True,
    )

    st.download_button(
        "⬇️ Download selected report (CSV)",
        data=csv_data.to_csv(index=False).encode("utf-8-sig"),
        file_name=f"{re.sub(r'[^a-zA-Z0-9_-]+', '_', report_name.lower()).strip('_')}.csv",
        mime="text/csv",
        use_container_width=True,
    )

    cleaned_export = df.copy()
    analysis_export = analysis.copy()
    if date_col:
        cleaned_export[date_col] = pd.to_datetime(cleaned_export[date_col], errors="coerce").dt.strftime("%d-%m-%Y")
        analysis_export[date_col] = pd.to_datetime(analysis_export[date_col], errors="coerce").dt.strftime("%d-%m-%Y")

    quality_export = df[["data_quality_status", "quality_issues"]].copy()
    all_sheets = {
        "Original data": raw_original,
        "Data quality": quality_export,
        "Cleaned data": cleaned_export,
        "Analysed data": analysis_export,
    }
    if not machine_summary.empty:
        all_sheets["Machine summary"] = machine_summary
    if not product_summary.empty:
        all_sheets["Product summary"] = product_summary
    if not shift_summary.empty:
        all_sheets["Shift summary"] = shift_summary
    if not line_summary.empty:
        all_sheets["Line summary"] = line_summary
    if not defect_summary.empty:
        all_sheets["Defect summary"] = defect_summary
    if not downtime_type_summary.empty:
        all_sheets["Downtime type"] = downtime_type_summary
    if not downtime_summary.empty:
        all_sheets["Downtime summary"] = downtime_summary

    st.download_button(
        "⬇️ Download complete analysis (Excel)",
        data=excel_download(all_sheets),
        file_name="manufacturing_oee_analysis.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )
    footer(len(analysis), uploaded.name)