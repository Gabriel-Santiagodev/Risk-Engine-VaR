import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

def get_db_engine() -> Engine:
    """Connect with PostgreSQL.

    This function is in charge to connect through an engine with PostgreSQL.

    Args:
        None: This functions does not have arguments.

    Returns:
        Engine: Connection with PostgreSQL.

    Raises:
        ValueError: If one of the environment variables does not exist.

    Examples:
        >>>engine = get_db_engine()
    
    """
    load_dotenv()
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")

    if not all([db_user,db_password,db_host,db_port,db_name]):
        raise ValueError("Error trying to load environment variables. Verify if all the variables exist in .env file")

    engine = create_engine(f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}")
    return engine