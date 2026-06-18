-- ============================================================
-- Patient360 | Gold Layer | SQL Views
-- Purpose: Reusable views on Gold tables for BI and reporting
-- ============================================================

USE CATALOG sdlc_catalog;
USE SCHEMA patient_360_gold;

-- VW-01: Patient Overview (joins master with risk)
CREATE OR REPLACE VIEW vw_patient_overview AS
SELECT
    m.patient_id,
    m.patient_name,
    m.sex,
    m.state,
    m.age,
    m.disease_name            AS primary_disease,
    m.total_appointments,
    m.last_appointment_date,
    m.unique_diagnoses,
    m.active_medications,
    m.total_lab_tests,
    m.abnormal_lab_count,
    m.total_treatment_cost,
    m.total_insurance_coverage,
    r.risk_category,
    r.overall_risk_score,
    m.gold_load_timestamp
FROM patient_360_master m
LEFT JOIN patient_risk_summary r ON m.patient_id = r.patient_id;

-- VW-02: KPI Summary View
CREATE OR REPLACE VIEW vw_executive_kpis AS
SELECT
    COUNT(DISTINCT patient_id)          AS total_patients,
    COUNT(DISTINCT CASE WHEN last_appointment_date >= CURRENT_DATE() - INTERVAL 90 DAYS
                        THEN patient_id END) AS active_patients,
    SUM(total_appointments)             AS total_appointments,
    ROUND(SUM(total_treatment_cost), 2) AS total_revenue_inr,
    ROUND(AVG(total_treatment_cost), 2) AS avg_treatment_cost_inr
FROM patient_360_master;

-- VW-03: Disease Prevalence View
CREATE OR REPLACE VIEW vw_disease_prevalence AS
SELECT
    primary_disease,
    COUNT(DISTINCT patient_id)   AS patient_count,
    ROUND(COUNT(DISTINCT patient_id) * 100.0
          / SUM(COUNT(DISTINCT patient_id)) OVER (), 2) AS prevalence_pct,
    AVG(total_treatment_cost)    AS avg_treatment_cost
FROM patient_360_master
WHERE primary_disease IS NOT NULL
GROUP BY primary_disease;

-- VW-04: High Risk Patient View
CREATE OR REPLACE VIEW vw_high_risk_patients AS
SELECT
    r.patient_id,
    m.patient_name,
    m.age,
    m.state,
    r.risk_category,
    r.overall_risk_score,
    r.age_risk,
    r.lab_risk,
    r.financial_risk,
    m.total_treatment_cost,
    m.abnormal_lab_count
FROM patient_risk_summary r
JOIN patient_360_master m ON r.patient_id = m.patient_id
WHERE r.risk_category = 'HIGH_RISK'
ORDER BY r.overall_risk_score DESC;

-- VW-05: Doctor Revenue View
CREATE OR REPLACE VIEW vw_doctor_revenue AS
SELECT
    doctor_name,
    department,
    total_appointments,
    unique_patients,
    ROUND(avg_charge_inr, 2)    AS avg_charge_inr,
    ROUND(total_revenue_inr, 2) AS total_revenue_inr,
    ROUND(total_revenue_inr / NULLIF(unique_patients, 0), 2) AS revenue_per_patient
FROM doctor_performance_summary
ORDER BY total_revenue_inr DESC;

-- VW-06: Medication Adherence Overview
CREATE OR REPLACE VIEW vw_medication_adherence AS
SELECT
    disease,
    COUNT(DISTINCT patient_id)    AS patient_count,
    ROUND(AVG(adherence_rate), 2) AS avg_adherence_pct,
    ROUND(SUM(total_medicine_cost), 2) AS total_cost
FROM medication_adherence_summary
GROUP BY disease
ORDER BY avg_adherence_pct ASC;
