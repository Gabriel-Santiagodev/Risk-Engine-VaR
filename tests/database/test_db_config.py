import pytest

from database.db_config import get_db_engine


def test_db_config_success_with_correct_engine_creation(mocker):
    """Tests that no exception is raised when the engine is created."""
    mocker.patch('database.db_config.load_dotenv')

    mocker.patch('database.db_config.os.getenv', side_effect={
        "DB_USER": "postgres",
        "DB_PASSWORD": "12345",
        "DB_HOST": "localhost",
        "DB_PORT": "4321",
        "DB_NAME": "test",
    }.get)

    fake_engine = mocker.patch('database.db_config.create_engine')

    get_db_engine()

    fake_engine.assert_called_once_with("postgresql+psycopg2://postgres:12345@localhost:4321/test")


def test_db_config_raises_with_missing_environmental_variables(mocker):
    """Tests that a ValueError is raised when one or more environmental variables are missing."""

    mocker.patch('database.db_config.load_dotenv')

    mocker.patch('database.db_config.os.getenv', side_effect={
        "DB_USER": "postgres",
        "DB_PASSWORD": "12345"   
    }.get)

    with pytest.raises(ValueError) as exc_info:
        get_db_engine()
    assert "Error trying to load environment variables" in str(exc_info.value)