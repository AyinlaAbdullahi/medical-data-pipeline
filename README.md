# Medical Data Pipeline

I built this project to practice building a real data engineering pipeline from scratch. The idea was simple — take publicly available health data, automate the collection, store it properly, and make it easy to explore visually.

## What it does

Every day at 1PM, the pipeline automatically pulls data from the WHO and OpenFDA APIs, cleans it, loads it into Snowflake, runs dbt transformations, and updates the Metabase dashboard.

## Data Sources

- **WHO** — HIV cases, new infections, prevalence, and life expectancy across countries and years
- **OpenFDA** — Drug adverse event reports (what drugs people reported reactions to, and where)

## Tools Used

| Layer | Tool |
|---|---|
| Ingestion | Python (httpx, pandas) |
| Orchestration | Apache Airflow running in Docker |
| Storage | Snowflake |
| Transformation | dbt |
| Visualization | Metabase |

## How the pipeline runs

The Airflow DAG runs these steps in order:

1. Collect WHO data from the GHO API
2. Clean and standardize the WHO data
3. Collect OpenFDA drug adverse event data
4. Clean the OpenFDA data
5. Load everything into Snowflake (raw and staging layers)
6. Run dbt models to create analytics-ready tables

## dbt Models

Three models sit on top of the staging data:

- `hiv_unified` — brings together HIV total cases, prevalence, and new infections into one table
- `health_summary` — adds life expectancy to the HIV data, one row per country per year
- `drug_reactions` — counts adverse reactions grouped by drug and country

## Dashboard

The Metabase dashboard has four charts:

- Life expectancy trend over time (it's been going up)
- HIV new infections over time (peaked around 2000, declining since)
- HIV total cases by country
- Most reported drugs in adverse event reports

## Running it locally

Clone the repo and create a `.env` file with:

```bash
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_USER=your_user
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_DATABASE=MEDICAL_DB
OPENFDA_API_KEY=your_api_key
```

Install dependencies:
```bash
pip install httpx pandas "snowflake-connector-python[pandas]" python-dotenv dbt-snowflake
```

Start Airflow:
```bash
cd airflow
docker compose up -d
```

Then trigger the DAG from the Airflow UI at `localhost:8081`.