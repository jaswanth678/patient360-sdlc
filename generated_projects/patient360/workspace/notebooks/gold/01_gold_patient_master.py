# Databricks notebook source
# MAGIC %md
# MAGIC # Patient360 | Gold Layer | Patient 360 Master
# MAGIC Unified patient view joining all Silver tables on patient_id

# COMMAND ----------
import logging
from pyspark.sql.functions import (
    col, count, countDistinct, sum, avg, max, when, current_timestamp
)
logger = logging.getLogger("gold_patient_master")

dbutils.widgets.text("catalog", "sdlc_catalog")
dbutils.widgets.text("silver_schema", "patient_360_silver")
dbutils.widgets.text("gold_schema", "patient_360_gold")
CATALOG = dbutils.widgets.get("catalog")
SILVER  = dbutils.widgets.get("silver_schema")
GOLD    = dbutils.widgets.get("gold_schema")

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{GOLD}")

def sv(t): return spark.read.table(f"{CATALOG}.{SILVER}.{t}")

# COMMAND ----------
# MAGIC %md ## Build Aggregates
pat  = sv("silver_patient")

appt_agg = sv("silver_appointment").groupBy("patient_id").agg(
    count("appointment_id").alias("total_appointments"),
    max("booking_date").alias("last_appointment_date")
)
diag_agg = sv("silver_diagnosis").groupBy("patient_id").agg(
    countDistinct("diagnosis_code").alias("unique_diagnoses"),
    count("record_id").alias("total_diagnoses")
)
med_agg = sv("silver_medication").filter(col("is_active_flag")==True).groupBy("patient_id").agg(
    count("medication_id").alias("active_medications")
)
lab_agg = sv("silver_lab").groupBy("patient_id").agg(
    count("serial_number").alias("total_lab_tests"),
    sum(when(col("lab_status") != "NORMAL", 1).otherwise(0)).alias("abnormal_lab_count")
)
bill_agg = sv("silver_billing").groupBy("patient_id").agg(
    sum("treatment_cost").alias("total_treatment_cost"),
    sum("insurance_coverage").alias("total_insurance_coverage")
)

# COMMAND ----------
# MAGIC %md ## Join & Write
master = (
    pat
    .join(appt_agg, "patient_id", "left")
    .join(diag_agg, "patient_id", "left")
    .join(med_agg,  "patient_id", "left")
    .join(lab_agg,  "patient_id", "left")
    .join(bill_agg, "patient_id", "left")
    .withColumn("gold_load_timestamp", current_timestamp())
)

master.write.format("delta").mode("overwrite").option("overwriteSchema","true") \
    .saveAsTable(f"{CATALOG}.{GOLD}.patient_360_master")

count = master.count()
logger.info(f"patient_360_master: {count} records")
dbutils.notebook.exit(f"SUCCESS: {count}")
