# Patient360 Analytics Platform

End-to-end healthcare analytics platform on Databricks using Medallion Architecture. Ingests 7 CSV source datasets, transforms them through Raw → Bronze → Silver → Gold layers, and surfaces 4 interactive AI/BI Dashboards deployed via Databricks Asset Bundles.

**Workspace:** https://dbc-b779df5b-df6a.cloud.databricks.com  
**Catalog:** `sdlc_catalog`  
**Deployment:** Databricks Asset Bundle (DAB) — `databricks bundle deploy --target dev`

---

## Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│  SOURCE LAYER                                                       │
│  /Volumes/sdlc_catalog/patient_360/source/                         │
│  Patient_records.csv | Appointment_record.csv | Diagnosis_record.csv│
│  Medication.csv | Lab_report.csv | Billing_record.csv | Patient_history.csv│
└──────────────────────────────┬─────────────────────────────────────┘
                               │ Incremental CSV Read + Metadata Injection
                               ▼
┌────────────────────────────────────────────────────────────────────┐
│  RAW LAYER  [sdlc_catalog.patient_360_raw]                         │
│  + ingestion_timestamp  + source_file_name  + load_date  + record_hash│
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
└──────────────────────────────┬─────────────────────────────────────┘
                               │
                               ▼
┌────────────────────────────────────────────────────────────────────┐
│  AI/BI DASHBOARDS (Databricks — 4 deployed via DAB)                │
│  Executive | Clinical | Operational | Financial                    │
└────────────────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
patient360/
├── databricks.yml                  # DAB bundle — jobs + 4 dashboards
├── resources/
│   └── jobs.yml                    # Pipeline job task definitions
├── src/
│   ├── ingestion/
│   │   └── ingest_patient_records.py   # CSV → Raw schema
│   ├── bronze/
│   │   └── bronze_load_all.py          # Raw → Bronze Delta (MERGE INTO)
│   ├── silver/
│   │   ├── silver_transform_all.py     # Bronze → Silver (DQ + dedup)
│   │   └── dq_rules_engine.py          # Config-driven DQ rule engine
│   └── gold/
│       ├── gold_build_all.py           # Silver → Gold analytics tables
│       └── refresh_dashboard_datasets.py  # Post-pipeline dashboard refresh
├── dashboards/
│   ├── patient360_executive.lvdash.json    # Executive AI/BI Dashboard
│   ├── patient360_clinical.lvdash.json     # Clinical AI/BI Dashboard
│   ├── patient360_operational.lvdash.json  # Operational AI/BI Dashboard
│   ├── patient360_financial.lvdash.json    # Financial AI/BI Dashboard
│   ├── dashboard_spec.md                   # Original dashboard specification
│   ├── dashboard_kpis.yml                  # KPI definitions
│   ├── dashboard_filters.yml               # Filter definitions
│   ├── dashboard_queries.sql               # Source query spec
│   ├── dashboard_layout.json               # Layout spec
│   └── dashboard_documentation.md         # Dashboard field reference
├── tests/
│   ├── conftest.py
│   ├── test_ingestion.py
│   ├── test_bronze.py
│   ├── test_silver.py
│   └── test_gold.py
├── docs/
│   ├── architecture.md             # Detailed architecture document
│   ├── Dashboard_Specification.md  # Dashboard business requirements
│   ├── Deployment_Guide.md         # Step-by-step deploy guide
│   ├── PRD.md                      # Product Requirements Document
│   ├── runbook.md                  # Operational runbook
│   └── source_to_target_mapping.md # Column-level data lineage
├── .github/
│   └── workflows/
│       ├── validate.yml            # PR validation
│       ├── unit-test.yml           # Unit test runner
│       ├── deploy-dev.yml          # Auto-deploy to dev on merge
│       ├── deploy-qa.yml           # QA deployment
│       └── deploy-prod.yml         # Production deployment
└── README.md                       # This file
```

---

## Deployed Resources (DEV)

### Job Pipeline

| Field | Value |
|-------|-------|
| **Job Name** | `[dev jaswanthkadali] Patient360 Analytics Pipeline - dev` |
| **Job ID** | `661870938048958` |
| **URL** | https://dbc-b779df5b-df6a.cloud.databricks.com/jobs/661870938048958 |
| **Schedule** | Daily 02:00 IST (Asia/Kolkata) |
| **Tasks** | `ingest_source → bronze_load → silver_transform → gold_build → dashboard_refresh` |

### AI/BI Dashboards

All 4 dashboards are deployed to `sdlc_catalog.patient_360_gold` and visible in the Databricks workspace. Each dashboard has interactive multi-select filters, KPI counters, trend charts, distribution charts, and a drill-down detail table.

| Dashboard | ID | URL | Widgets | Queries | Visualizations |
|-----------|-----|-----|---------|---------|----------------|
| **Executive** | `01f16bab4b1716c38d3bc1a0915e1284` | [Open](https://dbc-b779df5b-df6a.cloud.databricks.com/dashboardsv3/01f16bab4b1716c38d3bc1a0915e1284/published?w=7474646775525983) | 18 | 6 | 13 |
| **Clinical** | `01f16bab4b3312f4ac6db856fcb10c58` | [Open](https://dbc-b779df5b-df6a.cloud.databricks.com/dashboardsv3/01f16bab4b3312f4ac6db856fcb10c58/published?w=7474646775525983) | 17 | 6 | 12 |
| **Operational** | `01f16bab4afb12ebae0228527bd91435` | [Open](https://dbc-b779df5b-df6a.cloud.databricks.com/dashboardsv3/01f16bab4afb12ebae0228527bd91435/published?w=7474646775525983) | 16 | 5 | 11 |
| **Financial** | `01f16bab4b351289aaf18e47b9e03e6d` | [Open](https://dbc-b779df5b-df6a.cloud.databricks.com/dashboardsv3/01f16bab4b351289aaf18e47b9e03e6d/published?w=7474646775525983) | 17 | 5 | 12 |
| **Total** | | | **68** | **22** | **48** |

#### Executive Dashboard
C-level overview: patient volumes, revenue trends, and state-level breakdowns.
- **KPIs:** Total Patients, Total Revenue (INR), Active Patients (90d), Total Appointments, Avg Treatment Cost, Avg Insurance Coverage %
- **Charts:** Revenue by State (bar), Monthly Patient Activity Trend (line), Age Distribution (bar), Sex Distribution (pie)
- **Table:** State Revenue Summary (drill-down)
- **Filters:** State, Sex
- **Gold tables:** `patient_360_master`, `patient_financial_summary`

#### Clinical Dashboard
Disease distribution, lab risk, medication adherence, and patient risk stratification.
- **KPIs:** Lab Risk Patients, Lab Abnormality Rate, Avg Medication Adherence, Unique Diseases, Active Medications, Total Diagnosis Records
- **Charts:** Disease Distribution (pie), Risk Category (bar), Adherence by Disease (horizontal bar)
- **Table:** Patient Risk Detail — top 50 by risk score
- **Filters:** Risk Category, Disease
- **Gold tables:** `patient_clinical_summary`, `medication_adherence_summary`, `patient_risk_summary`, `patient_360_master`

#### Operational Dashboard
Doctor performance, department workload, and patient demographics for administrators.
- **KPIs:** Active Doctors, Total Appointments, Active Departments, Unique Patients, Doctor Revenue (INR), Avg Appts/Department
- **Charts:** Department Workload (horizontal bar), Revenue by Doctor (horizontal bar), Patient Age Distribution (bar)
- **Table:** Doctor Performance Detail — top 15 by appointments
- **Filters:** Department
- **Gold tables:** `doctor_performance_summary`, `patient_360_master`

#### Financial Dashboard
Revenue trends, insurance coverage, payment mode analysis, and patient billing detail.
- **KPIs:** Total Revenue (INR), Avg Treatment Cost (INR), Avg Insurance Coverage %, Paid Bills, UPI Transactions, Cash Transactions
- **Charts:** Monthly Revenue Trend (line), Payment Mode Distribution (pie), Revenue by State (bar)
- **Table:** Patient Financial Detail — top 50 by out-of-pocket cost
- **Filters:** State, Payment Mode
- **Gold tables:** `patient_financial_summary`, `patient_360_master`

---

## Gold Layer Tables

All dashboards source exclusively from `sdlc_catalog.patient_360_gold`.

| Table | Rows | Key Metrics |
|-------|------|-------------|
| `patient_360_master` | 100 | Unified patient view — demographics, appointments, treatment cost |
| `patient_financial_summary` | 100 | Per-patient: total cost, insurance coverage, UPI/cash payments, paid bills |
| `patient_risk_summary` | 100 | Age/lab/financial risk scores per patient |
| `patient_clinical_summary` | 100 | Lab test results, abnormality flags, active medications |
| `doctor_performance_summary` | 44 | Per-doctor: appointments, unique patients, revenue, avg charge |
| `medication_adherence_summary` | 146 | Per-patient/disease: adherence rate, medicine cost |

---

## Source Datasets

| CSV File | Raw Table | Primary Key | Rows |
|----------|-----------|-------------|------|
| Patient_records.csv | `raw_patient_records` | patient_id | 100 |
| Appointment_record.csv | `raw_appointment_records` | appointment_id | 100 |
| Diagnosis_record.csv | `raw_diagnosis_records` | record_id | 100 |
| Medication.csv | `raw_medication` | medication_id | 200 |
| Lab_report.csv | `raw_lab_reports` | serial_number | 251 |
| Billing_record.csv | `raw_billing_records` | bill_id | 100 |
| Patient_history.csv | `raw_patient_history` | appointment_id + patient_id | 100 |

---

## Data Quality Framework

8 rules enforced at Silver layer via the config-driven `dq_rules_engine.py`. Failures are quarantined to `dq_rejection_log` — never silently dropped.

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

---

## Quick Start

### Prerequisites

- Databricks CLI v1.0+ installed
- Authenticated profile (`databricks auth profiles`)
- Access to `https://dbc-b779df5b-df6a.cloud.databricks.com`
- Unity Catalog: `sdlc_catalog` with source volume at `patient_360/source/`

