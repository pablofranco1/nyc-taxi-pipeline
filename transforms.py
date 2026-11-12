from pyspark.sql import functions as F


def normalizar(df):
    return df.select(
        F.col("tpep_pickup_datetime").cast("timestamp").alias("pickup_at"),
        F.col("tpep_dropoff_datetime").cast("timestamp").alias("dropoff_at"),
        F.col("passenger_count").cast("int").alias("pasajeros"),
        F.col("trip_distance").alias("distancia_millas"),
        F.col("PULocationID").alias("zona_origen_id"),
        F.col("DOLocationID").alias("zona_destino_id"),
        F.col("payment_type").cast("int").alias("tipo_pago_id"),
        F.col("fare_amount").alias("tarifa"),
        F.col("tip_amount").alias("propina"),
        F.col("total_amount").alias("total"),
    )


def marcar_calidad(df, inicio, fin):
    duracion = (F.unix_timestamp("dropoff_at") - F.unix_timestamp("pickup_at")) / 60
    inicio = F.lit(inicio).cast("timestamp")
    fin = F.lit(fin).cast("timestamp")

    motivo = (
        F.when((F.col("pickup_at") < inicio) | (F.col("pickup_at") >= fin), "fecha_fuera_de_periodo")
        .when((duracion <= 0) | (duracion > 360), "duracion_invalida")
        .when((F.col("distancia_millas") <= 0) | (F.col("distancia_millas") > 100), "distancia_invalida")
        .when((F.col("tarifa") <= 0) | (F.col("total") <= 0) | (F.col("tarifa") > 500), "importe_invalido")
        .when((F.col("pasajeros") == 0) | (F.col("pasajeros") > 6), "pasajeros_invalidos")
    )

    return df.withColumn("duracion_min", F.round(duracion, 1)).withColumn("motivo_descarte", motivo)


def enriquecer(df, zonas):
    tipo_pago = (
        F.when(F.col("tipo_pago_id") == 1, "tarjeta")
        .when(F.col("tipo_pago_id") == 2, "efectivo")
        .when(F.col("tipo_pago_id") == 3, "sin cargo")
        .when(F.col("tipo_pago_id") == 4, "disputa")
        .otherwise("desconocido")
    )

    origen = zonas.select(
        F.col("LocationID").alias("zona_origen_id"),
        F.col("Borough").alias("distrito_origen"),
        F.col("Zone").alias("zona_origen"),
    )
    destino = zonas.select(
        F.col("LocationID").alias("zona_destino_id"),
        F.col("Borough").alias("distrito_destino"),
        F.col("Zone").alias("zona_destino"),
    )

    return (
        df.withColumn("tipo_pago", tipo_pago)
        .withColumn("propina_pct", F.round(F.col("propina") / F.col("tarifa") * 100, 1))
        .join(F.broadcast(origen), "zona_origen_id", "left")
        .join(F.broadcast(destino), "zona_destino_id", "left")
    )