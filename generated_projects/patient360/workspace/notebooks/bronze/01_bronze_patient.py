# Databricks notebook source
# MAGIC %md
# MAGIC # Patient360 | Bronze Layer | Patient Records
# MAGIC **Layer:** Bronze | **Table:** bronze_patient | **PK:** patient_id
# MAGIC **Schedule:** Daily | **Load:** Incremental MERGE

# COMMAND ----------
import logging
from pyspark.sql.functions import col, trim, lower, upper, current_timestamp, lit
from pyspark.sql import DataFrame

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bronze_patient")

# COMMAND ----------
# MAGIC %md ## Parameters
dbutils.widgets.text("catalog",    "sdlc_catalog")
dbutils.widgets.text("raw_schema", "patient_360_raw")

CATALOG    = dbutils.widgets.get("catalog")
RAW_SCHEMA = dbutils.widgets.get("raw_schema")
BRONZE_SCHEMA = "patient_360_bronze"
TARGET     = f"{CATALOG}.{BRONZE_SCHEMA}.bronze_patient"

# COMMAND ----------
# MAGIC %md ## Extract
try:
    df_raw = spark.read.table(f"{CATALOG}.{RAW_SCHEMA}.raw_patient_records")
    logger.info(f"Extracted {df_raw.count()} records from raw_patient_records")
except Exception as e:
    logger.error(f"Extraction failed: {e}")
    raise

# COMMAND ----------
# MAGIC %md ## Transform — Column Sanitization
def sanitize(df: DataFrame) -> DataFrame:
    df = df.toDF(*[c.strip().lower().replace(" ", "_") for c in df.columns])
    str_cols = [f.name for f in df.schema.fields if str(f.dataType) == "StringType()"]
    for c in str_cols:
        df = df.withColumn(c, trim(col(c)))
    return df

df_bronze = sanitize(df_raw)
df_bronze = df_bronze.withColumn("bronze_load_timestamp", current_timestamp()) \
                     .withColumn("bronze_table_name", lit("bronze_patient"))

# COMMAND ----------
# MAGIC %md ## Load — MERGE INTO Bronze
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{BRONZE_SCHEMA}")

if not spark.catalog.tableExists(TARGET):
    df_bronze.write.format("delta").saveAsTable(TARGET)
    logger.info(f"Created new table {TARGET}")
else:
    df_bronze.createOrReplaceTempView("src_patient")
    spark.sql(f"""
        MERGE INTO {TARGET} AS tgt
        USING src_patient AS src ON tgt.patient_id = src.patient_id
        WHEN MATCHED THEN UPDATE SET *
        WHEN NOT MATCHED THEN INSERT *
    """)
    logger.info(f"Merged records into {TARGET}")

# COMMAND ----------
# MAGIC %md ## Execution Summary
count = spark.read.table(TARGET).count()
print(f"bronze_patient record count: {count}")
dbutils.notebook.exit(f"SUCCESS: {count} records in {TARGET}")
