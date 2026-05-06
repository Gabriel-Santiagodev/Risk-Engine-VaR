from typing import Any

import numpy as np
from numpy.typing import NDArray
import pandas as pd
from scipy.stats import norm
from sqlalchemy.engine import Engine

from src.utils.js_type import JsonConfig
from src.utils.logger import setup_logging

logger = setup_logging(__name__)


def _sql_validation(df: pd.DataFrame) -> None:
    """Validates the historical market data.

    Validates if the historical market data is empty or not.

    Args:
        df (pd.DataFrame): Raw historical market data dataframe.

    Returns:
        None: This function returns nothing.

    Raises:
        ValueError: If the historical market data is empty.

    Examples:
        >>> _sql_validation(df)
        ValueError: Dataframe selected is empty.

    """
    if df.empty:
        logger.error("Database query returned an empty DataFrame. Cannot proceed with VaR calculations.")
        raise ValueError("Dataframe selected is empty.")


def _load_raw_dataframe(table_name: str, engine: Engine) -> pd.DataFrame:
    """Executes a SQL query to load raw historical market data.

    Executes a SQL query to extract the market_date, ticker, and adj_close columns.

    Args:
        table_name(str): PostgreSQL table's name.
        engine(Engine): Connection with PostgreSQL.

    Returns:
        pd.DataFrame: Historical market data with the selected columns.

    Raises:
        Exception: If PostgreSQL's database is turned off, loses connection, or if query fails.
        ValueError: Error Inherited from sql_validation function when the dataframe is empty.

    Examples:
        >>> _load_raw_dataframe(table_name, engine)
            market_date ticker  adj_close
        0     2020-01-02   AAPL    72.4005
        1     2020-01-02  GOOGL    67.8730
        2     2020-01-02   MSFT   152.1584

    """
    query = f"SELECT market_date, ticker, adj_close FROM {table_name}"

    try:
        df = pd.read_sql_query(
            sql=query,
            con=engine
        )
    except Exception as e:
        logger.exception(f"Failed to execute SQL query on table '{table_name}': {e}")
        raise 
    
    _sql_validation(df)

    return df


