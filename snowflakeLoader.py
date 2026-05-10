import os
import re
import glob
import pandas as pd
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
from dotenv import load_dotenv

load_dotenv()

ACCOUNT  = os.getenv("SNOWFLAKE_ACCOUNT")
USER     = os.getenv("SNOWFLAKE_USER")
PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")
DATABASE = os.getenv("SNOWFLAKE_DATABASE")


def get_connection(schema: str = None):
    return snowflake.connector.connect(
        account=ACCOUNT,
        user=USER,
        password=PASSWORD,
        database=DATABASE,
        schema=schema,
    )


def bootstrap():
    conn = get_connection()
    cur  = conn.cursor()

    cur.execute("""
        CREATE WAREHOUSE IF NOT EXISTS medical_wh
            WAREHOUSE_SIZE = 'X-SMALL'
            AUTO_SUSPEND   = 60
            AUTO_RESUME    = TRUE
    """)
    cur.execute("USE WAREHOUSE medical_wh")
    cur.execute(f"CREATE SCHEMA IF NOT EXISTS {DATABASE}.RAW")
    cur.execute(f"CREATE SCHEMA IF NOT EXISTS {DATABASE}.STAGING")

    cur.close()
    conn.close()
    print("Warehouse + schemas ready.")


def csv_to_table_name(filepath: str) -> str:
    name = os.path.splitext(os.path.basename(filepath))[0]
    name = re.sub(r"_\d{8}_\d{6}$", "", name)
    return name.upper()


def load_csv(filepath: str, schema: str):
    table = csv_to_table_name(filepath)
    df    = pd.read_csv(filepath)
    df.columns = [c.upper() for c in df.columns]

    conn = get_connection(schema=schema)
    cur  = conn.cursor()
    cur.execute("USE WAREHOUSE medical_wh")

    success, _, nrows, _ = write_pandas(
        conn=conn,
        df=df,
        table_name=table,
        schema=schema,
        database=DATABASE,
        auto_create_table=True,
        overwrite=True,
    )

    cur.close()
    conn.close()

    status = "✓" if success else "✗"
    print(f"  {status}  {schema}.{table}  ({nrows} rows)")


def load_all(data_dir: str = "/opt/airflow/project/data"):
    bootstrap()

    raw_files     = glob.glob(os.path.join(data_dir, "raw",     "*.csv"))
    staging_files = glob.glob(os.path.join(data_dir, "staging", "*.csv"))

    print(f"\nLoading {len(raw_files)} raw file(s)...")
    for f in raw_files:
        load_csv(f, schema="RAW")

    print(f"\nLoading {len(staging_files)} staging file(s)...")
    for f in staging_files:
        load_csv(f, schema="STAGING")

    print("\nAll files loaded.")


if __name__ == "__main__":
    load_all()