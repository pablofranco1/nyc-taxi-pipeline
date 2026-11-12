from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from spark_session import get_spark

spark = get_spark("charts")
Path("docs").mkdir(exist_ok=True)

hora = spark.read.parquet("data/gold/por_hora").orderBy("hora").collect()
horas = [r["hora"] for r in hora]

fig, ax = plt.subplots(figsize=(9, 4))
ax.bar(horas, [r["viajes"] for r in hora], color="#4c72b0")
ax.set_xlabel("Hora de recogida")
ax.set_ylabel("Viajes")
ax.set_xticks(horas)
ax2 = ax.twinx()
ax2.plot(horas, [r["tarifa_media"] for r in hora], color="#dd8452", marker="o")
ax2.set_ylabel("Tarifa media ($)", color="#dd8452")
ax.set_title("Viajes y tarifa media por hora del día (enero 2024)")
fig.tight_layout()
fig.savefig("docs/viajes_por_hora.png", dpi=120)

calidad = (
    spark.read.csv("data/silver/informe_calidad", header=True, inferSchema=True)
    .filter("motivo_descarte IS NOT NULL")
    .orderBy("count")
    .collect()
)

fig, ax = plt.subplots(figsize=(8, 3.5))
ax.barh([r["motivo_descarte"] for r in calidad], [r["count"] for r in calidad], color="#c44e52")
ax.set_xlabel("Viajes descartados")
ax.set_title("Motivos de descarte en la capa silver")
fig.tight_layout()
fig.savefig("docs/descartes.png", dpi=120)

print("Gráficos guardados en docs/")