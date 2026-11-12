import shutil
import urllib.request
from pathlib import Path

MONTH = "2024-01"
BASE = "https://d37ci6vzurychx.cloudfront.net"
FILES = {
    f"yellow_tripdata_{MONTH}.parquet": f"{BASE}/trip-data/yellow_tripdata_{MONTH}.parquet",
    "taxi_zone_lookup.csv": f"{BASE}/misc/taxi_zone_lookup.csv",
}

RAW = Path("data/raw")
RAW.mkdir(parents=True, exist_ok=True)

for name, url in FILES.items():
    dest = RAW / name
    if dest.exists():
        print(f"Ya existe: {name}")
        continue
    print(f"Descargando {name}...")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as response, open(dest, "wb") as f:
        shutil.copyfileobj(response, f)

print("Descarga completada")