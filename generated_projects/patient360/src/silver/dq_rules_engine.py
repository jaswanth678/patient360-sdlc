# Patient360 - Data Quality Rules Engine
# Config-driven DQ validation with quarantine table

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import (
    col, current_timestamp, lit, when, regexp_extract,
    to_date, current_date, expr
)
from typing import List, Dict

DQ_RULES = [
    {
        "rule_id": "DQ001", "rule_name": "patient_id_not_null",
        "table": "silver_patient", "column": "patient_id",
        "condition": "patient_id IS NOT NULL",
        "description": "patient_id must not be null"
    },
    {
        "rule_id": "DQ002", "rule_name": "appointment_id_not_null",
        "table": "silver_appointment", "column": "appointment_id",
        "condition": "appointment_id IS NOT NULL",
        "description": "appointment_id must not be null"
    },
    {
        "rule_id": "DQ003", "rule_name": "diagnosis_code_not_null",
        "table": "silver_diagnosis", "column": "diagnosis_code",
        "condition": "diagnosis_code IS NOT NULL",
        "description": "diagnosis_code must not be null"
    },
    {
        "rule_id": "DQ004", "rule_name": "treatment_cost_non_negative",
        "table": "silver_billing", "column": "treatment_cost",
        "condition": "treatment_cost >= 0",
        "description": "treatment_cost must be >= 0"
    },
    {
        "rule_id": "DQ005", "rule_name": "medicine_price_non_negative",
        "table": "silver_medication", "column": "medicine_price",
        "condition": "medicine_price >= 0",
        "description": "medicine_price must be >= 0"
    },
    {
        "rule_id": "DQ006", "rule_name": "email_format_valid",
        "table": "silver_patient", "column": "email",
        "condition": "email RLIKE '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\\\.[A-Za-z]{2,}$'",
        "description": "email must match valid format"
    },
    {
        "rule_id": "DQ007", "rule_name": "booking_date_not_future",
        "table": "silver_appointment", "column": "booking_date",
        "condition": "booking_date <= current_date()",
        "description": "booking_date must be <= current date"
    },
    {
        "rule_id": "DQ008", "rule_name": "patient_age_valid_range",
        "table": "silver_patient", "column": "age",
        "condition": "age BETWEEN 0 AND 120",
        "description": "patient age must be between 0 and 120"
    },
]


def apply_dq_rules(
    spark: SparkSession,
    df: DataFrame,
    table_name: str,
    catalog: str,
    silver_schema: str
) -> DataFrame:
    """Apply DQ rules for the given table. Returns clean records, writes failures to quarantine."""
    rules = [r for r in DQ_RULES if r["table"] == table_name]
    if not rules:
        return df

    clean_df = df
    quarantine_table = f"{catalog}.{silver_schema}.dq_rejection_log"

    for rule in rules:
        failing = df.filter(~expr(rule["condition"]))
        if failing.count() > 0:
            rejection = failing.select(
                lit(rule["rule_id"]).alias("rule_id"),
                lit(rule["rule_name"]).alias("rule_name"),
                lit(rule["column"]).alias("failed_column"),
                lit(rule["description"]).alias("rule_description"),
                lit(table_name).alias("source_table"),
                current_timestamp().alias("rejection_timestamp"),
                col(rule["column"]).cast("string").alias("failed_value")
            )
            rejection.write.format("delta").mode("append").option(
                "mergeSchema", "true"
            ).saveAsTable(quarantine_table)

        clean_df = clean_df.filter(expr(rule["condition"]))

    return clean_df
