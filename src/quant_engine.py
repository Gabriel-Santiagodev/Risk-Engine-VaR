import pandas as pd
from db_config import get_db_engine
from sqlalchemy.engine import Engine

def load_raw_data(table_name:str,engine:Engine) -> pd.DataFrame:
    query = f"SELECT market_date, ticker, adj_close from {table_name}"
    df = pd.read_sql_query(
        sql=query,
        con=engine
    )
    return df

def build_portfolio_matrix(df:pd.DataFrame) -> pd.DataFrame:
    pivoted_df = pd.pivot_table(
        df,
        values= 'adj_close',
        index= 'market_date',
        columns= 'ticker'
    )
    return pivoted_df

