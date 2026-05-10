import pandas as pd
import os

df = pd.read_csv("/opt/airflow/project/data/raw/openfda.csv")

df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')

df['drug'] = df['drug'].str.strip().str.rstrip('.')

df['country'] = df['country'].fillna('Unknown')

str_cols = df.select_dtypes(include=['object', 'string']).columns
df[str_cols] = df[str_cols].apply(lambda x: x.str.strip())

df = df.drop_duplicates()

df['source'] = 'OpenFDA'
df['ingested_at'] = pd.Timestamp.now()

os.makedirs("/opt/airflow/project/data/staging", exist_ok=True)
df.to_csv("/opt/airflow/project/data/staging/clean_openfda.csv", index=False)

print(df.shape)
print(df.isnull().sum())
print(df.head())