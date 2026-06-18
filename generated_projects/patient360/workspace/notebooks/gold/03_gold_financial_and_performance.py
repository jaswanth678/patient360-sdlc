# Databricks notebook source
# MAGIC %md
# MAGIC # Patient360 | Gold Layer | Financial Summary + Doctor Performance + Medication Adherence

# COMMAND ----------
import logging
from pyspark.sql.functions import (
    col, count, countDistinct, sum, avg, when, current_timestamp,
    round as spark_round, array_join, collect_list
)
logger = logging.getLogger("gold_financial_perf")

dbutils.widgets.text("catalog", "sdlc_catalog")
dbutils.widgets.text("silver_schema", "patient_360_silver")
dbutils.widgets.text("gold_schema", "patient_360_gold")
CATALOG = dbutils.widgets.get("catalog")
SILVER  = dbutils.widgets.get("silver_schema")
GOLD    = dbutils.widgets.get("gold_schema")

def sv(t): return spark.read.table(f"{CATALOG}.{SILVER}.{t}")

# COMMAND ----------
# MAGIC %md ## Patient Financial Summary
bill = sv("silver_billing")
pat  = sv("silver_patient").select("patient_id", "state")

fin = (
    bill.join(pat, "patient_id", "left")
    .groupBy("patient_id", "state")
    .agg(
        sum("treatment_cost").alias("total_treatment_cost"),
        sum("insurance_coverage").alias("total_insurance_coverage"),
        avg("treatment_cost").alias("avg_treatment_cost"),
        count("bill_id").alias("total_bills"),
        sum(when(col("payment_status") == "PAID", 1).otherwise(0)).alias("paid_bills"),
        sum(when(col("payment_mode") == "UPI",  1).otherwise(0)).alias("upi_payments"),
        sum(when(col("payment_mode") == "CASH", 1).otherwise(0)).alias("cash_payments")
    )
    .withColumn("insurance_coverage_pct",
        spark_round(col("total_insurance_coverage") / col("total_treatment_cost") * 100, 2))
    .withColumn("gold_load_timestamp", current_timestamp())
)
fin.write.format("delta").mode("overwrite").option("overwriteSchema","true") \
    .saveAsTable(f"{CATALOG}.{GOLD}.patient_financial_summary")
print(f"patient_financial_summary: {fin.count()}")

# COMMAND ----------
# MAGIC %md ## Doctor Performance Summary
appt = sv("silver_appointment")
diag = sv("silver_diagnosis")

appt_agg = appt.groupBy("doctore_id", "doctor_name", "department").agg(
    count("appointment_id").alias("total_appointments"),
    countDistinct("patient_id").alias("unique_patients")
)
diag_agg = diag.groupBy("doctor_id").agg(
    avg("doctor_charge_inr").alias("avg_charge_inr"),
    sum("doctor_charge_inr").alias("total_revenue_inr")
)
perf = (
    appt_agg
    .join(diag_agg, appt_agg.doctore_id == diag_agg.doctor_id, "left")
    .withColumn("gold_load_timestamp", current_timestamp())
)
perf.write.format("delta").mode("overwrite").option("overwriteSchema","true") \
    .saveAsTable(f"{CATALOG}.{GOLD}.doctor_performance_summary")
print(f"doctor_performance_summary: {perf.count()}")

# COMMAND ----------
# MAGIC %md ## Medication Adherence Summary
med = sv("silver_medication")
adherence = (
    med.groupBy("patient_id", "disease")
    .agg(
        count("medication_id").alias("total_medications"),
        sum(when(col("is_active_flag")==True, 1).otherwise(0)).alias("active_medications"),
        avg("medicine_price").alias("avg_medicine_price"),
        sum("medicine_price").alias("total_medicine_cost")
    )
    .withColumn("adherence_rate",
        spark_round(col("active_medications") / col("total_medications") * 100, 2))
    .withColumn("gold_load_timestamp", current_timestamp())
)
adherence.write.format("delta").mode("overwrite").option("overwriteSchema","true") \
    .saveAsTable(f"{CATALOG}.{GOLD}.medication_adherence_summary")
print(f"medication_adherence_summary: {adherence.count()}")

dbutils.notebook.exit("SUCCESS: patient_financial_summary, doctor_performance_summary, medication_adherence_summary")
