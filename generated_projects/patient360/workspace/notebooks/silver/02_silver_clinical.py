# Databricks notebook source
# MAGIC %md
# MAGIC # Patient360 | Silver Layer | Clinical (Appointment + Diagnosis + Medication + Lab)

# COMMAND ----------
import logging
from pyspark.sql.functions import (
    col, trim, upper, lower, to_date, current_timestamp, when, current_date, row_number, desc
)
from pyspark.sql.window import Window
logger = logging.getLogger("silver_clinical")

dbutils.widgets.text("catalog", "sdlc_catalog")
dbutils.widgets.text("silver_schema", "patient_360_silver")
CATALOG = dbutils.widgets.get("catalog")
SILVER = dbutils.widgets.get("silver_schema")
BRONZE = "patient_360_bronze"

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{SILVER}")

# COMMAND ----------
# MAGIC %md ## Silver Appointment
w = Window.partitionBy("appointment_id").orderBy(desc("ingestion_timestamp"))
df_appt = (
    spark.read.table(f"{CATALOG}.{BRONZE}.bronze_appointment")
    .filter(col("appointment_id").isNotNull())
    .withColumn("rn", row_number().over(w)).filter(col("rn") == 1).drop("rn")
    .withColumn("booking_date", to_date(col("booking_date"), "yyyy-MM-dd"))
    .withColumn("status_flag", when(col("status") == "y", True).otherwise(False))
    .withColumn("department", upper(trim(col("department"))))
    .withColumn("visit_type", lower(trim(col("visit_type"))))
    .withColumn("silver_load_timestamp", current_timestamp())
)
df_appt = df_appt.filter(col("booking_date") <= current_date())
df_appt.write.format("delta").mode("overwrite").option("overwriteSchema","true") \
    .saveAsTable(f"{CATALOG}.{SILVER}.silver_appointment")
print(f"silver_appointment: {df_appt.count()}")

# COMMAND ----------
# MAGIC %md ## Silver Diagnosis
df_diag = (
    spark.read.table(f"{CATALOG}.{BRONZE}.bronze_diagnosis")
    .filter(col("diagnosis_code").isNotNull())
    .withColumn("checkup_date", to_date(col("checkup_date"), "yyyy-MM-dd"))
    .withColumn("diagnosis_code", upper(trim(col("diagnosis_code"))))
    .withColumn("disease_name", upper(trim(col("disease_name"))))
    .withColumn("doctor_charge_inr", col("doctor_charge_inr").cast("double"))
    .withColumn("silver_load_timestamp", current_timestamp())
)
df_diag.write.format("delta").mode("overwrite").option("overwriteSchema","true") \
    .saveAsTable(f"{CATALOG}.{SILVER}.silver_diagnosis")
print(f"silver_diagnosis: {df_diag.count()}")

# COMMAND ----------
# MAGIC %md ## Silver Medication
df_med = (
    spark.read.table(f"{CATALOG}.{BRONZE}.bronze_medication")
    .withColumn("start_date", to_date(col("start_date"), "yyyy-MM-dd"))
    .withColumn("end_date",   to_date(col("end_date"),   "yyyy-MM-dd"))
    .withColumn("is_active_flag",
        when((col("end_date").isNull()) | (col("end_date") >= current_date()), True).otherwise(False))
    .withColumn("route", lower(trim(col("route"))))
    .withColumn("medicine_price", col("medicine_price").cast("double"))
    .withColumn("silver_load_timestamp", current_timestamp())
)
df_med = df_med.filter(col("medicine_price") >= 0)
df_med.write.format("delta").mode("overwrite").option("overwriteSchema","true") \
    .saveAsTable(f"{CATALOG}.{SILVER}.silver_medication")
print(f"silver_medication: {df_med.count()}")

# COMMAND ----------
# MAGIC %md ## Silver Lab Reports
df_lab = (
    spark.read.table(f"{CATALOG}.{BRONZE}.bronze_lab")
    .withColumn("booking_date",       to_date(col("booking_date"),       "yyyy-MM-dd"))
    .withColumn("collect_report_date",to_date(col("collect_report_date"),"yyyy-MM-dd"))
    .withColumn("test_result_num",    col("test_result").cast("double"))
    .withColumn("normal_range_min",   col("normal_range_min").cast("double"))
    .withColumn("normal_range_max",   col("normal_range_max").cast("double"))
    .withColumn("lab_status",
        when(col("test_result_num") < col("normal_range_min"), "BELOW_NORMAL")
        .when(col("test_result_num") > col("normal_range_max"), "ABOVE_NORMAL")
        .otherwise("NORMAL"))
    .withColumn("cost", col("cost").cast("double"))
    .withColumn("silver_load_timestamp", current_timestamp())
)
df_lab.write.format("delta").mode("overwrite").option("overwriteSchema","true") \
    .saveAsTable(f"{CATALOG}.{SILVER}.silver_lab")
print(f"silver_lab: {df_lab.count()}")

dbutils.notebook.exit("SUCCESS: silver_appointment, silver_diagnosis, silver_medication, silver_lab")
