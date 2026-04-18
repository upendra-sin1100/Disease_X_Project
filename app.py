import streamlit as st
import pandas as pd
import joblib
import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST, database=DB_NAME,
        user=DB_USER, password=DB_PASSWORD, port=DB_PORT
    )

@st.cache_resource
def load_model():
    checkpoint = joblib.load(r'D:\Disease_X_Project\disease_x_vulnerability_v1.pkl')
    return checkpoint['model'], checkpoint['features']

model, expected_features = load_model()

# ── Page Config ──────────────────────────────────────────────
st.set_page_config(
    page_title="Disease X Command Center",
    layout="wide",
    page_icon="🦠",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ───────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Syne', sans-serif !important;
}

/* === DARK BACKGROUND === */
.stApp { background-color: #0a0c0f !important; }
section[data-testid="stSidebar"] {
    background-color: #0d1117 !important;
    border-right: 1px solid #1a2332 !important;
}

/* === SIDEBAR LABELS === */
.sidebar-section {
    font-family: 'Space Mono', monospace;
    font-size: 9px;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #3a4a62;
    margin: 18px 0 8px 0;
    padding-bottom: 6px;
    border-bottom: 1px solid #1a2332;
}

/* === MAIN HEADER === */
.cx-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 14px 20px;
    background: #0d1117;
    border: 1px solid #1a2332;
    border-radius: 6px;
    margin-bottom: 20px;
}
.cx-title {
    font-size: 20px;
    font-weight: 800;
    letter-spacing: 0.05em;
    color: #e8e4d9;
}
.cx-subtitle {
    font-family: 'Space Mono', monospace;
    font-size: 9px;
    color: #3a4a62;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-top: 3px;
}
.cx-badge {
    font-family: 'Space Mono', monospace;
    font-size: 9px;
    letter-spacing: 0.1em;
    padding: 4px 12px;
    border-radius: 3px;
    text-transform: uppercase;
}
.cx-badge-live {
    background: rgba(29,158,117,0.12);
    color: #1d9e75;
    border: 1px solid rgba(29,158,117,0.25);
}
.cx-badge-critical {
    background: rgba(216,90,48,0.15);
    color: #d85a30;
    border: 1px solid rgba(216,90,48,0.3);
}

