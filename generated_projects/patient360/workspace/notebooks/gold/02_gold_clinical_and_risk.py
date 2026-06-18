# Databricks notebook source
# MAGIC %md
# MAGIC # Patient360 | Gold Layer | Clinical Summary + Risk Summary

# COMMAND ----------
import logging
from pyspark.sql.functions import (
    col, count, sum, when, avg, array_join, collect_list,
    current_timestamp, round as spark_round
)
logger = logging.getLogger("gold_clinical_risk")

dbutils.widgets.text("catalog", "sdlc_catalog")
dbutils.widgets.text("silver_schema", "patient_360_silver")
dbutils.widgets.text("gold_schema", "patient_360_gold")
CATALOG = dbutils.widgets.get("catalog")
SILVER  = dbutils.widgets.get("silver_schema")
GOLD    = dbutils.widgets.get("gold_schema")

def sv(t): return spark.read.table(f"{CATALOG}.{SILVER}.{t}")
def gv(t): return spark.read.table(f"{CATALOG}.{GOLD}.{t}")

# COMMAND ----------
# MAGIC %md ## Patient Clinical Summary
diag_agg = sv("silver_diagnosis").groupBy("patient_id").agg(
    count("record_id").alias("total_diagnoses"),
    countDistinct("disease_name").alias("unique_diseases"),
    max("checkup_date").alias("last_checkup_date")
) if False else sv("silver_diagnosis").groupBy("patient_id").agg(
    count("record_id").alias("total_diagnoses")
)
from pyspark.sql.functions import countDistinct, max
diag_agg = sv("silver_diagnosis").groupBy("patient_id").agg(
    count("record_id").alias("total_diagnoses"),
    countDistinct("disease_name").alias("unique_diseases"),
    max("checkup_date").alias("last_checkup_date")
)
lab_agg = sv("silver_lab").groupBy("patient_id").agg(
    count("serial_number").alias("total_lab_tests"),
    sum(when(col("lab_status") == "ABOVE_NORMAL", 1).otherwise(0)).alias("above_normal_count"),
    sum(when(col("lab_status") == "BELOW_NORMAL", 1).otherwise(0)).alias("below_normal_count")
)
med_agg = sv("silver_medication").filter(col("is_active_flag")==True).groupBy("patient_id").agg(
    count("medication_id").alias("active_med_count"),
    array_join(collect_list("medication_name"), ", ").alias("active_medications")
)

clinical = (
    diag_agg
    .join(lab_agg, "patient_id", "left")
    .join(med_agg, "patient_id", "left")
    .withColumn("lab_risk_flag",
        when(col("above_normal_count") + col("below_normal_count") > 2, True).otherwise(False))
    .withColumn("gold_load_timestamp", current_timestamp())
)
clinical.write.format("delta").mode("overwrite").option("overwriteSchema","true") \
    .saveAsTable(f"{CATALOG}.{GOLD}.patient_clinical_summary")
print(f"patient_clinical_summary: {clinical.count()}")

# COMMAND ----------
# MAGIC %md ## Patient Risk Summary
master = gv("patient_360_master")
pat = sv("silver_patient").select("patient_id", "age")

risk = (
    master.join(pat, "patient_id", "left")
    .withColumn("age_risk",
        when(col("age") >= 65, "HIGH").when(col("age") >= 40, "MEDIUM").otherwise("LOW"))
    .withColumn("lab_risk",
        when(col("abnormal_lab_count") > 3, "HIGH")
        .when(col("abnormal_lab_count") > 1, "MEDIUM").otherwise("LOW"))
    .withColumn("financial_risk",
        when(col("total_treatment_cost") - col("total_insurance_coverage") > 100000, "HIGH").otherwise("LOW"))
    .withColumn("overall_risk_score",
        when(col("age_risk") == "HIGH", 3).when(col("age_risk") == "MEDIUM", 2).otherwise(1)
        + when(col("lab_risk") == "HIGH", 3).when(col("lab_risk") == "MEDIUM", 2).otherwise(1)
        + when(col("financial_risk") == "HIGH", 2).otherwise(1))
    .withColumn("risk_category",
        when(col("overall_risk_score") >= 7, "HIGH_RISK")
        .when(col("overall_risk_score") >= 4, "MEDIUM_RISK")
        .otherwise("LOW_RISK"))
    .withColumn("gold_load_timestamp", current_timestamp())
)
risk.write.format("delta").mode("overwrite").option("overwriteSchema","true") \
    .saveAsTable(f"{CATALOG}.{GOLD}.patient_risk_summary")
print(f"patient_risk_summary: {risk.count()}")

dbutils.notebook.exit("SUCCESS: patient_clinical_summary, patient_risk_summary")
