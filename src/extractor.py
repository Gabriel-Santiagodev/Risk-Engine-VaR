import yfinance as yf
import pandas as pd
import requests
import os
import json
from dotenv import load_dotenv
from datetime import datetime
from sqlalchemy import create_engine
from typing import Any

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
    
def data_extractor(tickers:list[str], start_date:str,end_date:str) -> pd.DataFrame:
    """Download a dataframe 
    
    This function downloads the historical market using for a given ticker, start date and end date.
    All parameters must be strings.

    Args:
        tickers (list[str]): Companies's ticker. (e.g, "AAPL", "MSFT").
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
        >>>data_extractor(["GOOGL","AAPL"],"2020-01-01","2024-01-01")
        Price        Adj Close                   Close              ...        Open                 Volume
        Ticker            AAPL       GOOGL        AAPL       GOOGL  ...        AAPL       GOOGL       AAPL     GOOGL
        Date                                                        ...
        2020-01-02   72.400513   67.873024   75.087502   68.433998  ...   74.059998   67.420502  135480400  27278000
        2020-01-03   71.696617   67.517975   74.357498   68.075996  ...   74.287498   67.400002  146322800  23408000
        2020-01-06   72.267921   69.317604   74.949997   69.890503  ...   73.447502   67.581497  118387200  46768000
        2020-01-07   71.928062   69.183693   74.597504   69.755501  ...   74.959999   70.023003  108872000  34330000
        2020-01-08   73.085098   69.676125   75.797501   70.251999  ...   74.290001   69.740997  132079200  35314000
        ...                ...         ...         ...         ...  ...         ...         ...        ...       ...
        2023-12-22  191.609451  140.330170  193.600006  141.490005  ...  195.179993  140.770004   37149600  26532200
        2023-12-26  191.065125  140.359940  193.050003  141.520004  ...  193.610001  141.589996   28919300  16780300
        2023-12-27  191.164108  139.219376  193.149994  140.369995  ...  192.490005  141.589996   48087700  19628600
        2023-12-28  191.589691  139.080505  193.580002  140.229996  ...  194.139999  140.779999   34049900  16045700
        2023-12-29  190.550476  138.544922  192.529999  139.690002  ...  193.899994  139.630005   42672100  18733000

    """
    start_date, end_date = date_validator(start_date, end_date)
    try:
        data = yf.download(
            tickers=tickers,
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
        raise ValueError(f"data from {start_date} to {end_date} not found using {tickers} tickers")
    return data

def data_to_sql(df:pd.DataFrame,table_name:str) -> None:
    """Connect with PostgreSQL

    This function connects data with PostgreSQL using, cleaning and transforming the dataframe 
    given by the data_extractor function.

    Args:
        df (pd.DataFrame): Historical market data.
        table_name (str): Name of the selected table to connect it with PostgreSQL.

    Returns:
        None: Returns nothing.

    Raises:
        sqlalchemy.exc.OperationalError: If the database is turned off or the password/host is incorrect.
        sqlalchemy.exc.IntegrityError: If there is an attempt to insert duplicate rows that violate the primary key constraint (e.g., same ticker and date).

    Examples:
        >>>data_to_sql(df,table_name)
        None

    """
    load_dotenv()
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")
    engine = create_engine(f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}")
    df = df.stack()
    df = df.reset_index()
    df = df.rename(columns={'Date': 'market_date','Close': 'close_price','High': 'high_price','Low': 'low_price','Open': 'open_price','Volume': 'volume','Adj Close': 'adj_close','Ticker':'ticker'})
    df.to_sql(name=table_name, con=engine, if_exists='append',index=False)

def json_config() -> dict[str, Any]:
    """Download data from json file

    This functions downloads tickers, table_name, start_date and end_date data from config.json file

    Args:
        None: This funcionts does not have arguments.

    Returns:
        dict[str, any]: Dictionary with tickers list, table_name, start_date and end_date data.

    Raises:
        ValueError: If there is an error decoding the json file.
        RuntimeError: If theres an error trying to read the json file.

    Examples:
    
    """
    route = "config/config.json"
    if not os.path.exists(route):
        raise FileNotFoundError(f"Route {route} or file config.json do not exist.")
    try:
        with open(route,"r",encoding="utf-8") as f:
            data = json.load(f)
            return data
    except json.JSONDecodeError as e:
        raise ValueError(f"Error decoding json file {e}")
    except Exception as e:
        raise RuntimeError(f"Error trying to read json file {e}")

def main():
    """
    Execute the ETL pipeline. Extracts historical data for a specific ticker and loads it into the local PostgreSQL database.
    """
    data = json_config()
    tickers = data["tickers"]
    table_name = data["table_name"]
    start_date = data["start_date"]
    end_date = data["end_date"]
    df = data_extractor(tickers,start_date,end_date)
    data_to_sql(df,table_name)
    
if __name__ == "__main__":
    main()


