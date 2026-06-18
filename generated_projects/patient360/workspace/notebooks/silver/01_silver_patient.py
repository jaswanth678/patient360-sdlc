# Databricks notebook source
# MAGIC %md
# MAGIC # Patient360 | Silver Layer | Patient
# MAGIC **Transformations:** Dedup, normalize name/email, DQ rules DQ001 DQ006 DQ008

# COMMAND ----------
import logging
from pyspark.sql.functions import (
    col, trim, upper, lower, to_date, current_timestamp,
    regexp_replace, row_number, desc, expr
)
from pyspark.sql.window import Window

logger = logging.getLogger("silver_patient")

dbutils.widgets.text("catalog", "sdlc_catalog")
dbutils.widgets.text("silver_schema", "patient_360_silver")
CATALOG = dbutils.widgets.get("catalog")
SILVER = dbutils.widgets.get("silver_schema")
BRONZE = "patient_360_bronze"

# COMMAND ----------
# MAGIC %md ## Extract from Bronze
try:
    df = spark.read.table(f"{CATALOG}.{BRONZE}.bronze_patient")
    logger.info(f"Read {df.count()} records from bronze_patient")
except Exception as e:
    logger.error(f"Bronze read failed: {e}"); raise

# COMMAND ----------
# MAGIC %md ## Transform
w = Window.partitionBy("patient_id").orderBy(desc("ingestion_timestamp"))
df = (
    df
    .filter(col("patient_id").isNotNull())
    .withColumn("rn", row_number().over(w)).filter(col("rn") == 1).drop("rn")
    .withColumn("patient_name",  upper(trim(col("patient_name"))))
    .withColumn("email",         lower(trim(col("email"))))
    .withColumn("sex",           upper(trim(col("sex"))))
    .withColumn("state",         upper(trim(col("state"))))
    .withColumn("dob",           to_date(col("dob"), "yyyy-MM-dd"))
    .withColumn("age",           col("age").cast("int"))
    .withColumn("contact",       regexp_replace(col("contact"), "[^0-9]", ""))
    .withColumn("silver_load_timestamp", current_timestamp())
)

# COMMAND ----------
# MAGIC %md ## DQ Rules
# DQ001 - patient_id not null (already filtered above)
# DQ006 - email format
# DQ008 - age 0–120
from sys import path; path.insert(0, "/Workspace/patient360/src/silver")
try:
    from dq_rules_engine import apply_dq_rules
    df = apply_dq_rules(spark, df, "silver_patient", CATALOG, SILVER)
except ImportError:
    df = df.filter(expr(r"email RLIKE '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'"))
    df = df.filter((col("age") >= 0) & (col("age") <= 120))

# COMMAND ----------
# MAGIC %md ## Load
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{SILVER}")
df.write.format("delta").mode("overwrite").option("overwriteSchema", "true") \
    .saveAsTable(f"{CATALOG}.{SILVER}.silver_patient")

count = df.count()
logger.info(f"silver_patient written: {count} records")
dbutils.notebook.exit(f"SUCCESS: {count}")
