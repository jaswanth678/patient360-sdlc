# Patient 360 Analytics Platform — Product Requirements Document (PRD)

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

- Ingest healthcare data from multiple CSV datasets.
- Build a governed data platform using Unity Catalog.
- Standardize and cleanse healthcare records.
- Create Patient 360 analytical views.
- Generate healthcare KPIs and dashboards.
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
Cluster ID:         Not applicable — serverless compute is used; `cluster_id` is intentionally left empty
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

- Patient_records.csv
- Appointment_record.csv
- Diagnosis_record.csv
- Medication.csv
- Lab_report.csv
- Billing_record.csv
- Patient_history.csv

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

## Raw Layer Requirements
- Store source files without business transformation.
- Add `ingestion_timestamp`.
- Add `source_file_name`.
- Maintain complete lineage.
- Catalog: sdlc_catalog · Schema: patient_360_raw

## Bronze Layer Requirements

Create Bronze Delta tables:
- bronze_patient
- bronze_appointment
- bronze_diagnosis
- bronze_medication
- bronze_lab
- bronze_billing
- bronze_patient_history

Target Schema: sdlc_catalog.patient_360_bronze
Transformations: column sanitization · metadata columns · schema evolution · audit tracking

## Silver Layer Requirements

Transformations:
- Remove duplicates
- Handle null values
- Standardize dates
- Data quality validation
- Normalize patient information
- Derive lab status indicators
- Create patient visit metrics
- Standardize insurance and payment fields

Target Schema: sdlc_catalog.patient_360_silver

## Gold Layer Requirements

Create analytical datasets:
- patient_360_master
- patient_clinical_summary
- patient_financial_summary
- doctor_performance_summary
- medication_adherence_summary
- patient_risk_summary

Target Schema: sdlc_catalog.patient_360_gold

KPIs:
- Total Patients
- Active Patients
- Total Appointments
- Disease Distribution
- Average Treatment Cost
- Revenue by State
- Doctor Workload
- High Risk Patients
- Medication Adherence Rate
- Lab Abnormality Rate

---

# 6. Data Quality Rules

- Rule 1: patient_id must not be null
- Rule 2: appointment_id must not be null
- Rule 3: diagnosis_code must not be null
- Rule 4: treatment_cost >= 0
- Rule 5: medicine_price >= 0
- Rule 6: email format validation
- Rule 7: booking_date <= current date
- Rule 8: patient age between 0 and 120

---

# 7. Pipeline Requirements

```
Pipeline Type: Batch
Schedule:      Daily
Trigger:       Databricks Workflow
Orchestration: Databricks Asset Bundle
Monitoring:    Workflow Notifications
```

---

# 8. Dashboard Requirements

**Executive Dashboard:** Total Patients · Total Revenue · Total Appointments · Active Cases
**Clinical Dashboard:** Disease Analysis · Lab Risk Trends · Patient Health Status
**Operational Dashboard:** Doctor Performance · Department Workload · Visit Frequency
**Financial Dashboard:** Revenue Trends · Insurance Coverage Analysis · Billing Summary

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
- No PII (patient email, contact, address) exposed in Gold dashboards — mask or exclude sensitive columns.
- Credentials and tokens never hardcoded — sourced from Databricks secrets / CI environment variables.
- Audit lineage maintained from Raw through Gold via ingestion metadata columns.

---

# 11. Deployment Requirements

```
Environments:      DEV → QA → PROD   (auto-promotion via GitHub Actions; all targets use the same workspace host)
Deployment Method: Databricks Asset Bundle
Source Control:    GitHub
CI/CD:             GitHub Actions
```

---

# 12. Team Roster (for Jira ownership)

```
team_roster:
  - { name: "Sweta Kumari", email: "", role: "Developer" }
```

> Sweta Kumari is the Developer — all generated Jira Epics/Features/Stories/Tasks are
> assigned to her. (Add her email to enable account lookup if name resolution is ambiguous.)

---

# 13. Deliverables & Success Criteria

## Deliverables
- Databricks Asset Bundle
- Jobs Configuration
- DLT / PySpark Pipelines
- Dashboard JSON
- Unit Tests
- Architecture Diagram
- README.md
- PRD Document
- Deployment Guide

## Success Criteria
- Data successfully ingested from source location
- Bronze, Silver, Gold layers created
- Patient 360 view generated
- Dashboards operational
- Data quality rules passing
- CI/CD deployment successful
- Business stakeholders able to perform healthcare analytics
