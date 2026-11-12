from pyspark.sql import functions as F

from spark_session import get_spark

spark = get_spark("bronze")

trips = (
    spark.read.parquet("data/raw/yellow_tripdata_*.parquet")
    .withColumn("source_file", F.col("_metadata.file_name"))
    .withColumn("ingested_at", F.current_timestamp())
)
zones = spark.read.csv("data/raw/taxi_zone_lookup.csv", header=True, inferSchema=True)

trips.write.mode("overwrite").parquet("data/bronze/trips")
zones.write.mode("overwrite").parquet("data/bronze/zones")

print(f"Viajes cargados: {trips.count():,}")
print(f"Zonas cargadas: {zones.count():,}")
trips.printSchema()