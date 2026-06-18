-- ============================================================
-- Patient360 | KPI Queries
-- All 10 KPIs from PRD requirements
-- ============================================================

-- KPI-1: Total Patients
SELECT COUNT(DISTINCT patient_id) AS total_patients
FROM sdlc_catalog.patient_360_gold.patient_360_master;

-- KPI-2: Active Patients (appointment in last 90 days)
SELECT COUNT(DISTINCT patient_id) AS active_patients
FROM sdlc_catalog.patient_360_gold.patient_360_master
WHERE last_appointment_date >= CURRENT_DATE() - INTERVAL 90 DAYS;

-- KPI-3: Total Appointments
SELECT SUM(total_appointments) AS total_appointments
FROM sdlc_catalog.patient_360_gold.patient_360_master;

-- KPI-4: Disease Distribution
SELECT
    primary_disease,
    COUNT(DISTINCT patient_id) AS patient_count,
    ROUND(COUNT(DISTINCT patient_id) * 100.0
        / SUM(COUNT(DISTINCT patient_id)) OVER (), 2) AS pct
FROM sdlc_catalog.patient_360_gold.patient_360_master
WHERE primary_disease IS NOT NULL
GROUP BY primary_disease
ORDER BY patient_count DESC;

-- KPI-5: Average Treatment Cost
SELECT ROUND(AVG(total_treatment_cost), 2) AS avg_treatment_cost_inr
FROM sdlc_catalog.patient_360_gold.patient_financial_summary;

-- KPI-6: Revenue by State
SELECT
    state,
    ROUND(SUM(total_treatment_cost), 2) AS total_revenue_inr
FROM sdlc_catalog.patient_360_gold.patient_financial_summary
GROUP BY state
ORDER BY total_revenue_inr DESC;

-- KPI-7: Doctor Workload
SELECT
    doctor_name,
    department,
    total_appointments,
    unique_patients
FROM sdlc_catalog.patient_360_gold.doctor_performance_summary
ORDER BY total_appointments DESC;

-- KPI-8: High Risk Patients
SELECT
    risk_category,
    COUNT(patient_id) AS patient_count
FROM sdlc_catalog.patient_360_gold.patient_risk_summary
GROUP BY risk_category
ORDER BY patient_count DESC;

-- KPI-9: Medication Adherence Rate
SELECT ROUND(AVG(adherence_rate), 2) AS overall_adherence_rate_pct
FROM sdlc_catalog.patient_360_gold.medication_adherence_summary;

-- KPI-10: Lab Abnormality Rate
SELECT
    ROUND(
        SUM(above_normal_count + below_normal_count) * 100.0
        / NULLIF(SUM(total_lab_tests), 0), 2
    ) AS lab_abnormality_rate_pct
FROM sdlc_catalog.patient_360_gold.patient_clinical_summary;
