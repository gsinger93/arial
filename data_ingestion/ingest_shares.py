import os
import logging
import pandas as pd
from dotenv import load_dotenv
from alpha_vantage.timeseries import TimeSeries
from google.cloud import bigquery
from google.api_core import exceptions
from google.oauth2 import service_account
from datetime import datetime, timezone # --- ADDED --- Import datetime for timestamps

# This line is crucial for local development. It looks for a .env file in your
# project root and loads the variables from it into the environment.
load_dotenv()

# --- Configuration ---
# Load all settings from environment variables. This makes the script portable
# and keeps secrets out of the code.
ALPHA_VANTAGE_API_KEY = os.environ.get("ALPHA_VANTAGE_API_KEY")
GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
BIGQUERY_DATASET_ID = os.environ.get("BIGQUERY_DATASET_ID", "financial_data")
BIGQUERY_TABLE_ID = os.environ.get("BIGQUERY_TABLE_ID", "raw_shares")
STOCK_SYMBOL_TO_FETCH = os.environ.get("STOCK_SYMBOL_TO_FETCH", "IBM")
GOOGLE_APPLICATION_CREDENTIALS_PATH = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

# --- Validate Configuration ---
# Fail fast if essential secrets or configurations are missing.
if not ALPHA_VANTAGE_API_KEY:
    raise ValueError("ERROR: ALPHA_VANTAGE_API_KEY is not set in the environment or .env file.")
if not GCP_PROJECT_ID:
    raise ValueError("ERROR: GCP_PROJECT_ID is not set in the environment or .env file.")
if not GOOGLE_APPLICATION_CREDENTIALS_PATH:
    raise ValueError("ERROR: GOOGLE_APPLICATION_CREDENTIALS path is not set in the environment or .env file.")


# --- Setup Logging ---
# This provides clean, informative output about the script's execution.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# --- Main Script Logic ---
def main():
    """
    The main function to orchestrate the data ingestion pipeline.
    """
    logging.info("--- Starting Share Data Ingestion Pipeline ---")
    logging.info(f"Target stock symbol: {STOCK_SYMBOL_TO_FETCH}")
    logging.info(f"Target BigQuery Project: {GCP_PROJECT_ID}")

    # 1. Fetch Data from Alpha Vantage
    try:
        logging.info("Connecting to Alpha Vantage to fetch daily share data...")
        ts = TimeSeries(key=ALPHA_VANTAGE_API_KEY, output_format='pandas')
        # We fetch 'full' to ensure we get the latest data even if the API hasn't updated 'compact'
        data, meta_data = ts.get_daily(symbol=STOCK_SYMBOL_TO_FETCH, outputsize='full')
        logging.info(f"Successfully fetched {len(data)} total data points from API.")

        # --- ADDED --- Isolate only the most recent day's data to prevent duplicates
        latest_data = data[data.index == data.index.max()].copy()
        if latest_data.empty:
            logging.warning("No new data found to load. Exiting.")
            return
        
        logging.info(f"Isolated latest data for date: {latest_data.index.max().date()}")
        
        # --- ADDED --- Add the ingestion timestamp column using a timezone-aware UTC timestamp
        latest_data['ingest_dateTime'] = datetime.now(timezone.utc)
        
        # Prepare DataFrame for BigQuery
        latest_data['symbol'] = STOCK_SYMBOL_TO_FETCH
        latest_data.reset_index(inplace=True)
        latest_data.rename(columns={'date': 'price_date',
                                '1. open': 'open',
                                '2. high': 'high',
                                '3. low': 'low',
                                '4. close': 'close',
                                '5. volume': 'volume'}, inplace=True)
        logging.info("Data prepared for loading.")

    except Exception as e:
        logging.error(f"Failed to fetch data from Alpha Vantage: {e}")
        return

    # 2. Authenticate and Load Data into BigQuery
    try:
        logging.info("Authenticating with Google Cloud using explicit credentials...")

        # This block explicitly loads credentials from the file path in your .env file.
        credentials = service_account.Credentials.from_service_account_file(GOOGLE_APPLICATION_CREDENTIALS_PATH)
        bigquery_client = bigquery.Client(project=GCP_PROJECT_ID, credentials=credentials)
        
        table_ref = f"{GCP_PROJECT_ID}.{BIGQUERY_DATASET_ID}.{BIGQUERY_TABLE_ID}"
        logging.info(f"Preparing to load data into BigQuery table: {table_ref}")

        # Configure the load job.
        job_config = bigquery.LoadJobConfig(
            # --- CHANGED --- Set to APPEND to add new rows instead of overwriting the table
            write_disposition="WRITE_APPEND",
            # We define the schema explicitly now that we have a datetime column
            schema=[
                bigquery.SchemaField("price_date", "DATE"),
                bigquery.SchemaField("open", "FLOAT64"),
                bigquery.SchemaField("high", "FLOAT64"),
                bigquery.SchemaField("low", "FLOAT64"),
                bigquery.SchemaField("close", "FLOAT64"),
                bigquery.SchemaField("volume", "INT64"),
                bigquery.SchemaField("symbol", "STRING"),
                bigquery.SchemaField("ingest_dateTime", "TIMESTAMP"),
            ],
        )

        # --- CHANGED --- Load the 'latest_data' DataFrame, not the full 'data'
        job = bigquery_client.load_table_from_dataframe(latest_data, table_ref, job_config=job_config)
        job.result()  # Wait for the job to complete.

        logging.info(f"Success! Loaded {job.output_rows} rows into {table_ref}.")

    except exceptions.NotFound as e:
        logging.error(f"BigQuery error: The dataset '{BIGQUERY_DATASET_ID}' or project might not exist. {e}")
    except Exception as e:
        logging.error(f"Failed to load data into BigQuery: {e}")
        return

    logging.info("--- Share Data Ingestion Pipeline Finished ---")

if __name__ == "__main__":
    main()