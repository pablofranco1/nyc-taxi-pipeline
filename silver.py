from pyspark.sql import functions as F

from spark_session import get_spark
from transforms import enriquecer, marcar_calidad, normalizar

INICIO, FIN = "2024-01-01", "2024-02-01"

spark = get_spark("silver")
trips = spark.read.parquet("data/bronze/trips")
zonas = spark.read.parquet("data/bronze/zones")

marcados = marcar_calidad(normalizar(trips), INICIO, FIN).cache()
total = marcados.count()

informe = marcados.groupBy("motivo_descarte").count().orderBy(F.desc("count"))
informe.coalesce(1).write.mode("overwrite").option("header", True).csv("data/silver/informe_calidad")

print(f"\nInforme de calidad ({total:,} viajes)\n")
for fila in informe.collect():
    motivo = fila["motivo_descarte"] or "válidos"
    print(f"{motivo:<25}{fila['count']:>12,}{fila['count'] / total:>9.2%}")

validos = marcados.filter(F.col("motivo_descarte").isNull()).drop("motivo_descarte")
enriquecer(validos, zonas).write.mode("overwrite").parquet("data/silver/trips")
print("\nSilver guardado en data/silver/trips")