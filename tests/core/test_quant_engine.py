from unittest.mock import Mock

import numpy as np
from numpy.testing import assert_array_almost_equal
import pandas as pd
from pandas.testing import assert_frame_equal, assert_series_equal
import pytest

from src.core.quant_engine import (
    _data_validation,
    _load_raw_dataframe,
    _build_portfolio_matrix,
    _calculate_percentage_change,
    _variance_covariance_matrix,
    _percentage_change_matrix_means,
    _vector_to_array,
    _calculate_portfolio_percentage_changes,
    _portfolio_variance,
    _portfolio_volatility,
    _calculate_portfolio_mean,
    _z_score_calculator,
    _parametric_var_calculator,
    _var_money_calculator,
    _weights_vector_extraction,
    _confidence_level_extraction,
    _portfolio_value_extraction,
    run_quant_engine
)


@pytest.fixture
def fake_percentages_changes_dataframe():
    fake_percentage_changes_dict = {
        "AAPL": {
            "2020-01-03": -0.009722,
            "2020-01-06": 0.007968
        },
        "GOOGL": {
            "2020-01-03": -0.005230,
            "2020-01-06": 0.026654
        },
        "MSFT": {
            "2020-01-03": -0.012451,
            "2020-01-06": 0.002584
        }
    }

    fake_percentages_changes_dataframe = pd.DataFrame(fake_percentage_changes_dict)
    fake_percentages_changes_dataframe.index = pd.to_datetime(fake_percentages_changes_dataframe.index)
    fake_percentages_changes_dataframe.index.name = 'market_date'
    fake_percentages_changes_dataframe.columns.name = 'ticker'
    return fake_percentages_changes_dataframe


def test_data_validation_success_with_valid_dataframe():
    """Tests that no exception is raised when the data is not empty."""
    fake_dataframe = pd.DataFrame({
        "id": [1, 2, 3],
        "Name": ["Ana", "Luis", "María"],
        "Age": [23, 30, 27],
        "State": [True, False, True]
    })

    _data_validation(fake_dataframe)


def test_data_validation_raises_with_invalid_dataframe():
    """Tests that a ValueError is raised when the data is empty."""
    fake_dataframe = pd.DataFrame()

    with pytest.raises(ValueError) as exc_info:
        _data_validation(fake_dataframe)
    assert "returned an empty DataFrame" in str(exc_info.value)


def test_load_raw_dataframe_success_with_valid_sql_query_execution(mocker):
    """Tests that no exception is raised when the sql query execution is successful."""
    mocker.patch('src.core.quant_engine.pd.read_sql_query')
    _load_raw_dataframe("fake_table_name", "fake_engine")


def test_load_raw_dataframe_raises_with_invalid_sql_query_execution(mocker):
    """Tests that an Exception is raised when the sql query execution failed."""
    mocker.patch('src.core.quant_engine.pd.read_sql_query', side_effect=Exception)

    with pytest.raises(Exception) as exc_info:
        _load_raw_dataframe("fake_table_name", "fake_engine")
    assert "Failed to execute SQL query" in str(exc_info.value)


def test_load_raw_dataframe_raises_with_dataframe_empty(mocker):
    """Tests that a ValueError is raised when the dataframe returned is empty."""
    mocker.patch('src.core.quant_engine.pd.read_sql_query', return_value=pd.DataFrame())

    with pytest.raises(ValueError) as exc_info:
        _load_raw_dataframe("fake_table_name", "fake_engine")
    assert "returned an empty DataFrame" in str(exc_info.value)


def test_build_portfolio_matrix_success_with_valid_pivoted_data():
    """Tests that no exception is raised when data is pivoted."""
    fake_raw_dataframe = {
        "market_date": [
            "2020-01-02", "2020-01-02", "2020-01-02",
            "2020-01-03", "2020-01-03", "2020-01-03",
            "2020-01-06", "2020-01-06", "2020-01-06"
        ],
        "ticker": [
            "AAPL", "GOOGL", "MSFT",
            "AAPL", "GOOGL", "MSFT",
            "AAPL", "GOOGL", "MSFT"
        ],
        "adj_close": [
            72.4005, 67.8730, 152.1584,
            71.6966, 67.5180, 150.2638,
            72.2679, 69.3176, 150.6521
        ]
    }

    fake_raw_dataframe = pd.DataFrame(fake_raw_dataframe)

    fake_raw_pivoted_dataframe = {
        "AAPL": {
            "2020-01-02": 72.4005,
            "2020-01-03": 71.6966,
            "2020-01-06": 72.2679
        },
        "GOOGL": {
            "2020-01-02": 67.8730,
            "2020-01-03": 67.5180,
            "2020-01-06": 69.3176
        },
        "MSFT": {
            "2020-01-02": 152.1584,
            "2020-01-03": 150.2638,
            "2020-01-06": 150.6521
        }
    }

    fake_pivoted_dataframe = pd.DataFrame(fake_raw_pivoted_dataframe)
    fake_pivoted_dataframe.index = pd.to_datetime(fake_pivoted_dataframe.index)
    fake_pivoted_dataframe.index.name = 'market_date'
    fake_pivoted_dataframe.columns.names = 'ticker'

    assert_frame_equal(_build_portfolio_matrix(fake_raw_dataframe), fake_pivoted_dataframe)


