# Databricks notebook source
# Patient360 - Bronze Layer Orchestrator
# Loads all 7 raw tables into Bronze Delta tables with sanitization

# COMMAND ----------
from pyspark.sql.functions import col, trim, lower, current_timestamp, lit, to_timestamp, row_number, desc
from pyspark.sql.window import Window
from pyspark.sql import DataFrame

dbutils.widgets.text("catalog", "sdlc_catalog")
dbutils.widgets.text("raw_schema", "patient_360_raw")

CATALOG = dbutils.widgets.get("catalog")
RAW_SCHEMA = dbutils.widgets.get("raw_schema")
BRONZE_SCHEMA = "patient_360_bronze"

# COMMAND ----------
def sanitize_columns(df: DataFrame) -> DataFrame:
    """Lowercase column names and trim string values."""
    df = df.toDF(*[c.strip().lower().replace(" ", "_") for c in df.columns])
    str_cols = [f.name for f in df.schema.fields if str(f.dataType) == "StringType()"]
    for c in str_cols:
        df = df.withColumn(c, trim(col(c)))
    return df

def add_bronze_metadata(df: DataFrame, table_name: str) -> DataFrame:
    return (
        df
        .withColumn("bronze_load_timestamp", current_timestamp())
        .withColumn("bronze_table_name", lit(table_name))
    )

def dedup_by_pk(df: DataFrame, pk_cols: list) -> DataFrame:
    """Keep the latest row per PK, eliminating duplicates from repeated ingestion runs."""
    w = Window.partitionBy(*pk_cols).orderBy(desc("ingestion_timestamp"))
    return (
        df.withColumn("_rn", row_number().over(w))
          .filter(col("_rn") == 1)
          .drop("_rn")
    )

def merge_into_bronze(df: DataFrame, target_table: str, pk_cols: list):
    target = f"{CATALOG}.{BRONZE_SCHEMA}.{target_table}"
    spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{BRONZE_SCHEMA}")

    df = dedup_by_pk(df, pk_cols)

    if not spark.catalog.tableExists(target):
        df.write.format("delta").saveAsTable(target)
        return

    merge_condition = " AND ".join([f"tgt.{k} = src.{k}" for k in pk_cols])
    df.createOrReplaceTempView("src_view")

    spark.sql(f"""
        MERGE INTO {target} AS tgt
        USING src_view AS src
        ON {merge_condition}
        WHEN MATCHED THEN UPDATE SET *
        WHEN NOT MATCHED THEN INSERT *
    """)

# COMMAND ----------
BRONZE_CONFIG = [
    {"raw_table": "raw_patient_records",    "bronze_table": "bronze_patient",         "pk": ["patient_id"]},
    {"raw_table": "raw_appointment_records","bronze_table": "bronze_appointment",      "pk": ["appointment_id"]},
    {"raw_table": "raw_diagnosis_records",  "bronze_table": "bronze_diagnosis",        "pk": ["record_id"]},
    {"raw_table": "raw_medication",         "bronze_table": "bronze_medication",       "pk": ["medication_id"]},
    {"raw_table": "raw_lab_reports",        "bronze_table": "bronze_lab",             "pk": ["serial_number"]},
    {"raw_table": "raw_billing_records",    "bronze_table": "bronze_billing",          "pk": ["bill_id"]},
    {"raw_table": "raw_patient_history",    "bronze_table": "bronze_patient_history",  "pk": ["appointment_id", "patient_id"]},
]

# COMMAND ----------
for cfg in BRONZE_CONFIG:
    raw = f"{CATALOG}.{RAW_SCHEMA}.{cfg['raw_table']}"
    df = spark.read.table(raw)
    df = sanitize_columns(df)
    df = add_bronze_metadata(df, cfg["bronze_table"])
    merge_into_bronze(df, cfg["bronze_table"], cfg["pk"])
    print(f"Bronze load complete: {cfg['bronze_table']}")

print("All Bronze tables loaded.")
