import pytest

from config.js_config import (
    _confidence_level_validation,
    _detect_duplicates,
    _vector_validation,
    get_js_config
)


def test_vector_validation_success_with_valid_weights():
    """Tests that no exception is raised when weights sum exactly to 1.0."""
    valid_weights = [0.5, 0.3, 0.2]
    _vector_validation(valid_weights)


def test_vector_validation_raises_with_invalid_weights():
    """Tests that a ValueError is raised when weights do not sum to 1.0."""
    invalid_weights = [0.5, 0.8, 0.2]
    with pytest.raises(ValueError) as exc_info:
        _vector_validation(invalid_weights)
    assert "Portfolio size error" in str(exc_info.value)


def test_detect_duplicates_success_with_valid_tuple_pair():
    """Tests that no exception is raised when there are no ticker duplicates."""
    valid_tuple_pair = [("AAPL", 0.5), ("MSFT", 0.5)]
    assert _detect_duplicates(valid_tuple_pair) == {"AAPL": 0.5, "MSFT": 0.5}


def test_detect_duplicates_raises_with_invalid_tuple_pair():
    """Tests that a ValueError is raised when there is a duplicated ticker."""
    invalid_tuple_pair = [("AAPL", 0.5), ("AAPL", 0.5)]
    with pytest.raises(ValueError) as exc_info:
        _detect_duplicates(invalid_tuple_pair)
    assert "Duplicate JSON key detected" in str(exc_info.value)


def test_confidence_level_validation_success_with_valid_confidence_level():
    """Tests that no exception is raised when the confidence level is between 0 and 1."""
    valid_confidence_level = 0.99
    _confidence_level_validation(valid_confidence_level)


def test_confidence_level_validation_raises_with_greater_confidence_level():
    """Tests that a ValueError is raised when the confidence level is greater than or equal to 1."""
    invalid_confidence_level = 1.5
    with pytest.raises(ValueError) as exc_info:
        _confidence_level_validation(invalid_confidence_level)
    assert "Must be strictly between 0 and 1" in str(exc_info.value)


def test_confidence_level_validation_raises_with_lower_confidence_level():
    """Tests that a ValueError is raised when the confidence level is less than or equal to 0."""
    invalid_confidence_level = 0
    with pytest.raises(ValueError) as exc_info:
        _confidence_level_validation(invalid_confidence_level)
    assert "Must be strictly between 0 and 1" in str(exc_info.value)


def test_get_js_config_raises_when_file_does_not_exist(mocker):
    """Tests that a FileNotFoundError is raised when config.json file does not exist."""
    mocker.patch('os.path.exists', return_value=False)
    with pytest.raises(FileNotFoundError) as exc_info:
        get_js_config()
    assert "does not exist." in str(exc_info.value)


def test_get_js_config_raises_when_file_cannot_be_parsed(mocker):
    """Tests that a ValueError is raised when config.json file cannot be loaded and parsed."""
    mocker.patch('os.path.exists', return_value=True)
    invalid_json_file = mocker.mock_open(read_data='Invalid Json File.')
    mocker.patch('builtins.open', invalid_json_file)
    with pytest.raises(ValueError) as exc_info:
        get_js_config()
    assert "Error decoding" in str(exc_info.value)


def test_get_js_config_returns_dict_when_file_is_valid(mocker):
    """Tests that no exception is raised and a valid dictionary is returned when the config.json file is loaded."""
    mocker.patch('os.path.exists', return_value=True)
    valid_json_file = mocker.mock_open(read_data="""{
        "weight_tickers": {"GOOGL": 0.5, "AAPL": 0.3, "MSFT": 0.2},
        "table_name": "historical_market_data",
        "start_date": "2018-01-01",
        "end_date": "2024-01-01",
        "portfolio_value": 100000,
        "confidence_level": 0.99
    }""")
    mocker.patch('builtins.open', valid_json_file)
    expected_keys = [
        "weight_tickers", "table_name", "start_date", 
        "end_date", "portfolio_value", "confidence_level", 
        "tickers_list"
    ]
    assert list(get_js_config().keys()) == expected_keys
