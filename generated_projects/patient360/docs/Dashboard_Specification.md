# Patient360 — Dashboard Specification

## Overview

Four Databricks AI/BI dashboards powered exclusively by Gold layer tables. Refresh daily after the pipeline completes (~04:00 IST).

---

## Dashboard 1: Executive Dashboard

**File:** `dashboards/dashboard_layout.json` → id: `executive_dashboard`  
**Audience:** C-suite, management  
**Data:** `patient_360_master`, `patient_financial_summary`, `kpi_summary`

### KPI Cards (Row 1)
| Widget | Metric | Query |
|--------|--------|-------|
| Total Patients | COUNT(DISTINCT patient_id) | EX-01 |
| Active Patients | patients with appt in 90 days | EX-01 |
| Total Revenue (INR) | SUM(total_treatment_cost) | EX-01 |
| Total Appointments | SUM(total_appointments) | EX-01 |
| Avg Treatment Cost | AVG(total_treatment_cost) | EX-01 |

### Charts (Row 2)
| Widget | Type | Axes | Query |
|--------|------|------|-------|
| Revenue by State | Horizontal bar | state / revenue | EX-02 |
| Monthly Appointment Trend | Line | month / count | EX-03 |

### Charts (Row 3)
| Widget | Type | Axes | Query |
|--------|------|------|-------|
| Age Distribution | Bar | age_group / count | EX-04 |
| Active vs Total | Donut | status / count | EX-01 |

---

## Dashboard 2: Clinical Dashboard

**File:** `dashboards/dashboard_layout.json` → id: `clinical_dashboard`  
**Audience:** Physicians, nurses, clinical staff

### KPI Cards
| Widget | Metric | Query |
|--------|--------|-------|
| High Risk Patients | COUNT where risk_category='HIGH_RISK' | CL-02 |
| Lab Abnormality Rate | % abnormal results | CL-03 |
| Medication Adherence | AVG(adherence_rate) | CL-04 |
| Unique Diseases | COUNT(DISTINCT disease) | CL-01 |

### Charts
| Widget | Type | Query |
|--------|------|-------|
| Disease Distribution | Pie | CL-01 |
| Risk Category Breakdown | Bar | CL-02 |
| Medication Adherence by Disease | Bar | CL-04 |
| High Risk Patient Table | Table | CL-05 |

---

## Dashboard 3: Operational Dashboard

**File:** `dashboards/dashboard_layout.json` → id: `operational_dashboard`  
**Audience:** Administrators, operations managers

### KPI Cards
| Widget | Metric |
|--------|--------|
| Total Doctors | COUNT(DISTINCT doctor_id) |
| Avg Patients/Doctor | AVG(unique_patients) |
| Total Appointments | SUM |
| Active Departments | COUNT(DISTINCT dept) |

### Charts
| Widget | Type | Query |
|--------|------|-------|
| Doctor Workload | Bar | OP-01 |
| Department Workload | Horizontal bar | OP-02 |
| Visit Frequency | Bar | OP-03 |

---

## Dashboard 4: Financial Dashboard

**File:** `dashboards/dashboard_layout.json` → id: `financial_dashboard`  
**Audience:** Finance team, billing department

### KPI Cards
| Widget | Metric |
|--------|--------|
| Total Revenue (INR) | SUM(treatment_cost) |
| Avg Insurance Coverage % | AVG(coverage_pct) |
| Avg Out-of-Pocket | AVG(out_of_pocket) |
| UPI Payment Share % | UPI/total * 100 |

### Charts
| Widget | Type | Query |
|--------|------|-------|
| Monthly Revenue Trend | Line | FI-03 |
| Payment Mode Distribution | Pie | FI-02 |
| Billing Status | Bar | FI-04 |
| Insurance Coverage Analysis | Stacked bar | FI-01 |

---

## Global Filters (All Dashboards)

| Filter | Type | Default |
|--------|------|---------|
| State | Multi-select | ALL |
| Date Range | Date range | Last 90 days |

## Dashboard Deployment Commands

```bash
# Create dashboard via Databricks CLI
databricks dashboards create --json dashboards/dashboard_layout.json

# List existing dashboards
databricks dashboards list

# Update dashboard
databricks dashboards update <dashboard_id> --json dashboards/dashboard_layout.json
```

## Query File Reference

All dashboard queries are in `workspace/sql/dashboard_queries.sql` with IDs matching the layout JSON (EX-01, CL-01, OP-01, FI-01, etc.).
