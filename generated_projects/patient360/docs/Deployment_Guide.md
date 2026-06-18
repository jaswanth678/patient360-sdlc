# Patient360 — Deployment Guide

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.11+ | Runtime |
| Databricks CLI | 0.220+ | Bundle deploy |
| Terraform | 1.5+ | IaC |
| Git | 2.x | Source control |

## Step 1: Clone Repository

```bash
git clone https://github.com/<org>/patient360.git
cd patient360
```

## Step 2: Authenticate with Databricks

```bash
databricks configure --host https://<workspace>.azuredatabricks.net --token
# Enter your PAT when prompted
```

Verify:
```bash
databricks clusters list
```

## Step 3: Validate the DAB Bundle

```bash
databricks bundle validate
```

Expected output: `Bundle configuration is valid.`

## Step 4: Deploy to DEV

```bash
databricks bundle deploy --target dev
```

This creates:
- Job: `Patient360 Analytics Pipeline - dev`
- All notebooks uploaded to `/Workspace/patient360/`

## Step 5: Run Tests

```bash
pip install pytest pyspark==3.5.0 pytest-cov
pytest tests/ -v --cov=src --cov-report=term-missing
```

Expected: All tests pass, coverage ≥ 80%

## Step 6: Trigger the Pipeline

```bash
databricks bundle run patient360_pipeline --target dev
```

Or from Databricks UI: Workflows → `Patient360 Analytics Pipeline - dev` → Run now

## Step 7: Validate Pipeline Output

```bash
# Run validation notebook via CLI
databricks runs submit --json '{
  "run_name": "validate_dev",
  "existing_cluster_id": "<cluster_id>",
  "notebook_task": {
    "notebook_path": "/Workspace/patient360/workspace/notebooks/validation/validate_pipeline",
    "base_parameters": {"catalog": "sdlc_catalog"}
  }
}'
```

Or run the SQL validation:
```sql
-- In Databricks SQL
SELECT * FROM sdlc_catalog.patient_360_gold.kpi_summary;
```

## Step 8: Deploy SQL Views

```bash
databricks workspace import workspace/sql/gold_views.sql \
  /Workspace/patient360/sql/gold_views.sql --overwrite
```

## Terraform Deployment (Infrastructure)

```bash
cd terraform
terraform init
terraform plan -var="databricks_host=https://<workspace>.azuredatabricks.net" \
               -var="databricks_token=<token>" \
               -var="cluster_id=<id>"
terraform apply
```

## Environment Variables (GitHub Secrets)

| Secret | Used By |
|--------|---------|
| DATABRICKS_HOST_DEV | deploy-dev.yml |
| DATABRICKS_TOKEN_DEV | deploy-dev.yml |
| DATABRICKS_HOST_QA | deploy-qa.yml |
| DATABRICKS_TOKEN_QA | deploy-qa.yml |
| DATABRICKS_HOST_PROD | deploy-prod.yml |
| DATABRICKS_TOKEN_PROD | deploy-prod.yml |
| CLUSTER_ID_DEV | deploy-dev.yml |

## CI/CD Pipeline Flow

```
Push to develop → validate.yml → unit-test.yml → deploy-dev.yml → smoke test
Push to main    → validate.yml → unit-test.yml → deploy-dev.yml → deploy-qa.yml
Manual trigger  → deploy-prod.yml (requires "DEPLOY" confirmation)
```

## Rollback

```bash
# Delta time travel rollback
databricks sql execute "
  RESTORE TABLE sdlc_catalog.patient_360_gold.patient_360_master
  TO VERSION AS OF <version>
"

# Bundle rollback
git checkout <previous-commit>
databricks bundle deploy --target dev
```
