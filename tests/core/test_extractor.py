import pandas as pd
from pandas.testing import assert_frame_equal
import pytest
import requests

from src.core.extractor import (
    _data_extractor,
    _data_to_sql,
    _date_validator,
    _transform_data,
    run_etl_pipeline
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
    expected_dataframe['market_date'] = pd.to_datetime(expected_dataframe['market_date'])
    expected_dataframe.columns.names = ['Price']

    assert_frame_equal(_transform_data(valid_dataframe), expected_dataframe)


def test_data_to_sql_success_with_data_load(mocker):
    """Tests that data is successfully loaded to SQL without exceptions."""
    fake_dataframe = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
    fake_engine = mocker.MagicMock()

    mock_to_sql = mocker.patch('pandas.DataFrame.to_sql')
    _data_to_sql(fake_dataframe, "fake_table", fake_engine)

    fake_engine.begin.assert_called_once()
    mock_to_sql.assert_called_once()


def test_data_to_sql_raises_with_database_error(mocker):
    """Tests that an Exception is raised when the data cannot be inserted into PostgreSQL."""
    fake_dataframe = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
    fake_engine = mocker.MagicMock()

    fake_engine.begin.side_effect = Exception("Error trying to insert data into PostgreSQL.")
    with pytest.raises(Exception) as exc_info:
        _data_to_sql(fake_dataframe, "fake_table", fake_engine)
    assert "Error trying to insert data into PostgreSQL." in str(exc_info.value)


def test_run_etl_pipeline_success_with_correct_orchestration(mocker):
    """Tests that the orchestrator behavior is correct when it runs."""
    fake_dictionary = {
        "tickers_list": ["AAPL", "MSFT"],
        "table_name": "fake_table",
        "start_date": "2018-01-01",
        "end_date": "2018-02-01",
    }

    fake_raw_dataframe = "fake_raw_df"
    fake_transformed_dataframe = "fake_transformed_df"

    fake_engine = mocker.MagicMock()

    mock_extractor = mocker.patch(
        'src.core.extractor._data_extractor', 
        return_value=fake_raw_dataframe
    )
    mock_transform = mocker.patch(
        'src.core.extractor._transform_data', 
        return_value=fake_transformed_dataframe
    )
    mock_sql = mocker.patch('src.core.extractor._data_to_sql')

    run_etl_pipeline(fake_dictionary, fake_engine)

    mock_extractor.assert_called_once_with(["AAPL", "MSFT"], "2018-01-01", "2018-02-01")
    mock_transform.assert_called_once_with(fake_raw_dataframe)
    mock_sql.assert_called_once_with(fake_transformed_dataframe, "fake_table", fake_engine)