import logging
import os
import sys
from logging.handlers import RotatingFileHandler


def setup_logger(log_file_path="application.log", log_level=logging.INFO):
    """
    Set up logger to write to both file and terminal in append mode

    Args:
        log_file_path: Path where log file will be stored
        log_level: Logging level (e.g., logging.INFO, logging.DEBUG)

    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Clear any existing handlers
    logger.handlers = []

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Setup file handler (in append mode by default)
    file_handler = RotatingFileHandler(
        log_file_path,
        maxBytes=10 * 1024 * 1024,  # 10MB max file size
        backupCount=5,  # Keep 5 backup copies
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    # Setup console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # Add both handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


logger = setup_logger(log_file_path=os.getenv("LOG_FILE_PATH"))
