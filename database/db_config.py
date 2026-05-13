import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from src.utils.logger import setup_logging

logger = setup_logging(__name__)


def get_db_engine() -> Engine:
    """Creates and returns a SQLAlchemy engine for PostgreSQL connection.

    Loads environment variables from a .env file to configure 
    and instantiate a SQLAlchemy engine. Note that the engine is created lazily; 
    the actual connection is established when the first query is executed.

    Args:
        None: This function does not take any arguments.

    Returns:
        Engine: The configured SQLAlchemy Engine object.

    Raises:
        ValueError: If one or more required environment variables are missing.

    Examples:
        >>> engine = get_db_engine()

    """
    load_dotenv()
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")

    if not all((db_user, db_password, db_host, db_port, db_name)):
        logger.error("Missing one or more required database environment variables.")
        raise ValueError("Error trying to load environment variables. Verify if all the variables exist in the .env file.")

    engine = create_engine(f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}")
    logger.info(f"Database engine successfully created for host: {db_host}, db: {db_name}")

    return engine