"""
Portfolio management tool wrappers
"""
from typing import Dict, Any, Optional
from datetime import datetime

from portfolio.manager import PortfolioManager
from analysis.portfolio_analyzer import get_portfolio_summary
from tools.rag_tools import refresh_embeddings
from utils.logger import get_logger
from utils.validators import validate_ticker, validate_shares, validate_price, sanitize_ticker

logger = get_logger(__name__)

# Singleton portfolio manager
_portfolio_mgr = None


def get_portfolio_manager() -> PortfolioManager:
    """Get or create portfolio manager instance"""
    global _portfolio_mgr
    if _portfolio_mgr is None:
        _portfolio_mgr = PortfolioManager()
        _portfolio_mgr.load_portfolio()
    return _portfolio_mgr


def get_portfolio_summary_tool() -> Dict[str, Any]:
    """
    Get complete portfolio summary with all positions

    Returns:
        Dict with total_value, total_gain_pct, positions[]
    """
    try:
        summary = get_portfolio_summary()
        logger.info("Retrieved portfolio summary")
        return summary

    except Exception as e:
        logger.error(f"Error getting portfolio summary: {e}")
        return {"error": str(e)}


def get_position_details(ticker: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific position

    Args:
        ticker: Stock ticker symbol

    Returns:
        Dict with shares, avg_cost, gain_loss_pct, etc.
    """
    try:
        ticker = sanitize_ticker(ticker)

        if not validate_ticker(ticker):
            return {"error": f"Invalid ticker: {ticker}"}

        portfolio_mgr = get_portfolio_manager()
        position = portfolio_mgr.portfolio.get_position(ticker)

        if not position:
            return {
                "ticker": ticker,
                "exists": False,
                "message": f"No position found for {ticker}"
            }

        # Get current price
        from tools.stock_data import get_current_stock_price
        price_data = get_current_stock_price(ticker)

        if "error" in price_data:
            return {"error": price_data["error"]}

        current_price = price_data['price']

        result = {
            "ticker": ticker,
            "exists": True,
            "shares": position.shares,
            "purchase_price": position.purchase_price,
            "purchase_date": position.purchase_date,
            "current_price": current_price,
            "current_value": round(position.current_value(current_price), 2),
            "cost_basis": round(position.shares * position.purchase_price, 2),
            "gain_loss": round(position.gain_loss(current_price), 2),
            "gain_loss_pct": round(position.gain_loss_pct(current_price), 2),
            "holding_period_days": position.holding_period_days()
        }

        logger.info(f"Retrieved position details for {ticker}")
        return result

    except Exception as e:
        logger.error(f"Error getting position details for {ticker}: {e}")
        return {"error": str(e)}


def add_position_tool(ticker: str, shares: float, price: float,
                     date: Optional[str] = None) -> Dict[str, Any]:
    """
    Add a new position or update existing one

    Args:
        ticker: Stock ticker symbol
        shares: Number of shares to add
        price: Purchase price per share
        date: Purchase date (YYYY-MM-DD), defaults to today

    Returns:
        Dict with success status and updated position
    """
    try:
        ticker = sanitize_ticker(ticker)

        # Validate inputs
        if not validate_ticker(ticker):
            return {"error": f"Invalid ticker: {ticker}"}

        if not validate_shares(shares):
            return {"error": f"Invalid shares quantity: {shares}"}

        if not validate_price(price):
            return {"error": f"Invalid price: {price}"}

        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        portfolio_mgr = get_portfolio_manager()
        position = portfolio_mgr.add_position(ticker, shares, price, date)

        # Refresh embeddings
        logger.info("Refreshing portfolio embeddings after adding position")
        refresh_embeddings()

        result = {
            "success": True,
            "action": "updated" if portfolio_mgr.portfolio.has_position(ticker) else "added",
            "ticker": ticker,
            "total_shares": position.shares,
            "avg_price": position.purchase_price,
            "message": f"Successfully added {shares} shares of {ticker} @ ${price}"
        }

        logger.info(f"Added position: {ticker} {shares} shares @ ${price}")
        return result

    except Exception as e:
        logger.error(f"Error adding position {ticker}: {e}")
        return {"success": False, "error": str(e)}


def remove_position_tool(ticker: str, shares: Optional[float] = None) -> Dict[str, Any]:
    """
    Remove shares from a position or entire position

    Args:
        ticker: Stock ticker symbol
        shares: Number of shares to remove (None = remove all)

    Returns:
        Dict with success status
    """
    try:
        ticker = sanitize_ticker(ticker)

        if not validate_ticker(ticker):
            return {"error": f"Invalid ticker: {ticker}"}

        if shares is not None and not validate_shares(shares):
            return {"error": f"Invalid shares quantity: {shares}"}

        portfolio_mgr = get_portfolio_manager()

        if not portfolio_mgr.portfolio.has_position(ticker):
            return {
                "success": False,
                "error": f"No position found for {ticker}"
            }

        # Get position before removing
        position = portfolio_mgr.portfolio.get_position(ticker)
        original_shares = position.shares

        success = portfolio_mgr.remove_position(ticker, shares)

        if success:
            # Refresh embeddings
            logger.info("Refreshing portfolio embeddings after removing position")
            refresh_embeddings()

            remaining_shares = portfolio_mgr.portfolio.total_shares(ticker)

            result = {
                "success": True,
                "ticker": ticker,
                "shares_removed": shares if shares else original_shares,
                "remaining_shares": remaining_shares,
                "fully_removed": remaining_shares == 0,
                "message": f"Successfully removed {'all' if shares is None else shares} shares of {ticker}"
            }

            logger.info(f"Removed position: {ticker}")
            return result
        else:
            return {"success": False, "error": "Failed to remove position"}

    except Exception as e:
        logger.error(f"Error removing position {ticker}: {e}")
        return {"success": False, "error": str(e)}


def list_all_positions() -> Dict[str, Any]:
    """
    List all positions in portfolio

    Returns:
        Dict with list of all tickers and basic info
    """
    try:
        portfolio_mgr = get_portfolio_manager()
        portfolio = portfolio_mgr.portfolio

        if portfolio.total_positions() == 0:
            return {
                "positions": [],
                "total_positions": 0,
                "message": "Portfolio is empty"
            }

        positions = []
        for position in portfolio.positions:
            positions.append({
                "ticker": position.ticker,
                "shares": position.shares,
                "purchase_price": position.purchase_price,
                "purchase_date": position.purchase_date
            })

        result = {
            "positions": positions,
            "total_positions": len(positions),
            "tickers": [p["ticker"] for p in positions]
        }

        logger.info(f"Listed {len(positions)} positions")
        return result

    except Exception as e:
        logger.error(f"Error listing positions: {e}")
        return {"error": str(e)}
