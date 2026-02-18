"""
Validators for user input and data
"""
import re
from typing import Optional
from utils.logger import get_logger

logger = get_logger(__name__)


def validate_ticker(ticker: str) -> bool:
    """
    Validate ticker symbol format

    Args:
        ticker: Stock ticker symbol

    Returns:
        True if valid, False otherwise
    """
    if not ticker:
        return False

    ticker = sanitize_ticker(ticker)

    # Basic validation: 1-5 uppercase letters
    # Can include dots for international stocks (e.g., BRK.B)
    pattern = r'^[A-Z]{1,5}(\.[A-Z])?$'

    if not re.match(pattern, ticker):
        logger.warning(f"Invalid ticker format: {ticker}")
        return False

    return True


def validate_shares(shares: float) -> bool:
    """
    Validate share quantity

    Args:
        shares: Number of shares

    Returns:
        True if valid, False otherwise
    """
    if shares <= 0:
        logger.warning(f"Invalid shares quantity: {shares}")
        return False

    return True


def validate_price(price: float) -> bool:
    """
    Validate stock price

    Args:
        price: Stock price

    Returns:
        True if valid, False otherwise
    """
    if price <= 0:
        logger.warning(f"Invalid price: {price}")
        return False

    return True


def validate_date(date_str: str) -> bool:
    """
    Validate date format (YYYY-MM-DD)

    Args:
        date_str: Date string

    Returns:
        True if valid, False otherwise
    """
    pattern = r'^\d{4}-\d{2}-\d{2}$'

    if not re.match(pattern, date_str):
        logger.warning(f"Invalid date format: {date_str} (expected YYYY-MM-DD)")
        return False

    # Further validation of actual date values
    try:
        year, month, day = map(int, date_str.split('-'))
        if not (1900 <= year <= 2100 and 1 <= month <= 12 and 1 <= day <= 31):
            logger.warning(f"Invalid date values: {date_str}")
            return False
    except ValueError:
        return False

    return True


def sanitize_ticker(ticker: str) -> str:
    """
    Sanitize ticker symbol (uppercase and strip whitespace)

    Args:
        ticker: Stock ticker symbol

    Returns:
        Sanitized ticker
    """
    return ticker.strip().upper()
