# Databricks notebook source
# Patient360 - Silver Layer Orchestrator
# Applies dedup, null handling, standardization, DQ for all 7 entities

# COMMAND ----------
from pyspark.sql.functions import (
    col, trim, lower, upper, to_date, to_timestamp,
    current_timestamp, lit, when, coalesce, datediff,
    current_date, regexp_replace, md5, concat_ws,
    row_number, desc, expr
)
from pyspark.sql.window import Window
from dq_rules_engine import apply_dq_rules

def flex_date(col_name: str):
    """Parse date columns that may be M/d/yyyy or yyyy-MM-dd."""
    return expr(
        f"coalesce(try_to_date({col_name}, 'M/d/yyyy'), try_to_date({col_name}, 'yyyy-MM-dd'))"
    )

dbutils.widgets.text("catalog", "sdlc_catalog")
dbutils.widgets.text("silver_schema", "patient_360_silver")

CATALOG = dbutils.widgets.get("catalog")
SILVER_SCHEMA = dbutils.widgets.get("silver_schema")
BRONZE_SCHEMA = "patient_360_bronze"

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{SILVER_SCHEMA}")

# COMMAND ----------
# --- Patient ---
def transform_patient():
    df = spark.read.table(f"{CATALOG}.{BRONZE_SCHEMA}.bronze_patient")
    w = Window.partitionBy("patient_id").orderBy(desc("ingestion_timestamp"))
    df = (
        df
        .filter(col("patient_id").isNotNull())
        .withColumn("rn", row_number().over(w))
        .filter(col("rn") == 1).drop("rn")
        .withColumn("patient_name", upper(trim(col("patient_name"))))
        .withColumn("email", lower(trim(col("email"))))
        .withColumn("sex", upper(trim(col("sex"))))
        .withColumn("state", upper(trim(col("state"))))
        .withColumn("dob", flex_date("dob"))
        .withColumn("age", col("age").cast("int"))
        .withColumn("contact", regexp_replace(col("contact"), "[^0-9]", ""))
        .withColumn("silver_load_timestamp", current_timestamp())
    )
    df = apply_dq_rules(spark, df, "silver_patient", CATALOG, SILVER_SCHEMA)
    df.write.format("delta").mode("overwrite").option("overwriteSchema", "true") \
        .saveAsTable(f"{CATALOG}.{SILVER_SCHEMA}.silver_patient")
    print(f"silver_patient: {df.count()} records")

# COMMAND ----------
# --- Appointment ---
def transform_appointment():
    df = spark.read.table(f"{CATALOG}.{BRONZE_SCHEMA}.bronze_appointment")
    w = Window.partitionBy("appointment_id").orderBy(desc("ingestion_timestamp"))
    df = (
        df
        .filter(col("appointment_id").isNotNull())
        .withColumn("rn", row_number().over(w)).filter(col("rn") == 1).drop("rn")
        .withColumn("booking_date", flex_date("booking_date"))
        .withColumn("status_flag", when(col("status_y_n") == "y", True).otherwise(False))
        .withColumn("department", upper(trim(col("department"))))
        .withColumn("visit_type", lower(trim(col("visit_type"))))
        .withColumn("silver_load_timestamp", current_timestamp())
    )
    df = apply_dq_rules(spark, df, "silver_appointment", CATALOG, SILVER_SCHEMA)
    df.write.format("delta").mode("overwrite").option("overwriteSchema", "true") \
        .saveAsTable(f"{CATALOG}.{SILVER_SCHEMA}.silver_appointment")
    print(f"silver_appointment: {df.count()} records")

# COMMAND ----------
# --- Diagnosis ---
def transform_diagnosis():
    df = spark.read.table(f"{CATALOG}.{BRONZE_SCHEMA}.bronze_diagnosis")
    df = (
        df
        .filter(col("diagnosis_code").isNotNull())
        .withColumn("checkup_date", flex_date("checkup_date"))
        .withColumn("diagnosis_code", upper(trim(col("diagnosis_code"))))
        .withColumn("disease_name", upper(trim(col("disease_name"))))
        .withColumn("doctor_charge_inr", col("doctor_charge_inr").cast("double"))
        .withColumn("silver_load_timestamp", current_timestamp())
    )
    df = apply_dq_rules(spark, df, "silver_diagnosis", CATALOG, SILVER_SCHEMA)
    df.write.format("delta").mode("overwrite").option("overwriteSchema", "true") \
        .saveAsTable(f"{CATALOG}.{SILVER_SCHEMA}.silver_diagnosis")
    print(f"silver_diagnosis: {df.count()} records")

