import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logging(name: str) -> logging.Logger:
    """Configures and returns a centralized logger instance.

    This function ensures the local 'logs' directory exists and initializes a 
    logger with the specified name. It implements the Singleton pattern 
    (avoiding duplicate handlers) and attaches console and rotating file 
    handlers to maintain a persistent and formatted audit trail.

    Args:
        name (str): The name used to identify the logger (typically __name__).

    Returns:
        logging.Logger: A configured logger object.

    Raises:
        None: This function does not have raises.

    Examples:
        >>> logger = setup_logging("extractor")
        >>> logger.info("Data extraction completed successfully.")
        # Console output: 2026-05-04 14:30:00 | INFO | extractor | Data extraction completed successfully.

    """
    os.makedirs('logs',exist_ok=True)
    logger = logging.getLogger(name) 
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return logger 

    formatter = logging.Formatter( 
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    console_handler = logging.StreamHandler() 
    console_handler.setFormatter(formatter)
    file_handler = RotatingFileHandler(
        filename='logs/app.log',
        maxBytes=1048576,
        backupCount=3,
        encoding='utf-8' 
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger 
