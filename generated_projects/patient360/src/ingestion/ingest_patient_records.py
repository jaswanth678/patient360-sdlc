# Databricks notebook source
# Patient360 - Source Ingestion Notebook
# Incremental load of 7 CSV datasets into patient_360_raw schema

# COMMAND ----------
import hashlib
from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    current_timestamp, lit, md5, concat_ws, col, input_file_name
)

# COMMAND ----------
# Parameters (injected by DAB job)
dbutils.widgets.text("catalog", "sdlc_catalog")
dbutils.widgets.text("source_schema", "patient_360")
dbutils.widgets.text("raw_schema", "patient_360_raw")

CATALOG = dbutils.widgets.get("catalog")
SOURCE_SCHEMA = dbutils.widgets.get("source_schema")
RAW_SCHEMA = dbutils.widgets.get("raw_schema")

SOURCE_PATH = f"/Volumes/{CATALOG}/{SOURCE_SCHEMA}/source"

# COMMAND ----------
DATASETS = [
    {"file": "Patient_records.csv",    "table": "raw_patient_records"},
    {"file": "Appointment_record.csv", "table": "raw_appointment_records"},
    {"file": "Diagnosis_record.csv",   "table": "raw_diagnosis_records"},
    {"file": "Medication.csv",         "table": "raw_medication"},
    {"file": "Lab_report.csv",         "table": "raw_lab_reports"},
    {"file": "Billing_record.csv",     "table": "raw_billing_records"},
    {"file": "Patient_history.csv",    "table": "raw_patient_history"},
]

# COMMAND ----------
import re

def sanitize_col_name(name: str) -> str:
    """Replace all non-alphanumeric chars (except underscore) with underscore."""
    sanitized = re.sub(r'[^a-zA-Z0-9_]+', '_', name).strip('_').lower()
    return sanitized or "col_unknown"

def sanitize_col_names(df):
    """Rename all columns to Delta-safe names."""
    for original in df.columns:
        safe = sanitize_col_name(original)
        if safe != original:
            print(f"  Renaming column: '{original}' -> '{safe}'")
            df = df.withColumnRenamed(original, safe)
    return df

def ingest_csv(file_name: str, table_name: str):
    file_path = f"{SOURCE_PATH}/{file_name}"
    df = (
        spark.read
        .option("header", "true")
        .option("inferSchema", "true")
        .option("mode", "PERMISSIVE")
        .csv(file_path)
    )
    df = sanitize_col_names(df)

    df = (
        df
        .withColumn("ingestion_timestamp", current_timestamp())
        .withColumn("source_file_name", lit(file_name))
        .withColumn("load_date", lit(datetime.now().strftime("%Y-%m-%d")))
        .withColumn(
            "record_hash",
            md5(concat_ws("|", *[col(c) for c in df.columns]))
        )
    )

    target = f"{CATALOG}.{RAW_SCHEMA}.{table_name}"
    (
        df.write
        .format("delta")
        .mode("append")
        .option("mergeSchema", "true")
        .saveAsTable(target)
    )
    print(f"Ingested {df.count()} records into {target}")

# COMMAND ----------
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{RAW_SCHEMA}")

for ds in DATASETS:
    ingest_csv(ds["file"], ds["table"])

print("Source ingestion complete.")
