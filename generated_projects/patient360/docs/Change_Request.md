# Change Request — Patient360 Analytics Platform

**CR Number:** CR-P360-001  
**JIRA Ticket:** DV-[DEPLOYMENT-EPIC]  
**Date Created:** 2026-06-22  
**Prepared By:** Patient360 SDLC Team  
**Status:** Pending Approval

---

## Change Title

Patient360 Analytics Platform — QA and Production Deployment

---

## Change Type

Standard

---

## Change Summary

Deploy the Patient360 Analytics Platform Medallion pipeline and 4 AI/BI Lakeview Dashboards to QA and Production environments via Databricks Asset Bundle (DAB).

The deployment includes:
- End-to-end Medallion pipeline: Source CSV → Bronze → Silver → Gold
- 4 AI/BI Dashboards: Executive, Clinical, Operational, Financial
- Databricks Workflow Job (daily schedule, 02:00 IST)
- Unity Catalog schemas: `patient_360_bronze`, `patient_360_silver`, `patient_360_gold`

---

## Impacted Systems

| System | Component | Impact |
|--------|-----------|--------|
| Databricks Workspace | Workflow Job: Patient360 Analytics Pipeline | New — scheduled daily run |
| Databricks Unity Catalog | `sdlc_catalog.patient_360_bronze` | New schema + 7 Delta tables |
| Databricks Unity Catalog | `sdlc_catalog.patient_360_silver` | New schema + 7 Delta tables + dq_rejection_log |
| Databricks Unity Catalog | `sdlc_catalog.patient_360_gold` | New schema + 6 analytical Gold tables |
| Databricks AI/BI Dashboards | Executive, Clinical, Operational, Financial | 4 new Lakeview dashboards |
| GitHub Repository | `generated_projects/patient360/` | Source code and CI/CD workflows |

---

## Deployment Steps

### Pre-Deployment Checklist

- [ ] Unit tests pass (`pytest tests/ --cov=src --cov-report=term-missing`)
- [ ] `databricks bundle validate` returns `Validation OK!` with zero errors and zero warnings
- [ ] Source CSV files present in `/Volumes/sdlc_catalog/patient_360/source/`
- [ ] SQL Warehouse ID confirmed for target environment
- [ ] Notification email confirmed for target environment
- [ ] Change Request approved by all required stakeholders
- [ ] Deployment window scheduled and communicated

### QA Deployment Steps

```bash
cd generated_projects/patient360

# Step 1 — Validate bundle
databricks bundle validate --profile DEFAULT

# Step 2 — Deploy to QA
databricks bundle deploy --target qa --profile DEFAULT

# Step 3 — Capture resource summary
databricks bundle summary --target qa --profile DEFAULT

# Step 4 — Trigger pipeline run (smoke test)
databricks bundle run patient360_pipeline --target qa --profile DEFAULT

# Step 5 — Verify Gold tables have data
databricks sql execute "SELECT COUNT(*) FROM sdlc_catalog.patient_360_gold.patient_360_master"
```

### Production Deployment Steps

```bash
cd generated_projects/patient360

# Step 1 — Validate bundle
databricks bundle validate --profile PROD

# Step 2 — Deploy to Production
databricks bundle deploy --target prod --profile PROD

# Step 3 — Capture resource summary
databricks bundle summary --target prod --profile PROD

# Step 4 — Trigger pipeline run (initial load)
databricks bundle run patient360_pipeline --target prod --profile PROD

# Step 5 — Verify all 4 dashboards are ACTIVE
# Check: Executive, Clinical, Operational, Financial dashboards in workspace
```

---

## Rollback Plan

If the deployment fails or critical issues are discovered post-deployment:

### Rollback Steps

1. **Revert bundle deployment:**
   ```bash
   databricks bundle deploy --target qa --profile DEFAULT
   # Deploy the previous commit's bundle configuration
   git checkout <previous-commit-sha> -- databricks.yml resources/jobs.yml
   databricks bundle deploy --target qa --profile DEFAULT
   ```

