import pandas as pd
import numpy as np
from scipy.stats import norm
from db_config import get_db_engine
from js_config import get_js_config
from sqlalchemy.engine import Engine
from typing import Union
from numpy.typing import NDArray
from js_type import JsonConfig

def sql_validation(df:pd.DataFrame) -> None:
    """Validate the historical market dataframe information.

    This functions validates if the historical market dataframe is empty or not.

    Args:
        df (pd.DataFrame): Raw historical market data dataframe.

    Returns:
        None: This function returns nothing.

    Raises:
        ValueError: If the the historical market dataframe is empty.

    Examples:
        >>> sql_validation(df)
        ValueError: Dataframe selected is empty.

    """
    if df.empty:
        raise ValueError("Dataframe selected is empty.")

def load_raw_dataframe(table_name:str,engine:Engine) -> pd.DataFrame:
    """Load raw data frame to make a SQL query.

    This function is in charge to load raw historical market data to select through a SQL query the market_date, ticker and adj_close columns.

    Args:
        table_name(str): PostgreSQL table's name.
        engine(Engine): Connection with PostgreSQL.

    Returns:
        pd.DataFrame: Historical market data with the selected columns.

    Raises:
        sqlalchemy.exc.OperationalError: If PostgreSQL's database is turned off or if it losses connection.
        sqlalchemy.exc.ProgrammingError: If the table_name is incorrect or it does not exist.
        ValueError: Error Inherited from sql_validation function when the dataframe is empty.

    Examples:
        >>> load_raw_dataframe(table_name,engine)
            market_date ticker  adj_close
        0     2020-01-02   AAPL    72.4005
        1     2020-01-02  GOOGL    67.8730
        2     2020-01-02   MSFT   152.1584
        3     2020-01-03   AAPL    71.6966
        4     2020-01-03  GOOGL    67.5180
        ...          ...    ...        ...
        3013  2023-12-28  GOOGL   139.0805
        3014  2023-12-28   MSFT   368.9248
        3015  2023-12-29   AAPL   190.5505
        3016  2023-12-29  GOOGL   138.5449
        3017  2023-12-29   MSFT   369.6719

    """
    query = f"SELECT market_date, ticker, adj_close from {table_name}"
    df = pd.read_sql_query(
        sql=query,
        con=engine
    )
    sql_validation(df)
    return df

def build_portfolio_matrix(df:pd.DataFrame) -> pd.DataFrame:
    """Pivot the historical market dataframe.

    This functions pivots the historical market dataframe changing from long format to wide format.

    Args:
        df (pd.DataFrame): Historical market dataframe.

    Returns:
        pd.DataFrame: Pivoted historical market dataframe.

    Raises:
        KeyError: If adj_close, marke_date or ticker column does not exist.

    Examples:
        >>> build_portfolio_matrix(df)
        ticker           AAPL     GOOGL      MSFT
        market_date                              
        2020-01-02    72.4005   67.8730  152.1584
        2020-01-03    71.6966   67.5180  150.2638
        2020-01-06    72.2679   69.3176  150.6521
        2020-01-07    71.9281   69.1837  149.2785
        2020-01-08    73.0851   69.6761  151.6563
        ...               ...       ...       ...
        2023-12-22   191.6095  140.3302  368.2366
        2023-12-26   191.0651  140.3599  368.3152
        2023-12-27   191.1641  139.2194  367.7353
        2023-12-28   191.5897  139.0805  368.9248
        2023-12-29   190.5505  138.5449  369.6719

    """
    portfolio_matrix = pd.pivot_table(
        df,
        values= 'adj_close',
        index= 'market_date',
        columns= 'ticker'
    )
    return portfolio_matrix.ffill()

