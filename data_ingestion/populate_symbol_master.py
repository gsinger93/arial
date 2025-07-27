# data_ingestion/populate_symbol_master.py

import pandas as pd
from dotenv import load_dotenv
from data_ingestion.common.fmp_api_utils import fetch_from_fmp
from common.gcp_utils import load_df_to_bigquery

load_dotenv()

def main():
    """Main function to fetch symbol lists and load them to BigQuery."""

    endpoints_to_fetch = {
        'Stock list': 'Stock list'
    }
    
    successful_dfs = []  # A list to hold DataFrames from successful API calls

    print("--- Starting Symbol Ingestion ---")

    for endpoint, index_name in endpoints_to_fetch.items():
        print(f"Fetching data for: {index_name}...")
        constituent_list = fetch_from_fmp()
        print(constituent_list)
        
        # Check if the API call was successful and returned data
        if constituent_list and isinstance(constituent_list, list):
            df = pd.DataFrame(constituent_list)
            # Ensure the dataframe isn't empty after creation
            if not df.empty:
                df['index'] = index_name
                successful_dfs.append(df)
                print(f"Successfully processed {len(df)} symbols for {index_name}.")
            else:
                print(f"Data for {index_name} was empty.")
        else:
            print(f"Could not retrieve valid data for {index_name}.")

    # Proceed only if we successfully fetched data from at least one endpoint
    if successful_dfs:
        # Combine all the successful dataframes into one
        all_symbols_df = pd.concat(successful_dfs, ignore_index=True)
        
        print(f"\nTotal symbols to load: {len(all_symbols_df)}")

        # Check that the combined data has the columns we need before trying to use them
        required_cols = {'symbol', 'name', 'exchangeShortName'}
        if not required_cols.issubset(all_symbols_df.columns):
            print("Error: The fetched data is missing required columns ('symbol', 'name', 'exchangeShortName'). Cannot proceed.")
            return

        final_df = all_symbols_df[['symbol', 'name', 'exchangeShortName', 'index']].rename(
            columns={'exchangeShortName': 'exchange'}
        )
        
        # Load the final combined data to BigQuery
        dataset_name = 'financial_data_landing'
        table_name = 'symbol_master'
        load_df_to_bigquery(final_df, dataset_name, table_name)
    else:
        print("\nNo data was successfully fetched from any endpoint. BigQuery not updated.")

    print("\n--- Symbol Ingestion Finished ---")


if __name__ == "__main__":
    main()