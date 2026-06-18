# Databricks notebook source
# MAGIC %md
# MAGIC # Patient360 | Bronze Layer | Diagnosis Records
# MAGIC **Layer:** Bronze | **Table:** bronze_diagnosis | **PK:** record_id

# COMMAND ----------
import logging
from pyspark.sql.functions import col, trim, current_timestamp, lit
logger = logging.getLogger("bronze_diagnosis")

dbutils.widgets.text("catalog", "sdlc_catalog")
dbutils.widgets.text("raw_schema", "patient_360_raw")
CATALOG = dbutils.widgets.get("catalog")
RAW_SCHEMA = dbutils.widgets.get("raw_schema")
BRONZE_SCHEMA = "patient_360_bronze"
TARGET = f"{CATALOG}.{BRONZE_SCHEMA}.bronze_diagnosis"

# COMMAND ----------
df_raw = spark.read.table(f"{CATALOG}.{RAW_SCHEMA}.raw_diagnosis_records")
df = df_raw.toDF(*[c.strip().lower().replace(" ", "_") for c in df_raw.columns])
str_cols = [f.name for f in df.schema.fields if str(f.dataType) == "StringType()"]
for c in str_cols:
    df = df.withColumn(c, trim(col(c)))
df = df.withColumn("bronze_load_timestamp", current_timestamp()) \
       .withColumn("bronze_table_name", lit("bronze_diagnosis"))

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{BRONZE_SCHEMA}")
if not spark.catalog.tableExists(TARGET):
    df.write.format("delta").saveAsTable(TARGET)
else:
    df.createOrReplaceTempView("src_diag")
    spark.sql(f"""
        MERGE INTO {TARGET} tgt USING src_diag src ON tgt.record_id = src.record_id
        WHEN MATCHED THEN UPDATE SET * WHEN NOT MATCHED THEN INSERT *
    """)

count = spark.read.table(TARGET).count()
print(f"bronze_diagnosis: {count} records")
dbutils.notebook.exit(f"SUCCESS: {count}")
