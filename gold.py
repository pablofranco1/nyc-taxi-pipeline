from pyspark.sql import functions as F

from spark_session import get_spark

spark = get_spark("gold")
trips = spark.read.parquet("data/silver/trips").cache()

tablas = {
    "por_hora": trips.groupBy(F.hour("pickup_at").alias("hora")).agg(
        F.count("*").alias("viajes"),
        F.round(F.avg("tarifa"), 2).alias("tarifa_media"),
        F.round(F.avg("duracion_min"), 1).alias("duracion_media_min"),
    ).orderBy("hora"),

    "por_zona": trips.groupBy("distrito_origen", "zona_origen").agg(
        F.count("*").alias("viajes"),
        F.round(F.sum("total"), 2).cast("decimal(14,2)").alias("facturacion"),
        F.round(F.avg("propina_pct"), 1).alias("propina_media_pct"),
    ).orderBy(F.desc("viajes")),

    "por_pago": trips.groupBy("tipo_pago").agg(
        F.count("*").alias("viajes"),
        F.round(F.avg("propina_pct"), 1).alias("propina_media_pct"),
    ).orderBy(F.desc("viajes")),

    "rutas": trips.groupBy("zona_origen", "zona_destino").agg(
        F.count("*").alias("viajes"),
        F.round(F.avg("tarifa"), 2).alias("tarifa_media"),
    ).orderBy(F.desc("viajes")).limit(50),
}

for nombre, df in tablas.items():
    df.write.mode("overwrite").parquet(f"data/gold/{nombre}")
    print(f"\n== {nombre} ==")
    df.show(10, truncate=False)