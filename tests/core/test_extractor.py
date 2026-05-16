import pandas as pd
from pandas.testing import assert_frame_equal
import pytest
import requests

from src.core.extractor import (
    _data_extractor,
    _date_validator,
    _transform_data,
)


def test_date_validator_success_with_valid_dates():
    """Tests that no exception is raised when the date format is correct."""
    valid_start_date = "2020-01-01"
    valid_end_date = "2024-01-01"
    assert _date_validator(valid_start_date, valid_end_date) == ("2020-01-01", "2024-01-01")


def test_date_validator_raises_with_wrong_format_dates():
    """Tests that a ValueError is raised when the date format is incorrect."""
    valid_start_date = "2020-01-01"
    invalid_end_date = "01-01-2024"
    with pytest.raises(ValueError) as exc_info:
        _date_validator(valid_start_date, invalid_end_date)
    assert "does not match format" in str(exc_info.value)


def test_date_validator_raises_with_invalid_parsing():
    """Tests that a ValueError is raised when the date cannot be parsed."""
    valid_start_date = "2020-01-01"
    invalid_end_date = "2020-01-234"
    with pytest.raises(ValueError) as exc_info:
        _date_validator(valid_start_date, invalid_end_date)
    assert "unconverted" in str(exc_info.value)


def test_data_extractor_success_with_valid_dataframe(mocker):
    """Tests that no exception is raised when the data extraction is correct."""
    valid_dict = {
        "tickers_list": ["AAPL"],
        "start_date": "2018-01-01",
        "end_date": "2018-02-01",
    }
    valid_df = pd.DataFrame(valid_dict)
    mocker.patch('src.core.extractor.yf.download', return_value=valid_df)
    assert_frame_equal(_data_extractor(["AAPL"], "2018-01-01", "2018-02-01"), valid_df) 


def test_data_extractor_raises_with_connection_error(mocker):
    """Tests that a requests.exceptions.ConnectionError is raised when there is no internet connection."""
    mocker.patch('src.core.extractor.yf.download', side_effect=requests.exceptions.ConnectionError("No internet connection."))
    with pytest.raises(requests.exceptions.ConnectionError) as exc_info:
        _data_extractor(["AAPL"], "2018-01-01", "2018-02-01")
    assert "No internet connection" in str(exc_info.value)


def test_data_extractor_raises_with_empty_data(mocker):
    """Tests that a ValueError is raised when the data is empty."""
    mocker.patch('src.core.extractor.yf.download', return_value=pd.DataFrame())
    with pytest.raises(ValueError) as exc_info:
        _data_extractor(["AAPL"], "2018-01-01", "2018-02-01")
    assert "not found using" in str(exc_info.value)


def test_transform_data_success_with_valid_dataframe():
    """Tests that no exception is raised when the data to transform is correct."""
    raw_dictionary = {
        ('Adj Close', 'AAPL'):  {'2020-01-02': 72.400513},
        ('Adj Close', 'GOOGL'): {'2020-01-02': 67.873024},
        ('Adj Close', 'MSFT'):  {'2020-01-02': 152.158386},
        ('Close', 'AAPL'):      {'2020-01-02': 75.087502},
        ('Close', 'GOOGL'):     {'2020-01-02': 68.433998},
        ('Close', 'MSFT'):      {'2020-01-02': 160.619995},
        ('High', 'AAPL'):       {'2020-01-02': 75.150002},
        ('High', 'GOOGL'):      {'2020-01-02': 68.433998},
        ('High', 'MSFT'):       {'2020-01-02': 160.729996},
        ('Low', 'AAPL'):        {'2020-01-02': 73.797501},
        ('Low', 'GOOGL'):       {'2020-01-02': 67.324501},
        ('Low', 'MSFT'):        {'2020-01-02': 158.330002},
        ('Open', 'AAPL'):       {'2020-01-02': 74.059998},
        ('Open', 'GOOGL'):      {'2020-01-02': 67.420502},
        ('Open', 'MSFT'):       {'2020-01-02': 158.779999},
        ('Volume', 'AAPL'):     {'2020-01-02': 135480400},
        ('Volume', 'GOOGL'):    {'2020-01-02': 27278000},
        ('Volume', 'MSFT'):     {'2020-01-02': 22622100}
    }
    
    valid_dataframe = pd.DataFrame(raw_dictionary)
    valid_dataframe.index = pd.to_datetime(valid_dataframe.index)
    valid_dataframe.index.name = 'Date'
    valid_dataframe.columns.names = ['Price', 'Ticker']

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

    expected_dataframe = pd.DataFrame(expected_dictionary)
    expected_dataframe['market_date'] = pd.to_datetime(expected_dataframe['market_date']).dt.date
    expected_dataframe.columns.name = 'Price'

    assert_frame_equal(_transform_data(valid_dataframe), expected_dataframe)