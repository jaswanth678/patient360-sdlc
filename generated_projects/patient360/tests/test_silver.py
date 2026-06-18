import pytest
from pyspark.sql.functions import col, to_date, trim, upper, lower, when, current_date, expr
from datetime import date


class TestSilverDQRules:
    def test_dq001_patient_id_not_null(self, spark):
        data = [("P001", "Alice"), (None, "Bob")]
        df = spark.createDataFrame(data, ["patient_id", "name"])
        clean = df.filter(col("patient_id").isNotNull())
        assert clean.count() == 1

    def test_dq002_appointment_id_not_null(self, spark):
        data = [("A001", "P001"), (None, "P002")]
        df = spark.createDataFrame(data, ["appointment_id", "patient_id"])
        clean = df.filter(col("appointment_id").isNotNull())
        assert clean.count() == 1

    def test_dq003_diagnosis_code_not_null(self, spark):
        data = [("ICD001", "P001"), (None, "P002")]
        df = spark.createDataFrame(data, ["diagnosis_code", "patient_id"])
        clean = df.filter(col("diagnosis_code").isNotNull())
        assert clean.count() == 1

    def test_dq004_treatment_cost_non_negative(self, spark):
        data = [(500.0, "B001"), (-100.0, "B002"), (0.0, "B003")]
        df = spark.createDataFrame(data, ["treatment_cost", "bill_id"])
        clean = df.filter(col("treatment_cost") >= 0)
        assert clean.count() == 2

    def test_dq005_medicine_price_non_negative(self, spark):
        data = [(25.0, "M001"), (-5.0, "M002")]
        df = spark.createDataFrame(data, ["medicine_price", "medication_id"])
        clean = df.filter(col("medicine_price") >= 0)
        assert clean.count() == 1

    def test_dq006_email_format_valid(self, spark):
        data = [("alice@example.com", "P001"), ("not-an-email", "P002"), ("bob@test.org", "P003")]
        df = spark.createDataFrame(data, ["email", "patient_id"])
        clean = df.filter(expr(r"email RLIKE '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'"))
        assert clean.count() == 2

    def test_dq007_booking_date_not_future(self, spark):
        data = [("2024-01-15", "A001"), ("2099-12-31", "A002")]
        df = spark.createDataFrame(data, ["booking_date_str", "appointment_id"])
        df = df.withColumn("booking_date", to_date(col("booking_date_str"), "yyyy-MM-dd"))
        clean = df.filter(col("booking_date") <= current_date())
        assert clean.count() == 1

    def test_dq008_patient_age_valid_range(self, spark):
        data = [(25, "P001"), (-1, "P002"), (121, "P003"), (0, "P004"), (120, "P005")]
        df = spark.createDataFrame(data, ["age", "patient_id"])
        clean = df.filter((col("age") >= 0) & (col("age") <= 120))
        assert clean.count() == 3

    def test_deduplication_keeps_latest_record(self, spark):
        from pyspark.sql.functions import row_number, desc
        from pyspark.sql.window import Window
        data = [
            ("P001", "Alice", "2024-01-01"),
            ("P001", "Alice Updated", "2024-06-01"),
            ("P002", "Bob", "2024-01-01"),
        ]
        df = spark.createDataFrame(data, ["patient_id", "name", "ingestion_timestamp"])
        w = Window.partitionBy("patient_id").orderBy(desc("ingestion_timestamp"))
        from pyspark.sql.functions import row_number
        df = df.withColumn("rn", row_number().over(w)).filter(col("rn") == 1).drop("rn")
        assert df.count() == 2
        alice = df.filter(col("patient_id") == "P001").collect()[0]
        assert alice["name"] == "Alice Updated"

    def test_lab_status_derivation(self, spark):
        data = [(5.0, 4.0, 8.0), (10.0, 4.0, 8.0), (2.0, 4.0, 8.0)]
        df = spark.createDataFrame(data, ["test_result", "normal_range_min", "normal_range_max"])
        df = df.withColumn(
            "lab_status",
            when(col("test_result") < col("normal_range_min"), "BELOW_NORMAL")
            .when(col("test_result") > col("normal_range_max"), "ABOVE_NORMAL")
            .otherwise("NORMAL")
        )
        results = {r["test_result"]: r["lab_status"] for r in df.collect()}
        assert results[5.0] == "NORMAL"
        assert results[10.0] == "ABOVE_NORMAL"
        assert results[2.0] == "BELOW_NORMAL"
