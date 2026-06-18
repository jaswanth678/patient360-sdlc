# Patient360 Dashboard Documentation

## Dashboard Inventory

| Dashboard | ID | Purpose | Audience | Refresh |
|---|---|---|---|---|
| Executive Dashboard | executive_dashboard | KPIs, revenue, trends | C-suite, management | Daily 04:00 IST |
| Clinical Dashboard | clinical_dashboard | Disease, labs, risk | Clinicians, medical staff | Daily 04:00 IST |
| Operational Dashboard | operational_dashboard | Doctor & dept performance | Admins, ops | Daily 04:00 IST |
| Financial Dashboard | financial_dashboard | Revenue, billing, insurance | Finance team | Daily 04:00 IST |

## Data Sources (Gold Layer Only)

All dashboards query `sdlc_catalog.patient_360_gold.*` exclusively.

| Table | Used By |
|---|---|
| patient_360_master | Executive, Clinical |
| patient_clinical_summary | Clinical |
| patient_financial_summary | Executive, Financial |
| doctor_performance_summary | Operational |
| medication_adherence_summary | Clinical |
| patient_risk_summary | Clinical |
| kpi_summary | Executive |
| risk_distribution | Clinical |

## Widget Types Used

| Type | Description |
|---|---|
| counter | Single KPI metric card |
| bar | Categorical comparison |
| line | Time-series trend |
| pie | Proportional distribution |
| table | Detailed record view |
| scatter | Bivariate correlation |

## Filters

Global filters applied across all dashboards:
- **State** — Filter patients by geographic state
- **Date Range** — Constrain appointment date window (default: last 90 days)
- **Risk Category** — Clinical dashboard filter

Dashboard-specific filters:
- Clinical: Disease, Lab Status
- Operational: Department, Doctor
- Financial: Payment Mode, Insurance Provider

## Deployment

```bash
# Deploy dashboard via Databricks CLI
databricks dashboards create --json dashboards/dashboard_layout.json

# Or via DAB (add to resources/dashboards.yml)
databricks bundle deploy --target dev
```

## Access Control

| Role | Access |
|---|---|
| data_analysts | View all 4 dashboards |
| clinical_staff | Clinical dashboard only |
| finance_team | Financial dashboard only |
| admins | All dashboards + edit |

## Refresh Schedule

Dashboards are refreshed automatically after the `dashboard_refresh` task completes in the pipeline job (daily ~04:00 IST). Manual refresh: open dashboard → click Refresh.
