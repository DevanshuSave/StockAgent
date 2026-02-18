"""
Stock data fetching tools using yfinance
"""
import yfinance as yf
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import pandas as pd

import config
from utils.logger import get_logger
from utils.validators import validate_ticker, sanitize_ticker

logger = get_logger(__name__)


def get_current_stock_price(ticker: str) -> Dict[str, Any]:
    """
    Fetch current stock price and trading data

    Args:
        ticker: Stock ticker symbol

    Returns:
        Dict with price, volume, market_cap, change_percent
    """
    try:
        ticker = sanitize_ticker(ticker)
        if not validate_ticker(ticker):
            return {"error": f"Invalid ticker symbol: {ticker}"}

        stock = yf.Ticker(ticker)
        info = stock.info

        # Get current price
        current_price = info.get('currentPrice') or info.get('regularMarketPrice')

        if current_price is None:
            return {"error": f"Could not fetch price data for {ticker}"}

        # Get previous close to calculate change
        previous_close = info.get('previousClose', current_price)
        change_percent = ((current_price - previous_close) / previous_close * 100) if previous_close else 0

        result = {
            "ticker": ticker,
            "price": round(current_price, 2),
            "volume": info.get('volume', 0),
            "market_cap": info.get('marketCap', 0),
            "change_percent": round(change_percent, 2),
            "previous_close": round(previous_close, 2),
            "currency": info.get('currency', 'USD')
        }

        logger.info(f"Fetched price for {ticker}: ${result['price']}")
        return result

    except Exception as e:
        logger.error(f"Error fetching price for {ticker}: {e}")
        return {"error": str(e)}


def get_stock_fundamentals(ticker: str) -> Dict[str, Any]:
    """
    Fetch stock fundamental data

    Args:
        ticker: Stock ticker symbol

    Returns:
        Dict with pe_ratio, eps, dividend_yield, sector, industry
    """
    try:
        ticker = sanitize_ticker(ticker)
        if not validate_ticker(ticker):
            return {"error": f"Invalid ticker symbol: {ticker}"}

        stock = yf.Ticker(ticker)
        info = stock.info

        result = {
            "ticker": ticker,
            "company_name": info.get('longName', ticker),
            "sector": info.get('sector', 'Unknown'),
            "industry": info.get('industry', 'Unknown'),
            "pe_ratio": info.get('trailingPE'),
            "forward_pe": info.get('forwardPE'),
            "eps": info.get('trailingEps'),
            "dividend_yield": info.get('dividendYield'),
            "market_cap": info.get('marketCap'),
            "beta": info.get('beta'),
            "52_week_high": info.get('fiftyTwoWeekHigh'),
            "52_week_low": info.get('fiftyTwoWeekLow'),
            "revenue_growth": info.get('revenueGrowth'),
            "earnings_growth": info.get('earningsGrowth'),
            "profit_margin": info.get('profitMargins'),
            "debt_to_equity": info.get('debtToEquity'),
        }

        # Clean up None values and format percentages
        for key, value in result.items():
            if value is None:
                result[key] = "N/A"
            elif key in ['dividend_yield', 'revenue_growth', 'earnings_growth', 'profit_margin']:
                if value != "N/A":
                    result[key] = round(value * 100, 2)  # Convert to percentage

        logger.info(f"Fetched fundamentals for {ticker}")
        return result

    except Exception as e:
        logger.error(f"Error fetching fundamentals for {ticker}: {e}")
        return {"error": str(e)}


