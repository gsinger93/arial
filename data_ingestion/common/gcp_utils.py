# data_ingestion/common/gcp_utils.py

import os
import pandas as pd
from google.cloud import bigquery

def load_df_to_bigquery(df: pd.DataFrame, dataset_id: str, table_id: str):
    """
    Loads a Pandas DataFrame to a specified BigQuery table.

    Args:
        df: The DataFrame to load.
        dataset_id: The BigQuery dataset ID.
        table_id: The BigQuery table ID to create or overwrite.
    """
    project_id = os.getenv("GCP_PROJECT_ID")
    if not project_id:
        raise ValueError("GCP_PROJECT_ID environment variable not set.")

    client = bigquery.Client(project=project_id)
    table_ref = f"{project_id}.{dataset_id}.{table_id}"
    
    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_TRUNCATE",  # Overwrite the table if it exists
    )

    try:
        job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)
        job.result()  # Wait for the job to complete
        print(f"Successfully loaded {len(df)} rows to {table_ref}")
    except Exception as e:
        print(f"Error loading data to BigQuery: {e}")