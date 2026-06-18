# Databricks notebook source
# MAGIC %md
# MAGIC # Patient360 | Validation | End-to-End Pipeline Validation
# MAGIC Checks record counts, schema presence, and DQ metrics after each pipeline run.

# COMMAND ----------
import logging
logger = logging.getLogger("validate_pipeline")

dbutils.widgets.text("catalog", "sdlc_catalog")
CATALOG = dbutils.widgets.get("catalog")

BRONZE = f"{CATALOG}.patient_360_bronze"
SILVER = f"{CATALOG}.patient_360_silver"
GOLD   = f"{CATALOG}.patient_360_gold"

results = {}
failures = []

# COMMAND ----------
# MAGIC %md ## Bronze Validation
BRONZE_TABLES = [
    "bronze_patient", "bronze_appointment", "bronze_diagnosis",
    "bronze_medication", "bronze_lab", "bronze_billing", "bronze_patient_history"
]
for t in BRONZE_TABLES:
    try:
        cnt = spark.read.table(f"{BRONZE}.{t}").count()
        results[f"bronze.{t}"] = cnt
        if cnt == 0:
            failures.append(f"WARN: {BRONZE}.{t} has 0 records")
        logger.info(f"{BRONZE}.{t}: {cnt} records")
    except Exception as e:
        failures.append(f"ERROR: {BRONZE}.{t} - {e}")

# COMMAND ----------
# MAGIC %md ## Silver Validation
SILVER_TABLES = [
    "silver_patient", "silver_appointment", "silver_diagnosis",
    "silver_medication", "silver_lab", "silver_billing", "silver_patient_history"
]
for t in SILVER_TABLES:
    try:
        cnt = spark.read.table(f"{SILVER}.{t}").count()
        results[f"silver.{t}"] = cnt
        if cnt == 0:
            failures.append(f"WARN: {SILVER}.{t} has 0 records")
    except Exception as e:
        failures.append(f"ERROR: {SILVER}.{t} - {e}")

# COMMAND ----------
# MAGIC %md ## Gold Validation
GOLD_TABLES = [
    "patient_360_master", "patient_clinical_summary", "patient_financial_summary",
    "doctor_performance_summary", "medication_adherence_summary", "patient_risk_summary",
    "kpi_summary"
]
for t in GOLD_TABLES:
    try:
        cnt = spark.read.table(f"{GOLD}.{t}").count()
        results[f"gold.{t}"] = cnt
        if cnt == 0:
            failures.append(f"WARN: {GOLD}.{t} has 0 records")
    except Exception as e:
        failures.append(f"ERROR: {GOLD}.{t} - {e}")

# COMMAND ----------
# MAGIC %md ## DQ Rejection Log Check
try:
    dq_cnt = spark.read.table(f"{SILVER}.dq_rejection_log").count()
    results["silver.dq_rejection_log"] = dq_cnt
    logger.info(f"DQ rejections today: {dq_cnt}")
    if dq_cnt > 1000:
        failures.append(f"WARN: High DQ rejection count: {dq_cnt}")
except Exception:
    results["silver.dq_rejection_log"] = 0

# COMMAND ----------
# MAGIC %md ## Validation Report
print("\n===== PIPELINE VALIDATION REPORT =====")
for k, v in results.items():
    print(f"  {k}: {v} records")

if failures:
    print("\n===== WARNINGS / FAILURES =====")
    for f in failures:
        print(f"  {f}")
    dbutils.notebook.exit(f"COMPLETED WITH WARNINGS: {len(failures)} issues")
else:
    print("\nAll validations PASSED.")
    dbutils.notebook.exit("SUCCESS: All tables validated")