def test_calculate_percentage_change_success_with_valid_percentage_changes_calculation(fake_percentages_changes_dataframe):
    """Tests that no exception is raised when percentage changes are calculated."""
    fake_raw_pivoted_dataframe = {
        "AAPL": {
            "2020-01-02": 72.4005,
            "2020-01-03": 71.6966,
            "2020-01-06": 72.2679
        },
        "GOOGL": {
            "2020-01-02": 67.8730,
            "2020-01-03": 67.5180,
            "2020-01-06": 69.3176
        },
        "MSFT": {
            "2020-01-02": 152.1584,
            "2020-01-03": 150.2638,
            "2020-01-06": 150.6521
        }
    }

    fake_pivoted_dataframe = pd.DataFrame(fake_raw_pivoted_dataframe)
    fake_pivoted_dataframe.index = pd.to_datetime(fake_pivoted_dataframe.index)
    fake_pivoted_dataframe.index.name = 'market_date'
    fake_pivoted_dataframe.columns.names = 'ticker'

    assert_frame_equal(_calculate_percentage_change(fake_raw_pivoted_dataframe), fake_percentages_changes_dataframe)


def test_variance_covariance_matrix_success_with_valid_var_cov_matrix_creation(fake_percentages_changes_dataframe):
    """Tests that no exception is raised when the variance-covariance matrix is created."""
    fake_var_cov_matrix_dict = {
        "AAPL": {
            "AAPL": 0.000156,
            "GOOGL": 0.000282,
            "MSFT": 0.000133
        },
        "GOOGL": {
            "AAPL": 0.000282,
            "GOOGL": 0.000508,
            "MSFT": 0.000240
        },
        "MSFT": {
            "AAPL": 0.000133,
            "GOOGL": 0.000240,
            "MSFT": 0.000113
        }
    }

    fake_var_cov_matrix = pd.DataFrame(fake_var_cov_matrix_dict)

    fake_var_cov_matrix.index.name = 'ticker'
    fake_var_cov_matrix.columns.name = 'ticker'

    assert_frame_equal(_variance_covariance_matrix(fake_percentages_changes_dataframe), fake_var_cov_matrix)


def test_percentage_change_matrix_means_success_with_valid_percentage_change_means_series(fake_percentages_changes_dataframe):
    """Tests that no exception is raised when the percentage change means series is created."""
    fake_means_dict = {
        "AAPL": -0.000877,
        "GOOGL": 0.010712,
        "MSFT": -0.0049335
    }

    fake_percentage_changes_means_series = pd.Series(fake_means_dict)
    fake_percentage_changes_means_series.index.name = 'ticker'

    assert_series_equal(_percentage_change_matrix_means(fake_percentages_changes_dataframe), fake_percentage_changes_means_series)


def test_vector_to_array_success_with_valid_vector_transformation_to_array():
    """Tests that no exception is raised when a vector is transformed to an array."""
    fake_vector = ["0.3", "0.5", "0.2"]
    fake_array = np.array([0.3, 0.5, 0.2])

    assert_array_almost_equal(_vector_to_array(fake_vector), fake_array)


def test_calculate_portfolio_percentage_changes_success_with_valid_daily_percentage_changes_calculation(fake_percentages_changes_dataframe):
    """Tests that no exception is raised when the daily percentage changes are calculated."""
    fake_array = np.array([0.3, 0.5, 0.2])

    fake_percentages_changes_series = pd.Series(
    data=[-0.0080218, 0.0162342],
    index=pd.to_datetime(["2020-01-03", "2020-01-06"])
    )

    assert_series_equal(_calculate_portfolio_percentage_changes(fake_percentages_changes_dataframe, fake_array), fake_percentages_changes_series)


def test_portfolio_variance_success_with_valid_portfolio_variance_calculation():
    """Tests that no exception is raised when the portfolio variance is calculated."""
    fake_var_cov_matrix_dict = {
        "AAPL": {
            "AAPL": 0.000156,
            "GOOGL": 0.000282,
            "MSFT": 0.000133
        },
        "GOOGL": {
            "AAPL": 0.000282,
            "GOOGL": 0.000508,
            "MSFT": 0.000240
        },
        "MSFT": {
            "AAPL": 0.000133,
            "GOOGL": 0.000240,
            "MSFT": 0.000113
        }
    }

    fake_var_cov_matrix = pd.DataFrame(fake_var_cov_matrix_dict)

    fake_var_cov_matrix.index.name = 'ticker'
    fake_var_cov_matrix.columns.name = 'ticker'

    fake_array = np.array([0.3, 0.5, 0.2])

    assert _portfolio_variance(fake_var_cov_matrix, fake_array) == pytest.approx(0.00029412)


