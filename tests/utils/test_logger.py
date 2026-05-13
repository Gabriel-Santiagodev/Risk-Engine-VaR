import logging

import pytest

from src.utils.logger import setup_logging


@pytest.fixture
def clean_logger():
    """Fixture that guarantees the logger handlers are cleaned up after the test."""
    yield
    logging.getLogger("test_logger_1").handlers.clear()
    logging.getLogger("test_logger_2").handlers.clear()


def test_setup_logging_success_with_valid_logger_creation(mocker, clean_logger):
    """Tests that no exception is raised when the logger is created."""
    mock_makedirs = mocker.patch('src.utils.logger.os.makedirs')
    mock_rotating_handler = mocker.patch('src.utils.logger.RotatingFileHandler')

    logger = setup_logging("test_logger_1")

    mock_makedirs.assert_called_once_with('logs', exist_ok=True)
    assert len(logger.handlers) == 2


def test_setup_logging_success_with_valid_singleton_verification(mocker, clean_logger):
    """Tests that no exception is raised when the singleton pattern is verified."""
    mock_makedirs = mocker.patch('src.utils.logger.os.makedirs')
    mock_rotating_handler = mocker.patch('src.utils.logger.RotatingFileHandler')

    logger_first = setup_logging("test_logger_2")
    logger_second = setup_logging("test_logger_2")

    assert logger_first is logger_second
    assert len(logger_first.handlers) == 2