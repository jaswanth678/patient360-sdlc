import pytest
from pyspark.sql import SparkSession


@pytest.fixture(scope="session")
def spark():
    return (
        SparkSession.builder
        .master("local[2]")
        .appName("patient360_tests")
        .config("spark.sql.shuffle.partitions", "2")
        .config("spark.databricks.unityCatalog.enabled", "false")
        .getOrCreate()
    )