def test_portfolio_volatility_success_with_valid_portfolio_volatility_calculation():
    """Tests that no exception is raised when the portfolio volatility is calculated."""
    fake_portfolio_variance = 0.00029412
    assert _portfolio_volatility(fake_portfolio_variance) == pytest.approx(0.01714992711354673)


def test_portfolio_volatility_raises_with_invalid_portfolio_variance():
    """Tests that no exception is raised when the portfolio volatility is calculated."""
    fake_portfolio_variance = 0

    with pytest.raises(ValueError) as exc_info:
        _portfolio_volatility(fake_portfolio_variance)
    assert "Portfolio variance is zero or negative." in str(exc_info.value)


def test_calculate_portfolio_mean_success_with_valid_portfolio_mean_calculation():
    """Tests that no exception is raised when the portfolio mean is calculated."""
    fake_means_dict = {
        "AAPL": -0.000877,
        "GOOGL": 0.010712,
        "MSFT": -0.0049335
    }

    fake_percentage_changes_means_series = pd.Series(fake_means_dict)
    fake_percentage_changes_means_series.index.name = 'ticker'

    fake_array = np.array([0.3, 0.5, 0.2])

    assert _calculate_portfolio_mean(fake_percentage_changes_means_series, fake_array) == pytest.approx(0.0041062)


def test_z_score_calculator_success_with_valid_z_score_calculation():
    """Tests that no exception is raised when the z-score value is calculated."""
    fake_confidence_level = 0.99

    assert _z_score_calculator(fake_confidence_level) == pytest.approx(-2.3263)


def test_parametric_var_calculator_success_with_valid_var_calculation():
    """Tests that no exception is raised when the percentage VaR value is calculated."""
    fake_z_score = -2.3263
    fake_portfolio_mean = 0.0041062
    fake_portfolio_vol = 0.01714992711354673

    assert _parametric_var_calculator(fake_z_score, fake_portfolio_mean, fake_portfolio_vol) == pytest.approx(-0.03578967544424376)


def test_var_money_calculator_success_with_valid_var_money_calculation():
    """Tests that no exception is raised when the percentage VaR money value is calculated."""
    fake_var_value = -0.03578967544424376
    fake_portfolio_value = 100000

    assert _var_money_calculator(fake_var_value, fake_portfolio_value) == pytest.approx(3578.96754)


def test_weights_vector_extraction_with_valid_vector_extraction():
    """Tests that no exception is raised when the vector is extracted."""
    fake_config = {
        "weight_tickers": {"GOOGL": 0.5, "AAPL": 0.3, "MSFT": 0.2},
        "portfolio_value": 100000,
        "confidence_level": 0.99
    }

    fake_dataframe = pd.DataFrame(columns=["GOOGL", "AAPL", "MSFT"])

    assert _weights_vector_extraction(fake_config, fake_dataframe.columns) == [0.5, 0.3, 0.2]


def test_confidence_level_extraction_success_with_valid_confidence_level_extraction():
    """Tests that no exception is raised when the confidence level is extracted."""
    fake_config = {
        "confidence_level": 0.99
    }

    assert _confidence_level_extraction(fake_config) == 0.99


def test_portfolio_value_extraction_success_with_valid_portfolio_value_extraction():
    """Tests that no exception is raised when the portfolio value is extracted."""
    fake_config = {
        "portfolio_value": 100000
    }

    assert _portfolio_value_extraction(fake_config) == 100000


def test_run_quant_engine_success(mocker):
    """Tests that no exception is raised when run_quant_engine runs."""
    fake_config = {
    "weight_tickers": {"GOOGL": 0.4, "AAPL": 0.6},
    "table_name": "test_portfolio_table",
    "start_date": "2020-01-02",
    "end_date": "2020-01-06",
    "portfolio_value": 100000,
    "confidence_level": 0.99
    }

    fake_engine = Mock()

    mock_db_data = pd.DataFrame({
        "market_date": ["2020-01-02", "2020-01-02", "2020-01-03", "2020-01-03", "2020-01-06", "2020-01-06"],
        "ticker":      ["AAPL",       "GOOGL",      "AAPL",       "GOOGL",      "AAPL",       "GOOGL"],
        "adj_close":   [100.0,        50.0,         101.0,        51.0,         99.0,         52.0]
    })

    mock_db_data['market_date'] = pd.to_datetime(mock_db_data['market_date'])

    mocker.patch('src.core.quant_engine._load_raw_dataframe',
                return_value=mock_db_data)
    
    result = run_quant_engine(fake_config, fake_engine)

    assert isinstance(result, dict) 

    expected_keys = {
        "portfolio_percentage_changes", "var_value", "var_money", 
        "portfolio_value", "confidence_level", "portfolio_vol", "portfolio_mean"
    }

    assert set(result.keys()) == expected_keys 
    assert result["portfolio_value"] == 100000
    assert result["confidence_level"] == 0.99
    assert result["portfolio_vol"] > 0 
    assert isinstance(result["var_money"], float)