import math
import pandas as pd
import requests
import streamlit as st
import os

# ----------------------------------------------------------------
# Page config — MUST be first streamlit command
# ----------------------------------------------------------------
st.set_page_config(
    page_title="DiabetesIQ — Risk Predictor",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed",
)

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")


def check_api_health():
    try:
        r = requests.get(f"{API_URL}/health", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


# ----------------------------------------------------------------
# CSS — full custom design system (Original Design)
# ----------------------------------------------------------------
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=Space+Grotesk:wght@500;700&display=swap');

/* ── Reset & shell ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"] {
    background: #0F1B2D !important;
    font-family: 'DM Sans', sans-serif;
    color: #E2EAF4;
}

[data-testid="stAppViewContainer"] > .main {
    background: #0F1B2D !important;
}

/* Hide streamlit chrome */
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"] { display: none !important; }

/* ── Layout wrapper ── */
.block-container {
    max-width: 1080px !important;
    padding: 2rem 2rem 4rem !important;
    margin: 0 auto;
}

/* ── Top bar ── */
.topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 0 2rem 0;
    border-bottom: 1px solid #1E3050;
    margin-bottom: 2.5rem;
}
.topbar-brand {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.4rem;
    font-weight: 700;
    color: #00BFA6;
    letter-spacing: -0.5px;
}
.topbar-brand span { color: #E2EAF4; }
.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 0.75rem;
    font-weight: 500;
    padding: 5px 12px;
    border-radius: 999px;
    letter-spacing: 0.3px;
}
.status-online  { background: #0D2E1F; color: #00BFA6; border: 1px solid #00BFA6; }
.status-offline { background: #2E0D0D; color: #F87171; border: 1px solid #F87171; }

/* ── Hero ── */
.hero {
    text-align: center;
    margin-bottom: 3rem;
}
.hero-eyebrow {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #00BFA6;
    margin-bottom: 0.75rem;
}
.hero-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: clamp(1.8rem, 4vw, 2.8rem);
    font-weight: 700;
    color: #F0F4F8;
    line-height: 1.15;
    margin-bottom: 0.75rem;
    letter-spacing: -1px;
}
.hero-title em { color: #00BFA6; font-style: normal; }
.hero-sub {
    font-size: 0.95rem;
    color: #7A94B0;
    max-width: 480px;
    margin: 0 auto;
    line-height: 1.6;
}

/* ── Card ── */
.card {
    background: #162236;
    border: 1px solid #1E3050;
    border-radius: 14px;
    padding: 1.75rem;
    margin-bottom: 1.25rem;
}
.card-title {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    color: #4A6785;
    margin-bottom: 1.25rem;
}

/* ── Field labels ── */
.field-label {
    font-size: 0.8rem;
    font-weight: 500;
    color: #7A94B0;
    margin-bottom: 3px;
    display: block;
}
.field-hint {
    font-size: 0.7rem;
    color: #3D5A78;
    margin-top: 2px;
}

/* ── Streamlit widget overrides ── */
[data-testid="stNumberInput"] input,
[data-testid="stTextInput"] input {
    background: #0F1B2D !important;
    border: 1px solid #1E3050 !important;
    border-radius: 8px !important;
    color: #E2EAF4 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.9rem !important;
    padding: 0.5rem 0.75rem !important;
    transition: border-color 0.2s;
}
[data-testid="stNumberInput"] input:focus {
    border-color: #00BFA6 !important;
    box-shadow: 0 0 0 2px rgba(0,191,166,0.12) !important;
    outline: none !important;
}
[data-testid="stNumberInput"] label,
[data-testid="stSlider"] label { display: none !important; }
[data-testid="stNumberInput"] button {
    background: #1E3050 !important;
    border: none !important;
    color: #7A94B0 !important;
}
[data-testid="stNumberInput"] button:hover { color: #00BFA6 !important; }

/* ── Slider ── */
[data-testid="stSlider"] > div > div > div {
    background: #1E3050 !important;
}
[data-testid="stSlider"] > div > div > div > div {
    background: #00BFA6 !important;
}

/* ── Button ── */
div.stButton > button {
    width: 100%;
    background: #00BFA6 !important;
    color: #0F1B2D !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 0.95rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.3px !important;
    padding: 0.8rem 2rem !important;
    border: none !important;
    border-radius: 10px !important;
    cursor: pointer;
    transition: all 0.2s ease !important;
}
div.stButton > button:hover {
    background: #00D4B8 !important;
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(0,191,166,0.25) !important;
}
div.stButton > button:active { transform: translateY(0); }

/* ── Result section ── */
.result-header {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #4A6785;
    margin-bottom: 1.5rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid #1E3050;
}

/* ── Gauge ── */
.gauge-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
}
.gauge-svg { overflow: visible; }
.gauge-label {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #4A6785;
}

/* ── Verdict ── */
.verdict-wrap {
    display: flex;
    flex-direction: column;
    justify-content: center;
    height: 100%;
    padding-left: 1rem;
}
.verdict-risk-badge {
    display: inline-block;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    padding: 4px 10px;
    border-radius: 4px;
    margin-bottom: 0.75rem;
}
.badge-HIGH   { background: #2E0D0D; color: #F87171; border: 1px solid #F87171; }
.badge-MEDIUM { background: #2E1D0D; color: #FBBF24; border: 1px solid #FBBF24; }
.badge-LOW    { background: #0D2E1F; color: #34D399; border: 1px solid #34D399; }

.verdict-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.8rem;
    font-weight: 700;
    line-height: 1.1;
    margin-bottom: 0.5rem;
    color: #F0F4F8;
}
.verdict-message {
    font-size: 0.85rem;
    color: #7A94B0;
    line-height: 1.6;
    margin-bottom: 1.25rem;
}

/* ── Stat pills ── */
.stat-row { display: flex; gap: 0.75rem; flex-wrap: wrap; }
.stat-pill {
    background: #0F1B2D;
    border: 1px solid #1E3050;
    border-radius: 8px;
    padding: 0.6rem 1rem;
    display: flex;
    flex-direction: column;
    gap: 2px;
    min-width: 110px;
}
.stat-pill-label {
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #4A6785;
}
.stat-pill-value {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.2rem;
    font-weight: 700;
    color: #F0F4F8;
}

/* ── Model footnote ── */
.model-footnote {
    font-size: 0.7rem;
    color: #3D5A78;
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid #1E3050;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.model-footnote span { color: #4A6785; }

/* ── Alert ── */
.alert-offline {
    background: #2E0D0D;
    border: 1px solid #7F1D1D;
    border-radius: 10px;
    padding: 1rem 1.25rem;
    color: #FCA5A5;
    font-size: 0.85rem;
    margin-bottom: 1rem;
}

/* ── Metrics row ── */
.metrics-row {
    display: flex;
    gap: 1rem;
    margin-bottom: 2.5rem;
    justify-content: center;
}
.metric-chip {
    background: #162236;
    border: 1px solid #1E3050;
    border-radius: 10px;
    padding: 0.75rem 1.25rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
    min-width: 90px;
}
.metric-chip-val {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.25rem;
    font-weight: 700;
    color: #00BFA6;
}
.metric-chip-label {
    font-size: 0.65rem;
    font-weight: 500;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: #4A6785;
}

/* Streamlit column gap fix */
[data-testid="column"] { padding: 0 0.4rem !important; }
</style>
""",
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------
# Top bar
# ----------------------------------------------------------------
api_online = check_api_health()
status_html = (
    '<span class="status-pill status-online">● API Online</span>'
    if api_online
    else '<span class="status-pill status-offline">● API Offline</span>'
)
st.markdown(
    f"""
<div class="topbar">
    <div class="topbar-brand">Diabetes<span>IQ</span></div>
    {status_html}
</div>
""",
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------
# Hero
# ----------------------------------------------------------------
st.markdown(
    """
<div class="hero">
    <div class="hero-eyebrow">Clinical Decision Support</div>
    <div class="hero-title">Know your <em>diabetes risk</em><br>before it knows you.</div>
    <div class="hero-sub">
        Enter eight standard lab values. Our model — trained on 768 clinical
        cases — returns a risk score in under a second.
    </div>
</div>
""",
    unsafe_allow_html=True,
)

# Model performance chips
st.markdown(
    """
<div class="metrics-row">
    <div class="metric-chip">
        <div class="metric-chip-val">77%</div>
        <div class="metric-chip-label">Accuracy</div>
    </div>
    <div class="metric-chip">
        <div class="metric-chip-val">76%</div>
        <div class="metric-chip-label">Recall</div>
    </div>
    <div class="metric-chip">
        <div class="metric-chip-val">0.83</div>
        <div class="metric-chip-label">ROC-AUC</div>
    </div>
    <div class="metric-chip">
        <div class="metric-chip-val">768</div>
        <div class="metric-chip-label">Training cases</div>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

if not api_online:
    st.markdown(
        """
    <div class="alert-offline">
        ⚠️  FastAPI server is not reachable. Start it with:
        <code style="background:#1a0000;padding:2px 6px;border-radius:4px;">
        cd api && uvicorn main:app --reload
        </code>
    </div>
    """,
        unsafe_allow_html=True,
    )

# ----------------------------------------------------------------
# Input cards — two columns
# ----------------------------------------------------------------
st.markdown(
    '<div class="card"><div class="card-title">Blood Chemistry</div>',
    unsafe_allow_html=True,
)
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(
        '<span class="field-label">Glucose <span style="color:#3D5A78">(mg/dL)</span></span>',
        unsafe_allow_html=True,
    )
    glucose = st.number_input(
        "glucose",
        min_value=0,
        max_value=300,
        value=120,
        step=1,
        label_visibility="collapsed",
    )
    st.markdown(
        '<span class="field-hint">Fasting plasma glucose. Normal ≤ 140</span>',
        unsafe_allow_html=True,
    )

with c2:
    st.markdown(
        '<span class="field-label">Insulin <span style="color:#3D5A78">(mu U/ml)</span></span>',
        unsafe_allow_html=True,
    )
    insulin = st.number_input(
        "insulin",
        min_value=0,
        max_value=900,
        value=80,
        step=1,
        label_visibility="collapsed",
    )
    st.markdown(
        '<span class="field-hint">2-hr serum insulin. Enter 0 if unknown</span>',
        unsafe_allow_html=True,
    )

with c3:
    st.markdown(
        '<span class="field-label">Blood Pressure <span style="color:#3D5A78">(mmHg)</span></span>',
        unsafe_allow_html=True,
    )
    blood_pressure = st.number_input(
        "bp",
        min_value=0,
        max_value=200,
        value=70,
        step=1,
        label_visibility="collapsed",
    )
    st.markdown(
        '<span class="field-hint">Diastolic reading. Normal 60–80</span>',
        unsafe_allow_html=True,
    )

st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    '<div class="card"><div class="card-title">Physical Measurements</div>',
    unsafe_allow_html=True,
)
c4, c5, c6 = st.columns(3)

with c4:
    st.markdown(
        '<span class="field-label">BMI <span style="color:#3D5A78">(kg/m²)</span></span>',
        unsafe_allow_html=True,
    )
    bmi = st.number_input(
        "bmi",
        min_value=0.0,
        max_value=70.0,
        value=25.0,
        step=0.1,
        format="%.1f",
        label_visibility="collapsed",
    )
    st.markdown(
        '<span class="field-hint">Healthy 18.5–24.9 · Obese ≥ 30</span>',
        unsafe_allow_html=True,
    )

with c5:
    st.markdown(
        '<span class="field-label">Skin Thickness <span style="color:#3D5A78">(mm)</span></span>',
        unsafe_allow_html=True,
    )
    skin_thickness = st.number_input(
        "skin",
        min_value=0,
        max_value=100,
        value=20,
        step=1,
        label_visibility="collapsed",
    )
    st.markdown(
        '<span class="field-hint">Tricep skinfold. Enter 0 if unknown</span>',
        unsafe_allow_html=True,
    )

with c6:
    st.markdown(
        '<span class="field-label">Pregnancies</span>', unsafe_allow_html=True
    )
    pregnancies = st.number_input(
        "preg",
        min_value=0,
        max_value=20,
        value=1,
        step=1,
        label_visibility="collapsed",
    )
    st.markdown(
        '<span class="field-hint">Total number of pregnancies</span>',
        unsafe_allow_html=True,
    )

st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    '<div class="card"><div class="card-title">Patient History</div>',
    unsafe_allow_html=True,
)
c7, c8 = st.columns(2)

with c7:
    st.markdown(
        '<span class="field-label">Age <span style="color:#3D5A78">(years)</span></span>',
        unsafe_allow_html=True,
    )
    age = st.number_input(
        "age",
        min_value=1,
        max_value=120,
        value=30,
        step=1,
        label_visibility="collapsed",
    )
    st.markdown(
        '<span class="field-hint">Patient age in years</span>', unsafe_allow_html=True
    )

with c8:
    st.markdown(
        '<span class="field-label">Diabetes Pedigree Function</span>',
        unsafe_allow_html=True,
    )
    dpf = st.number_input(
        "dpf",
        min_value=0.0,
        max_value=3.0,
        value=0.500,
        step=0.001,
        format="%.3f",
        label_visibility="collapsed",
    )
    st.markdown(
        '<span class="field-hint">Genetic risk score — based on family history</span>',
        unsafe_allow_html=True,
    )

st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------------------------------------------
# Predict button
# ----------------------------------------------------------------
_, btn_col, _ = st.columns([1, 2, 1])
with btn_col:
    clicked = st.button("Run Risk Assessment →")

# ----------------------------------------------------------------
# Result
# ----------------------------------------------------------------
if clicked:
    if not api_online:
        st.markdown(
            '<div class="alert-offline">⚠️ API is offline. Cannot run prediction.</div>',
            unsafe_allow_html=True,
        )
        st.stop()

    payload = {
        "Pregnancies": pregnancies,
        "Glucose": glucose,
        "BloodPressure": blood_pressure,
        "SkinThickness": skin_thickness,
        "Insulin": insulin,
        "BMI": bmi,
        "DiabetesPedigreeFunction": dpf,
        "Age": age,
    }

    with st.spinner("Analysing..."):
        try:
            resp = requests.post(f"{API_URL}/predict", json=payload, timeout=10)
            resp.raise_for_status()
            r = resp.json()

            prob_d = float(r["probability_diabetes"])  # e.g. 83.45
            prob_h = float(r["probability_healthy"])
            risk = str(r["risk_level"])  # HIGH / MEDIUM / LOW
            label = str(r["prediction_label"])
            message = str(r["message"])
            version = str(r["model_version"])
            confidence = float(r.get("confidence", prob_d))

            # ── colour tokens by risk ──
            if risk == "HIGH":
                arc_color = "#F87171"
                badge_class = "badge-HIGH"
                verdict_color = "#F87171"
            elif risk == "MEDIUM":
                arc_color = "#FBBF24"
                badge_class = "badge-MEDIUM"
                verdict_color = "#FBBF24"
            else:
                arc_color = "#34D399"
                badge_class = "badge-LOW"
                verdict_color = "#34D399"

            # ── SVG gauge calculation ──
            R = 70  # radius
            CX, CY = 90, 90  # centre
            START_DEG = 225
            SWEEP_DEG = 270

            angle = START_DEG + (prob_d / 100.0) * SWEEP_DEG
            end_rad = math.radians(angle)
            ex = CX + R * math.cos(end_rad)
            ey = CY + R * math.sin(end_rad)
            large_arc = 1 if (prob_d / 100.0) * SWEEP_DEG > 180 else 0

            start_rad = math.radians(START_DEG)
            sx = CX + R * math.cos(start_rad)
            sy = CY + R * math.sin(start_rad)

            end_full_rad = math.radians(START_DEG + SWEEP_DEG)
            fx = CX + R * math.cos(end_full_rad)
            fy = CY + R * math.sin(end_full_rad)

            fill_path = (
                f'<path d="M {sx:.1f} {sy:.1f} A {R} {R} 0 {large_arc} 1 {ex:.1f} {ey:.1f}" '
                f'fill="none" stroke="{arc_color}" stroke-width="10" stroke-linecap="round"/>'
                if prob_d >= 1
                else ""
            )

            gauge_svg = f"""<svg class="gauge-svg" width="180" height="165" viewBox="0 0 180 165">
              <path d="M {sx:.1f} {sy:.1f} A {R} {R} 0 1 1 {fx:.1f} {fy:.1f}" fill="none" stroke="#1E3050" stroke-width="10" stroke-linecap="round"/>
              {fill_path}
              <text x="90" y="86" text-anchor="middle" font-family="Space Grotesk, sans-serif" font-size="26" font-weight="700" fill="{arc_color}">{prob_d:.0f}%</text>
              <text x="90" y="106" text-anchor="middle" font-family="DM Sans, sans-serif" font-size="9" font-weight="500" fill="#4A6785" letter-spacing="2">DIABETES PROB.</text>
            </svg>"""

            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown(
                '<div class="result-header">Assessment Result</div>',
                unsafe_allow_html=True,
            )

            gcol, vcol = st.columns([1, 2])

            with gcol:
                st.markdown(
                    f'<div class="gauge-wrap">{gauge_svg}<div class="gauge-label">Risk Meter</div></div>',
                    unsafe_allow_html=True,
                )

            with vcol:
                st.markdown(
                    f"""
                <div class="verdict-wrap">
                    <div>
                        <span class="verdict-risk-badge {badge_class}">{risk} RISK</span>
                    </div>
                    <div class="verdict-title" style="color:{verdict_color};">{label}</div>
                    <div class="verdict-message">{message}</div>
                    <div class="stat-row">
                        <div class="stat-pill">
                            <div class="stat-pill-label">Diabetes</div>
                            <div class="stat-pill-value">{prob_d:.1f}%</div>
                        </div>
                        <div class="stat-pill">
                            <div class="stat-pill-label">Healthy</div>
                            <div class="stat-pill-value">{prob_h:.1f}%</div>
                        </div>
                        <div class="stat-pill">
                            <div class="stat-pill-label">Confidence</div>
                            <div class="stat-pill-value">{confidence:.1f}%</div>
                        </div>
                    </div>
                    <div class="model-footnote">
                        <span>Model v{version}</span> · Random Forest ·
                        <span>For educational use only — not a medical diagnosis</span>
                    </div>
                </div>
                """,
                    unsafe_allow_html=True,
                )

            st.markdown("</div>", unsafe_allow_html=True)

        except requests.exceptions.ConnectionError:
            st.markdown(
                '<div class="alert-offline">⚠️ Lost connection to API.</div>',
                unsafe_allow_html=True,
            )
        except Exception as e:
            st.markdown(
                f'<div class="alert-offline">⚠️ Error: {e}</div>',
                unsafe_allow_html=True,
            )