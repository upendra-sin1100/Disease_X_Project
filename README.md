# 🦠 Disease X Command Center

> **A full-stack pandemic response simulation and real-time triage system built with PostgreSQL, Machine Learning, and Streamlit.**

![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square&logo=python)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-336791?style=flat-square&logo=postgresql)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-FF4B4B?style=flat-square&logo=streamlit)
![ML](https://img.shields.io/badge/ML-Logistic%20Regression-orange?style=flat-square&logo=scikit-learn)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=flat-square)

---

## 📌 What Is "Disease X"?

**Disease X** is the WHO's official placeholder name for an unknown pathogen that could cause a future global epidemic — a disease we don't have a name for yet, but must be prepared to fight.

> *"Disease X represents the knowledge that a serious international epidemic could be caused by a pathogen currently unknown to cause human disease."* — World Health Organization

This project simulates the **command-and-control system** that a government health authority or hospital network would use during such an outbreak. It predicts patient risk in real time, auto-allocates critical resources, and tracks hospital capacity — all automatically.

---

## 🎯 What Problem Does It Solve?

During a disease outbreak, hospitals face three simultaneous crises:

| Problem | How This System Solves It |
|---|---|
| Don't know which patients will deteriorate | ML model scores every patient 0–100% on admission |
| Ventilators and critical resources run out | DB trigger auto-deducts resources the moment a Critical patient is admitted |
| Can't track capacity across multiple facilities | DB trigger updates bed occupancy instantly on every admission |
| No early warning for resource shortages | `Resource_Alerts` view fires when inventory drops below threshold |
| Risk of admitting to an overcrowded facility | Surge-protection trigger blocks admission at 95%+ capacity |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    STREAMLIT UI (app.py)                 │
│         Dark command-center dashboard                    │
│   Sidebar input → ML score → 2-step confirm → DB write  │
└──────────────────────┬──────────────────────────────────┘
                       │ psycopg2
┌──────────────────────▼──────────────────────────────────┐
│              PYTHON ML BRIDGE                            │
│   joblib loads .pkl → predict_proba() → risk score      │
│   Maps score to clinical_status → prepares DB payload   │
└──────────────────────┬──────────────────────────────────┘
                       │ SQL INSERT
┌──────────────────────▼──────────────────────────────────┐
│              POSTGRESQL DATABASE                         │
│   6 Tables · 3 Triggers · 4 Views · 1 Surge Function    │
└─────────────────────────────────────────────────────────┘
```

---

## 🗄️ Database Schema

### Tables

```
Zones ──────────────── Facilities ──────── Resources
                            │
                        Patients ────────── Patient_Symptoms
                        
Pathogen_Profiles (standalone reference table)
```

| Table | Purpose |
|---|---|
| `Zones` | Geographic hotspot areas with threat levels (Low/Medium/High/Critical) |
| `Facilities` | Hospitals, ICUs, quarantine centers linked to zones |
| `Patients` | Core patient records with ML vulnerability score |
| `Patient_Symptoms` | Each symptom logged separately per patient |
| `Resources` | Medical equipment inventory per facility (ventilators, etc.) |
| `Pathogen_Profiles` | Known/hypothetical pathogen definitions |

---

## ⚡ Database Triggers

Two triggers fire **automatically** on every patient admission — you never call them manually.

### `trigger_patient_occupancy`
Fires `AFTER INSERT OR DELETE` on `Patients`.
- **INSERT** → `current_occupancy + 1`
- **DELETE** → `current_occupancy - 1`

### `trigger_critical_allocation`
Fires `AFTER INSERT OR UPDATE` on `Patients` where `clinical_status = 'Critical'`.
```sql
UPDATE Resources
SET quantity_available = quantity_available - 1
WHERE facility_id = NEW.facility_id
  AND defense_category = 'Life Support'
  AND quantity_available > 0;
```

### `trigger_surge_block`
Fires `BEFORE INSERT` on `Patients`. Blocks admission if facility is at **95%+ capacity**.
```sql
IF cap_ratio >= 0.95 THEN
    RAISE EXCEPTION 'Facility % is at 95%% capacity - admission blocked.', NEW.facility_id;
END IF;
```

---

## 👁️ Database Views

| View | What It Shows |
|---|---|
| `Crisis_Command_Dashboard` | Zone + facility + bed count + critical patient count per row |
| `Resource_Alerts` | Resources that have dropped below `critical_threshold` |
| `Zone_Outbreak_Summary` | Total patients, critical count, avg ML score per zone |
| `Symptom_Frequency` | Which symptoms appear most and lead to Critical status |

---

## 🔍 SQL Reference Queries

Run these in **pgAdmin** or **psql** to inspect your live data.

### 1. All Admitted Patients
```sql
SELECT patient_id, facility_id, age, clinical_status,
       ml_vulnerability_score, admission_date
FROM Patients
ORDER BY admission_date DESC;
```

### 2. Patients With Their Symptoms
```sql
SELECT p.patient_id, p.age, p.clinical_status,
       p.ml_vulnerability_score,
       ps.symptom_name, ps.severity_level
FROM Patients p
JOIN Patient_Symptoms ps ON p.patient_id = ps.patient_id
ORDER BY p.patient_id DESC;
```

### 3. Critical Patients Only
```sql
SELECT patient_id, age, facility_id, ml_vulnerability_score, admission_date
FROM Patients
WHERE clinical_status = 'Critical'
ORDER BY ml_vulnerability_score DESC;
```

### 4. Crisis Command Dashboard
```sql
SELECT * FROM Crisis_Command_Dashboard;
```
Shows zone, threat level, facility, beds available, and critical patient count in one row.

### 5. Ventilator Deductions — Trigger Proof
```sql
SELECT r.item_type, r.defense_category,
       r.quantity_available, r.critical_threshold,
       f.facility_name
FROM Resources r
JOIN Facilities f ON r.facility_id = f.facility_id;
```
Every Critical admission should have decremented `quantity_available` by 1.

### 6. Facility Occupancy — Trigger Proof
```sql
SELECT facility_id, facility_name,
       max_capacity, current_occupancy,
       (max_capacity - current_occupancy) AS beds_free
FROM Facilities;
```

### 7. Full Patient Report — Everything Joined
```sql
SELECT
    p.patient_id,
    f.facility_name,
    z.zone_name,
    z.threat_level,
    p.age,
    p.clinical_status,
    p.ml_vulnerability_score,
    STRING_AGG(ps.symptom_name, ', ') AS symptoms,
    p.admission_date
FROM Patients p
JOIN Facilities f ON p.facility_id = f.facility_id
JOIN Zones z ON f.zone_id = z.zone_id
LEFT JOIN Patient_Symptoms ps ON p.patient_id = ps.patient_id
GROUP BY p.patient_id, f.facility_name, z.zone_name,
         z.threat_level, p.age, p.clinical_status,
         p.ml_vulnerability_score, p.admission_date
ORDER BY p.admission_date DESC;
```

### 8. Low Resource Alerts
```sql
SELECT * FROM Resource_Alerts;
```
Empty result = all resources are safe. Any row = action required.

---

## 🖥️ How Patient Admission Works

The system uses a **two-step confirmation flow** so a supervisor must approve before any Critical patient is committed to the database.

```
1. Operator fills sidebar (age, gender, symptoms, conditions, facility)
        ↓
2. Click "Calculate Risk & Admit" → ML model scores the patient
        ↓
3. Result shows as PENDING — nothing written to DB yet
        ↓
4. Supervisor clicks CONFIRM & ADMIT  ──or──  REJECT / DISCARD
        ↓
5. On confirm: INSERT into Patients + Patient_Symptoms
        ↓
6. trigger_patient_occupancy fires → facility occupancy +1
        ↓
7. If Critical → trigger_critical_allocation fires → ventilator -1
        ↓
8. Terminal log shows all events with timestamps
```

---

## 🚀 Setup & Running

### Requirements
- Python 3.9+
- PostgreSQL 14+
- pgAdmin 4 (recommended)

### Install Python dependencies
```bash
pip install streamlit psycopg2-binary pandas joblib scikit-learn python-dotenv
```

### Step 1 — Create the database
In pgAdmin or psql, run the SQL files in this order:
1. Schema (all CREATE TABLE statements)
2. Triggers
3. Views
4. Seed data

### Step 2 — Seed initial data
```sql
INSERT INTO Zones (zone_id, zone_name, threat_level, population_density) VALUES
(1, 'North Sector', 'High', 150000),
(2, 'South Sector', 'Low', 80000);

INSERT INTO Facilities (facility_id, zone_id, facility_name, facility_type, max_capacity, current_occupancy) VALUES
(1, 1, 'Central City Hospital', 'Hospital', 500, 0),
(2, 1, 'Mercy General', 'Hospital', 300, 0),
(3, 2, 'County Medical Center', 'ICU', 400, 0);

INSERT INTO Resources (facility_id, item_type, defense_category, quantity_available, critical_threshold) VALUES
(1, 'Ventilator Model-X', 'Life Support', 20, 5),
(2, 'Ventilator Model-X', 'Life Support', 10, 2),
(3, 'BSL-4 Isolation Pod', 'Life Support', 5, 1);
```

### Step 3 — Create `.env` file
```
DB_USER=your_postgres_username
DB_PASSWORD=your_postgres_password
```

### Step 4 — Run the app
```bash
streamlit run app.py
```

---

## 📁 Project Structure

```
Disease_X_Project/
├── app.py                           # Main Streamlit application
├── .env                             # DB credentials (never commit this!)
├── .gitignore                       # Should include .env and .pkl
├── disease_x_vulnerability_v1.pkl   # Trained ML model checkpoint
├── sql/
│   ├── 01_schema.sql                # All CREATE TABLE statements
│   ├── 02_triggers.sql              # All trigger functions
│   ├── 03_views.sql                 # All CREATE VIEW statements
│   └── 04_seed_data.sql             # Initial zones/facilities/resources
└── README.md                        # This file
```

---

## ⚠️ Important — `.gitignore`

Make sure you **never upload** your credentials or model file accidentally. Create a `.gitignore`:

```
.env
*.pkl
__pycache__/
*.pyc
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Database | PostgreSQL 14 with PL/pgSQL triggers |
| ML Model | Scikit-learn Logistic Regression |
| ML Serialization | joblib (.pkl checkpoint) |
| Backend / Bridge | Python 3, psycopg2 |
| Frontend | Streamlit with custom CSS |
| Environment | python-dotenv |

---

*Built as a pandemic response simulation — Disease X Command Center*
#   D i s e a s e _ X _ P r o j e c t  
 