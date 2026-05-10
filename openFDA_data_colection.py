import httpx
import csv
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENFDA_API_KEY")

def fetch_openfda(endpoint, params):
    r = httpx.get(
        f"https://api.fda.gov/{endpoint}",
        params={"api_key": API_KEY, **params},
        timeout=30
    )
    r.raise_for_status()
    return r.json()

def extract_records(data):
    records = []
    for event in data["results"]:
        records.append({
            "report_id": event.get("safetyreportid", ""),
            "date": event.get("receivedate", ""),
            "country": event.get("occurcountry", ""),
            "drug": event.get("patient", {}).get("drug", [{}])[0].get("medicinalproduct", ""),
            "reaction": event.get("patient", {}).get("reaction", [{}])[0].get("reactionmeddrapt", "")
        })
    return records

def save_to_csv(records):
    Path("/opt/airflow/project/data/raw").mkdir(parents=True, exist_ok=True)
    filepath = "/opt/airflow/project/data/raw/openfda.csv"

    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=records[0].keys())
        writer.writeheader()
        writer.writerows(records)

    print(f"Saved {len(records)} records to {filepath}")

data = fetch_openfda("drug/event.json", {"search": "patient.reaction.reactionmeddrapt:fever", "limit": 1000})
records = extract_records(data)
save_to_csv(records)