def calculate_percentage_change(portfolio_matrix:pd.DataFrame) -> pd.DataFrame:
    """Calculate the percentage change in each column.

    This function calculates the percentage change price in each ticker column dropping NaN values.
    
    Args:
        portfolio_matrix (pd.DataFrame): Pivoted historical market dataframe.

    Returns:
        pd.DataFrame: Pivoted historical market dataframe with percentage changes.

    Raises:
        None: This function does not have raises.

    Examples:
        >>> calculate_percentage_change(portfolio_matrix)
        ticker           AAPL     GOOGL      MSFT
        market_date                              
        2020-01-03  -0.009722 -0.005230 -0.012451
        2020-01-06   0.007968  0.026654  0.002584
        2020-01-07  -0.004702 -0.001932 -0.009118
        2020-01-08   0.016086  0.007117  0.015929
        2020-01-09   0.021241  0.010499  0.012493
        ...               ...       ...       ...
        2023-12-22  -0.005548  0.007621  0.002784
        2023-12-26  -0.002841  0.000212  0.000213
        2023-12-27   0.000518 -0.008126 -0.001574
        2023-12-28   0.002226 -0.000998  0.003235
        2023-12-29  -0.005424 -0.003851  0.002025    
    
    """
    return portfolio_matrix.pct_change().dropna()

def variance_covariance_matrix(percentage_change_matrix:pd.DataFrame) -> pd.DataFrame:
    """Create variance-covariance matrix.

    This function transforms the pivoted historical market dataframe with percentage changes into a variance-covariance matrix.

    Args:
    percentage_change_matrix (pd.DataFrame): Pivoted historical market dataframe with percentage changes.

    Returns:
    pd.DataFrame: Variance-Covariance Matrix.

    Raises:
    None: This function does not have raises.

    Examples:
    >>> variance_covariance_matrix(percentage_change_matrix)
    ticker      AAPL     GOOGL      MSFT
    ticker                              
    AAPL    0.000447  0.000309  0.000338
    GOOGL   0.000309  0.000446  0.000335
    MSFT    0.000338  0.000335  0.000422

    """
    return percentage_change_matrix.cov() 

def weights_vector_extraction(data:JsonConfig, matrix_columns:pd.Index) -> list[Union[int,float]]:
    """Extract weights vector values.

    This functions extracts from config.json the weights of each ticker in order to create a weights vector.

    Args:
        data (JsonConfig): Json dictionary parameters.
        matrix_columns (pd.Index): Pivoted historical market dataframe columns.

    Returns:
        list[Union[int,float]]: Weights vector.

    Raises: 
        ValueError: Error Inherited from vector_validation function when the sum of the weights is not equal to 1.0.
        KeyError: If the dataframe tickers columns are different than the tickers in the weights_vector. 

    Examples:
        >>> weights_vector_extraction(data,portfolio_matrix.columns)
        [0.3, 0.5, 0.2]

    """
    weight_vector = [data["weight_tickers"][ticker]for ticker in matrix_columns]
    vector_validation(weight_vector)
    return weight_vector

def vector_to_array(weights_vector:list[Union[int,float]]) -> NDArray:
    """Transform weights vector to an array.

    This function is in charge to transform weights vector to a weights array in order to do matrices operations.

    Args:
        weight_vector (list[Union[int,float]]): Weights vector.

    Returns:
        NDArray: Weights Array.

    Raises:
        None: This function does not have raises.

    Examples:
        >>> vector_to_array(weights_vector)
        [0.3 0.5 0.2]

    """
    return np.array(weights_vector)

def calculate_portfolio_percentages_changes(percentage_change_matrix:pd.DataFrame, weight_array:NDArray) -> pd.Series:
    """Calculate the daily portfolio percentage changes.

    This function is in charge to calculate the daily portfolio percentage changes multiplying the
    daily percentage change of each ticker column times their weight.

    Args: 
        percentage_change_matrix (pd.DataFrame): Pivoted historical market dataframe with percentage changes.
        weights_array (NDArray): Weights Array.

    Returns:
        pd.Series: Daily portfolio percentage changes.

    Raises:
        ValueError: If the dimension of one of the matrices are incompatible to multiply.

    Examples:
        >>>calculate_portfolio_percentages_changes(percentage_change_matrix,weights_array)
        market_date
        2020-01-03   -0.008022
        2020-01-06    0.016234
        2020-01-07   -0.004200
        2020-01-08    0.011571
        2020-01-09    0.014120
                        ...   
        2023-12-22    0.002703
        2023-12-26   -0.000703
        2023-12-27   -0.004223
        2023-12-28    0.000816
        2023-12-29   -0.003148
        Length: 1005, dtype: float64

    """
    return percentage_change_matrix @ weight_array

