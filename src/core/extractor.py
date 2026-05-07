from datetime import datetime

import pandas as pd
import requests
from sqlalchemy import text
from sqlalchemy.engine import Engine
import yfinance as yf

from src.utils.js_type import JsonConfig
from src.utils.logger import setup_logging

logger = setup_logging(__name__)


def _date_validator(start_date: str, end_date: str) -> tuple[str, str]:
    """Validates the date format.
    
    Validates if the date format is correct. All parameters must be strings.

    Args:
        start_date (str): First date to be validated. Must be in the following format: "YYYY-MM-DD".
        end_date (str): End date to be validated. Must be in the following format: "YYYY-MM-DD".

    Returns:
        tuple[str, str]: Both validated dates.

    Raises:
        ValueError: If the date format is incorrect.
    
    Examples:
        >>> _date_validator("2020-01-01", "2024-01-01")
        ("2020-01-01", "2024-01-01")

    """
    datetime.strptime(start_date, "%Y-%m-%d")
    datetime.strptime(end_date, "%Y-%m-%d")

    return start_date, end_date


def _data_extractor(tickers: list[str], start_date: str, end_date: str) -> pd.DataFrame:
    """Extracts raw historical market data from Yahoo Finance.
    
    Extracts raw historical market data for the specified tickers tickers from Yahoo Finance 
    using a date range defined by start_date and end_date.

    Args:
        tickers (list[str]): List of company tickers. (e.g., ['AAPL', 'MSFT']).
        start_date (str): Start date of the historical market. Must be in the following format: "YYYY-MM-DD".
        end_date (str): End date of the historical market. Must be in the following format: "YYYY-MM-DD".

    Returns:
        pd.DataFrame: Historical market dataframe.

    Raises:
        ValueError: If the ticker format or date format is incorrect.
        requests.exceptions.ConnectionError: If there is no internet connection or the server does not respond.
        requests.exceptions.Timeout: If Yahoo Finance request exceeded waiting time.
        requests.exceptions.HTTPError: If there is a HTTP error.

    Examples:
        >>> _data_extractor(["GOOGL", "AAPL"], "2020-01-01", "2024-01-01")
        Price        Adj Close                   Close              ...        Open                 Volume
        Ticker            AAPL       GOOGL        AAPL       GOOGL  ...        AAPL       GOOGL       AAPL     GOOGL
        Date                                                        ...
        2020-01-02   72.400513   67.873024   75.087502   68.433998  ...   74.059998   67.420502  135480400  27278000
        2020-01-03   71.696617   67.517975   74.357498   68.075996  ...   74.287498   67.400002  146322800  23408000
        2020-01-06   72.267921   69.317604   74.949997   69.890503  ...   73.447502   67.581497  118387200  46768000

    """
    start_date, end_date = _date_validator(start_date, end_date)

    try:
        data = yf.download(
            tickers=tickers,
            start=start_date,
            end=end_date,
            auto_adjust=False
        )

    except requests.exceptions.ConnectionError as e:
        logger.error(f"No internet connection or server does not respond: {e}")
        raise

    except requests.exceptions.Timeout as e:
        logger.error(f"Yahoo Finance request exceeded waiting time: {e}")
        raise

    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error occurred while connecting to Yahoo Finance: {e}")
        raise

    if data.empty:
        logger.error(f"Data from {start_date} to {end_date} not found using {tickers} tickers.")
        raise ValueError(f"Data from {start_date} to {end_date} not found using {tickers} tickers.")
    logger.info(f"Successfully downloaded historical data for {len(tickers)} tickers.")

    return data


def _transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """Transforms raw historical market data.

    Transforms the columns' names, adds a ticker column, and resets indexes.

    Args:
        df (pd.DataFrame): Raw historical market dataframe returned by the _data_extractor function.

    Returns:
        pd.DataFrame: Transformed historical market dataframe.

    Raises:
        None: This function does not have raises.
    
    Examples:
        >>> _transform_data(df)
        Price market_date ticker   adj_close  close_price  high_price   low_price  open_price     volume
        0      2020-01-02   AAPL   72.400513    75.087502   75.150002   73.797501   74.059998  135480400
        1      2020-01-02  GOOGL   67.873024    68.433998   68.433998   67.324501   67.420502   27278000
        2      2020-01-02   MSFT  152.158386   160.619995  160.729996  158.330002  158.779999   22622100
        
    """
    df = df.stack()
    df = df.reset_index()
    df = df.rename(columns={
        'Date': 'market_date', 'Close': 'close_price', 'High': 'high_price',
        'Low': 'low_price', 'Open': 'open_price', 'Volume': 'volume',
        'Adj Close': 'adj_close', 'Ticker': 'ticker'
    })

    return df


def _data_to_sql(df: pd.DataFrame, table_name: str, engine: Engine) -> None:
    """Loads transformed historical market data to PostgreSQL.

    Loads the transformed historical market data into a PostgreSQL table.

    Args:
        df (pd.DataFrame): Transformed historical market dataframe.
        table_name (str): PostgreSQL table's name.
        engine (Engine): Connection with PostgreSQL.

    Returns:
        None: This function returns nothing.

    Raises:
        Exception: If a database error occurs during the insertion process.

    Examples:
        >>> _data_to_sql(df, 'historical_market_data', engine)

    """
    try:
        with engine.begin() as conn:
            conn.execute(text(f"TRUNCATE TABLE {table_name}"))
            df.to_sql(name=table_name, con=conn, if_exists='append', index=False)
            logger.info(f"Data successfully saved to PostgreSQL in table '{table_name}'.")
        
    except Exception:
        logger.exception("Error trying to insert data into PostgreSQL.")
        raise 


def run_etl_pipeline(data: JsonConfig, engine: Engine) -> None:
    """Executes the ETL pipeline.
    
    Extracts historical data for specific tickers, transforms the data structure,
    and loads it into the local PostgreSQL database.

    Args:
        data (JsonConfig): Json dictionary parameters.
        engine (Engine): Connection with PostgreSQL.

    Returns:
        None: This function does not have returns.

    Raises:
        None: This function does not have raises.

    """
    logger.info("Starting ETL pipeline...")
    tickers = data["tickers_list"]
    table_name = data["table_name"]
    start_date = data["start_date"]
    end_date = data["end_date"]

    df = _data_extractor(tickers, start_date, end_date)
    df = _transform_data(df)
    _data_to_sql(df, table_name, engine)

    logger.info("ETL pipeline finished executing.")