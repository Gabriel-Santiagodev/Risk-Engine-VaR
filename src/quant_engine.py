import pandas as pd
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

def sql_connection(table_name:str):
    load_dotenv()
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")
    engine = create_engine(f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}")
    query = f"SELECT market_date, ticker, adj_close from {table_name}"
    df = pd.read_sql_query(
        sql=query,
        con=engine
    )
    pivot = pd.pivot_table(
        df,
        values= 'adj_close',
        index= 'market_date',
        columns= 'ticker'
    )