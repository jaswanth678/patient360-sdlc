# Databricks notebook source
# Patient360 — Delta Live Tables Pipeline
# Reads from bronze tables, applies DQ and transforms, writes silver + gold

# COMMAND ----------
import dlt
from pyspark.sql.functions import (
    col, trim, lower, upper, when, current_timestamp, expr,
    coalesce, lit, regexp_replace, datediff, count, sum, avg,
    max, first, countDistinct, row_number, desc
)
from pyspark.sql.window import Window

CATALOG = "sdlc_catalog"
BRONZE  = "patient_360_bronze"

def flex_date(col_name):
    return expr(
        f"coalesce(try_to_date({col_name}, 'M/d/yyyy'), try_to_date({col_name}, 'yyyy-MM-dd'))"
    )

# ── SILVER ─────────────────────────────────────────────────────────────────

@dlt.table(name="silver_patient", comment="Deduplicated, standardised patient records")
def silver_patient():
    w = Window.partitionBy("patient_id").orderBy(desc("ingestion_timestamp"))
    return (
        spark.read.table(f"{CATALOG}.{BRONZE}.bronze_patient")
        .filter(col("patient_id").isNotNull())
        .withColumn("_rn", row_number().over(w)).filter(col("_rn") == 1).drop("_rn")
        .withColumn("patient_name", upper(trim(col("patient_name"))))
        .withColumn("email", lower(trim(col("email"))))
        .withColumn("sex", upper(trim(col("sex"))))
        .withColumn("state", upper(trim(col("state"))))
        .withColumn("dob", flex_date("dob"))
        .withColumn("age", col("age").cast("int"))
        .withColumn("contact", regexp_replace(col("contact"), "[^0-9]", ""))
        .withColumn("silver_load_timestamp", current_timestamp())
    )

@dlt.table(name="silver_appointment", comment="Appointment records with status flag")
def silver_appointment():
    w = Window.partitionBy("appointment_id").orderBy(desc("ingestion_timestamp"))
    return (
        spark.read.table(f"{CATALOG}.{BRONZE}.bronze_appointment")
        .filter(col("appointment_id").isNotNull())
        .withColumn("_rn", row_number().over(w)).filter(col("_rn") == 1).drop("_rn")
        .withColumn("booking_date", flex_date("booking_date"))
        .withColumn("status_flag", when(col("status_y_n") == "y", True).otherwise(False))
        .withColumn("department", upper(trim(col("department"))))
        .withColumn("visit_type", lower(trim(col("visit_type"))))
        .withColumn("silver_load_timestamp", current_timestamp())
    )

@dlt.table(name="silver_diagnosis", comment="Diagnosis records with standardised codes")
def silver_diagnosis():
    return (
        spark.read.table(f"{CATALOG}.{BRONZE}.bronze_diagnosis")
        .filter(col("diagnosis_code").isNotNull())
        .withColumn("checkup_date", flex_date("checkup_date"))
        .withColumn("diagnosis_code", upper(trim(col("diagnosis_code"))))
        .withColumn("disease_name", upper(trim(col("disease_name"))))
        .withColumn("doctor_charge_inr", col("doctor_charge_inr").cast("double"))
        .withColumn("silver_load_timestamp", current_timestamp())
    )

@dlt.table(name="silver_medication", comment="Medication with active flag")
def silver_medication():
    from pyspark.sql.functions import current_date as cur_date
    return (
        spark.read.table(f"{CATALOG}.{BRONZE}.bronze_medication")
        .withColumn("start_date", flex_date("start_date"))
        .withColumn("end_date", flex_date("end_date"))
        .withColumn(
            "is_active_flag",
            when((col("end_date").isNull()) | (col("end_date") >= cur_date()), True).otherwise(False)
        )
        .withColumn("route", lower(trim(col("route"))))
        .withColumn("medicine_price", col("medicine_price").cast("double"))
        .withColumn("silver_load_timestamp", current_timestamp())
    )

@dlt.table(name="silver_lab", comment="Lab results with normal/abnormal classification")
def silver_lab():
    return (
        spark.read.table(f"{CATALOG}.{BRONZE}.bronze_lab")
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

@dlt.table(name="silver_billing", comment="Billing with insurance and OOP amounts")
def silver_billing():
    return (
        spark.read.table(f"{CATALOG}.{BRONZE}.bronze_billing")
        .withColumn("treatment_cost", col("treatment_cost").cast("double"))
        .withColumn("insurance_coverage", col("insurence_coverage").cast("double"))
        .withColumn("payment_mode", upper(trim(col("payment_mode_upi_cash"))))
        .withColumn("payment_date", flex_date("payment_date"))
        .withColumn("out_of_pocket",
            col("treatment_cost") - coalesce(col("insurance_coverage"), lit(0.0)))
        .withColumn("silver_load_timestamp", current_timestamp())
    )

@dlt.table(name="silver_patient_history", comment="Patient visit history with days-between-visits")
def silver_patient_history():
    return (
        spark.read.table(f"{CATALOG}.{BRONZE}.bronze_patient_history")
        .withColumn("current_visit_date", flex_date("current_visit_date"))
        .withColumn("prior_visit_date", flex_date("prior_visit_date"))
        .withColumn(
            "days_between_visits",
            when(col("prior_visit_date").isNotNull(),
                 datediff(col("current_visit_date"), col("prior_visit_date"))
            ).otherwise(lit(None))
        )
        .withColumn("visit_type", lower(trim(col("visit_type"))))
        .withColumn("silver_load_timestamp", current_timestamp())
    )