### Deploy to DEV

```bash
# Validate bundle (zero-error check)
databricks bundle validate --profile DEFAULT

# Deploy all resources (job + 4 dashboards)
databricks bundle deploy --target dev --profile DEFAULT

# Verify deployed resources
databricks bundle summary --target dev --profile DEFAULT

# Run the full pipeline
databricks bundle run patient360_pipeline --target dev --profile DEFAULT
```

### Deploy to QA / PROD

```bash
databricks bundle deploy --target qa --profile DEFAULT
databricks bundle deploy --target prod --profile DEFAULT
```

### Run Tests Locally

```bash
pip install pytest pyspark==3.5.0 pytest-cov
pytest tests/ -v --cov=src --cov-report=term-missing
```

---

## Bundle Configuration

`databricks.yml` defines 3 targets (`dev`, `qa`, `prod`) and inlines all 4 dashboard resources:

```yaml
resources:
  dashboards:
    executive_dashboard:
      file_path: ./dashboards/patient360_executive.lvdash.json
      warehouse_id: ${var.warehouse_id}
    clinical_dashboard:
      file_path: ./dashboards/patient360_clinical.lvdash.json
      warehouse_id: ${var.warehouse_id}
    operational_dashboard:
      file_path: ./dashboards/patient360_operational.lvdash.json
      warehouse_id: ${var.warehouse_id}
    financial_dashboard:
      file_path: ./dashboards/patient360_financial.lvdash.json
      warehouse_id: ${var.warehouse_id}
```

