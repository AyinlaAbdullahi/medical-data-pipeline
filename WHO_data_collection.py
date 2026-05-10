import httpx
import csv
from pathlib import Path

def fetch_who(indicator):
    r = httpx.get(
        f"https://ghoapi.azureedge.net/api/{indicator}",
        timeout=30
    )
    r.raise_for_status()
    return r.json()

def extract_records(data, indicator_name):
    records = []
    for row in data["value"]:
        records.append({
            "indicator": indicator_name,
            "country": row.get("SpatialDim", ""),
            "year": row.get("TimeDim", ""),
            "value": row.get("NumericValue", ""),
            "sex": row.get("Dim1", ""),
        })
    return records

def save_to_csv(records, name):
    Path("/opt/airflow/project/data/raw").mkdir(parents=True, exist_ok=True)
    filepath = f"/opt/airflow/project/data/raw/who_{name}.csv"

    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=records[0].keys())
        writer.writeheader()
        writer.writerows(records)

    print(f"Saved {len(records)} records to {filepath}")

indicators = [
    ("WHOSIS_000001",  "life_expectancy"),
    ("HIV_0000000001", "hiv_total"),
    ("MDG_0000000029", "hiv_prevalence"),
    ("HIV_0000000026", "hiv_new_infections"),
]

for code, name in indicators:
    data = fetch_who(code)
    records = extract_records(data, name)
    save_to_csv(records, name)