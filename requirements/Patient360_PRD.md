# **Patient 360 Analytics Platform \- Product Requirements Document (PRD)**

**Project Name:** Patient360

## **Project Description**

Build an end-to-end Patient 360 analytics platform on Databricks using a Medallion Architecture (Source → Bronze → Silver → Gold). The platform consolidates patient demographics, appointments, diagnoses, medications, lab reports, billing, and visit history into a unified patient view for healthcare analytics.

## **Business Objective**

The solution should:  
• Ingest healthcare data from multiple CSV datasets.  
• Build a governed data platform using Unity Catalog.  
• Standardize and cleanse healthcare records.  
• Create Patient 360 analytical views.  
• Generate healthcare KPIs and dashboards.  
• Enable clinical, operational, and financial reporting.

## **Jira Information**

Jira Project Key: DV

## **Source Information**

Source Type: CSV  
Source Path: sdlc\_catalog.patient\_360.source

Datasets:  
• Patient\_records.csv  
• Appointment\_record.csv  
• Diagnosis\_record.csv  
• Medication.csv  
• Lab\_report.csv  
• Billing\_record.csv  
• Patient\_history.csv

Load Type: Incremental  
Primary Key: patient\_id (domain-specific keys retained per dataset)

## **Dataset Information**

Patient Records:  
Patient\_ID, Patient\_NAME, SEX, State, Age, Diease\_name, Doctor\_id, Doctors\_name, DOB, Contact, email, address

Appointments:  
Patient\_id, Appointment\_id, doctor\_name, doctore\_id, booking\_date, department, visit\_type, status(y/n)

Diagnosis:  
Record\_Id, Patient\_Id, Doctor\_name, Doctor\_Id, Disease\_name, diagnosis\_description, encounter\_id, rank, checkup\_date, diagnosis\_code, Doctor\_Charge\_INR

Medication:  
medication\_id, Doctor\_id, Patient\_id, encounter\_id, medication\_name, dosage, route, start\_date, end\_date, is\_active, Disease, medicine\_price

Lab Reports:  
Serial\_number, Patient\_id, Doctor's\_id, lab\_test\_name, test\_result, normal\_range\_min, normal\_range\_max, Booking\_date, Collect\_report\_date, collect report(y/n), cost

Billing:  
bill\_id, patient\_id, Patient\_name, appointment\_id, treatment\_cost, insurence\_number, insurence\_coverage, payment\_status, payment\_mode(UPI/cash), Payment\_Date, insurence\_provider

Patient History:  
appointment\_id, patient\_id, doctor\_name, doctor\_id, visit\_type, current\_visit\_date, prior\_visit\_date

## **Raw Layer Requirements**

Store source files without business transformation.  
Add ingestion\_timestamp.  
Add source\_file\_name.  
Maintain complete lineage.  
Catalog: sdlc\_catalog  
Schema: patient\_360\_raw

## **Bronze Layer Requirements**

Create Bronze Delta tables:  
bronze\_patient  
bronze\_appointment  
bronze\_diagnosis  
bronze\_medication  
bronze\_lab  
bronze\_billing  
bronze\_patient\_history

Transformations:  
• Column sanitization  
• Metadata columns  
• Schema evolution support  
• Audit tracking

## **Silver Layer Requirements**

Transformations:  
• Remove duplicates  
• Handle null values  
• Standardize dates  
• Data quality validation  
• Normalize patient information  
• Derive lab status indicators  
• Create patient visit metrics  
• Standardize insurance and payment fields

Target Schema:  
sdlc\_catalog.patient\_360\_silver

## **Gold Layer Requirements**

Create analytical datasets:  
• patient\_360\_master  
• patient\_clinical\_summary  
• patient\_financial\_summary  
• doctor\_performance\_summary  
• medication\_adherence\_summary  
• patient\_risk\_summary

KPIs:  
• Total Patients  
• Active Patients  
• Total Appointments  
• Disease Distribution  
• Average Treatment Cost  
• Revenue by State  
• Doctor Workload  
• High Risk Patients  
• Medication Adherence Rate  
• Lab Abnormality Rate

## **Data Quality Rules**

Rule 1: patient\_id must not be null  
Rule 2: appointment\_id must not be null  
Rule 3: diagnosis\_code must not be null  
Rule 4: treatment\_cost \>= 0  
Rule 5: medicine\_price \>= 0  
Rule 6: email format validation  
Rule 7: booking\_date \<= current date  
Rule 8: patient age between 0 and 120

## **Pipeline Requirements**

Pipeline Type: Batch  
Schedule: Daily  
Trigger: Databricks Workflow  
Orchestration: Databricks Asset Bundle  
Monitoring: Workflow Notifications

## **Dashboard Requirements**

Executive Dashboard:  
• Total Patients  
• Total Revenue  
• Total Appointments  
• Active Cases

Clinical Dashboard:  
• Disease Analysis  
• Lab Risk Trends  
• Patient Health Status

Operational Dashboard:  
• Doctor Performance  
• Department Workload  
• Visit Frequency

Financial Dashboard:  
• Revenue Trends  
• Insurance Coverage Analysis  
• Billing Summary

## **Testing Requirements**

Generate unit tests for:  
• Ingestion Layer  
• Bronze Layer  
• Silver Layer  
• Gold Layer  
Coverage Target: 80%+

## **Deployment Requirements**

Environment: DEV 

Deployment Method: Databricks Asset Bundle  
Source Control: GitHub  
CI/CD: GitHub Actions

## **Deliverables**

• Databricks Asset Bundle  
• Jobs Configuration  
• DLT / PySpark Pipelines  
• Dashboard JSON  
• Unit Tests  
• Architecture Diagram  
• README.md  
• PRD Document  
• Deployment Guide

## **Success Criteria**

• Data successfully ingested from source location  
• Bronze, Silver, Gold layers created  
• Patient 360 view generated  
• Dashboards operational  
• Data quality rules passing  
• CI/CD deployment successful  
• Business stakeholders able to perform healthcare analytics