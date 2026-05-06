import os
import json
from typing import Any

import numpy as np

from src.utils.logger import setup_logging

logger = setup_logging(__name__)


def _detect_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Detects duplicate keys during JSON parsing.

    Detects if there is any duplicated key in the JSON configuration 
    file to prevent silent overwrites.

    Args:
        pairs (list[tuple[str, Any]]): "List of key-value tuple pairs.

    Returns:
        dict[str, Any]: Dictionary created from the parsed key-value pairs.

    Raises:
        ValueError: If there is a key duplicated.

    Examples:
        >>> _detect_duplicates([("GOOGL", 0.5), ("AAPL", 0.3), ("MSFT", 0.2)])
            {"GOOGL": 0.5, "AAPL": 0.3, "MSFT": 0.2}

    """
    seen = {}
    for key, value in pairs:
        if key in seen:
            logger.error(f"Duplicate JSON key detected: {key}")
            raise ValueError(f"Duplicate JSON key detected: {key}")
        seen[key] = value
    return seen


def _vector_validation(weights_vector: list[int | float]) -> None:
    """Validates weights vector values.

    Validates if the sum of weights from the weights vector is equal to 1.0.

    Args:
        weights_vector (list[int | float]): Weights vector.

    Returns:
        None: This function returns nothing.

    Raises:
        ValueError: If the sum of weights vector is not equal to 1.0.

    Examples:
        >>> _vector_validation([0.5, 0.6, 0.2])
        ValueError: Portfolio size error [0.6, 0.5, 0.2]. Must be equal or near to 1.0.

    """
    if not np.isclose(np.sum(weights_vector), 1.0):
        logger.error(f"Validation failed: Sum of weights {weights_vector} is {np.sum(weights_vector)}, expected 1.0.")
        raise ValueError(f"Portfolio size error {weights_vector}. Must be equal or near to 1.0")


def get_js_config() -> dict[str, Any]:
    """Loads data from the JSON configuration file.

    Loads the tickers list, table_name, start_date, end_date, weight_vector, 
    portfolio_value and confidence_level data from config.json file.

    Args:
        None: This function does not have arguments.

    Returns:
        dict[str, Any]: Dictionary with tickers list, table_name, start_date, end_date data, 
                        weight_vector, portfolio_value and confidence_level.

    Raises:
        FileNotFoundError: If the config.json file does not exist.
        ValueError: If there is an error decoding the json file.
        RuntimeError: If there is an error trying to read the json file.

    Examples:
        >>> data = get_js_config()
        >>> tickers = data["tickers_list"]
        >>> table_name = data["table_name"]
        >>> start_date = data["start_date"]
        >>> end_date = data["end_date"]
        >>> portfolio_value = data["portfolio_value"]
        >>> confidence_level = data["confidence_level"]
    
    """
    route = os.path.join(os.path.dirname(__file__), "config.json")
    if not os.path.exists(route):
        logger.error(f"Route {route} or file config.json do not exist.")
        raise FileNotFoundError(f"Route {route} or file config.json do not exist.")
    
    try:
        with open(route, "r", encoding="utf-8") as f:
            data = json.load(f, object_pairs_hook=_detect_duplicates)
            _vector_validation(list(data["weight_tickers"].values()))
            data["tickers_list"] = list(data["weight_tickers"].keys())
            logger.info("JSON configuration file successfully loaded and parsed.")
            return data
        
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding json file: {e}")
        raise ValueError(f"Error decoding json file {e}")
    
    except Exception as e:
        logger.exception(f"Unexpected error trying to read json file: {e}")
        raise RuntimeError(f"Unexpected error trying to read json file: {e}")
