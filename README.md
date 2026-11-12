# \# NYC Taxi Pipeline

# 

# !\[tests](https://github.com/pablofranco1/nyc-taxi-pipeline/actions/workflows/tests.yml/badge.svg)

# 

# Pipeline de datos con PySpark sobre los viajes de taxi amarillo de Nueva York (enero de 2024, casi 3 millones de viajes), con arquitectura medallion: bronze, silver y gold. Todo se ejecuta en Docker.

# 

# ```mermaid

# flowchart LR

# &#x20;   A\[NYC TLC<br>Parquet + CSV] --> B\[Bronze<br>datos en bruto<br>+ trazabilidad]

# &#x20;   B --> C\[Silver<br>limpieza, reglas de calidad<br>y enriquecimiento]

# &#x20;   C --> D\[Gold<br>tablas agregadas]

# &#x20;   C --> E\[Informe de calidad]

# ```

# 

# \## Capas

# 

# \- \*\*Bronze:\*\* ingesta de los datos tal cual llegan, añadiendo el archivo de origen y la fecha de carga de cada fila.

# \- \*\*Silver:\*\* columnas normalizadas, reglas de calidad, cruce con las zonas de la ciudad y cálculo de duración y porcentaje de propina. Cada viaje descartado guarda el motivo.

# \- \*\*Gold:\*\* tablas listas para análisis: viajes por hora, por zona, por tipo de pago y rutas más frecuentes.

# 

# \## Calidad de datos

# 

# De 2.964.624 viajes, el 95,7 % pasa todas las reglas:

# 

# | Motivo | Viajes | % |

# |---|---:|---:|

# | Distancia de 0 millas o más de 100 | 59.650 | 2,01 % |

# | Tarifa o total negativos, a cero o tarifa de más de 500 $ | 34.546 | 1,17 % |

# | 0 pasajeros o más de 6 | 30.700 | 1,04 % |

# | Termina antes de empezar o dura más de 6 horas | 2.642 | 0,09 % |

# | Fecha fuera del periodo | 18 | 0,00 % |

# 

# !\[Descartes](docs/descartes.png)

# 

# \## Hallazgos

# 

# \- \*\*Las propinas en efectivo no se registran.\*\* Los pagos con tarjeta tienen una propina media del 25,7 % y los de efectivo, un 0,0 %. No es que no se deje propina: el dato no existe. Cualquier análisis de propinas que incluya el efectivo sale sesgado.

# \- \*\*El aeropuerto JFK factura más del triple que Midtown Center\*\* con un número de viajes similar (11,1 M $ frente a 3,3 M $), por la longitud de los trayectos. Es también la zona con menor propina media (14,2 %).

# \- \*\*La tarifa media se dispara de madrugada:\*\* a las 5 de la mañana llega a 27,5 $, frente a unos 18 $ en hora punta. Hay pocos viajes, pero muchos son al aeropuerto.

# \- \*\*Las rutas más frecuentes son cortas:\*\* las cuatro primeras son trayectos dentro del Upper East Side, con tarifas medias de 7 a 9 $.

# 

# !\[Viajes por hora](docs/viajes\_por\_hora.png)

# 

# \## Ejecución

# 

# Requisitos: Docker.

# 

# ```

# git clone https://github.com/pablofranco1/nyc-taxi-pipeline.git

# cd nyc-taxi-pipeline

# docker compose build

# docker compose run --rm pipeline python download.py

# docker compose run --rm pipeline python bronze.py

# docker compose run --rm pipeline python silver.py

# docker compose run --rm pipeline python gold.py

# docker compose run --rm pipeline python charts.py

# ```

# 

# \## Tests

# 

# Cada regla de calidad tiene su test, y se ejecutan en GitHub Actions en cada push:

# 

# ```

# docker compose run --rm pipeline pytest -v

# ```

# 

# \## Estructura

# 

# \- `download.py`: descarga de los datos públicos de NYC TLC

# \- `bronze.py`, `silver.py`, `gold.py`: una capa cada uno

# \- `transforms.py`: reglas de limpieza y enriquecimiento

# \- `test\_transforms.py`: tests de las reglas de calidad

# \- `charts.py`: gráficos de los resultados

# \- `spark\_session.py`: configuración común de Spark