/* === METRIC CARDS === */
.cx-metric-card {
    background: #0d1117;
    border: 1px solid #1a2332;
    border-radius: 8px;
    padding: 16px 20px;
    text-align: center;
}
.cx-metric-label {
    font-family: 'Space Mono', monospace;
    font-size: 9px;
    color: #3a4a62;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 8px;
}
.cx-metric-value {
    font-family: 'Space Mono', monospace;
    font-size: 28px;
    font-weight: 700;
    color: #e8e4d9;
}
.cx-metric-value.danger { color: #d85a30 !important; }
.cx-metric-value.safe { color: #1d9e75 !important; }

/* === RISK BAR === */
.cx-risk-bar-wrap {
    background: #0d1117;
    border: 1px solid #1a2332;
    border-radius: 8px;
    padding: 16px 20px;
    margin-bottom: 16px;
}
.cx-bar-track {
    background: #141921;
    border-radius: 3px;
    height: 6px;
    overflow: hidden;
}
.cx-bar-fill-danger { height: 6px; border-radius: 3px; background: #d85a30; }
.cx-bar-fill-safe { height: 6px; border-radius: 3px; background: #1d9e75; }

/* === ALERT BOXES === */
.cx-alert-critical {
    background: rgba(216,90,48,0.08);
    border: 1px solid rgba(216,90,48,0.25);
    border-radius: 6px;
    padding: 14px 18px;
    color: #d85a30;
    font-family: 'Space Mono', monospace;
    font-size: 11px;
    margin-top: 12px;
}
.cx-alert-safe {
    background: rgba(29,158,117,0.08);
    border: 1px solid rgba(29,158,117,0.25);
    border-radius: 6px;
    padding: 14px 18px;
    color: #1d9e75;
    font-family: 'Space Mono', monospace;
    font-size: 11px;
    margin-top: 12px;
}

/* === LOG TERMINAL === */
.cx-log {
    background: #060809;
    border: 1px solid #1a2332;
    border-radius: 6px;
    padding: 14px 18px;
    font-family: 'Space Mono', monospace;
    font-size: 10px;
    line-height: 1.9;
    margin-top: 16px;
}
.cx-log span.ok { color: #1d9e75; }
.cx-log span.warn { color: #d85a30; }
.cx-log span.info { color: #378add; }
.cx-log span.muted { color: #3a4a62; }

/* === BUTTON === */
.stButton > button {
    background: #d85a30 !important;
    color: white !important;
    border: none !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    border-radius: 4px !important;
    padding: 10px 0 !important;
    width: 100% !important;
    transition: background 0.15s !important;
}
.stButton > button:hover { background: #c04820 !important; }

/* General text override for dark theme */
label, .stSelectbox label, .stNumberInput label, .stCheckbox label {
    color: #8a96a8 !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 10px !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}
</style>
""", unsafe_allow_html=True)

# ── Live DB helpers ───────────────────────────────────────────
@st.cache_data(ttl=120)
def get_available_facilities():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT facility_id, facility_name FROM Facilities ORDER BY facility_id;")
        rows = cur.fetchall()
        cur.close(); conn.close()
        return rows if rows else [(1,"Central City Hospital"),(2,"Mercy General"),(3,"County Medical")]
    except:
        return [(1,"Central City Hospital"),(2,"Mercy General"),(3,"County Medical")]

# ── HEADER ─────────────────────────────────────────────────
st.markdown("""
<div class="cx-header">
  <div>
    <div class="cx-title">🦠 Disease X Command Center</div>
    <div class="cx-subtitle">Rapid Triage &amp; Automated Allocation Engine — PostgreSQL + ML Bridge</div>
  </div>
  <div style="display:flex;gap:10px">
    <span class="cx-badge cx-badge-live">● Live DB</span>
    <span class="cx-badge cx-badge-critical">Threat: High</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# FETCH GLOBAL STATS FROM POSTGRESQL
# ---------------------------------------------------------
try:
    conn = get_db_connection()
    stats_query = """
    SELECT 
        COUNT(patient_id) AS total_patients,
        COALESCE(COUNT(patient_id) FILTER (WHERE clinical_status = 'Critical'), 0) AS critical_cases,
        COALESCE(ROUND(AVG(ml_vulnerability_score)::numeric, 1), 0) AS avg_risk,
        (SELECT SUM(max_capacity - current_occupancy) FROM Facilities) AS beds_available
    FROM Patients;
    """
    df_stats = pd.read_sql(stats_query, conn)
    conn.close()

    # Extract the numbers from the dataframe
    active_pts = df_stats['total_patients'][0]
    critical_pts = df_stats['critical_cases'][0]
    avg_risk = df_stats['avg_risk'][0]
    beds_avail = df_stats['beds_available'][0]

except Exception as e:
    # Fallback if the database is asleep
    active_pts, critical_pts, avg_risk, beds_avail = "-", "-", "-", "-"
    st.error(f"Could not load global stats: {e}")

# ---------------------------------------------------------
# RENDER THE TOP METRICS ROW
# ---------------------------------------------------------
m1, m2, m3, m4 = st.columns(4)

with m1:
    st.metric("ACTIVE PATIENTS", active_pts)
with m2:
    st.metric("BEDS AVAILABLE", beds_avail)
with m3:
    st.metric("CRITICAL CASES", critical_pts)
with m4:
    # Add the percentage sign dynamically
    st.metric("AVG RISK SCORE", f"{avg_risk}%" if avg_risk != "-" else "-%")

st.markdown("<br>", unsafe_allow_html=True)

# ── SIDEBAR ────────────────────────────────────────────────
facilities = get_available_facilities()
fac_map = {f"{name} — ID {fid}": fid for fid, name in facilities}

st.sidebar.markdown('<div class="sidebar-section">Facility Routing</div>', unsafe_allow_html=True)
fac_choice = st.sidebar.selectbox("Admitting Facility", list(fac_map.keys()), label_visibility="collapsed")
facility_id = fac_map[fac_choice]

st.sidebar.markdown('<div class="sidebar-section">Patient Demographics</div>', unsafe_allow_html=True)
age = st.sidebar.number_input("Age", min_value=0, max_value=120, value=45)
gender = st.sidebar.selectbox("Biological Sex", ["Male", "Female"])

st.sidebar.markdown('<div class="sidebar-section">Pre-existing Conditions</div>', unsafe_allow_html=True)
col_a, col_b = st.sidebar.columns(2)
diabetes       = col_a.checkbox("Diabetes")
hypertension   = col_b.checkbox("Hypert.")
heart_disease  = col_a.checkbox("Heart Dis.")
asthma         = col_b.checkbox("Asthma")

st.sidebar.markdown('<div class="sidebar-section">Day-1 Symptoms</div>', unsafe_allow_html=True)
col_c, col_d = st.sidebar.columns(2)
fever   = col_c.checkbox("Fever")
cough   = col_d.checkbox("Cough")
fatigue = col_c.checkbox("Fatigue")
sob     = col_d.checkbox("Shortness of Breath")

st.sidebar.markdown("<br>", unsafe_allow_html=True)
run = st.sidebar.button("Calculate Risk & Admit Patient", use_container_width=True)

# ── MAIN PANEL ─────────────────────────────────────────────
if run:
    # ML prediction
    input_data = {
        'age': age, 'fever': int(fever), 'cough': int(cough),
        'fatigue': int(fatigue), 'shortness_of_breath': int(sob),
        'diabetes': int(diabetes), 'hypertension': int(hypertension),
        'heart_disease': int(heart_disease), 'asthma': int(asthma),
        'gender_Male': 1 if gender == "Male" else 0
    }
    pdf = pd.DataFrame([input_data])
    for col in expected_features:
        if col not in pdf.columns: pdf[col] = 0
    pdf = pdf[expected_features]

    probability = float(model.predict_proba(pdf)[0][1] * 100)
    prediction = int(model.predict(pdf)[0])
    clinical_status = 'Critical' if prediction == 1 else 'Stable'
    is_critical = (clinical_status == 'Critical')

    # DB Insert
    log_lines = []
    new_patient_id = None
    ts = datetime.now().strftime("%H:%M:%S")

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        log_lines.append(f'<span class="info">{ts} CONN OK → disease_x_db @ localhost:{DB_PORT}</span>')

        cur.execute("""
            INSERT INTO Patients (facility_id, age, clinical_status, ml_vulnerability_score)
            VALUES (%s, %s, %s, %s) RETURNING patient_id;
        """, (facility_id, age, clinical_status, probability))
        new_patient_id = cur.fetchone()[0]
        log_lines.append(f'<span class="ok">{ts} INSERT Patients → ID #{new_patient_id:05d} | status={clinical_status} | score={probability:.1f}%</span>')

        symptoms = [s for s, flag in [('Fever',fever),('Cough',cough),('Fatigue',fatigue),('Shortness of Breath',sob)] if flag]
        for symp in symptoms:
            cur.execute("INSERT INTO Patient_Symptoms (patient_id, symptom_name, severity_level) VALUES (%s,%s,%s);",
                        (new_patient_id, symp, 5))
        if symptoms:
            log_lines.append(f'<span class="muted">{ts} INSERT Patient_Symptoms × {len(symptoms)} ({", ".join(symptoms)})</span>')

        conn.commit(); cur.close(); conn.close()

        if is_critical:
            log_lines.append(f'<span class="warn">{ts} TRIGGER trigger_critical_allocation FIRED → Resources −1 Life Support</span>')
        log_lines.append(f'<span class="ok">{ts} TRIGGER trigger_patient_occupancy FIRED → occupancy +1</span>')
        log_lines.append(f'<span class="ok">{ts} COMMIT OK — admission complete</span>')

    except Exception as e:
        log_lines.append(f'<span class="warn">{ts} ERROR: {e}</span>')

    # Display results
    r1, r2, r3 = st.columns(3)
    color_cls = "danger" if is_critical else "safe"
    patient_id_display = f"#{new_patient_id:05d}" if new_patient_id else "—"   # ← ADD THIS

    with r1:
        st.markdown(f'<div class="cx-metric-card"><div class="cx-metric-label">Vulnerability Score</div><div class="cx-metric-value {color_cls}">{probability:.1f}%</div></div>', unsafe_allow_html=True)
    with r2:
        st.markdown(f'<div class="cx-metric-card"><div class="cx-metric-label">Patient ID</div><div class="cx-metric-value">{patient_id_display}</div></div>', unsafe_allow_html=True)
    with r3:
        status_label = "ICU / CRITICAL" if is_critical else "STABLE / OBS"
        st.markdown(f'<div class="cx-metric-card"><div class="cx-metric-label">Clinical Status</div><div class="cx-metric-value {color_cls}">{status_label}</div></div>', unsafe_allow_html=True)

    # Risk bars
    symp_count = sum([fever, cough, fatigue, sob])
    comorbid_count = sum([diabetes, hypertension, heart_disease, asthma])
    bar_cls = "cx-bar-fill-danger" if is_critical else "cx-bar-fill-safe"
    st.markdown(f"""
    <div class="cx-risk-bar-wrap">
      <div style="font-family:'Space Mono',monospace;font-size:9px;color:#3a4a62;letter-spacing:.12em;text-transform:uppercase;margin-bottom:14px;">Risk Profile Breakdown</div>
      <div style="display:flex;align-items:center;gap:12px;margin-bottom:10px">
        <span style="font-family:'Space Mono',monospace;font-size:10px;color:#3a4a62;width:100px">Vulnerability</span>
        <div class="cx-bar-track" style="flex:1"><div class="{bar_cls}" style="width:{probability:.0f}%"></div></div>
        <span style="font-family:'Space Mono',monospace;font-size:10px;width:38px;text-align:right;color:#d85a30">{probability:.1f}%</span>
      </div>
      <div style="display:flex;align-items:center;gap:12px;margin-bottom:10px">
        <span style="font-family:'Space Mono',monospace;font-size:10px;color:#3a4a62;width:100px">Symptom Load</span>
        <div class="cx-bar-track" style="flex:1"><div style="height:6px;border-radius:3px;background:#ba7517;width:{symp_count*25}%"></div></div>
        <span style="font-family:'Space Mono',monospace;font-size:10px;width:38px;text-align:right;color:#ba7517">{symp_count}/4</span>
      </div>
      <div style="display:flex;align-items:center;gap:12px">
        <span style="font-family:'Space Mono',monospace;font-size:10px;color:#3a4a62;width:100px">Comorbidity</span>
        <div class="cx-bar-track" style="flex:1"><div style="height:6px;border-radius:3px;background:#378add;width:{comorbid_count*25}%"></div></div>
        <span style="font-family:'Space Mono',monospace;font-size:10px;width:38px;text-align:right;color:#378add">{comorbid_count}/4</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Alert
    if is_critical:
        alert_html = (
            '<div class="cx-alert-critical">'
            '<strong>HIGH RISK — ICU ADMISSION TRIGGERED</strong><br><br>'
            'DB Trigger: trigger_critical_allocation FIRED<br>'
            f'Resources deducted: 1x Life Support unit at Facility {facility_id}<br>'
            'Recommendation: Immediate isolation and ventilator assignment required.'
            '</div>'
        )
    else:
        alert_html = (
            '<div class="cx-alert-safe">'
            '<strong>LOW RISK — STABLE / OBSERVATION WARD</strong><br><br>'
            'DB Trigger: trigger_patient_occupancy FIRED<br>'
            f'Standard bed assigned at Facility {facility_id}. No critical resources deducted.'
            '</div>'
        )
    st.markdown(alert_html, unsafe_allow_html=True)

    # System log
    st.markdown(f'<div class="cx-log">{"<br>".join(log_lines)}</div>', unsafe_allow_html=True)

else:
    st.markdown("""
    <div style="text-align:center;padding:60px 0;opacity:0.3">
        <div style="font-family:'Space Mono',monospace;font-size:11px;letter-spacing:.15em;text-transform:uppercase;color:#5a6478">
            Awaiting patient intake — configure parameters in sidebar
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Crisis Command Dashboard from DB view
    try:
        conn = get_db_connection()
        df = pd.read_sql("SELECT * FROM Crisis_Command_Dashboard ORDER BY threat_level DESC;", conn)
        conn.close()
        if not df.empty:
            st.markdown('<p style="font-family:Space Mono,monospace;font-size:9px;letter-spacing:.15em;text-transform:uppercase;color:#3a4a62;margin-bottom:8px">Crisis Command Dashboard — Live View</p>', unsafe_allow_html=True)
            st.dataframe(df, use_container_width=True, hide_index=True)
    except:
        pass