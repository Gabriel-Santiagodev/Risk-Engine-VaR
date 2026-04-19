from typing import TypedDict, Any
from typing import Union

class JsonConfig(TypedDict): 
    weight_tickers: dict[str, Any]
    table_name: str
    start_date: str
    end_date: str
    portfolio_value: int
    confidence_level: Union[int,float]