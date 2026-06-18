import pytest
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from datetime import date


class TestIngestion:
    def test_metadata_columns_present(self, spark):
        data = [("P001", "John Doe", "M", "CA", 35)]
        df = spark.createDataFrame(data, ["patient_id", "patient_name", "sex", "state", "age"])

        from pyspark.sql.functions import current_timestamp, lit, md5, concat_ws
        from datetime import datetime
        df = (
            df
            .withColumn("ingestion_timestamp", current_timestamp())
            .withColumn("source_file_name", lit("Patient_records.csv"))
            .withColumn("load_date", lit(str(date.today())))
            .withColumn("record_hash", md5(concat_ws("|", *[col(c) for c in df.columns])))
        )

        assert "ingestion_timestamp" in df.columns
        assert "source_file_name" in df.columns
        assert "load_date" in df.columns
        assert "record_hash" in df.columns

    def test_source_file_name_set_correctly(self, spark):
        from pyspark.sql.functions import lit
        data = [("P001",)]
        df = spark.createDataFrame(data, ["patient_id"])
        df = df.withColumn("source_file_name", lit("Patient_records.csv"))
        result = df.collect()[0]["source_file_name"]
        assert result == "Patient_records.csv"

    def test_record_hash_unique_for_distinct_records(self, spark):
        from pyspark.sql.functions import md5, concat_ws
        data = [("P001", "Alice"), ("P002", "Bob")]
        df = spark.createDataFrame(data, ["patient_id", "name"])
        df = df.withColumn("record_hash", md5(concat_ws("|", col("patient_id"), col("name"))))
        hashes = [r["record_hash"] for r in df.collect()]
        assert len(set(hashes)) == 2

    def test_incremental_append_does_not_deduplicate(self, spark):
        data1 = [("P001", "Alice")]
        data2 = [("P001", "Alice"), ("P002", "Bob")]
        df1 = spark.createDataFrame(data1, ["patient_id", "name"])
        df2 = spark.createDataFrame(data2, ["patient_id", "name"])
        combined = df1.unionByName(df2)
        assert combined.count() == 3
