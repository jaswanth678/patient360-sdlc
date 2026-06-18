# Databricks notebook source
# MAGIC %md
# MAGIC # Patient360 | Silver Layer | Financial (Billing + Patient History)

# COMMAND ----------
import logging
from pyspark.sql.functions import (
    col, trim, upper, to_date, current_timestamp, datediff, when, lit, coalesce
)
logger = logging.getLogger("silver_financial")

dbutils.widgets.text("catalog", "sdlc_catalog")
dbutils.widgets.text("silver_schema", "patient_360_silver")
CATALOG = dbutils.widgets.get("catalog")
SILVER = dbutils.widgets.get("silver_schema")
BRONZE = "patient_360_bronze"

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{SILVER}")

# COMMAND ----------
# MAGIC %md ## Silver Billing
df_bill = (
    spark.read.table(f"{CATALOG}.{BRONZE}.bronze_billing")
    .withColumn("treatment_cost",      col("treatment_cost").cast("double"))
    .withColumn("insurance_coverage",  col("insurence_coverage").cast("double"))
    .withColumn("payment_mode",        upper(trim(col("payment_mode_upi_cash_"))))
    .withColumn("payment_date",        to_date(col("payment_date"), "yyyy-MM-dd"))
    .withColumn("out_of_pocket",
        col("treatment_cost") - coalesce(col("insurance_coverage"), lit(0.0)))
    .withColumn("silver_load_timestamp", current_timestamp())
)
df_bill = df_bill.filter(col("treatment_cost") >= 0)
df_bill.write.format("delta").mode("overwrite").option("overwriteSchema","true") \
    .saveAsTable(f"{CATALOG}.{SILVER}.silver_billing")
print(f"silver_billing: {df_bill.count()}")

# COMMAND ----------
# MAGIC %md ## Silver Patient History
df_hist = (
    spark.read.table(f"{CATALOG}.{BRONZE}.bronze_patient_history")
    .withColumn("current_visit_date", to_date(col("current_visit_date"), "yyyy-MM-dd"))
    .withColumn("prior_visit_date",   to_date(col("prior_visit_date"),   "yyyy-MM-dd"))
    .withColumn("days_between_visits",
        when(col("prior_visit_date").isNotNull(),
             datediff(col("current_visit_date"), col("prior_visit_date"))).otherwise(lit(None)))
    .withColumn("visit_type", col("visit_type"))
    .withColumn("silver_load_timestamp", current_timestamp())
)
df_hist.write.format("delta").mode("overwrite").option("overwriteSchema","true") \
    .saveAsTable(f"{CATALOG}.{SILVER}.silver_patient_history")
print(f"silver_patient_history: {df_hist.count()}")

dbutils.notebook.exit("SUCCESS: silver_billing, silver_patient_history")
