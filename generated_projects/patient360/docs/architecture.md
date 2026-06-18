# Patient360 Analytics Platform - Architecture Document

## Overview

The Patient360 Analytics Platform is a Databricks-native, Medallion architecture solution ingesting 7 healthcare CSV datasets and transforming them into a unified Patient 360 analytical view for clinical, operational, and financial reporting.

## Data Flow Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│  SOURCE LAYER                                                       │
│  /Volumes/sdlc_catalog/patient_360/source/                         │
│  Patient_records.csv | Appointment_record.csv | Diagnosis_record.csv │
│  Medication.csv | Lab_report.csv | Billing_record.csv | Patient_history.csv │
└──────────────────────────────┬─────────────────────────────────────┘
                               │ Incremental CSV Read + Metadata Injection
                               ▼
┌────────────────────────────────────────────────────────────────────┐
│  RAW LAYER  [sdlc_catalog.patient_360_raw]                         │
│  + ingestion_timestamp  + source_file_name  + load_date  + record_hash │
└──────────────────────────────┬─────────────────────────────────────┘
                               │ Column Sanitization + MERGE INTO
                               ▼
┌────────────────────────────────────────────────────────────────────┐
│  BRONZE LAYER  [sdlc_catalog.patient_360_bronze]                   │
│  bronze_patient | bronze_appointment | bronze_diagnosis            │
│  bronze_medication | bronze_lab | bronze_billing | bronze_history  │
└──────────────────────────────┬─────────────────────────────────────┘
                               │ DQ Rules + Dedup + Standardization
                               ▼
┌────────────────────────────────────────────────────────────────────┐
│  SILVER LAYER  [sdlc_catalog.patient_360_silver]                   │
│  silver_patient | silver_appointment | silver_diagnosis            │
│  silver_medication | silver_lab | silver_billing | silver_history  │
│  dq_rejection_log                                                  │
└──────────────────────────────┬─────────────────────────────────────┘
                               │ Joins + Aggregations + KPI Computation
                               ▼
┌────────────────────────────────────────────────────────────────────┐
│  GOLD LAYER  [sdlc_catalog.patient_360_gold]                       │
│  patient_360_master | patient_clinical_summary                     │
│  patient_financial_summary | doctor_performance_summary            │
│  medication_adherence_summary | patient_risk_summary               │
│  kpi_summary | risk_distribution                                   │
└──────────────────────────────┬─────────────────────────────────────┘
                               │
                               ▼
┌────────────────────────────────────────────────────────────────────┐
│  DASHBOARDS (Databricks AI/BI)                                     │
│  Executive | Clinical | Operational | Financial                    │
└────────────────────────────────────────────────────────────────────┘
```

## Unity Catalog Structure

```
sdlc_catalog
├── patient_360 (source schema)
│   └── source/ (volume with 7 CSV files)
├── patient_360_raw
│   ├── raw_patient_records
│   ├── raw_appointment_records
│   ├── raw_diagnosis_records
│   ├── raw_medication
│   ├── raw_lab_reports
│   ├── raw_billing_records
│   └── raw_patient_history
├── patient_360_bronze
│   ├── bronze_patient
│   ├── bronze_appointment
│   ├── bronze_diagnosis
│   ├── bronze_medication
│   ├── bronze_lab
│   ├── bronze_billing
│   └── bronze_patient_history
├── patient_360_silver
│   ├── silver_patient
│   ├── silver_appointment
│   ├── silver_diagnosis
│   ├── silver_medication
│   ├── silver_lab
│   ├── silver_billing
│   ├── silver_patient_history
│   └── dq_rejection_log
└── patient_360_gold
    ├── patient_360_master
    ├── patient_clinical_summary
    ├── patient_financial_summary
    ├── doctor_performance_summary
    ├── medication_adherence_summary
    ├── patient_risk_summary
    ├── kpi_summary
    └── risk_distribution
```

## Pipeline Orchestration

- **Type:** Batch (Databricks Workflow)
- **Schedule:** Daily at 02:00 IST
- **Task Dependencies:** ingest → bronze → silver → gold → dashboard_refresh
- **Deployment:** Databricks Asset Bundle (DAB)
- **IaC:** Terraform (Databricks provider)
- **CI/CD:** GitHub Actions (validate → test → deploy-dev → deploy-qa → deploy-prod)

## Data Quality Framework

8 rules enforced at Silver layer. Failures quarantined to `dq_rejection_log`.

| Rule | Table | Condition |
|------|-------|-----------|
| DQ001 | silver_patient | patient_id NOT NULL |
| DQ002 | silver_appointment | appointment_id NOT NULL |
| DQ003 | silver_diagnosis | diagnosis_code NOT NULL |
| DQ004 | silver_billing | treatment_cost >= 0 |
| DQ005 | silver_medication | medicine_price >= 0 |
| DQ006 | silver_patient | email format valid |
| DQ007 | silver_appointment | booking_date <= today |
| DQ008 | silver_patient | age BETWEEN 0 AND 120 |

## Key Design Decisions

1. **Incremental load via append** at Raw layer — full history preserved
2. **MERGE INTO** at Bronze layer — upsert deduplication per primary key
3. **Row-number deduplication** at Silver — latest record wins per PK
4. **Config-driven DQ engine** — rules in Python dict, no hardcoded SQL per column
5. **Delta format throughout** — enables time travel, schema evolution, ACID transactions
6. **Unity Catalog** — centralized governance, lineage, and access control