def get_historical_data(ticker: str, period: str = None) -> Dict[str, Any]:
    """
    Fetch historical price data

    Args:
        ticker: Stock ticker symbol
        period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)

    Returns:
        Dict with dates, prices, and calculated returns
    """
    try:
        ticker = sanitize_ticker(ticker)
        if not validate_ticker(ticker):
            return {"error": f"Invalid ticker symbol: {ticker}"}

        if period is None:
            period = config.DEFAULT_HISTORICAL_PERIOD

        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)

        if hist.empty:
            return {"error": f"No historical data available for {ticker}"}

        # Extract data
        dates = [date.strftime('%Y-%m-%d') for date in hist.index]
        closes = hist['Close'].tolist()

        # Calculate returns
        returns_pct = []
        for i in range(1, len(closes)):
            ret = ((closes[i] - closes[i-1]) / closes[i-1]) * 100
            returns_pct.append(round(ret, 2))

        # Calculate summary statistics
        total_return = ((closes[-1] - closes[0]) / closes[0]) * 100 if len(closes) > 0 else 0
        avg_volume = hist['Volume'].mean()

        result = {
            "ticker": ticker,
            "period": period,
            "start_date": dates[0] if dates else None,
            "end_date": dates[-1] if dates else None,
            "start_price": round(closes[0], 2) if closes else None,
            "end_price": round(closes[-1], 2) if closes else None,
            "total_return_pct": round(total_return, 2),
            "avg_daily_volume": int(avg_volume),
            "data_points": len(dates),
            "dates": dates[-30:],  # Return last 30 days only to save space
            "prices": [round(p, 2) for p in closes[-30:]],
            "returns_pct": returns_pct[-30:] if returns_pct else []
        }

        logger.info(f"Fetched historical data for {ticker} ({period})")
        return result

    except Exception as e:
        logger.error(f"Error fetching historical data for {ticker}: {e}")
        return {"error": str(e)}


def get_stock_news(ticker: str, max_items: int = 5) -> Dict[str, Any]:
    """
    Fetch recent news for a stock

    Args:
        ticker: Stock ticker symbol
        max_items: Maximum number of news items to return

    Returns:
        Dict with news items
    """
    try:
        ticker = sanitize_ticker(ticker)
        if not validate_ticker(ticker):
            return {"error": f"Invalid ticker symbol: {ticker}"}

        stock = yf.Ticker(ticker)
        news = stock.news

        if not news:
            return {
                "ticker": ticker,
                "news_items": [],
                "message": "No recent news available"
            }

        # Format news items
        news_items = []
        for item in news[:max_items]:
            news_items.append({
                "title": item.get('title', 'No title'),
                "publisher": item.get('publisher', 'Unknown'),
                "link": item.get('link', ''),
                "published": datetime.fromtimestamp(item.get('providerPublishTime', 0)).strftime('%Y-%m-%d %H:%M') if item.get('providerPublishTime') else 'Unknown'
            })

        result = {
            "ticker": ticker,
            "news_count": len(news_items),
            "news_items": news_items
        }

        logger.info(f"Fetched {len(news_items)} news items for {ticker}")
        return result

    except Exception as e:
        logger.error(f"Error fetching news for {ticker}: {e}")
        return {"error": str(e)}


def get_company_info(ticker: str) -> Dict[str, Any]:
    """
    Get comprehensive company information

    Args:
        ticker: Stock ticker symbol

    Returns:
        Dict with company details
    """
    try:
        ticker = sanitize_ticker(ticker)
        if not validate_ticker(ticker):
            return {"error": f"Invalid ticker symbol: {ticker}"}

        stock = yf.Ticker(ticker)
        info = stock.info

        result = {
            "ticker": ticker,
            "company_name": info.get('longName', ticker),
            "description": info.get('longBusinessSummary', 'No description available'),
            "sector": info.get('sector', 'Unknown'),
            "industry": info.get('industry', 'Unknown'),
            "website": info.get('website', 'N/A'),
            "employees": info.get('fullTimeEmployees', 'N/A'),
            "country": info.get('country', 'N/A'),
            "city": info.get('city', 'N/A'),
        }

        logger.info(f"Fetched company info for {ticker}")
        return result

    except Exception as e:
        logger.error(f"Error fetching company info for {ticker}: {e}")
        return {"error": str(e)}
