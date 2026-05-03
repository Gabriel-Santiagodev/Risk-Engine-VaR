"""Type definitions for the JSON configuration file

This module provides the static typing structures required to validate and
handle the data extracted  from the 'config.json' file across
the entire quantitative risk engine
"""

from typing import TypedDict, Any

class JsonConfig(TypedDict): 
    """Configuration dictionary structure for the VaR Quant Engine.

    This TypedDict defines the exact keys and their expected data types
    when loading the initialization parameters from the JSON file. It acts
    as a contract to prevent runtime errors caused by missing keys or 
    incorrect data types.

    Attributes:
        weight_tickers (dict[str, Any]): A dictionary mapping stock tickers (str)
            to their respective porfolio weights. The sum of all weights must equal
            1.0. (e.g., {"AAPL": 0.5, "GOOGL": 0.5}).
        table_name (str): The name of the PostgreSQL table where historical market data is stored.
        start_date (str): The starting date fot the historical market data extraction.
            Must be formatted as "YYYY-MM-DD"
        end_date (str): The ending date for the historical market data extraction.
            Must be formatted as "YYYY-MM-DD"
        portfolio_value (int): The portfolio size which means the amount of money invested in the
            entire portfolio.
        confidence_level (int | float): The statistical confidence level indicating the probability 
            that the portfolio's losses will not exceed the calculated VaR. (e.g., confidence_level": 0.99).

    """
    weight_tickers: dict[str, Any]
    table_name: str
    start_date: str
    end_date: str
    portfolio_value: int
    confidence_level: int | float