def _build_portfolio_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Pivots the historical market data.

    Pivots the historical market data changing from long format to wide format.

    Args:
        df (pd.DataFrame): Historical market dataframe.

    Returns:
        pd.DataFrame: Pivoted historical market dataframe.

    Raises:
        None: This function does not have raises.

    Examples:
        >>> _build_portfolio_matrix(df)
        ticker           AAPL     GOOGL      MSFT
        market_date                              
        2020-01-02    72.4005   67.8730  152.1584
        2020-01-03    71.6966   67.5180  150.2638
        2020-01-06    72.2679   69.3176  150.6521

    """
    portfolio_matrix = pd.pivot_table(
        df,
        values='adj_close',
        index='market_date',
        columns='ticker'
    )

    return portfolio_matrix.ffill()


def _calculate_percentage_change(portfolio_matrix: pd.DataFrame) -> pd.DataFrame:
    """Calculates the percentage change in each column.

    Calculates the daily percentage change for each ticker, dropping NaN values.
    
    Args:
        portfolio_matrix (pd.DataFrame): Pivoted historical market dataframe.

    Returns:
        pd.DataFrame: Pivoted historical market dataframe with percentage changes.

    Raises:
        None: This function does not have raises.

    Examples:
        >>> _calculate_percentage_change(portfolio_matrix)
        ticker           AAPL     GOOGL      MSFT
        market_date                              
        2020-01-03  -0.009722 -0.005230 -0.012451
        2020-01-06   0.007968  0.026654  0.002584
        2020-01-07  -0.004702 -0.001932 -0.009118    
    
    """
    return portfolio_matrix.pct_change().dropna()


def _variance_covariance_matrix(percentage_change_matrix: pd.DataFrame) -> pd.DataFrame:
    """Creates variance-covariance matrix.

    Computes the variance-covariance matrix from the daily percentage changes.

    Args:
        percentage_change_matrix (pd.DataFrame): Pivoted historical market dataframe with percentage changes.

    Returns:
        pd.DataFrame: Variance-Covariance Matrix.

    Raises:
        None: This function does not have raises.

    Examples:
        >>> _variance_covariance_matrix(percentage_change_matrix)
        ticker      AAPL     GOOGL      MSFT
        ticker                              
        AAPL    0.000447  0.000309  0.000338
        GOOGL   0.000309  0.000446  0.000335
        MSFT    0.000338  0.000335  0.000422

    """
    return percentage_change_matrix.cov() 


def _weights_vector_extraction(data: JsonConfig, matrix_columns: pd.Index) -> list[int | float]:
    """Extracts weights vector values.

    Extracts from config.json the weights of each ticker in order to create a weights vector.

    Args:
        data (JsonConfig): Json dictionary parameters.
        matrix_columns (pd.Index): Pivoted historical market dataframe columns.

    Returns:
        list[int | float]: Weights vector.

    Raises: 
        None: This function does not have raises.

    Examples:
        >>> _weights_vector_extraction(data, portfolio_matrix.columns)
        [0.3, 0.5, 0.2]

    """
    weight_vector = [data["weight_tickers"][ticker] for ticker in matrix_columns]    

    return weight_vector


def _vector_to_array(weights_vector: list[int | float]) -> NDArray:
    """Transforms weights vector to an array.

    Transforms weights vector to a weights array in order to do matrices operations.

    Args:
        weights_vector (list[int | float]): Weights vector.

    Returns:
        NDArray: Weights Array.

    Raises:
        None: This function does not have raises.

    Examples:
        >>> _vector_to_array(weights_vector)
        [0.3 0.5 0.2]

    """
    return np.array(weights_vector)


def _calculate_portfolio_percentage_changes(percentage_change_matrix: pd.DataFrame, weight_array: NDArray) -> pd.Series:
    """Calculates the daily portfolio percentage changes.

    Calculates the daily portfolio percentage change by multiplying the daily 
    percentage change of each ticker by its corresponding weight.

    Args: 
        percentage_change_matrix (pd.DataFrame): Pivoted historical market dataframe with percentage changes.
        weights_array (NDArray): Weights Array.

    Returns:
        pd.Series: Daily portfolio percentage changes.

    Raises:
        ValueError: If the dimension of one of the matrices are incompatible to multiply.

    Examples:
        >>> _calculate_portfolio_percentage_changes(percentage_change_matrix, weights_array)
        market_date
        2020-01-03   -0.008022
        2020-01-06    0.016234
        2020-01-07   -0.004200
        Length: 1005, dtype: float64

    """
    return percentage_change_matrix @ weight_array


def _portfolio_variance(var_cov_matrix: pd.DataFrame, weights_array: NDArray) -> float:
    r"""Calculates portfolio variance.

    Calculates the portfolio variance using the formula: $w^T \cdot \Sigma \cdot w$.

    Args:
        var_cov_matrix (pd.DataFrame): Variance-Covariance Matrix.
        weights_array (NDArray): Weights Array.

    Returns:
        float: Portfolio variance value.

    Raises:
        ValueError: If the dimension of one of the matrices are incompatible to multiply.

    Examples:
        >>> _portfolio_variance(var_cov_matrix, weights_array)
        0.0003689105202275977

    """
    return weights_array @ var_cov_matrix @ weights_array


def _portfolio_volatility(portfolio_var: float) -> float:
    r"""Calculates portfolio volatility.

    Calculates portfolio volatility value using the following formula: $\sigma_p = \sqrt{\sigma_p^2}$.

    Args:
        portfolio_var (float): Portfolio variance value.

    Returns:
        float: Portfolio volatility value.

    Raises:
        None: This function does not have raises.

    Examples:
        >>> _portfolio_volatility(portfolio_var)
        0.019207043505641303

    """
    return np.sqrt(portfolio_var)


def _percentage_change_matrix_means(percentage_change_matrix: pd.DataFrame) -> pd.Series:
    """Calculates means for each ticker column.

    Calculates the mean of percentages changes for each ticker column.

    Args:
        percentage_change_matrix (pd.DataFrame): Pivoted historical market dataframe.

    Returns:
        pd.Series: Mean value of each ticker column.

    Raises:
        None: This function does not have raises.

    Examples:
        >>> _percentage_change_matrix_means(percentage_change_matrix)
        ticker
        AAPL     0.001187
        GOOGL    0.000934
        MSFT     0.001095
        dtype: float64

    """
    return percentage_change_matrix.mean()


def _calculate_portfolio_mean(percentage_change_means: pd.Series, weight_array: NDArray) -> float:
    """Calculates portfolio mean.

    Calculates portfolio mean multiplying mean values of each ticker column times
    their weight.

    Args:
        percentage_change_means (pd.Series): Mean value of each ticker column.
        weight_array (NDArray): Weights Array.

    Returns:
        float: Portfolio mean value.

    Raises:
        ValueError: If the dimension of one of the matrices are incompatible to multiply.

    Examples:
        >>> _calculate_portfolio_mean(percentage_change_means, weights_array)
        0.0010416584517025326

    """
    return percentage_change_means @ weight_array


def _confidence_level_extraction(data: JsonConfig) -> float | int:
    """Extracts confidence level.

    Extracts confidence level from config.json.

    Args:
        data (JsonConfig): Json dictionary parameters.

    Returns:
        float | int: Confidence level value.

    Raises:
        KeyError: If confidence_level key does not exist.
        
    Examples:
        >>> _confidence_level_extraction(data)
        0.99

    """
    return data["confidence_level"]


def _z_score_calculator(confidence_level: float | int) -> float:
    """Calculates z-score value.

    Calculates negative z-score using confidence level given from config.json.

    Args:
        confidence_level (float | int): Confidence level value.

    Returns:
        float: Negative z-score value.

    Raises:
        None: This function does not have raises.

    Examples:
        >>> _z_score_calculator(confidence_level)
        -2.3263478740408408

    """
    return norm.ppf(1 - confidence_level)


def _parametric_var_calculator(z_score: float, portfolio_mean: float, portfolio_vol: float) -> float:
    r"""Calculates Percentage Value at Risk value.

    Calculates through VaR formula ($x = \mu + (Z \cdot \sigma_p)$) the percentage VaR value.

    Args:
        z_score (float): Negative z-score value.
        portfolio_mean (float): Portfolio mean value.
        portfolio_vol (float): Portfolio volatility value.

    Returns:
        float: Percentage VaR value.

    Raises:
        None: This function does not have raises.

    Examples:
        >>> _parametric_var_calculator(z_score, portfolio_mean, portfolio_vol)
        -0.043640606374256055

    """
    return portfolio_mean + (z_score * portfolio_vol)


def _portfolio_value_extraction(data: JsonConfig) -> float | int:
    """Extracts portfolio value.

    Extracts portfolio value from config.json.

    Args:
        data (JsonConfig): Json dictionary parameters.

    Returns:
        float | int: Portfolio value.

    Raises:
        KeyError: If portfolio_value key does not exist.
        
    Examples:
        >>> _portfolio_value_extraction(data)
        100000

    """
    return data["portfolio_value"]


def _var_money_calculator(var_value: float, portfolio_value: float | int) -> float:
    """Transforms VaR value to money.

    Transforms percentage VaR value to dollar VaR multiplying it with
    portfolio value and with minus one to make the value positive.
    
    Args:
        var_value (float): Percentage VaR value.
        portfolio_value (float | int): Portfolio value.

    Returns:
        float: VaR money value.

    Raises:
        None: This function does not have raises.

    Examples:
        >>> _var_money_calculator(var_value,portfolio_value)
        4364.060637425606

    """
    return var_value * portfolio_value * -1


def run_quant_engine(data: JsonConfig, engine: Engine) -> dict[str, Any]:
    """Executes the quantitative risk pipeline. 

    It extracts historical market data from
    PostgreSQL, computes the portfolio's variance-covariance matrix, and calculates
    the 1-day parametric Value at Risk (VaR).

    Args:
        data (JsonConfig): Json dictionary parameters.
        engine (Engine): Connection with PostgreSQL.

    Returns:
        dict[str, Any]: Dictionary with the following keys portfolio_percentages_changes, 
        var_value, var_money, portfolio_value, confidence_level, portfolio_vol, portfolio_mean 
        and their values.

    Raises:
        None: This function does not have raises.
        
    """
    logger.info("Starting quantitative risk engine...")

    table_name = data["table_name"]
    df = _load_raw_dataframe(table_name, engine)
    portfolio_matrix = _build_portfolio_matrix(df)
    weights_vector = _weights_vector_extraction(data, portfolio_matrix.columns)
    percentage_change_matrix = _calculate_percentage_change(portfolio_matrix)
    var_cov_matrix = _variance_covariance_matrix(percentage_change_matrix)
    weights_array = _vector_to_array(weights_vector)
    portfolio_percentage_changes = _calculate_portfolio_percentage_changes(percentage_change_matrix, weights_array)
    portfolio_var = _portfolio_variance(var_cov_matrix, weights_array)
    portfolio_vol = _portfolio_volatility(portfolio_var)
    percentage_change_means = _percentage_change_matrix_means(percentage_change_matrix)
    portfolio_mean = _calculate_portfolio_mean(percentage_change_means, weights_array)
    confidence_level = _confidence_level_extraction(data)
    z_score = _z_score_calculator(confidence_level)
    var_value = _parametric_var_calculator(z_score, portfolio_mean, portfolio_vol)
    portfolio_value = _portfolio_value_extraction(data)
    var_money = _var_money_calculator(var_value, portfolio_value)

    logger.info(f"VaR calculation successfully completed. 1-Day VaR: ${var_money:.2f}")

    return {
        "portfolio_percentage_changes": portfolio_percentage_changes,
        "var_value": var_value,
        "var_money": var_money,
        "portfolio_value": portfolio_value,
        "confidence_level": confidence_level,
        "portfolio_vol": portfolio_vol,
        "portfolio_mean": portfolio_mean
    }
