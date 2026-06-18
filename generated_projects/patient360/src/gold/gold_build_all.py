# Databricks notebook source
# Patient360 - Gold Layer Builder
# Creates 6 analytical Gold datasets and computes all 10 KPIs

# COMMAND ----------
from pyspark.sql.functions import (
    col, count, countDistinct, sum, avg, max, min,
    when, lit, round as spark_round, current_timestamp,
    first, collect_list, array_join, datediff, current_date,
    dense_rank, percent_rank
)
from pyspark.sql.window import Window

dbutils.widgets.text("catalog", "sdlc_catalog")
dbutils.widgets.text("silver_schema", "patient_360_silver")
dbutils.widgets.text("gold_schema", "patient_360_gold")

CATALOG = dbutils.widgets.get("catalog")
SILVER = dbutils.widgets.get("silver_schema")
GOLD = dbutils.widgets.get("gold_schema")

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{GOLD}")

def silver(t): return spark.read.table(f"{CATALOG}.{SILVER}.{t}")
def save_gold(df, t):
    df.write.format("delta").mode("overwrite").option("overwriteSchema", "true") \
        .saveAsTable(f"{CATALOG}.{GOLD}.{t}")
    print(f"Gold table written: {t} ({df.count()} rows)")

# COMMAND ----------
# 1. patient_360_master - Unified patient view
def build_patient_360_master():
    pat = silver("silver_patient")
    appt = silver("silver_appointment").groupBy("patient_id").agg(
        count("appointment_id").alias("total_appointments"),
        max("booking_date").alias("last_appointment_date")
    )
    diag = silver("silver_diagnosis").groupBy("patient_id").agg(
        countDistinct("diagnosis_code").alias("unique_diagnoses"),
        first("disease_name").alias("primary_disease")
    )
    med = silver("silver_medication").filter(col("is_active_flag") == True).groupBy("patient_id").agg(
        count("medication_id").alias("active_medications")
    )
    lab = silver("silver_lab").groupBy("patient_id").agg(
        count("serial_number").alias("total_lab_tests"),
        sum(when(col("lab_status") != "NORMAL", 1).otherwise(0)).alias("abnormal_lab_count")
    )
    bill = silver("silver_billing").groupBy("patient_id").agg(
        sum("treatment_cost").alias("total_treatment_cost"),
        sum("insurance_coverage").alias("total_insurance_coverage")
    )

    master = (
        pat
        .join(appt, "patient_id", "left")
        .join(diag, "patient_id", "left")
        .join(med, "patient_id", "left")
        .join(lab, "patient_id", "left")
        .join(bill, "patient_id", "left")
        .withColumn("gold_load_timestamp", current_timestamp())
    )
    save_gold(master, "patient_360_master")

# COMMAND ----------
# 2. patient_clinical_summary
def build_patient_clinical_summary():
    diag = silver("silver_diagnosis")
    lab = silver("silver_lab")
    med = silver("silver_medication").filter(col("is_active_flag") == True)

    diag_agg = diag.groupBy("patient_id").agg(
        count("record_id").alias("total_diagnoses"),
        countDistinct("disease_name").alias("unique_diseases"),
        max("checkup_date").alias("last_checkup_date")
    )
    lab_agg = lab.groupBy("patient_id").agg(
        count("serial_number").alias("total_lab_tests"),
        sum(when(col("lab_status") == "ABOVE_NORMAL", 1).otherwise(0)).alias("above_normal_count"),
        sum(when(col("lab_status") == "BELOW_NORMAL", 1).otherwise(0)).alias("below_normal_count")
    )
    med_agg = med.groupBy("patient_id").agg(
        count("medication_id").alias("active_med_count"),
        array_join(collect_list("medication_name"), ", ").alias("active_medications")
    )

    clinical = (
        diag_agg
        .join(lab_agg, "patient_id", "left")
        .join(med_agg, "patient_id", "left")
        .withColumn(
            "lab_risk_flag",
            when(col("above_normal_count") + col("below_normal_count") > 2, True).otherwise(False)
        )
        .withColumn("gold_load_timestamp", current_timestamp())
    )
    save_gold(clinical, "patient_clinical_summary")

