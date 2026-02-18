"""
Logging configuration for the Stock Agent
"""
import logging
import sys
import config


def get_logger(name: str) -> logging.Logger:
    """
    Get a configured logger instance

    Args:
        name: Logger name (typically __name__ from calling module)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Only configure if not already configured
    if not logger.handlers:
        logger.setLevel(getattr(logging, config.LOG_LEVEL))

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, config.LOG_LEVEL))

        # Formatter
        formatter = logging.Formatter(config.LOG_FORMAT)
        console_handler.setFormatter(formatter)

        logger.addHandler(console_handler)

    return logger
