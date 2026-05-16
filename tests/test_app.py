import unittest.mock as mock

import pandas as pd
from pandas.testing import assert_frame_equal

from app import fetch_market_data

def test_fetch_market_data_success(mocker):
    """Tests that no exception is raised when the fetch_market_data wraps extraction and transformation functions."""
    mock.patch("streamlit.cache_data", lambda f: f).start()

    fake_dict = {
        "tickers_list": ["AAPL", "GOOGL", "MSFT"],
        "start_date": "2020-01-02",
        "end_date": "2021-01-02",
    }
    fake_raw_df = pd.DataFrame(fake_dict)

    expected_dictionary = {
        "market_date": {0: "2020-01-02", 1: "2020-01-02", 2: "2020-01-02"},
        "ticker": {0: "AAPL", 1: "GOOGL", 2: "MSFT"},
        "adj_close": {0: 72.400513, 1: 67.873024, 2: 152.158386},
        "close_price": {0: 75.087502, 1: 68.433998, 2: 160.619995},
        "high_price": {0: 75.150002, 1: 68.433998, 2: 160.729996},
        "low_price": {0: 73.797501, 1: 67.324501, 2: 158.330002},
        "open_price": {0: 74.059998, 1: 67.420502, 2: 158.779999},
        "volume": {0: 135480400, 1: 27278000, 2: 22622100}
    }

    fake_transformed_df = pd.DataFrame(expected_dictionary)
    fake_transformed_df['market_date'] = pd.to_datetime(fake_transformed_df['market_date'])
    fake_transformed_df.columns.name = 'Price'

    mock_extractor = mocker.patch("app._data_extractor", return_value=fake_raw_df)
    mock_transform = mocker.patch("app._transform_data", return_value=fake_transformed_df)

    result = fetch_market_data(fake_dict["tickers_list"], fake_dict["start_date"], fake_dict["end_date"])

    mock_extractor.assert_called_once_with(fake_dict["tickers_list"], fake_dict["start_date"], fake_dict["end_date"])
    mock_transform.assert_called_once_with(fake_raw_df)
    
    assert_frame_equal(result, fake_transformed_df)