# COMMAND ----------
# 3. patient_financial_summary
def build_patient_financial_summary():
    bill = silver("silver_billing")
    pat = silver("silver_patient").select("patient_id", "state")

    fin = (
        bill
        .join(pat, "patient_id", "left")
        .groupBy("patient_id", "state")
        .agg(
            sum("treatment_cost").alias("total_treatment_cost"),
            sum("insurance_coverage").alias("total_insurance_coverage"),
            avg("treatment_cost").alias("avg_treatment_cost"),
            count("bill_id").alias("total_bills"),
            sum(when(col("payment_status") == "PAID", 1).otherwise(0)).alias("paid_bills"),
            sum(when(col("payment_mode") == "UPI", 1).otherwise(0)).alias("upi_payments"),
            sum(when(col("payment_mode") == "CASH", 1).otherwise(0)).alias("cash_payments")
        )
        .withColumn(
            "insurance_coverage_pct",
            spark_round(
                col("total_insurance_coverage") / col("total_treatment_cost") * 100, 2
            )
        )
        .withColumn("gold_load_timestamp", current_timestamp())
    )
    save_gold(fin, "patient_financial_summary")

# COMMAND ----------
# 4. doctor_performance_summary
def build_doctor_performance_summary():
    appt = silver("silver_appointment")
    diag = silver("silver_diagnosis")

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
    save_gold(perf, "doctor_performance_summary")

# COMMAND ----------
# 5. medication_adherence_summary
def build_medication_adherence_summary():
    med = silver("silver_medication")
    adherence = (
        med
        .groupBy("patient_id", "disease")
        .agg(
            count("medication_id").alias("total_medications"),
            sum(when(col("is_active_flag") == True, 1).otherwise(0)).alias("active_medications"),
            avg("medicine_price").alias("avg_medicine_price"),
            sum("medicine_price").alias("total_medicine_cost")
        )
        .withColumn(
            "adherence_rate",
            spark_round(col("active_medications") / col("total_medications") * 100, 2)
        )
        .withColumn("gold_load_timestamp", current_timestamp())
    )
    save_gold(adherence, "medication_adherence_summary")

# COMMAND ----------
# 6. patient_risk_summary
def build_patient_risk_summary():
    master = spark.read.table(f"{CATALOG}.{GOLD}.patient_360_master")
    pat = silver("silver_patient").select("patient_id", col("diease_name").alias("disease_name"))

    risk = (
        master
        .join(pat, "patient_id", "left")
        .withColumn(
            "age_risk",
            when(col("age") >= 65, "HIGH").when(col("age") >= 40, "MEDIUM").otherwise("LOW")
        )
        .withColumn(
            "lab_risk",
            when(col("abnormal_lab_count") > 3, "HIGH")
            .when(col("abnormal_lab_count") > 1, "MEDIUM")
            .otherwise("LOW")
        )
        .withColumn(
            "financial_risk",
            when(
                col("total_treatment_cost") - col("total_insurance_coverage") > 100000, "HIGH"
            ).otherwise("LOW")
        )
        .withColumn(
            "overall_risk_score",
            when(col("age_risk") == "HIGH", 3).when(col("age_risk") == "MEDIUM", 2).otherwise(1)
            + when(col("lab_risk") == "HIGH", 3).when(col("lab_risk") == "MEDIUM", 2).otherwise(1)
            + when(col("financial_risk") == "HIGH", 2).otherwise(1)
        )
        .withColumn(
            "risk_category",
            when(col("overall_risk_score") >= 7, "HIGH_RISK")
            .when(col("overall_risk_score") >= 4, "MEDIUM_RISK")
            .otherwise("LOW_RISK")
        )
        .withColumn("gold_load_timestamp", current_timestamp())
    )
    save_gold(risk, "patient_risk_summary")

# COMMAND ----------
build_patient_360_master()
build_patient_clinical_summary()
build_patient_financial_summary()
build_doctor_performance_summary()
build_medication_adherence_summary()
build_patient_risk_summary()

print("All Gold tables built successfully.")