# COMMAND ----------
# --- Medication ---
def transform_medication():
    df = spark.read.table(f"{CATALOG}.{BRONZE_SCHEMA}.bronze_medication")
    df = (
        df
        .withColumn("start_date", flex_date("start_date"))
        .withColumn("end_date", flex_date("end_date"))
        .withColumn(
            "is_active_flag",
            when(
                (col("end_date").isNull()) | (col("end_date") >= current_date()), True
            ).otherwise(False)
        )
        .withColumn("route", lower(trim(col("route"))))
        .withColumn("medicine_price", col("medicine_price").cast("double"))
        .withColumn("silver_load_timestamp", current_timestamp())
    )
    df = apply_dq_rules(spark, df, "silver_medication", CATALOG, SILVER_SCHEMA)
    df.write.format("delta").mode("overwrite").option("overwriteSchema", "true") \
        .saveAsTable(f"{CATALOG}.{SILVER_SCHEMA}.silver_medication")
    print(f"silver_medication: {df.count()} records")

# COMMAND ----------
# --- Lab Reports ---
def transform_lab():
    df = spark.read.table(f"{CATALOG}.{BRONZE_SCHEMA}.bronze_lab")
    df = (
        df
        .withColumn("booking_date", flex_date("booking_date"))
        .withColumn("collect_report_date", flex_date("collect_report_date"))
        .withColumn("test_result_num", col("test_result").cast("double"))
        .withColumn("normal_range_min", col("normal_range_min").cast("double"))
        .withColumn("normal_range_max", col("normal_range_max").cast("double"))
        .withColumn(
            "lab_status",
            when(col("test_result_num") < col("normal_range_min"), "BELOW_NORMAL")
            .when(col("test_result_num") > col("normal_range_max"), "ABOVE_NORMAL")
            .otherwise("NORMAL")
        )
        .withColumn("cost", col("cost").cast("double"))
        .withColumn("silver_load_timestamp", current_timestamp())
    )
    df.write.format("delta").mode("overwrite").option("overwriteSchema", "true") \
        .saveAsTable(f"{CATALOG}.{SILVER_SCHEMA}.silver_lab")
    print(f"silver_lab: {df.count()} records")

# COMMAND ----------
# --- Billing ---
def transform_billing():
    df = spark.read.table(f"{CATALOG}.{BRONZE_SCHEMA}.bronze_billing")
    df = (
        df
        .withColumn("treatment_cost", col("treatment_cost").cast("double"))
        .withColumn("insurance_coverage", col("insurence_coverage").cast("double"))
        .withColumn("payment_mode", upper(trim(col("payment_mode_upi_cash"))))
        .withColumn("payment_date", flex_date("payment_date"))
        .withColumn("out_of_pocket", col("treatment_cost") - coalesce(col("insurance_coverage"), lit(0.0)))
        .withColumn("silver_load_timestamp", current_timestamp())
    )
    df = apply_dq_rules(spark, df, "silver_billing", CATALOG, SILVER_SCHEMA)
    df.write.format("delta").mode("overwrite").option("overwriteSchema", "true") \
        .saveAsTable(f"{CATALOG}.{SILVER_SCHEMA}.silver_billing")
    print(f"silver_billing: {df.count()} records")

# COMMAND ----------
# --- Patient History ---
def transform_patient_history():
    df = spark.read.table(f"{CATALOG}.{BRONZE_SCHEMA}.bronze_patient_history")
    df = (
        df
        .withColumn("current_visit_date", flex_date("current_visit_date"))
        .withColumn("prior_visit_date", flex_date("prior_visit_date"))
        .withColumn(
            "days_between_visits",
            when(
                col("prior_visit_date").isNotNull(),
                datediff(col("current_visit_date"), col("prior_visit_date"))
            ).otherwise(lit(None))
        )
        .withColumn("visit_type", lower(trim(col("visit_type"))))
        .withColumn("silver_load_timestamp", current_timestamp())
    )
    df.write.format("delta").mode("overwrite").option("overwriteSchema", "true") \
        .saveAsTable(f"{CATALOG}.{SILVER_SCHEMA}.silver_patient_history")
    print(f"silver_patient_history: {df.count()} records")

# COMMAND ----------
transform_patient()
transform_appointment()
transform_diagnosis()
transform_medication()
transform_lab()
transform_billing()
transform_patient_history()

print("All Silver transformations complete.")
