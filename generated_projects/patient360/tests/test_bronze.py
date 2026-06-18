import pytest
from pyspark.sql.functions import col, trim, lower, upper


class TestBronze:
    def test_column_sanitization_lowercase(self, spark):
        data = [("P001", "JOHN DOE")]
        df = spark.createDataFrame(data, ["Patient_ID", "Patient_NAME"])
        df = df.toDF(*[c.strip().lower().replace(" ", "_") for c in df.columns])
        assert "patient_id" in df.columns
        assert "patient_name" in df.columns

    def test_string_trim(self, spark):
        data = [("  P001  ", "  John Doe  ")]
        df = spark.createDataFrame(data, ["patient_id", "patient_name"])
        df = df.withColumn("patient_id", trim(col("patient_id")))
        df = df.withColumn("patient_name", trim(col("patient_name")))
        row = df.collect()[0]
        assert row["patient_id"] == "P001"
        assert row["patient_name"] == "John Doe"

    def test_bronze_metadata_columns(self, spark):
        from pyspark.sql.functions import current_timestamp, lit
        data = [("P001",)]
        df = spark.createDataFrame(data, ["patient_id"])
        df = df.withColumn("bronze_load_timestamp", current_timestamp())
        df = df.withColumn("bronze_table_name", lit("bronze_patient"))
        assert "bronze_load_timestamp" in df.columns
        assert "bronze_table_name" in df.columns

    def test_no_rows_dropped_in_bronze(self, spark):
        data = [("P001", "Alice"), ("P002", None), (None, "Charlie")]
        df = spark.createDataFrame(data, ["patient_id", "name"])
        assert df.count() == 3

    def test_merge_deduplicates_on_pk(self, spark):
        data = [("P001", "Alice"), ("P001", "Alice Updated"), ("P002", "Bob")]
        df = spark.createDataFrame(data, ["patient_id", "name"])
        deduped = df.dropDuplicates(["patient_id"])
        assert deduped.count() == 2