The job definition is in `resources/jobs.yml` (included via `include: [resources/jobs.yml]`).

---

## CI/CD

GitHub Actions workflows in `.github/workflows/`:

| Workflow | Trigger | Action |
|----------|---------|--------|
| `validate.yml` | Pull Request | `databricks bundle validate` |
| `unit-test.yml` | Pull Request | `pytest tests/` |
| `deploy-dev.yml` | Merge to `master` | `bundle deploy --target dev` |
| `deploy-qa.yml` | Manual dispatch | `bundle deploy --target qa` |
| `deploy-prod.yml` | Manual dispatch | `bundle deploy --target prod` |

---

## Key Design Decisions

1. **Incremental load via append** at Raw — full history preserved with `ingestion_timestamp`
2. **MERGE INTO** at Bronze — upsert deduplication per primary key (prevents duplicates on re-run)
3. **Row-number deduplication** at Silver — latest record wins per PK
4. **Config-driven DQ engine** — rules defined in a Python dict, single engine handles all tables
5. **Delta format throughout** — time travel, schema evolution, ACID transactions
6. **Unity Catalog** — centralized governance, lineage tracking, access control
7. **DAB for IaC** — single `databricks bundle deploy` deploys job + all 4 dashboards atomically
8. **Gold-only dashboards** — all 22 dataset queries exclusively hit `sdlc_catalog.patient_360_gold`
9. **Percent scaling** — `adherence_rate` and `insurance_coverage_pct` divided by 100 in SQL to satisfy Lakeview's 0–1 percent format requirement

---

## Deployment History

| Date | Action | Details |
|------|--------|---------|
| 2026-06-18 | Initial deployment | Medallion pipeline + 7 legacy dashboards via ai-dev-kit |
| 2026-06-19 | DAB migration | Rewrote bundle config; fixed 5 DAB validation errors; deployed 4 new AI/BI dashboards via `databricks bundle deploy` |
| 2026-06-19 | Cleanup | Deleted 1 duplicate job + 7 stale dashboards; removed orphaned `resources/dashboards.yml` |
