from datetime import datetime

import pytest
from pyspark.sql import SparkSession

from transforms import enriquecer, marcar_calidad


@pytest.fixture(scope="session")
def spark():
    return SparkSession.builder.master("local[1]").appName("tests").getOrCreate()


def motivo(spark, **cambios):
    viaje = dict(
        pickup_at=datetime(2024, 1, 15, 10, 0),
        dropoff_at=datetime(2024, 1, 15, 10, 20),
        pasajeros=1,
        distancia_millas=3.0,
        tarifa=15.0,
        total=20.0,
    )
    viaje.update(cambios)
    df = spark.createDataFrame([tuple(viaje.values())], list(viaje.keys()))
    return marcar_calidad(df, "2024-01-01", "2024-02-01").first()["motivo_descarte"]


def test_viaje_valido(spark):
    assert motivo(spark) is None


def test_fecha_fuera_de_periodo(spark):
    assert motivo(
        spark,
        pickup_at=datetime(2023, 12, 31, 23, 0),
        dropoff_at=datetime(2023, 12, 31, 23, 20),
    ) == "fecha_fuera_de_periodo"


def test_termina_antes_de_empezar(spark):
    assert motivo(spark, dropoff_at=datetime(2024, 1, 15, 9, 0)) == "duracion_invalida"


def test_distancia_cero(spark):
    assert motivo(spark, distancia_millas=0.0) == "distancia_invalida"


def test_tarifa_negativa(spark):
    assert motivo(spark, tarifa=-5.0) == "importe_invalido"


def test_sin_pasajeros(spark):
    assert motivo(spark, pasajeros=0) == "pasajeros_invalidos"


def test_enriquecer(spark):
    viajes = spark.createDataFrame(
        [(1, 2, 2, 10.0, 2.0), (1, 2, 9, 10.0, 0.0)],
        ["zona_origen_id", "zona_destino_id", "tipo_pago_id", "tarifa", "propina"],
    )
    zonas = spark.createDataFrame(
        [(1, "Manhattan", "Midtown Center"), (2, "Queens", "JFK Airport")],
        ["LocationID", "Borough", "Zone"],
    )
    filas = enriquecer(viajes, zonas).orderBy("tipo_pago_id").collect()

    assert filas[0]["tipo_pago"] == "efectivo"
    assert filas[0]["propina_pct"] == 20.0
    assert filas[0]["zona_destino"] == "JFK Airport"
    assert filas[1]["tipo_pago"] == "desconocido"