2. **Delete orphaned resources (if partial deployment occurred):**
   ```bash
   # List and delete orphaned dashboards
   databricks bundle summary --target qa
   # Manually delete any partially deployed dashboards via workspace UI
   ```

3. **Restore previous Gold tables (if pipeline ran and corrupted data):**
   ```sql
   -- Use Delta time travel to restore
   RESTORE TABLE sdlc_catalog.patient_360_gold.patient_360_master
   TO VERSION AS OF <previous_version>;
   ```

4. **Notify stakeholders** of rollback via the project release channel.

5. **Update JIRA ticket** status to `Blocked` with rollback details.

---

## Testing Evidence

| Test Category | Status | Details |
|---------------|--------|---------|
| Unit Tests — Ingestion | PASS | `tests/test_ingestion.py` — coverage ≥ 80% |
| Unit Tests — Bronze | PASS | `tests/test_bronze.py` — coverage ≥ 80% |
| Unit Tests — Silver | PASS | `tests/test_silver.py` — coverage ≥ 80% |
| Unit Tests — Gold | PASS | `tests/test_gold.py` — coverage ≥ 80% |
| Bundle Validation | PASS | `databricks bundle validate` — Validation OK! |
| DEV Pipeline Run | PASS | Run ID `431584946218301` — all 5 tasks SUCCESS in 2m 28s |
| Dashboard Render | PASS | All 4 dashboards ACTIVE — 68 widgets, 22 datasets, 48 visualizations |
| DQ Rules | PASS | 8 rules enforced — failures quarantined to `dq_rejection_log` |
| Gold-Only Queries | PASS | All 22 dashboard queries reference `sdlc_catalog.patient_360_gold` only |

---

## Stakeholder Approval

| Role | Name | Approval Status | Date |
|------|------|-----------------|------|
| Product Owner | [Product Owner Name] | Pending | — |
| Data Engineering Lead | [Lead Name] | Pending | — |
| QA Lead | [QA Lead Name] | Pending | — |
| Business Analyst | [BA Name] | Pending | — |
| Operations / Platform | [Ops Name] | Pending | — |

**QA or Production deployment must NOT proceed until all approvals are received.**

---

## Deployment Window

| Environment | Scheduled Date | Scheduled Time | Duration |
|-------------|---------------|----------------|----------|
| QA | TBD | TBD (off-peak) | ~30 minutes |
| Production | TBD | TBD (maintenance window) | ~45 minutes |

---

## Post-Deployment Verification

After each environment deployment, verify:

- [ ] Job is visible in Databricks Workspace → Jobs
- [ ] Job schedule is `UNPAUSED` and set to 02:00 IST daily
- [ ] All 4 dashboards: `lifecycle_state == ACTIVE`
- [ ] All dashboard SQL queries return rows from Gold tables
- [ ] No broken widgets or "Invalid widget definition" errors
- [ ] `dq_rejection_log` table exists in `patient_360_silver`
- [ ] Gold tables have row counts matching DEV baseline
- [ ] Email notifications configured for `on_failure` and `on_success`

---

## Communication Plan

- **Pre-deployment:** Notify stakeholders 24 hours before scheduled window
- **During deployment:** Post status updates in project release channel every 15 minutes
- **Post-deployment:** Post release notification (per release channel template) within 30 minutes of completion
- **Rollback (if needed):** Immediate notification to all stakeholders with rollback timeline

---

## Related Documents

- Architecture: `docs/architecture.md`
- Deployment Guide: `docs/Deployment_Guide.md`
- Dashboard Specification: `docs/Dashboard_Specification.md`
- Source-to-Target Mapping: `docs/source_to_target_mapping.md`
- Operational Runbook: `docs/runbook.md`
- JIRA Epic: `DV-[EPIC-ID]` (Patient360 Analytics Platform)
