-- ============================================================
-- Patient360 Dashboard Queries
-- All queries reference sdlc_catalog.patient_360_gold only
-- ============================================================

-- ============================================================
-- EXECUTIVE DASHBOARD
-- ============================================================

-- EX-01: KPI Summary Totals
SELECT
    COUNT(DISTINCT patient_id)          AS total_patients,
    SUM(total_appointments)             AS total_appointments,
    ROUND(SUM(total_treatment_cost), 2) AS total_revenue_inr,
    ROUND(AVG(total_treatment_cost), 2) AS avg_treatment_cost_inr,
    COUNT(DISTINCT CASE
        WHEN last_appointment_date >= CURRENT_DATE() - INTERVAL 90 DAYS
        THEN patient_id END)            AS active_patients
FROM sdlc_catalog.patient_360_gold.patient_360_master;

-- EX-02: Revenue by State
SELECT
    state,
    COUNT(DISTINCT patient_id)          AS patient_count,
    ROUND(SUM(total_treatment_cost), 2) AS total_revenue_inr,
    ROUND(AVG(total_treatment_cost), 2) AS avg_revenue_per_patient
FROM sdlc_catalog.patient_360_gold.patient_financial_summary
WHERE state IS NOT NULL
GROUP BY state
ORDER BY total_revenue_inr DESC;

-- EX-03: Monthly Appointment Trend
SELECT
    DATE_FORMAT(last_appointment_date, 'yyyy-MM') AS month,
    COUNT(DISTINCT patient_id)                    AS active_patients,
    SUM(total_appointments)                       AS total_appointments
FROM sdlc_catalog.patient_360_gold.patient_360_master
WHERE last_appointment_date IS NOT NULL
GROUP BY DATE_FORMAT(last_appointment_date, 'yyyy-MM')
ORDER BY month;

-- EX-04: Patient Age Group Distribution
SELECT
    CASE
        WHEN age < 18  THEN '0-17'
        WHEN age < 35  THEN '18-34'
        WHEN age < 50  THEN '35-49'
        WHEN age < 65  THEN '50-64'
        ELSE '65+'
    END AS age_group,
    COUNT(patient_id) AS patient_count
FROM sdlc_catalog.patient_360_gold.patient_360_master
GROUP BY 1
ORDER BY 1;

-- ============================================================
-- CLINICAL DASHBOARD
-- ============================================================

-- CL-01: Disease Distribution (Top 15)
SELECT
    primary_disease,
    COUNT(DISTINCT patient_id) AS patient_count,
    ROUND(COUNT(DISTINCT patient_id) * 100.0 / SUM(COUNT(DISTINCT patient_id)) OVER (), 2) AS pct_of_total
FROM sdlc_catalog.patient_360_gold.patient_360_master
WHERE primary_disease IS NOT NULL
GROUP BY primary_disease
ORDER BY patient_count DESC
LIMIT 15;

-- CL-02: Patient Risk Category Summary
SELECT
    risk_category,
    COUNT(patient_id)                 AS patient_count,
    ROUND(AVG(overall_risk_score), 2) AS avg_risk_score
FROM sdlc_catalog.patient_360_gold.patient_risk_summary
GROUP BY risk_category
ORDER BY avg_risk_score DESC;

-- CL-03: Lab Abnormality Rate by Patient
SELECT
    patient_id,
    total_lab_tests,
    above_normal_count,
    below_normal_count,
    ROUND(
        (above_normal_count + below_normal_count) * 100.0 / NULLIF(total_lab_tests, 0), 2
    ) AS abnormality_rate_pct,
    lab_risk_flag
FROM sdlc_catalog.patient_360_gold.patient_clinical_summary
ORDER BY abnormality_rate_pct DESC
LIMIT 50;

-- CL-04: Medication Adherence by Disease
SELECT
    disease,
    COUNT(DISTINCT patient_id)    AS patient_count,
    ROUND(AVG(adherence_rate), 2) AS avg_adherence_rate,
    ROUND(SUM(total_medicine_cost), 2) AS total_medicine_cost