def vector_validation(weights_vector:list[Union[int,float]]) -> None:
    """Validate weights vector values.

    This functions validates if the sum of weights from the weights vector is equal to 1.0.

    Args:
        weights_vector (list[Union[int,float]]): Weights vector.

    Returns:
        None: This function returns nothing.

    Raises:
        ValueError: If the sum of weights vector is not equal to 1.0.

    Examples:
        >>> vector_validation([0.5, 0.6, 0.2])
        ValueError: Portfolio size error [0.6, 0.5, 0.2]. Must be equal or near to 1.0

    """
    if not np.isclose(np.sum(weights_vector),1.0):
        raise ValueError(f"Portfolio size error {weights_vector}. Must be equal or near to 1.0")

def portfolio_variance(var_cov_matrix:pd.DataFrame,weights_array:NDArray) -> float:
    r"""Calculate portfolio variance.

    This function calculates the portfolio variance using the formula: w^T \cdot \Sigma \cdot w.

    Args:
        var_cov_matrix (pd.DataFrame): Variance-Covariance Matrix.
        weights_array (NDArray): Weights Array.

    Returns:
        float: Portfolio variance value.

    Raises:
        ValueError: If the dimension of one of the matrices are incompatible to multiply.

    Examples:
        >>> portfolio_variance(var_cov_matrix,weights_array)
        0.0003689105202275977

    """
    return weights_array @ var_cov_matrix @ weights_array

def portfolio_volatility(portfolio_var:float) -> float:
    r"""Calculate portfolio volatility.

    This function calculates portfolio volatility value using the next formula: \sigma_p = \sqrt{\sigma_p^2}.

    Args:
        portfolio_var (float): Portfolio variance value.

    Returns:
        float: Portfolio volatility value.

    Raises:
        None: This function does not have raises.

    Examples:
        >>> portfolio_volatility(portfolio_var)
        0.019207043505641303

    """
    return np.sqrt(portfolio_var)

def percentage_change_matrix_means(percentage_change_matrix:pd.DataFrame) -> pd.Series:
    """Calculate means for each ticker column.

    This function is in charge to calculate the mean of percentages changes for each ticker column.

    Args:
        percentage_change_matrix (pd.DataFrame): Pivoted historical market dataframe.

    Returns:
        pd.Series: Mean value of each ticker column.

    Raises:
        None: This function does not have raises.

    Examples:
        >>> percentage_change_matrix_means(percentage_change_matrix)
        ticker
        AAPL     0.001187
        GOOGL    0.000934
        MSFT     0.001095
        dtype: float64

    """
    return percentage_change_matrix.mean()

def calculate_portfolio_mean(percentage_change_means:pd.Series, weight_array:NDArray) -> float:
    """Calculate portfolio mean.

    This function calculates portfolio mean multiplying mean values of each ticker column times
    their weight.

    Args:
        percentage_change_means (pd.Series): Mean value of each ticker column.
        weight_array (NDArray): Weights Array.

    Returns:
        float: Portfolio mean value.

    Raises:
        ValueError: If the dimension of one of the matrices are incompatible to multiply.

    Examples:
        >>> calculate_portfolio_mean(percentage_change_means, weights_array)
        0.0010416584517025326

    """
    return percentage_change_means @ weight_array

def confidence_level_extraction(data:JsonConfig) -> Union[int, float]:
    """Extract confidence level.

    This function is in charge to extract confidence level from config.json.

    Args:
        data (JsonConfig): Json dictionary parameters.

    Returns:
        Union[int, float]: Confidence level value.

    Raises:
        KeyError: If confidence_level key does not exist.
        
    Examples:
        >>> confidence_level_extraction(data)
        0.99

    """
    return data["confidence_level"]

