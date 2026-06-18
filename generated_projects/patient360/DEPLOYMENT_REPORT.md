# Patient360 Analytics Platform — Final Deployment Report

**Date:** 2026-06-18  
**Deployed by:** jaswanthkadali@gmail.com  
**Workspace:** https://dbc-b779df5b-df6a.cloud.databricks.com  
**GitHub:** https://github.com/jaswanth678/patient360-sdlc  
**Release:** https://github.com/jaswanth678/patient360-sdlc/releases/tag/v1.0.0  
**Status:** DEPLOYMENT COMPLETE

---

## Databricks Assets

### Job Pipeline (Primary)
| Field | Value |
|-------|-------|
| Job ID | 444472832861238 |
| URL | https://dbc-b779df5b-df6a.cloud.databricks.com/jobs/444472832861238 |
| Tasks | ingest_source → bronze_load → silver_transform → gold_build → validate_pipeline |
| Schedule | 02:00 IST daily (paused) |
| Status | SUCCESS (all tasks completed end-to-end) |

### DLT Pipeline
| Field | Value |
|-------|-------|
| Pipeline ID | ecb7bda2-b245-4292-9c8f-551b98907a43 |
| URL | https://dbc-b779df5b-df6a.cloud.databricks.com/pipelines/ecb7bda2-b245-4292-9c8f-551b98907a43 |
| Target Schema | sdlc_catalog.patient_360_dlt |
| Status | COMPLETED (53 seconds, 7 silver tables) |
| Notebook | /Workspace/Users/jaswanthkadali@gmail.com/patient360/src/src/ingestion/patient360_dlt_pipeline.py |

### SQL Warehouse
| Field | Value |
|-------|-------|
| Warehouse ID | 5e872471aabd37ad |
| URL | https://dbc-b779df5b-df6a.cloud.databricks.com/sql/warehouses/5e872471aabd37ad |

---

## Unity Catalog — Table Inventory

### Raw Layer (`sdlc_catalog.patient_360_raw`)
7 tables — Patient, Appointment, Diagnosis, Medication, Lab, Billing, PatientHistory

### Bronze Layer (`sdlc_catalog.patient_360_bronze`)
7 tables — deduplicated MERGE with schema sanitization

### Silver Layer (`sdlc_catalog.patient_360_silver`)
| Table | Rows |
|-------|------|
| silver_patient | 100 |
| silver_appointment | 100 |
| silver_diagnosis | 100 |
| silver_medication | 200 |
| silver_lab | 251 |
| silver_billing | 100 |
| silver_patient_history | 100 |

### Gold Layer (`sdlc_catalog.patient_360_gold`)
| Table | Rows | Description |
|-------|------|-------------|
| patient_360_master | 100 | Unified patient view with all aggregates |
| patient_financial_summary | 100 | Per-patient financial breakdown |
| patient_risk_summary | 100 | Age/lab/financial risk scoring |
| patient_clinical_summary | 100 | Clinical diagnoses and lab risk flags |
| doctor_performance_summary | 44 | Doctor revenue and appointment counts |
| medication_adherence_summary | 146 | Medication adherence rates by disease |

### DLT Layer (`sdlc_catalog.patient_360_dlt`)
| Table | Rows |
|-------|------|
| silver_patient | 100 |
| silver_appointment | 100 |
| silver_billing | 100 |
| silver_diagnosis | 100 |
| silver_lab | 251 |
| silver_medication | 200 |
| silver_patient_history | 100 |

---

## AI/BI Dashboards (7 Published)

| Dashboard | ID | URL |
|-----------|----|-----|
| Executive | 01f16b2c29761be1b683af2fdfc75987 | https://dbc-b779df5b-df6a.cloud.databricks.com/sql/dashboardsv3/01f16b2c29761be1b683af2fdfc75987 |
| Clinical | 01f16b2c2bed127bbb817d31ee3bf197 | https://dbc-b779df5b-df6a.cloud.databricks.com/sql/dashboardsv3/01f16b2c2bed127bbb817d31ee3bf197 |
| Operational | 01f16b2c2e7d1ae8bcb3770c361f3657 | https://dbc-b779df5b-df6a.cloud.databricks.com/sql/dashboardsv3/01f16b2c2e7d1ae8bcb3770c361f3657 |
| Financial | 01f16b2c317614d7832a31cf12c9c7e4 | https://dbc-b779df5b-df6a.cloud.databricks.com/sql/dashboardsv3/01f16b2c317614d7832a31cf12c9c7e4 |
| Data Quality | 01f16b2c4fca1310b569134fde287768 | https://dbc-b779df5b-df6a.cloud.databricks.com/sql/dashboardsv3/01f16b2c4fca1310b569134fde287768 |
| KPI | 01f16b2c56fa14e4bdb74b2d944a9fa2 | https://dbc-b779df5b-df6a.cloud.databricks.com/sql/dashboardsv3/01f16b2c56fa14e4bdb74b2d944a9fa2 |
| Monitoring | 01f16b2c688f190eb93ee399ce4ae570 | https://dbc-b779df5b-df6a.cloud.databricks.com/sql/dashboardsv3/01f16b2c688f190eb93ee399ce4ae570 |

---

## GitHub Repository

| Item | Value |
|------|-------|
| Repository | https://github.com/jaswanth678/patient360-sdlc |
| Branch | master |
| Commit | d42ac18 — 67 files |
| Release | v1.0.0 |
| Release URL | https://github.com/jaswanth678/patient360-sdlc/releases/tag/v1.0.0 |

---

## Issues Fixed During Deployment

| # | Error | Root Cause | Fix |
|---|-------|-----------|-----|
| 1 | `DELTA_MULTIPLE_SOURCE_ROW_MATCHING_TARGET_ROW_IN_MERGE` | Repeated ingestion appended duplicates | Added `dedup_by_pk()` using `row_number().over(Window)` before MERGE |
| 2 | `CANNOT_PARSE_TIMESTAMP '2/2/2026'` | `M/d/yyyy` vs `yyyy-MM-dd` date format mismatch | Created `flex_date()` helper using `try_to_date` in coalesce |
| 3 | Slash/special chars in column names | Old regex didn't catch `/`, `'` | Broadened to `re.sub(r'[^a-zA-Z0-9_]+', '_', name)` |
| 4 | `UNRESOLVED_COLUMN payment_mode_upi_cash_` | Trailing underscore after `.strip('_')` | Changed to `payment_mode_upi_cash` |
| 5 | `UNRESOLVED_COLUMN disease_name` | CSV typo: `diease_name` | Used `col("diease_name").alias("disease_name")` |
| 6 | `AMBIGUOUS_REFERENCE age` | Both master and pat DataFrames had `age` after join | Removed `age` from `pat` select |
| 7 | DLT `root_path` not found | `dlt` directory never existed in workspace | Uploaded DLT file to existing path |
| 8 | DLT `UNSUPPORTED_SPARK_SQL_COMMAND CreateNamespace` | DDL not allowed in DLT SDP Python | Rewrote as proper `@dlt.table` notebook (no DDL) |
| 9 | DLT conflict with existing silver tables | Job already created managed tables in same schema | Pointed DLT to dedicated `patient_360_dlt` schema |
