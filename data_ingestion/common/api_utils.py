# data_ingestion/common/api_utils.py

import os
import requests

def fetch_from_fmp() -> list:
    """
    Fetches data from a specified Financial Modeling Prep API endpoint.

    Args:
        endpoint: The API endpoint to query (e.g., 'sp500_constituent').

    Returns:
        A list of dictionaries containing the data.
    """
    api_key = os.getenv("FMP_API_KEY")
    if not api_key:
        raise ValueError("FMP_API_KEY environment variable not set.")
    
    url = f"https://financialmodelingprep.com/api/v3/stock/list?apikey={api_key}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        print(f"Successfully fetched data from stock list")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from {url}: {e}")
        return []