def z_score_calculator(confidence_level:Union[int, float]) -> float:
    """Calculate z-score value.

    This function calculates negative z-score using confidence level given from config.json.

    Args:
        confidence_level (Union[int, float]): Confidence level value.

    Returns:
        float: Negative z-score value.

    Raises:
        None: This function does not have raises.

    Examples:
        >>> z_score_calculator(confidence_level)
        -2.3263478740408408

    """
    return norm.ppf(1-confidence_level)

def parametric_var_calculator(z_score:float,portfolio_mean:float,portfolio_vol:float) -> float:
    r"""Calculate Percentage Value at Risk value.

    This function calculates through VaR formula (x = \mu + (Z \cdot \sigma_p)) the percentage VaR value.

    Args:
        z_score (float): Negative z-score value.
        porfolio_mean (float): Portfolio mean value.
        portfolio_vol (float): Portfolio volatility value.

    Returns:
        float: Percentage VaR value.

    Raises:
        None: This function does not have raises.

    Examples:
        >>> parametric_var_calculator(z_score,portfolio_mean,portfolio_vol)
        -0.043640606374256055

    """
    return portfolio_mean + (z_score * portfolio_vol)

def portfolio_value_extraction(data:JsonConfig) -> Union[float,int]:
    """Extract portfolio value.

    This function is in charge to extract portfolio value from config.json.

    Args:
        data (JsonConfig): Json dictionary parameters.

    Returns:
        Union[int, float]: Portfolio value.

    Raises:
        KeyError: If portfolio_value key does not exist.
        
    Examples:
        >>> portfolio_value_extraction(data)
        100000

    """
    return data["portfolio_value"]

def var_money_calculator(var_value:float,portfolio_value:Union[float,int]) -> float:
    """Transform VaR value to money.

    This function is in charge to transform percentage VaR value to dollar VaR multiplying it with
    portfolio value and with minus one to make the value positive.
    
    Args:
        var_value (float): Percentage VaR value.
        portfolio_value (Union[float,int]): Portfolio value.

    Returns:
        float: VaR money value.

    Raises:
        None: This function does not have raises.

    Examples:
        >>> var_money_calculator(var_value,portfolio_value)
        4364.060637425606

    """
    return var_value * portfolio_value * -1

def run_engine():
    """
    Executes the quantitative risk pipeline. It extracts historical market data from
    PostgreSQL, computes the portfolio's variance-covariance matrix, and calculates
    the 1-day parametric Value at Risk (VaR).
    """
    data = get_js_config()
    engine = get_db_engine()
    table_name = data["table_name"]
    df = load_raw_dataframe(table_name,engine)
    portfolio_matrix = build_portfolio_matrix(df)
    weights_vector = weights_vector_extraction(data,portfolio_matrix.columns)
    percentage_change_matrix = calculate_percentage_change(portfolio_matrix)
    var_cov_matrix = variance_covariance_matrix(percentage_change_matrix)
    weights_array = vector_to_array(weights_vector)
    portfolio_percentages_changes = calculate_portfolio_percentages_changes(percentage_change_matrix,weights_array)
    portfolio_var = portfolio_variance(var_cov_matrix,weights_array)
    portfolio_vol = portfolio_volatility(portfolio_var)
    percentage_change_means = percentage_change_matrix_means(percentage_change_matrix)
    portfolio_mean = calculate_portfolio_mean(percentage_change_means, weights_array)
    confidence_level = confidence_level_extraction(data)
    z_score = z_score_calculator(confidence_level)
    var_value = parametric_var_calculator(z_score,portfolio_mean,portfolio_vol)
    portfolio_value = portfolio_value_extraction(data)
    var_money = var_money_calculator(var_value,portfolio_value)
    return {
        "portfolio_percentages_changes": portfolio_percentages_changes,
        "var_value": var_value,
        "var_money": var_money,
        "portfolio_value": portfolio_value,
        "confidence_level": confidence_level,
        "portfolio_vol": portfolio_vol,
        "portfolio_mean": portfolio_mean
    }

if __name__ == "__main__":
    quant_engine_dictionary = run_engine() 
    print("Quant engine has successfully finished")
    print("================Results================")
    for key, value in quant_engine_dictionary.items():
        print(f"{key}:\n{value}\n")


