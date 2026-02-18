"""
Analysis tool wrappers for agent use
"""
from typing import Dict, Any, Optional

from analysis.stock_analyzer import analyze_valuation, analyze_growth, analyze_risk, get_comprehensive_analysis
from analysis.portfolio_analyzer import calculate_portfolio_metrics, analyze_sector_exposure
from analysis.recommendation_engine import recommend_action, compare_stocks
from utils.logger import get_logger
from utils.validators import validate_ticker, sanitize_ticker

logger = get_logger(__name__)


def analyze_stock_valuation_tool(ticker: str) -> Dict[str, Any]:
    """
    Analyze stock valuation metrics

    Args:
        ticker: Stock ticker symbol

    Returns:
        Dict with valuation_summary, is_overvalued, reasoning
    """
    try:
        ticker = sanitize_ticker(ticker)

        if not validate_ticker(ticker):
            return {"error": f"Invalid ticker: {ticker}"}

        result = analyze_valuation(ticker)
        logger.info(f"Valuation analysis completed for {ticker}")
        return result

    except Exception as e:
        logger.error(f"Error in valuation analysis for {ticker}: {e}")
        return {"error": str(e)}


def analyze_stock_growth_tool(ticker: str) -> Dict[str, Any]:
    """
    Analyze stock growth metrics and momentum

    Args:
        ticker: Stock ticker symbol

    Returns:
        Dict with growth analysis
    """
    try:
        ticker = sanitize_ticker(ticker)

        if not validate_ticker(ticker):
            return {"error": f"Invalid ticker: {ticker}"}

        result = analyze_growth(ticker)
        logger.info(f"Growth analysis completed for {ticker}")
        return result

    except Exception as e:
        logger.error(f"Error in growth analysis for {ticker}: {e}")
        return {"error": str(e)}


def analyze_stock_risk_tool(ticker: str) -> Dict[str, Any]:
    """
    Analyze stock risk factors

    Args:
        ticker: Stock ticker symbol

    Returns:
        Dict with risk analysis
    """
    try:
        ticker = sanitize_ticker(ticker)

        if not validate_ticker(ticker):
            return {"error": f"Invalid ticker: {ticker}"}

        result = analyze_risk(ticker)
        logger.info(f"Risk analysis completed for {ticker}")
        return result

    except Exception as e:
        logger.error(f"Error in risk analysis for {ticker}: {e}")
        return {"error": str(e)}


def get_comprehensive_stock_analysis(ticker: str) -> Dict[str, Any]:
    """
    Get complete stock analysis (valuation, growth, risk)

    Args:
        ticker: Stock ticker symbol

    Returns:
        Dict with comprehensive analysis
    """
    try:
        ticker = sanitize_ticker(ticker)

        if not validate_ticker(ticker):
            return {"error": f"Invalid ticker: {ticker}"}

        result = get_comprehensive_analysis(ticker)
        logger.info(f"Comprehensive analysis completed for {ticker}")
        return result

    except Exception as e:
        logger.error(f"Error in comprehensive analysis for {ticker}: {e}")
        return {"error": str(e)}


def calculate_portfolio_metrics_tool() -> Dict[str, Any]:
    """
    Calculate portfolio-level metrics

    Returns:
        Dict with diversification_score, sector_allocation, etc.
    """
    try:
        result = calculate_portfolio_metrics()
        logger.info("Portfolio metrics calculated")
        return result

    except Exception as e:
        logger.error(f"Error calculating portfolio metrics: {e}")
        return {"error": str(e)}


def analyze_sector_exposure_tool(sector: str) -> Dict[str, Any]:
    """
    Analyze portfolio exposure to a specific sector

    Args:
        sector: Sector name (e.g., "Technology", "Healthcare")

    Returns:
        Dict with sector exposure details
    """
    try:
        result = analyze_sector_exposure(sector)
        logger.info(f"Sector exposure analysis completed for {sector}")
        return result

    except Exception as e:
        logger.error(f"Error analyzing sector exposure for {sector}: {e}")
        return {"error": str(e)}


def recommend_action_tool(ticker: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Generate buy/sell/hold recommendation

    Args:
        ticker: Stock ticker symbol
        context: Optional context from previous analysis or RAG

    Returns:
        Dict with action (BUY/SELL/HOLD/PASS), confidence, reasoning
    """
    try:
        ticker = sanitize_ticker(ticker)

        if not validate_ticker(ticker):
            return {"error": f"Invalid ticker: {ticker}"}

        result = recommend_action(ticker, context)
        logger.info(f"Recommendation generated for {ticker}: {result.get('action')}")
        return result

    except Exception as e:
        logger.error(f"Error generating recommendation for {ticker}: {e}")
        return {"error": str(e)}


def compare_stocks_tool(tickers: list) -> Dict[str, Any]:
    """
    Compare multiple stocks and rank them

    Args:
        tickers: List of stock ticker symbols

    Returns:
        Dict with comparison results
    """
    try:
        # Validate all tickers
        valid_tickers = []
        for ticker in tickers:
            ticker = sanitize_ticker(ticker)
            if validate_ticker(ticker):
                valid_tickers.append(ticker)

        if not valid_tickers:
            return {"error": "No valid tickers provided"}

        result = compare_stocks(valid_tickers)
        logger.info(f"Stock comparison completed for {len(valid_tickers)} stocks")
        return result

    except Exception as e:
        logger.error(f"Error comparing stocks: {e}")
        return {"error": str(e)}
