# Patient360 Analytics Platform — Product Requirements Document

**Project Name:** Patient360  
**Jira Epic:** DV-1  
**Version:** 1.0  
**Date:** 2026-06-18

---

## Project Description

End-to-end Patient 360 analytics platform on Databricks using a Medallion Architecture (Source → Bronze → Silver → Gold). The platform consolidates patient demographics, appointments, diagnoses, medications, lab reports, billing, and visit history into a unified patient view for healthcare analytics.

## Business Objective

- Ingest healthcare data from 7 CSV datasets
- Build governed data platform using Unity Catalog
- Standardize and cleanse healthcare records (8 DQ rules)
- Create Patient 360 analytical views (6 Gold tables)
- Generate healthcare KPIs and dashboards (4 dashboards, 10 KPIs)
- Enable clinical, operational, and financial reporting

## Source Information

- **Type:** CSV files  
- **Path:** `/Volumes/sdlc_catalog/patient_360/source/`  
- **Load Type:** Incremental  
- **PK:** patient_id (domain-specific keys per dataset)

### Datasets

| File | Primary Key |
|------|-------------|
| Patient_records.csv | patient_id |
| Appointment_record.csv | appointment_id |
| Diagnosis_record.csv | record_id |
| Medication.csv | medication_id |
| Lab_report.csv | serial_number |
| Billing_record.csv | bill_id |
| Patient_history.csv | appointment_id + patient_id |

## Medallion Architecture

| Layer | Catalog.Schema | Tables |
|-------|---------------|--------|
| Raw | sdlc_catalog.patient_360_raw | 7 raw tables |
| Bronze | sdlc_catalog.patient_360_bronze | 7 bronze tables |
| Silver | sdlc_catalog.patient_360_silver | 7 silver tables + dq_rejection_log |
| Gold | sdlc_catalog.patient_360_gold | 6 analytical tables + 2 KPI tables |

## Data Quality Rules

| ID | Rule | Table |
|----|------|-------|
| DQ001 | patient_id NOT NULL | silver_patient |
| DQ002 | appointment_id NOT NULL | silver_appointment |
| DQ003 | diagnosis_code NOT NULL | silver_diagnosis |
| DQ004 | treatment_cost >= 0 | silver_billing |
| DQ005 | medicine_price >= 0 | silver_medication |
| DQ006 | email format valid | silver_patient |
| DQ007 | booking_date <= current_date | silver_appointment |
| DQ008 | age BETWEEN 0 AND 120 | silver_patient |

## Gold Layer KPIs

Total Patients · Active Patients · Total Appointments · Disease Distribution · Average Treatment Cost · Revenue by State · Doctor Workload · High Risk Patients · Medication Adherence Rate · Lab Abnormality Rate

## Dashboard Requirements

| Dashboard | Audience |
|-----------|----------|
| Executive Dashboard | C-suite, management |
| Clinical Dashboard | Medical staff |
| Operational Dashboard | Administrators |
| Financial Dashboard | Finance team |

## Pipeline Requirements

- **Type:** Batch · **Schedule:** Daily 02:00 IST  
- **Orchestration:** Databricks Asset Bundle (DAB)  
- **Monitoring:** Email notifications on failure  
- **Deployment:** GitHub Actions CI/CD → DEV → QA → PROD

## Testing Requirements

- pytest unit tests for all 4 layers  
- Coverage target: 80%+  
- DQ rule tests: 8 rules validated

## Success Criteria

- Data ingested from source volume  
- Bronze/Silver/Gold layers created and populated  
- All 8 DQ rules passing (< 5% rejection rate)  
- 4 dashboards operational  
- CI/CD pipeline deploying to DEV  
- Business stakeholders can perform healthcare analytics
