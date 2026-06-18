# Patient360 Pipeline - Operations Runbook

## Daily Monitoring Checklist

1. Verify pipeline job completed: Databricks Workflows → patient360_pipeline → Latest run = "Succeeded"
2. Check record counts in Gold tables vs previous day (±20% alert threshold)
3. Review DQ rejection log: `SELECT * FROM sdlc_catalog.patient_360_silver.dq_rejection_log WHERE date(rejection_timestamp) = current_date()`
4. Confirm dashboard datasets refreshed: `SELECT kpi_refresh_timestamp FROM sdlc_catalog.patient_360_gold.kpi_summary`

## Common Failures & Recovery

### Pipeline Task Failed: ingest_source
**Cause:** Source files missing or volume permission issue  
**Fix:**
1. Check `/Volumes/sdlc_catalog/patient_360/source/` exists and files are present
2. Verify cluster has USE VOLUME privilege
3. Re-run task from Databricks Workflows UI (Repair Run → select failed task)

### Pipeline Task Failed: silver_transform
**Cause:** Schema mismatch or DQ rule blocking all records  
**Fix:**
1. Check Bronze table exists: `SHOW TABLES IN sdlc_catalog.patient_360_bronze`
2. Review Silver notebook output for error message
3. If schema evolved: Bronze uses `mergeSchema=true`; re-run bronze_load first
4. If DQ rejected all records: check dq_rejection_log for the failing rule

### Pipeline Task Failed: gold_build
**Cause:** Silver table missing or join key mismatch  
**Fix:**
1. Verify Silver tables exist: `SHOW TABLES IN sdlc_catalog.patient_360_silver`
2. Check patient_id consistency across silver tables
3. Re-run from gold_build task only (Repair Run)

## Rollback Procedure

### DAB Rollback
```bash
# List previous bundle deployments
databricks bundle deployment list --target dev

# The previous job configuration is in Git history
git log --oneline resources/jobs.yml
git checkout <previous-commit> -- resources/jobs.yml
databricks bundle deploy --target dev
```

### Data Rollback (Delta Time Travel)
```sql
-- View history
DESCRIBE HISTORY sdlc_catalog.patient_360_gold.patient_360_master;

-- Restore to previous version
RESTORE TABLE sdlc_catalog.patient_360_gold.patient_360_master TO VERSION AS OF <version_number>;
```

## DQ Monitoring Query
```sql
SELECT
    rule_name,
    source_table,
    count(*) as rejection_count,
    date(rejection_timestamp) as rejection_date
FROM sdlc_catalog.patient_360_silver.dq_rejection_log
WHERE date(rejection_timestamp) >= current_date() - 7
GROUP BY 1, 2, 4
ORDER BY 4 DESC, 3 DESC;
```

## Pipeline SLA
- Start time: 02:00 IST daily
- Expected completion: within 2 hours (by 04:00 IST)
- Alert: If not completed by 05:00 IST, investigate immediately
