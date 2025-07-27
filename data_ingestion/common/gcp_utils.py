# File: data_ingestion/common/gcp_utils.py

import os
import pandas as pd
from google.cloud import bigquery

def query_bigquery(query: str) -> pd.DataFrame | None:
    """
    Runs a query on BigQuery and returns the result as a pandas DataFrame.
    NOTE: This function will raise an exception if the query fails.
    """
    project_id = os.getenv("GCP_PROJECT_ID")
    if not project_id:
        raise ValueError("GCP_PROJECT_ID environment variable not set.")

    client = bigquery.Client(project=project_id)
    print(f"Running query: {query}")
    query_job = client.query(query)
    results = query_job.to_dataframe()
    print(f"✅ Query successful, returned {len(results)} rows.")
    return results

def load_df_to_bigquery(df: pd.DataFrame, dataset_id: str, table_id: str, write_disposition: str = "WRITE_TRUNCATE"):
    """
    Loads a Pandas DataFrame to a specified BigQuery table with a configurable write method.
    """
    if df.empty:
        print("DataFrame is empty, skipping load to BigQuery.")
        return

    project_id = os.getenv("GCP_PROJECT_ID")
    if not project_id:
        raise ValueError("GCP_PROJECT_ID environment variable not set.")

    client = bigquery.Client(project=project_id)
    table_ref = f"{project_id}.{dataset_id}.{table_id}"
    
    job_config = bigquery.LoadJobConfig(
        create_disposition="CREATE_IF_NEEDED",
        write_disposition=write_disposition,
        autodetect=True # Let BigQuery figure out the schema
    )

    try:
        job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)
        job.result()
        print(f"✅ Successfully loaded {len(df)} rows to {table_ref} with method '{write_disposition}'.")
    except Exception as e:
        print(f"❌ Error loading data to BigQuery: {e}")

def run_bq_dml(query: str):
    """
    Runs a DML (Data Manipulation Language) statement on BigQuery (e.g., UPDATE, INSERT).
    """
    project_id = os.getenv("GCP_PROJECT_ID")
    if not project_id:
        raise ValueError("GCP_PROJECT_ID environment variable not set.")

    try:
        client = bigquery.Client(project=project_id)
        print(f"Running DML: {query}")
        query_job = client.query(query)
        query_job.result()
        print("✅ DML statement completed successfully.")
    except Exception as e:
        print(f"❌ Error running DML statement: {e}")