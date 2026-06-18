# Databricks notebook source
# Patient360 - Dashboard Dataset Refresh
# Computes KPI summary table used by all 4 dashboards

# COMMAND ----------
from pyspark.sql.functions import col, count, countDistinct, sum, avg, current_timestamp, lit

dbutils.widgets.text("catalog", "sdlc_catalog")
dbutils.widgets.text("gold_schema", "patient_360_gold")

CATALOG = dbutils.widgets.get("catalog")
GOLD = dbutils.widgets.get("gold_schema")

def gold(t): return spark.read.table(f"{CATALOG}.{GOLD}.{t}")

# COMMAND ----------
# KPI Summary Table
master = gold("patient_360_master")
financial = gold("patient_financial_summary")
clinical = gold("patient_clinical_summary")
risk = gold("patient_risk_summary")

kpi = master.agg(
    countDistinct("patient_id").alias("total_patients"),
    count(col("last_appointment_date")).alias("active_patients"),
    sum("total_appointments").alias("total_appointments"),
    sum("total_treatment_cost").alias("total_revenue"),
    avg("total_treatment_cost").alias("avg_treatment_cost")
).withColumn("kpi_refresh_timestamp", current_timestamp())

kpi.write.format("delta").mode("overwrite").saveAsTable(f"{CATALOG}.{GOLD}.kpi_summary")

# High risk patient count
risk_summary = (
    risk
    .groupBy("risk_category")
    .agg(count("patient_id").alias("patient_count"))
    .withColumn("kpi_refresh_timestamp", current_timestamp())
)
risk_summary.write.format("delta").mode("overwrite").saveAsTable(f"{CATALOG}.{GOLD}.risk_distribution")

print("Dashboard datasets refreshed.")
