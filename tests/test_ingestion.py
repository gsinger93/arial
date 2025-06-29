# tests/test_ingestion.py
import pandas as pd

# IMPORTANT: import the function you want to test
from data_ingestion.ingest_shares import main as ingest_data

def test_ingestion_flow(mocker):
    """
    Tests that the ingest_data function calls the API and BigQuery client correctly.
    """
    # 1. ARRANGE: Set up our mocks.

    # Create a fake pandas DataFrame that mimics a real API response.
    fake_api_response_df = pd.DataFrame({
        '1. open': [150.0],
        '4. close': [152.5]
    })
    
    # Mock the Alpha Vantage API call.
    # We tell mocker to find the 'get_daily' method and return our fake data instead.
    mock_alpha_vantage = mocker.patch(
        'alpha_vantage.timeseries.TimeSeries.get_daily',
        return_value=(fake_api_response_df, {}) # Must return a tuple (data, meta_data)
    )

    # Mock the BigQuery Client.
    # We find the 'load_table_from_dataframe' method and replace it with a mock.
    mock_bigquery_load = mocker.patch(
        'google.cloud.bigquery.Client.load_table_from_dataframe'
    )

    # 2. ACT: Run the function we are testing.
    ingest_data()

    # 3. ASSERT: Check that our mocks were used as expected.

    # Was the Alpha Vantage API called?
    mock_alpha_vantage.assert_called_once()
    
    # Was the BigQuery load function called?
    mock_bigquery_load.assert_called_once()

    # We can even check WHAT BigQuery was asked to load.
    # This checks that the DataFrame from the API call was the one passed to BigQuery.
    first_arg_of_bq_call = mock_bigquery_load.call_args[0][0] # Gets the first argument of the call
    pd.testing.assert_frame_equal(first_arg_of_bq_call, fake_api_response_df)