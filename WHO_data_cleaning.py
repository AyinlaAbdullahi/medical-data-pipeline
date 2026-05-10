import pandas as pd
import os

RAW_DIR     = "/opt/airflow/project/data/raw"
STAGING_DIR = "/opt/airflow/project/data/staging"
os.makedirs(STAGING_DIR, exist_ok=True)

FILES = {
    "hiv_new_infections": "who_hiv_new_infections.csv",
    "hiv_prevalence":     "who_hiv_prevalence.csv",
    "hiv_total":          "who_hiv_total.csv",
    "life_expectancy":    "who_life_expectancy.csv",
}


def clean_who(df, dataset_name):
    print(f"\n{'='*50}")
    print(f"Cleaning: {dataset_name}")
    print(f"Before: {df.shape}")

    df = df.dropna(subset=["year"])

    if dataset_name != "life_expectancy":
        df = df.drop(columns=["sex"], errors="ignore")
    else:
        sex_map = {"SEX_MLE": "Male", "SEX_FMLE": "Female", "SEX_BTSX": "Both"}
        df["sex"] = df["sex"].map(sex_map).fillna("Unknown")

    if "value" in df.columns:
        df["value"] = df.groupby("country")["value"].transform(
            lambda x: x.fillna(x.median())
        )
        df["value"] = df["value"].fillna(df["value"].median())

    str_cols = df.select_dtypes(include=["object"]).columns
    df[str_cols] = df[str_cols].apply(lambda x: x.str.strip())

    df = df.drop_duplicates()

    df["source"] = "WHO"
    df["dataset"] = dataset_name
    df["ingested_at"] = pd.Timestamp.now()

    print(f"After:  {df.shape}")
    print(f"Missing values:\n{df.isnull().sum()}")
    return df


for dataset_name, filename in FILES.items():
    raw_path = os.path.join(RAW_DIR, filename)
    df = pd.read_csv(raw_path)
    df_clean = clean_who(df, dataset_name)

    out_path = os.path.join(STAGING_DIR, f"clean_who_{dataset_name}.csv")
    df_clean.to_csv(out_path, index=False)
    print(f"Saved → {out_path}")

print("\n All WHO files cleaned and saved to staging/")