FROM sdlc_catalog.patient_360_gold.medication_adherence_summary
GROUP BY disease
ORDER BY avg_adherence_rate ASC;

-- CL-05: High Risk Patients Detail
SELECT
    r.patient_id,
    r.risk_category,
    r.overall_risk_score,
    r.age_risk,
    r.lab_risk,
    r.financial_risk,
    m.total_appointments,
    m.total_treatment_cost
FROM sdlc_catalog.patient_360_gold.patient_risk_summary r
JOIN sdlc_catalog.patient_360_gold.patient_360_master m
  ON r.patient_id = m.patient_id
WHERE r.risk_category = 'HIGH_RISK'
ORDER BY r.overall_risk_score DESC;

-- ============================================================
-- OPERATIONAL DASHBOARD
-- ============================================================

-- OP-01: Doctor Performance Summary
SELECT
    doctor_name,
    department,
    total_appointments,
    unique_patients,
    ROUND(avg_charge_inr, 2)   AS avg_charge_inr,
    ROUND(total_revenue_inr, 2) AS total_revenue_inr
FROM sdlc_catalog.patient_360_gold.doctor_performance_summary
ORDER BY total_appointments DESC;

-- OP-02: Department Workload
SELECT
    department,
    SUM(total_appointments) AS total_appointments,
    COUNT(DISTINCT doctore_id) AS doctor_count,
    ROUND(AVG(total_appointments), 1) AS avg_appts_per_doctor
FROM sdlc_catalog.patient_360_gold.doctor_performance_summary
GROUP BY department
ORDER BY total_appointments DESC;

-- OP-03: Visit Frequency Distribution
SELECT
    CASE
        WHEN total_appointments = 1 THEN '1 visit'
        WHEN total_appointments BETWEEN 2 AND 5  THEN '2-5 visits'
        WHEN total_appointments BETWEEN 6 AND 10 THEN '6-10 visits'
        ELSE '10+ visits'
    END AS visit_frequency_band,
    COUNT(patient_id) AS patient_count
FROM sdlc_catalog.patient_360_gold.patient_360_master
GROUP BY 1;

-- ============================================================
-- FINANCIAL DASHBOARD
-- ============================================================

-- FI-01: Insurance Coverage Analysis
SELECT
    patient_id,
    state,
    ROUND(total_treatment_cost, 2)     AS total_cost,
    ROUND(total_insurance_coverage, 2) AS total_covered,
    ROUND(total_treatment_cost - total_insurance_coverage, 2) AS out_of_pocket,
    ROUND(insurance_coverage_pct, 2)   AS coverage_pct
FROM sdlc_catalog.patient_360_gold.patient_financial_summary
ORDER BY out_of_pocket DESC;

-- FI-02: Payment Mode Distribution
SELECT
    'UPI'  AS payment_mode, SUM(upi_payments)  AS transaction_count FROM sdlc_catalog.patient_360_gold.patient_financial_summary
UNION ALL
SELECT
    'CASH' AS payment_mode, SUM(cash_payments) AS transaction_count FROM sdlc_catalog.patient_360_gold.patient_financial_summary;

-- FI-03: Revenue Trend (Monthly)
SELECT
    DATE_FORMAT(payment_date, 'yyyy-MM') AS month,
    ROUND(SUM(treatment_cost), 2)        AS monthly_revenue,
    COUNT(bill_id)                       AS bill_count
FROM sdlc_catalog.patient_360_silver.silver_billing
GROUP BY DATE_FORMAT(payment_date, 'yyyy-MM')
ORDER BY month;

-- FI-04: Billing Status Summary
SELECT
    payment_status,
    COUNT(*)              AS bill_count,
    ROUND(SUM(treatment_cost), 2) AS total_amount
FROM sdlc_catalog.patient_360_silver.silver_billing
GROUP BY payment_status;
