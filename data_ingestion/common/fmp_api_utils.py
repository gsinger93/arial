# data_ingestion/common/api_utils.py

import os
import requests
import pandas as pd
from dotenv import load_dotenv

def _make_fmp_request(endpoint: str) -> list | None:
    """
    Internal helper function to make a request to a specified FMP API endpoint.
    """
    load_dotenv()
    api_key = os.getenv("FMP_API_KEY")
    ca_bundle = os.getenv("REQUESTS_CA_BUNDLE")

    if not api_key:
        raise ValueError("FMP_API_KEY environment variable not set.")

    base_url = "https://financialmodelingprep.com/api/v3/"
    url = f"{base_url}{endpoint}?apikey={api_key}"
    
    try:
        response = requests.get(url, verify=ca_bundle)
        response.raise_for_status()  # This will raise an HTTPError for 4xx/5xx responses
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        # Check if the error is specifically due to hitting the rate limit
        if http_err.response.status_code == 429:
            print("❌ API rate limit reached. Halting process.")
            raise  # Re-raise the exception to stop the script
        else:
            print(f"An HTTP error occurred: {http_err}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"An unknown error occurred while fetching data from FMP API ({url}): {e}")
        return None

def get_historical_daily_prices(symbol: str) -> pd.DataFrame | None:
    """
    Fetches the full daily historical price data for a given stock symbol.

    Args:
        symbol: The stock symbol to fetch (e.g., "AAPL").

    Returns:
        A pandas DataFrame containing the historical data, or None if the request fails.
    """
    response_data = _make_fmp_request(f"historical-price-full/{symbol}")
    
    if response_data and 'historical' in response_data:
        # The data is nested under the 'historical' key
        df = pd.DataFrame(response_data['historical'])
        # Add the symbol to each row for easy identification later
        df['symbol'] = response_data.get('symbol', symbol)
        return df
        
    print(f"No historical data found for symbol: {symbol}")
    return None

def fetch_all_tradable_symbols() -> list | None:
    """
    Fetches a list of all tradable symbols from the FMP API.
    """
    data = _make_fmp_request("stock/list")
    if data:
        print(f"Successfully fetched {len(data)} symbols from stock list.")
    return data