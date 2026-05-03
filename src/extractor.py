import yfinance as yf
import pandas as pd
import requests
from datetime import datetime
from sqlalchemy.engine import Engine
from js_type import JsonConfig

def tickers_list(data:JsonConfig) -> list[str]:
    """Extract the list of tickers from the configuration data (json.config)

    This function accesses the 'weight_tickers' dictionary inside the JSON configuration
    and extracts its keys to generate a list of the stock tickers to be analyzed.

    Args:
        data (JsonConfig): Json dictionary parameters.

    Returns:
        list[str]: A list containing the stock tickers (e.g., ['AAPL', 'GOOGL', 'MSFT']).

    Raises:
        KeyError: If the 'weight_tickers' key does not exist in the configuration file.
        AttributeError: If the values associated with 'weight_tickers' is not a dictionary.

    Examples:
        >>> tickers_list(data)
        ['GOOGL', 'AAPL', 'MSFT']

    """
    return list(data["weight_tickers"].keys()) 

def date_validator(start_date:str, end_date:str) -> tuple[str, str]:
    """Validate the date format.
    
    This function validates if the date format is correct. All parameters must be strings.

    Args:
        start_date (str): First date to be validated. Must be in the following format: "YYYY-MM-DD".
        end_date (str): End date to be validated. Must be in the following format: "YYYY-MM-DD".

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
    """Extract a raw dataframe  from yahoo finance.
    
    This function downloads the historical market using for a given ticker, start date and end date.
    All parameters must be strings.

    Args:
        tickers (list[str]): Companies's ticker. (e.g, "AAPL", "MSFT").
        start_date (str): Start date of the historical market. Must be in the following format: "YYYY-MM-DD".
        end_date (str): End date of the historical market. Must be in the following format: "YYYY-MM-DD".

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

def transform_data(df:pd.DataFrame) -> pd.DataFrame:
    """Transform raw dataframe.

    This functions is in charge to transform the columns name, add ticker columns and reset indexes.

    Args:
        df (pd.DataFrame): Raw historical market data dataframe downloaded given by data_extractor function.

    Returns:
        pd.DataFrame: Historical market dataframe transformed.

    Raises:
        None: This function does not have raises.
    
    Examples:
        >>>transform_data(df)
        Price market_date ticker   adj_close  close_price  high_price   low_price  open_price     volume
        0      2020-01-02   AAPL   72.400513    75.087502   75.150002   73.797501   74.059998  135480400
        1      2020-01-02  GOOGL   67.873024    68.433998   68.433998   67.324501   67.420502   27278000
        2      2020-01-02   MSFT  152.158386   160.619995  160.729996  158.330002  158.779999   22622100
        3      2020-01-03   AAPL   71.696648    74.357498   75.144997   74.125000   74.287498  146322800
        4      2020-01-03  GOOGL   67.517960    68.075996   68.687500   67.365997   67.400002   23408000
        ...           ...    ...         ...          ...         ...         ...         ...        ...
        3013   2023-12-28  GOOGL  139.080505   140.229996  141.139999  139.750000  140.779999   16045700
        3014   2023-12-28   MSFT  368.924835   375.279999  376.459991  374.160004  375.369995   14327000
        3015   2023-12-29   AAPL  190.550461   192.529999  194.399994  191.729996  193.899994   42672100
        3016   2023-12-29  GOOGL  138.544937   139.690002  140.360001  138.779999  139.630005   18733000
        3017   2023-12-29   MSFT  369.671906   376.040009  377.160004  373.480011  376.000000   18730800
        
    """
    df = df.stack()
    df = df.reset_index()
    df = df.rename(columns={'Date': 'market_date','Close': 'close_price','High': 'high_price','Low': 'low_price','Open': 'open_price','Volume': 'volume','Adj Close': 'adj_close','Ticker':'ticker'})
    return df

def data_to_sql(df:pd.DataFrame,table_name:str,engine:Engine) -> None:
    """Load historical market dataframe transformed to PostgreSQL.

    This function is in charge to load the historical market dataframe transformed given by transform_data function to postgreSQL.

    Args:
        df (pd.DataFrame): Historical market dataframe transformed.
        table_name (str): PostgreSQL table's name.
        engine (Engine): Connection with PostgreSQL.

    Returns:
        None: This function returns nothing.

    Raises:
        Exception: If a database error occurs that is not related to a UniqueViolation.

    Examples:
        >>>data_to_sql(df,'historical_market_data',engine)

    """
    try:
        df.to_sql(name=table_name, con=engine, if_exists='append',index=False)
        print("Data has been successfully saved in PostgreSQL.")
    except Exception as e:
        if "UniqueViolation" in str(e) or "llave duplicada" in str(e) or "duplicate key" in str(e):
            print("Data already exists. ETL pipeline has not been initialized thus going to run quant engine.")
        else:
            raise e

def run_etl_pipeline(data:JsonConfig,engine:Engine) -> None:
    """Executes the ETL pipeline.
    
    Extracts historical data for a specific ticker and loads it to the local PostgreSQL database.

    Args:
        data (JsonConfig): Json dictionary parameters.
        engine (Engine): Connection with PostgreSQL.

    Returns:
        None: This function does not have returns.

    Raises:
        None: This function does not have raises.

    """
    tickers = tickers_list(data)
    table_name = data["table_name"]
    start_date = data["start_date"]
    end_date = data["end_date"]
    df = data_extractor(tickers,start_date,end_date)
    df = transform_data(df)
    data_to_sql(df,table_name,engine)
    


