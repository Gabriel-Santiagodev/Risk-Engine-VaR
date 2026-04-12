import yfinance as yf
import pandas as pd
import requests
import os
from dotenv import load_dotenv
from datetime import datetime
from sqlalchemy import create_engine

def date_validator(start_date:str, end_date:str) -> tuple[str, str]:
    """Validate the date format
    
    This function validates if the date format is correct. All parameters must be strings.

    Args:
        start_date (str): First date to be validated. Must be in the next format: "YYYY-MM-DD".
        end_date (str): End date to be validated. Must be in the next format: "YYYY-MM-DD".

    Returns:
        tuple[str, str]: Both validated dates.

    Raises:
        ValueError: If the date format is incorrect.
    
    Examples:
        >>>date_validator("2020-01-01","2024-01-01")
        ("2020-01-01","2024-01-01")

    """

    datetime.strptime(start_date, "%Y-%m-%d")
    datetime.strptime(end_date, "%Y-%m-%d")
    return start_date, end_date
    
def data_extractor(ticker:str, start_date:str,end_date:str) -> pd.DataFrame:
    """Download a dataframe 
    
    This function downloads the historical market using for a given ticker, start date and end date.
    All parameters must be strings.

    Args:
        ticker (str): Company's ticker. (e.g, "AAPL", "MSFT").
        start_date (str): Start date of the historical market. Must be in the next format: "YYYY-MM-DD".
        end_date (str): End date of the historical market. Must be in the next format: "YYYY-MM-DD".

    Returns:
        pd.DataFrame: Historical market data.

    Raises:
        ValueError: If the ticker format or date format is incorrect.
        requests.exceptions.ConnectionError: If there is no internet connection or the server does not respond.
        requests.exceptions.Timeout: If Yahoo Finance request exceeded waiting time.
        requests.exceptions.HTTPError: If there is a HTTP error.

    Examples:
        >>>data_extractor("GOOGL","2020-01-01","2024-01-01")
        Price market_date ticker   adj_close  close_price  high_price   low_price  open_price    volume

        0      2020-01-02  GOOGL   67.873024    68.433998   68.433998   67.324501   67.420502  27278000

        1      2020-01-03  GOOGL   67.517952    68.075996   68.687500   67.365997   67.400002  23408000

        2      2020-01-06  GOOGL   69.317589    69.890503   69.916000   67.550003   67.581497  46768000

        3      2020-01-07  GOOGL   69.183701    69.755501   70.175003   69.578003   70.023003  34330000

        4      2020-01-08  GOOGL   69.676125    70.251999   70.592499   69.631500   69.740997  35314000
    
    """
    start_date, end_date = date_validator(start_date, end_date)
    try:
        data = yf.download(
            tickers=ticker,
            start=start_date,
            end=end_date,
            auto_adjust=False
        )
    except requests.exceptions.ConnectionError:
        print("Error: No internet connection or the server does not respond")
        raise
    except requests.exceptions.Timeout:
        print("Error: Yahoo Finance request exceeded waiting time")
        raise
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error {e}")
        raise
    if data.empty:
        raise ValueError(f"data from {start_date} to {end_date} not found using {ticker} ticker")
    return data

def data_to_sql(df:pd.DataFrame,table_name:str,ticker:str) -> None:
    """Connect with PostgreSQL

    This function connects data with PostgreSQL using, cleaning and transforming the dataframe 
    given by the data_extractor function.

    Args:
        df (pd.DataFrame): Historical market data.
        table_name (str): Name of the selected table to connect it with PostgreSQL.
        ticker (str): Company's ticker. (e.g, "AAPL", "MSFT").

    Returns:
        None: Returns nothing.

    Raises:
        sqlalchemy.exc.OperationalError: If the database is turned off or the password/host is incorrect.
        sqlalchemy.exc.IntegrityError: If there is an attempt to insert duplicate rows that violate the primary key constraint (e.g., same ticker and date).

    Examples:
        >>>data_to_sql(df,table_name,ticker)
        None

    """
    load_dotenv()
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")
    engine = create_engine(f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}")
    df = df.reset_index()
    df = df.droplevel('Ticker',axis=1)
    df = df.rename(columns={'Date': 'market_date','Close': 'close_price','High': 'high_price','Low': 'low_price','Open': 'open_price','Volume': 'volume','Adj Close': 'adj_close'})
    df.insert(1, 'ticker', ticker)
    df.to_sql(name=table_name, con=engine, if_exists='append',index=False)

def main():
    """
    Execute the ETL pipeline. Extracts historical data for a specific ticker and loads it into the local PostgreSQL database.
    """
    ticker = "GOOGL"
    table_name = 'historical_market_data'
    start_date = "2020-01-01"
    end_date = "2024-01-01"
    df = data_extractor(ticker,start_date,end_date)
    data_to_sql(df,table_name,ticker)

if __name__ == "__main__":
    main()


