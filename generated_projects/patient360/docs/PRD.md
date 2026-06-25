# Patient 360 Analytics Platform — Product Requirements Document (PRD)

**Jira Epic:** DV-1 · **Version:** 1.1 · **Date:** 2026-06-25
*(Authored against `requirements/PRD_format_template.md`. Canonical source: `requirements/Patient360_PRD.md`.)*

# 1. Project Identity

```
Project Name: Patient360
```

## Project Description

Build an end-to-end Patient 360 analytics platform on Databricks using a Medallion
Architecture (Source → Bronze → Silver → Gold). The platform consolidates patient
demographics, appointments, diagnoses, medications, lab reports, billing, and visit
history into a unified patient view for healthcare analytics.

## Business Objective

- Ingest healthcare data from 7 CSV datasets.
- Build a governed data platform using Unity Catalog.
- Standardize and cleanse healthcare records (8 DQ rules).
- Create Patient 360 analytical views (6 Gold tables).
- Generate healthcare KPIs and dashboards (4 dashboards, 10 KPIs).
- Enable clinical, operational, and financial reporting.

## Business Domain

```
Business Domain: Healthcare
```

> Primary Entity: Patient · Revenue Measure: Treatment Cost · Operational Measure: Admissions · Risk Measure: Risk Score

---

# 2. Jira Information

```
Jira Project Name: Databricks Vibecoding
Jira Project Key:  DV
```

---

# 3. Databricks Environment Configuration

```
Workspace Host:     https://dbc-b779df5b-df6a.cloud.databricks.com
Catalog Name:       sdlc_catalog
Source Schema:      patient_360
Raw Schema:         patient_360_raw
Bronze Schema:      patient_360_bronze
Silver Schema:      patient_360_silver
Gold Schema:        patient_360_gold
Warehouse ID:       5e872471aabd37ad
Cluster ID:         Not applicable — serverless compute is used
Notification Email: jaswanthkadali@gmail.com
```

---

# 4. Source Information

```
Source Type: CSV
Source Path: sdlc_catalog.patient_360.source
Load Type:   Incremental
Primary Key: patient_id (domain-specific keys retained per dataset)
```

## Datasets / Source Tables

| File | Primary Key |
|------|-------------|
| Patient_records.csv | patient_id |
| Appointment_record.csv | appointment_id |
| Diagnosis_record.csv | record_id |
| Medication.csv | medication_id |
| Lab_report.csv | serial_number |
| Billing_record.csv | bill_id |
| Patient_history.csv | appointment_id + patient_id |

## Dataset Information (schemas)

**Patient Records:**
Patient_ID, Patient_NAME, SEX, State, Age, Diease_name, Doctor_id, Doctors_name, DOB, Contact, email, address

**Appointments:**
Patient_id, Appointment_id, doctor_name, doctore_id, booking_date, department, visit_type, status(y/n)

**Diagnosis:**
Record_Id, Patient_Id, Doctor_name, Doctor_Id, Disease_name, diagnosis_description, encounter_id, rank, checkup_date, diagnosis_code, Doctor_Charge_INR

**Medication:**
medication_id, Doctor_id, Patient_id, encounter_id, medication_name, dosage, route, start_date, end_date, is_active, Disease, medicine_price

**Lab Reports:**
Serial_number, Patient_id, Doctor's_id, lab_test_name, test_result, normal_range_min, normal_range_max, Booking_date, Collect_report_date, collect report(y/n), cost

**Billing:**
bill_id, patient_id, Patient_name, appointment_id, treatment_cost, insurence_number, insurence_coverage, payment_status, payment_mode(UPI/cash), Payment_Date, insurence_provider

**Patient History:**
appointment_id, patient_id, doctor_name, doctor_id, visit_type, current_visit_date, prior_visit_date

---

# 5. Medallion Layer Requirements

