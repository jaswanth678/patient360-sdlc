-- ============================================================
-- Patient360 | Validation Queries
-- Run after each pipeline execution to verify data integrity
-- ============================================================

-- VAL-01: Record count by layer
SELECT 'raw_patient_records'     AS table_name, COUNT(*) AS record_count FROM sdlc_catalog.patient_360_raw.raw_patient_records UNION ALL
SELECT 'raw_appointment_records',                COUNT(*) FROM sdlc_catalog.patient_360_raw.raw_appointment_records UNION ALL
SELECT 'raw_diagnosis_records',                  COUNT(*) FROM sdlc_catalog.patient_360_raw.raw_diagnosis_records UNION ALL
SELECT 'raw_medication',                         COUNT(*) FROM sdlc_catalog.patient_360_raw.raw_medication UNION ALL
SELECT 'raw_lab_reports',                        COUNT(*) FROM sdlc_catalog.patient_360_raw.raw_lab_reports UNION ALL
SELECT 'raw_billing_records',                    COUNT(*) FROM sdlc_catalog.patient_360_raw.raw_billing_records UNION ALL
SELECT 'raw_patient_history',                    COUNT(*) FROM sdlc_catalog.patient_360_raw.raw_patient_history;

-- VAL-02: Bronze vs Silver row comparison
SELECT
    'bronze_patient'   AS bronze_table, COUNT(*) AS bronze_count FROM sdlc_catalog.patient_360_bronze.bronze_patient UNION ALL
SELECT 'silver_patient',                COUNT(*) FROM sdlc_catalog.patient_360_silver.silver_patient;

-- VAL-03: DQ Rejection Summary (today)
SELECT
    rule_name,
    source_table,
    COUNT(*) AS rejection_count,
    MAX(rejection_timestamp) AS last_rejected_at
FROM sdlc_catalog.patient_360_silver.dq_rejection_log
WHERE DATE(rejection_timestamp) = CURRENT_DATE()
GROUP BY rule_name, source_table
ORDER BY rejection_count DESC;

-- VAL-04: Gold table freshness check
SELECT
    'patient_360_master'        AS gold_table, MAX(gold_load_timestamp) AS last_updated FROM sdlc_catalog.patient_360_gold.patient_360_master UNION ALL
SELECT 'patient_clinical_summary',              MAX(gold_load_timestamp) FROM sdlc_catalog.patient_360_gold.patient_clinical_summary UNION ALL
SELECT 'patient_financial_summary',             MAX(gold_load_timestamp) FROM sdlc_catalog.patient_360_gold.patient_financial_summary UNION ALL
SELECT 'doctor_performance_summary',            MAX(gold_load_timestamp) FROM sdlc_catalog.patient_360_gold.doctor_performance_summary UNION ALL
SELECT 'medication_adherence_summary',          MAX(gold_load_timestamp) FROM sdlc_catalog.patient_360_gold.medication_adherence_summary UNION ALL
SELECT 'patient_risk_summary',                  MAX(gold_load_timestamp) FROM sdlc_catalog.patient_360_gold.patient_risk_summary;

-- VAL-05: Referential integrity - silver_appointment patient_ids exist in silver_patient
SELECT COUNT(*) AS orphan_appointments
FROM sdlc_catalog.patient_360_silver.silver_appointment a
LEFT JOIN sdlc_catalog.patient_360_silver.silver_patient p ON a.patient_id = p.patient_id
WHERE p.patient_id IS NULL;

-- VAL-06: DQ Rule 8 - Check age range compliance post-silver
SELECT
    CASE WHEN age < 0 OR age > 120 THEN 'OUT_OF_RANGE' ELSE 'VALID' END AS age_validity,
    COUNT(*) AS count
FROM sdlc_catalog.patient_360_silver.silver_patient
GROUP BY 1;

-- VAL-07: Null check on Gold master key columns
SELECT
    SUM(CASE WHEN patient_id IS NULL THEN 1 ELSE 0 END) AS null_patient_ids,
    SUM(CASE WHEN total_treatment_cost IS NULL THEN 1 ELSE 0 END) AS null_costs,
    SUM(CASE WHEN total_appointments IS NULL THEN 1 ELSE 0 END) AS null_appts
FROM sdlc_catalog.patient_360_gold.patient_360_master;
