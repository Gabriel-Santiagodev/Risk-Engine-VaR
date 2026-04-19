import pandas as pd
import numpy as np
from db_config import get_db_engine
from js_config import get_js_config
from sqlalchemy.engine import Engine
from typing import Union
from numpy.typing import NDArray

def load_raw_dataframe(table_name:str,engine:Engine) -> pd.DataFrame:
    query = f"SELECT market_date, ticker, adj_close from {table_name}"
    df = pd.read_sql_query(
        sql=query,
        con=engine
    )
    return df

def build_portfolio_matrix(df:pd.DataFrame) -> pd.DataFrame:
    portfolio_matrix = pd.pivot_table(
        df,
        values= 'adj_close',
        index= 'market_date',
        columns= 'ticker'
    )
    return portfolio_matrix.dropna()
#weight_vector:list[Union[int,float]],portfolio_value:int,confidence_level:Union[int,float]
def calculate_percentage_change(portfolio_matrix:pd.DataFrame) -> pd.DataFrame:
    return portfolio_matrix.pct_change().dropna()

def variance_covariance_matrix(percentage_change_matrix:pd.DataFrame) -> pd.DataFrame:
    return percentage_change_matrix.cov() * 252

def vector_to_array(weight_vector:list[Union[int,float]]) -> NDArray:
    return np.array(weight_vector)

def vector_validation(var_cov_matrix:pd.DataFrame,weight_array:NDArray,) -> None:
    if not len(var_cov_matrix.columns) == weight_array.shape[0]:
        raise ValueError(f"Shape of {weight_array} incompatible with variance-covariance matrix columns.")
    if not np.isclose(np.sum(weight_array),1.0):
        raise ValueError(f"Portfolio size error {weight_array}. Must be equal or near to 1.0")

def portfolio_variance(var_cov_matrix:pd.DataFrame,weight_array:NDArray) -> float:
    vector_validation(var_cov_matrix,weight_array)
    return np.dot(np.dot(weight_array,var_cov_matrix),weight_array)

def portfolio_volatility(portfolio_var:float) -> float:
    return np.sqrt(portfolio_var)

def main():
    data = get_js_config()
    engine = get_db_engine()
    table_name = data["table_name"]
    weight_vector = data["weight_vector"]
    df = load_raw_dataframe(table_name,engine)
    portfolio_matrix = build_portfolio_matrix(df)
    percentage_change_matrix = calculate_percentage_change(portfolio_matrix)
    var_cov_matrix = variance_covariance_matrix(percentage_change_matrix)
    weight_array = vector_to_array(weight_vector)
    portfolio_var = portfolio_variance(var_cov_matrix,weight_array)
    
main()
