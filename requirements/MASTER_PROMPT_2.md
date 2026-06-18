# **DATABRICKS DASHBOARD, WORKSPACE DEPLOYMENT AND GITHUB PUBLISHING**

## **DASHBOARD GENERATION**

For every use case, automatically generate dashboard assets from Gold Layer outputs.

Analyze the business requirements and identify:

* KPIs  
* Dimensions  
* Measures  
* Filters  
* Drill-down paths  
* Executive summary metrics

Generate dashboard specifications for Databricks AI/BI Dashboards.

Required dashboard artifacts:

dashboard\_spec.md

dashboard\_layout.json

dashboard\_queries.sql

dashboard\_kpis.yml

dashboard\_filters.yml

dashboard\_documentation.md

---

## **DATABRICKS AI/BI DASHBOARD CREATION**

When Gold tables are generated:

Automatically create dashboard definitions based on the Gold Layer.

Generate:

* KPI Cards  
* Trend Charts  
* Bar Charts  
* Pie Charts  
* Matrix Reports  
* Drill-down Reports  
* Executive Summary Dashboard

Example Dashboard Sections:

### **Executive Dashboard**

* Total Records  
* Active Records  
* Revenue Metrics  
* Processing Metrics

### **Operational Dashboard**

* Data Volume Trends  
* Processing Trends  
* Source System Statistics

### **Analytical Dashboard**

* Business KPIs  
* Aggregated Insights  
* Trend Analysis

All dashboard SQL must reference Gold tables only.

---

## **DATABRICKS WORKSPACE DEPLOYMENT**

After generating all assets:

Deploy all generated artifacts into the Databricks Workspace.

Create:

workspace/  
├── notebooks/  
├── dashboards/  
├── sql/  
├── jobs/  
├── pipelines/  
├── tests/  
├── docs/

Generate deployment commands.

Required deployment targets:

### **Notebooks**

/workspace/\<project\_name\>/notebooks

### **Dashboards**

/workspace/\<project\_name\>/dashboards

### **SQL**

/workspace/\<project\_name\>/sql

### **Tests**

/workspace/\<project\_name\>/tests

### **Documentation**

/workspace/\<project\_name\>/docs

---

## **DATABRICKS NOTEBOOK GENERATION**

Convert all PySpark source files into Databricks notebooks.

Generate:

* Bronze notebooks  
* Silver notebooks  
* Gold notebooks  
* Utility notebooks  
* Validation notebooks

Each notebook must contain:

* Header  
* Parameters  
* Logging  
* Error Handling  
* Execution Summary

---

## **DATABRICKS SQL ASSETS**

Generate SQL files for:

* Gold Views  
* KPI Queries  
* Dashboard Queries  
* Validation Queries

Store in:

sql/

---

## **DATABRICKS JOB CREATION**

Generate Databricks Job definitions for:

* Bronze Pipeline  
* Silver Pipeline  
* Gold Pipeline  
* Dashboard Refresh  
* Validation Framework

Generate:

resources/jobs.yml

Job dependency graph

Workflow documentation

---

## **DATABRICKS DASHBOARD REFRESH**

Generate dashboard refresh workflows.

After Gold Layer completion:

Gold Layer  
↓  
Dashboard Refresh  
↓  
Validation  
↓  
Publish

---

## **GITHUB REPOSITORY MANAGEMENT**

Use existing repository if provided.

Otherwise generate repository structure.

Repository Structure:

project\_name/

requirements/

src/

resources/

terraform/

tests/

dashboards/

docs/

.github/

---

## **GITHUB FILE PUBLISHING**

After generating all assets:

Automatically prepare files for GitHub publishing.

Required files:

README.md

Architecture.md

PRD.md

Deployment\_Guide.md

Runbook.md

Source\_To\_Target\_Mapping.md

Dashboard\_Specification.md

---

## **GIT COMMIT STRATEGY**

Generate commits grouped by feature.

Example:

feat(bronze): create bronze ingestion framework

feat(silver): create silver transformation layer

feat(gold): create patient360 gold views

feat(dashboard): create dashboard assets

feat(terraform): create infrastructure deployment

test(patient360): add unit tests

docs(patient360): add project documentation

---

## **GITHUB ACTIONS**

Generate CI/CD workflows.

Required pipelines:

validate.yml

unit-test.yml

deploy-dev.yml

deploy-qa.yml

deploy-prod.yml

---

## **FINAL EXECUTION WORKFLOW**

When a PRD is provided:

1. Analyze Requirements  
2. Create Jira Backlog in DV  
3. Generate Databricks Project  
4. Generate Bronze Assets  
5. Generate Silver Assets  
6. Generate Gold Assets  
7. Generate Dashboard Assets  
8. Generate SQL Assets  
9. Generate Unit Tests  
10. Generate DAB Assets  
11. Generate Terraform  
12. Deploy Assets to Databricks Workspace  
13. Prepare GitHub Repository  
14. Commit Generated Files  
15. Push Generated Files to GitHub  
16. Generate Deployment Report

Do not stop after code generation.

Continue until all assets are generated, organized, ready for deployment, and ready for GitHub publishing.

