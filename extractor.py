import yfinance as yf
import pandas as pd
import requests
from datetime import datetime

def date_validator(start_date:str, end_date:str) -> tuple[str, str]:
    """Validate the date format
    
    This function validates if the date format is correct. All parameters must be strings.

    Args:
        start_date (str): First date to be validated. Must be in the next format: "YYYY-MM-DD"
        end_date (str): End date to be validated. Must be in the next format: "YYYY-MM-DD"

    Returns:
        tuple[str, str]: Both validated dates.

    Raises:
        ValueError: If the date format is incorrect.
    
    Examples:
        >>>>date_validator("2020-01-01","2024-01-01")

    """

    datetime.strptime(start_date, "%Y-%m-%d")
    datetime.strptime(end_date, "%Y-%m-%d")
    return start_date, end_date
    
def data_extractor(ticker:str, start_date:str,end_date:str) -> pd.DataFrame:
    """Download a dataframe 
    
    This function downloads the historical market using for a given ticker, start date and end date.
    All parameters must be strings.

    Args:
        ticker (str): Company's ticker. (e.g, "AAPL", "MSFT")
        start_date (str): Start date of the historical market. Must be in the next format: "YYYY-MM-DD"
        end_date (str): End date of the historical market. Must be in the next format: "YYYY-MM-DD"

    Returns:
        pd.Dataframe: Historical market data.

    Raises:
        ValueError: If the ticker format or date format is incorrect.
        requests.exceptions.ConnectionError: If there is no internet connection or the server does not respond.
        requests.exceptions.Timeout: If Yahoo Finance request exceeded waiting time.
        requests.exceptions.HTTPError: If there is a HTTP error.

    Examples:
        >>>>data_extractor("GOOGL","2020-01-01","2024-01-01")
    
    """
    start_date, end_date = date_validator(start_date, end_date)
    try:
        data = yf.download(
            tickers=ticker,
            start=start_date,
            end=end_date
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

if __name__ == "__main__":
    print(data_extractor("GOOGL","2020-01-01","2024-01-01"))
