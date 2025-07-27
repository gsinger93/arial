# File: data_ingestion/ingest_shares.py

import os
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime

from data_ingestion.common.fmp_api_utils import get_historical_daily_prices
from data_ingestion.common.gcp_utils import query_bigquery, load_df_to_bigquery, run_bq_dml

def get_symbols_to_process(project_id: str, dataset_id: str, stock_table: str, symbol_table: str, limit: int) -> list:
    """
    Queries BigQuery to get a prioritised list of active symbols to ingest data for.
    """
    prioritised_query = f"""
        WITH last_update AS (
            SELECT symbol, MAX(ingest_dateTime) as last_ingested
            FROM `{project_id}.{dataset_id}.{stock_table}`
            GROUP BY symbol
        )
        SELECT m.symbol
        FROM `{project_id}.{dataset_id}.{symbol_table}` m
        LEFT JOIN last_update l ON m.symbol = l.symbol
        WHERE m.symbol IS NOT NULL AND m.is_active = TRUE
        ORDER BY l.last_ingested ASC NULLS FIRST
        LIMIT {limit}
    """
    
    try:
        print("Attempting to fetch prioritised symbols...")
        symbols_df = query_bigquery(prioritised_query)
    except Exception as e:
        print(f"Could not run prioritised query (this is expected on first run): {e}")
        print("Falling back to fetch initial symbols from master table...")
        
        fallback_query = f"""
            SELECT symbol
            FROM `{project_id}.{dataset_id}.{symbol_table}`
            WHERE symbol IS NOT NULL AND is_active = TRUE
            LIMIT {limit}
        """
        symbols_df = query_bigquery(fallback_query)

    if symbols_df is not None and not symbols_df.empty:
        return symbols_df['symbol'].tolist()
    
    return []

def main():
    """
    Main orchestrator to fetch and load prioritised share data.
    """
    load_dotenv()

    # --- Configuration ---
    project_id = os.getenv("GCP_PROJECT_ID")
    dataset_id = os.getenv("BIGQUERY_DATASET_ID", "financial_data_landing")
    stock_table_id = os.getenv("BIGQUERY_TABLE_ID", "stock_values")
    symbol_master_table_id = "symbol_master" # As per AC
    process_limit = int(os.getenv("PROCESS_LIMIT", "100")) # Configurable limit from AC

    # --- 1. Get Prioritised Symbols ---
    print(f"Getting up to {process_limit} symbols to process...")
    symbols = get_symbols_to_process(project_id, dataset_id, stock_table_id, symbol_master_table_id, process_limit)

    if not symbols:
        print("No symbols to process. Exiting.")
        return

    print(f"Symbols to process: {symbols}")

    # --- 2. Fetch Historical Data for all symbols ---
    all_historical_data = []
    for symbol in symbols:
        print(f"Fetching historical data for {symbol}...")
        historical_df = get_historical_daily_prices(symbol)
        
        if historical_df is not None and not historical_df.empty:
            all_historical_data.append(historical_df)
        else:
            print(f"Deactivating symbol {symbol} due to no data from API.")
            deactivation_query = f"""
                UPDATE `{project_id}.{dataset_id}.{symbol_master_table_id}`
                SET is_active = FALSE
                WHERE symbol = '{symbol}'
            """
            run_bq_dml(deactivation_query)

    # --- 3. Prepare and Load Data ---
    if not all_historical_data:
        print("No valid data was fetched for any symbols. Exiting.")
        return
    
    final_df = pd.concat(all_historical_data, ignore_index=True)
    
    final_df['ingest_dateTime'] = datetime.utcnow()
    
    # Rename for consistency with dbt models, if needed
    final_df.rename(columns={'date': 'price_date'}, inplace=True)

    print(f"Total of {len(final_df)} historical records fetched.")
    
    load_df_to_bigquery(
        df=final_df,
        dataset_id=dataset_id,
        table_id=stock_table_id,
        write_disposition="WRITE_APPEND" # Append data, don't overwrite!
    )

if __name__ == "__main__":
    main()