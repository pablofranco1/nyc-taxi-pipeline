from pyspark.sql import SparkSession


def get_spark(name):
    spark = (
        SparkSession.builder
        .appName(name)
        .master("local[*]")
        .config("spark.driver.memory", "2g")
        .config("spark.sql.session.timeZone", "UTC")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")
    return spark