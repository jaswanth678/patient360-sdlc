# Patient360 Analytics Platform

End-to-end healthcare analytics platform on Databricks using Medallion Architecture.

## Architecture

```
CSV Source (7 files)
     │
     ▼
[sdlc_catalog.patient_360_raw]      ← Raw / Source layer
     │
     ▼
[sdlc_catalog.patient_360_bronze]   ← Bronze: sanitized, schema-enforced Delta tables
     │
     ▼
[sdlc_catalog.patient_360_silver]   ← Silver: deduped, DQ-validated, standardized
     │
     ▼
[sdlc_catalog.patient_360_gold]     ← Gold: Patient360 views, KPIs, aggregations
     │
     ▼
Databricks AI/BI Dashboards (4)
```

## Project Structure

```
patient360/
├── databricks.yml              # DAB bundle configuration
├── resources/
│   └── jobs.yml                # Pipeline job definition
├── src/
│   ├── ingestion/              # Source CSV → Raw schema
│   ├── bronze/                 # Raw → Bronze Delta tables
│   ├── silver/                 # Bronze → Silver + DQ rules
│   └── gold/                   # Silver → Gold analytics
├── tests/                      # pytest unit tests
├── docs/                       # Architecture, STM, Runbook
├── terraform/                  # Infrastructure as Code
└── .github/workflows/          # GitHub Actions CI/CD
```

## Quick Start

### Prerequisites
- Databricks CLI installed (`pip install databricks-cli`)
- Databricks workspace with Unity Catalog enabled
- `sdlc_catalog` catalog with `patient_360` source volume

### Deploy to DEV

```bash
# Authenticate
databricks configure --token

# Validate bundle
databricks bundle validate

# Deploy to dev
databricks bundle deploy --target dev

# Run pipeline
databricks bundle run patient360_pipeline --target dev
```

### Run Tests Locally

```bash
pip install pytest pyspark==3.5.0 pytest-cov
pytest tests/ -v --cov=src --cov-report=term-missing
```

## Source Datasets

| File | Raw Table | Primary Key |
|------|-----------|-------------|
| Patient_records.csv | raw_patient_records | patient_id |
| Appointment_record.csv | raw_appointment_records | appointment_id |
| Diagnosis_record.csv | raw_diagnosis_records | record_id |
| Medication.csv | raw_medication | medication_id |
| Lab_report.csv | raw_lab_reports | serial_number |
| Billing_record.csv | raw_billing_records | bill_id |
| Patient_history.csv | raw_patient_history | appointment_id + patient_id |

## Gold Tables & KPIs

| Gold Table | Key KPIs |
|------------|----------|
| patient_360_master | Total Patients, Active Patients |
| patient_clinical_summary | Disease Distribution, Lab Abnormality Rate |
| patient_financial_summary | Avg Treatment Cost, Revenue by State |
| doctor_performance_summary | Doctor Workload |
| medication_adherence_summary | Medication Adherence Rate |
| patient_risk_summary | High Risk Patients |

## Jira Project

All work items tracked in Jira project **DV** (Databricks Vibecoding).
Epic: **DV-1** - Patient360 Analytics Platform