| Layer | Catalog.Schema | Tables |
|-------|---------------|--------|
| Raw | sdlc_catalog.patient_360_raw | 7 raw tables |
| Bronze | sdlc_catalog.patient_360_bronze | 7 bronze tables |
| Silver | sdlc_catalog.patient_360_silver | 7 silver tables + dq_rejection_log |
| Gold | sdlc_catalog.patient_360_gold | 6 analytical tables + 2 KPI tables |

## Raw Layer Requirements
- Store source files without business transformation.
- Add `ingestion_timestamp`, `source_file_name`.
- Maintain complete lineage.

## Bronze Layer Requirements
Create Bronze Delta tables: bronze_patient, bronze_appointment, bronze_diagnosis,
bronze_medication, bronze_lab, bronze_billing, bronze_patient_history.
Transformations: column sanitization · metadata columns · schema evolution · audit tracking.

## Silver Layer Requirements
Remove duplicates · handle nulls · standardize dates · DQ validation · normalize patient
information · derive lab status indicators · create patient visit metrics · standardize
insurance and payment fields.

## Gold Layer Requirements
Create analytical datasets: patient_360_master, patient_clinical_summary,
patient_financial_summary, doctor_performance_summary, medication_adherence_summary,
patient_risk_summary.

KPIs: Total Patients · Active Patients · Total Appointments · Disease Distribution ·
Average Treatment Cost · Revenue by State · Doctor Workload · High Risk Patients ·
Medication Adherence Rate · Lab Abnormality Rate.

---

# 6. Data Quality Rules

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

Failures are quarantined to `dq_rejection_log` — never silently dropped.

---

# 7. Pipeline Requirements

```
Pipeline Type: Batch
Schedule:      Daily 02:00 IST
Trigger:       Databricks Workflow
Orchestration: Databricks Asset Bundle
Monitoring:    Workflow Notifications (email on failure)
```

---

# 8. Dashboard Requirements

| Dashboard | Audience |
|-----------|----------|
| Executive Dashboard | C-suite, management |
| Clinical Dashboard | Medical staff |
| Operational Dashboard | Administrators |
| Financial Dashboard | Finance team |

---

# 9. Testing Requirements

```
Generate unit tests for: Ingestion · Bronze · Silver · Gold
Coverage Target: 80%+
```

---

# 10. Security Requirements

- Governance via Unity Catalog — all data assets registered under `sdlc_catalog`.
- Access control enforced through Unity Catalog grants on catalog, schemas, and tables.
- No PII (patient email, contact, address) exposed in Gold dashboards.
- Credentials and tokens never hardcoded — sourced from Databricks secrets / CI env vars.
- Audit lineage maintained from Raw through Gold via ingestion metadata columns.

---

# 11. Deployment Requirements

```
Environments:      DEV → QA → PROD   (auto-promotion via GitHub Actions; same workspace host)
Deployment Method: Databricks Asset Bundle
Source Control:    GitHub
CI/CD:             GitHub Actions
```

---

# 12. Team Roster (for Jira ownership)

```
team_roster:
  - { name: "Sweta Kumari", role: "Developer" }
```

> Sweta Kumari is the Developer — all DV Epics/Features/Stories/Tasks (DV-1 … DV-40) are
> assigned to her. Jira users in this project are identified by display name only (no emails
> on record), so assignment is resolved via Jira account lookup by name.

---

# 13. Deliverables & Success Criteria

## Deliverables
- Databricks Asset Bundle · Jobs Config · PySpark/DLT Pipelines · Dashboard JSON
- Unit Tests · Architecture Diagram · README.md · PRD Document · Deployment Guide

## Success Criteria
- Data ingested from source volume.
- Bronze/Silver/Gold layers created and populated.
- All 8 DQ rules passing (< 5% rejection rate).
- 4 dashboards operational.
- CI/CD pipeline deploying to DEV → QA → PROD.
- Business stakeholders able to perform healthcare analytics.
