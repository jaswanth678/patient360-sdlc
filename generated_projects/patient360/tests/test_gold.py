import pytest
from pyspark.sql.functions import col, sum, count, avg, when


class TestGold:
    def test_patient_360_master_join_completeness(self, spark):
        patients = spark.createDataFrame(
            [("P001", "Alice", "CA"), ("P002", "Bob", "TX")],
            ["patient_id", "name", "state"]
        )
        appointments = spark.createDataFrame(
            [("P001", "A001"), ("P001", "A002"), ("P002", "A003")],
            ["patient_id", "appointment_id"]
        )
        appt_agg = appointments.groupBy("patient_id").agg(
            count("appointment_id").alias("total_appointments")
        )
        master = patients.join(appt_agg, "patient_id", "left")
        assert master.count() == 2
        p001 = master.filter(col("patient_id") == "P001").collect()[0]
        assert p001["total_appointments"] == 2

    def test_financial_summary_kpi_accuracy(self, spark):
        billing = spark.createDataFrame(
            [("P001", 1000.0, 600.0), ("P001", 500.0, 200.0), ("P002", 300.0, 100.0)],
            ["patient_id", "treatment_cost", "insurance_coverage"]
        )
        fin = billing.groupBy("patient_id").agg(
            sum("treatment_cost").alias("total_cost"),
            sum("insurance_coverage").alias("total_coverage")
        )
        p001 = fin.filter(col("patient_id") == "P001").collect()[0]
        assert p001["total_cost"] == 1500.0
        assert p001["total_coverage"] == 800.0

    def test_risk_category_assignment(self, spark):
        data = [("P001", 70, 5), ("P002", 30, 1), ("P003", 50, 3)]
        df = spark.createDataFrame(data, ["patient_id", "age", "abnormal_lab_count"])
        df = df.withColumn(
            "age_risk",
            when(col("age") >= 65, 3).when(col("age") >= 40, 2).otherwise(1)
        ).withColumn(
            "lab_risk",
            when(col("abnormal_lab_count") > 3, 3)
            .when(col("abnormal_lab_count") > 1, 2)
            .otherwise(1)
        ).withColumn(
            "overall_risk_score", col("age_risk") + col("lab_risk")
        ).withColumn(
            "risk_category",
            when(col("overall_risk_score") >= 5, "HIGH_RISK")
            .when(col("overall_risk_score") >= 3, "MEDIUM_RISK")
            .otherwise("LOW_RISK")
        )
        p001 = df.filter(col("patient_id") == "P001").collect()[0]
        assert p001["risk_category"] == "HIGH_RISK"

    def test_medication_adherence_rate_calculation(self, spark):
        data = [
            ("P001", "MED_A", True),
            ("P001", "MED_B", False),
            ("P001", "MED_C", True),
            ("P002", "MED_D", False),
        ]
        df = spark.createDataFrame(data, ["patient_id", "medication_name", "is_active"])
        agg = df.groupBy("patient_id").agg(
            count("medication_name").alias("total"),
            sum(when(col("is_active") == True, 1).otherwise(0)).alias("active")
        ).withColumn("adherence_rate", col("active") / col("total") * 100)
        p001 = agg.filter(col("patient_id") == "P001").collect()[0]
        assert round(p001["adherence_rate"], 1) == 66.7

    def test_doctor_performance_unique_patients(self, spark):
        data = [
            ("D001", "Dr. Smith", "P001"),
            ("D001", "Dr. Smith", "P002"),
            ("D001", "Dr. Smith", "P001"),
        ]
        df = spark.createDataFrame(data, ["doctor_id", "doctor_name", "patient_id"])
        from pyspark.sql.functions import countDistinct
        perf = df.groupBy("doctor_id", "doctor_name").agg(
            countDistinct("patient_id").alias("unique_patients"),
            count("patient_id").alias("total_appointments")
        )
        row = perf.collect()[0]
        assert row["unique_patients"] == 2
        assert row["total_appointments"] == 3
