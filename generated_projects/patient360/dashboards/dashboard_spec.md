# Patient360 Dashboard Specification

## Overview
Four Databricks AI/BI dashboards built entirely on Gold layer tables from `sdlc_catalog.patient_360_gold`.

---

## Dashboard 1 — Executive Dashboard

**Purpose:** C-level overview of healthcare operations  
**Refresh:** Daily after pipeline completes  
**Source Tables:** `patient_360_master`, `kpi_summary`, `patient_financial_summary`

### KPI Cards
| Card | Metric | Source |
|------|--------|--------|
| Total Patients | COUNT(DISTINCT patient_id) | patient_360_master |
| Active Patients | patients with appointment in last 90 days | patient_360_master |
| Total Revenue (INR) | SUM(total_treatment_cost) | patient_financial_summary |
| Total Appointments | SUM(total_appointments) | patient_360_master |
| Active Cases | patients with is_active diagnosis | patient_clinical_summary |
| Avg Treatment Cost | AVG(treatment_cost) | patient_financial_summary |

### Charts
- **Revenue by State** — Horizontal bar chart, x=state, y=total_revenue
- **Monthly Appointment Trend** — Line chart, x=month, y=appointment_count
- **Patient Age Distribution** — Histogram, x=age_group, y=patient_count
- **Active vs Inactive Patients** — Donut chart

---

## Dashboard 2 — Clinical Dashboard

**Purpose:** Clinical analysis for medical staff  
**Source Tables:** `patient_clinical_summary`, `patient_risk_summary`, `medication_adherence_summary`

### KPI Cards
| Card | Metric |
|------|--------|
| Total Diagnoses | COUNT(total_diagnoses) |
| Unique Diseases | COUNT(DISTINCT disease_name) |
| High Risk Patients | COUNT where risk_category = 'HIGH_RISK' |
| Lab Abnormality Rate | abnormal_lab / total_lab * 100 |
| Medication Adherence Rate | AVG(adherence_rate) |

### Charts
- **Disease Distribution** — Pie chart, dimension=disease_name, measure=patient_count
- **Lab Risk Trends** — Area chart, x=month, y=abnormal_lab_count
- **Patient Risk Categories** — Bar chart, x=risk_category, y=patient_count
- **Top 10 Diseases** — Horizontal bar chart
- **Medication Adherence by Disease** — Bar chart

---

## Dashboard 3 — Operational Dashboard

**Purpose:** Operational performance for administrators  
**Source Tables:** `doctor_performance_summary`, `patient_360_master`

### KPI Cards
| Card | Metric |
|------|--------|
| Total Doctors | COUNT(DISTINCT doctor_id) |
| Avg Patients per Doctor | AVG(unique_patients) |
| Total Revenue by Doctors | SUM(total_revenue_inr) |
| Busiest Department | MAX(total_appointments) |

### Charts
- **Doctor Workload** — Bar chart, x=doctor_name, y=total_appointments
- **Department Workload** — Horizontal bar chart, x=department, y=appointment_count
- **Visit Frequency Distribution** — Histogram
- **Doctor Revenue Performance** — Scatter plot, x=unique_patients, y=total_revenue_inr

---

## Dashboard 4 — Financial Dashboard

**Purpose:** Financial analysis for billing and finance teams  
**Source Tables:** `patient_financial_summary`, `kpi_summary`

### KPI Cards
| Card | Metric |
|------|--------|
| Total Revenue | SUM(total_treatment_cost) |
| Insurance Coverage % | AVG(insurance_coverage_pct) |
| Out-of-Pocket Average | AVG(out_of_pocket) |
| UPI Payment Share | UPI count / total * 100 |

### Charts
- **Revenue by State** — Choropleth / bar chart
- **Insurance Coverage Analysis** — Stacked bar, covered vs out-of-pocket
- **Payment Mode Distribution** — Pie chart (UPI vs Cash)
- **Revenue Trend (Monthly)** — Line chart
- **Top Insurance Providers** — Bar chart
