import os
import json
from typing import Any
from typing import Union

def get_js_config() -> dict[Union[str, Any]]:
    """Download data from json file

    This functions downloads tickers, table_name, start_date,
    end_date, weight_vector, portfolio_value and confidence_level data from config.json file

    Args:
        None: This funcionts does not have arguments.

    Returns:
        dict[str, any]: Dictionary with tickers list, table_name, start_date, end_date data, 
                        weight_vector, portfolio_value and confidence_level.

    Raises:
        ValueError: If there is an error decoding the json file.
        RuntimeError: If theres an error trying to read the json file.

    Examples:
        >>>data = json_config()
        >>>tickers = data["tickers"]
        >>>table_name = data["table_name"]
        >>>start_date = data["start_date"]
        >>>end_date = data["end_date"]
        >>>weight_vector = data["weight_vector"]
        >>>portfolio_value = data["portfolio_value"]
        >>>confidence_level = data["confidence_level"]
    
    """
    route = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "config.json")
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