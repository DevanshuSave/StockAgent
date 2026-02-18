"""
RAG tool wrappers for agent use
"""
from typing import Dict, Any, List

from rag.retriever import PortfolioRetriever
from rag.embedder import PortfolioEmbedder
from portfolio.manager import PortfolioManager
from utils.logger import get_logger

logger = get_logger(__name__)

# Initialize retriever (singleton-like)
_retriever = None


def get_retriever() -> PortfolioRetriever:
    """Get or create retriever instance"""
    global _retriever
    if _retriever is None:
        _retriever = PortfolioRetriever()
    return _retriever


def search_portfolio_context(query: str, n_results: int = 5) -> Dict[str, Any]:
    """
    Search portfolio using semantic query

    Args:
        query: Natural language query (e.g., "tech stocks", "high growth companies")
        n_results: Maximum number of results to return

    Returns:
        Dict with relevant_positions and context_summary
    """
    try:
        retriever = get_retriever()
        result = retriever.search(query, n_results=n_results)

        logger.info(f"Portfolio search for '{query}' completed")
        return result

    except Exception as e:
        logger.error(f"Error in search_portfolio_context: {e}")
        return {
            "error": str(e),
            "relevant_positions": [],
            "context_summary": "Error during search"
        }


def get_sector_exposure(sector: str) -> Dict[str, Any]:
    """
    Get all positions in a specific sector and calculate exposure

    Args:
        sector: Sector name (e.g., "Technology", "Healthcare")

    Returns:
        Dict with positions, total value, and percentage of portfolio
    """
    try:
        retriever = get_retriever()
        result = retriever.get_by_sector(sector)

        if "error" in result:
            return result

        # Calculate sector value and percentage
        from tools.stock_data import get_current_stock_price
        from portfolio.manager import PortfolioManager

        portfolio_mgr = PortfolioManager()
        portfolio = portfolio_mgr.get_portfolio()

        sector_value = 0.0
        total_portfolio_value = 0.0

        # Calculate total portfolio value
        for position in portfolio.positions:
            price_data = get_current_stock_price(position.ticker)
            if "error" not in price_data:
                current_value = position.shares * price_data['price']
                total_portfolio_value += current_value

                # Add to sector value if in this sector
                if position.ticker in [p['ticker'] for p in result['positions']]:
                    sector_value += current_value

        sector_pct = (sector_value / total_portfolio_value * 100) if total_portfolio_value > 0 else 0

        result['sector_value'] = round(sector_value, 2)
        result['sector_pct_of_portfolio'] = round(sector_pct, 2)
        result['total_portfolio_value'] = round(total_portfolio_value, 2)

        logger.info(f"Sector exposure for {sector}: {sector_pct:.2f}%")
        return result

    except Exception as e:
        logger.error(f"Error in get_sector_exposure: {e}")
        return {"error": str(e), "positions": []}


def find_similar_holdings(ticker: str, n_results: int = 3) -> Dict[str, Any]:
    """
    Find portfolio positions similar to a given ticker

    Args:
        ticker: Stock ticker symbol
        n_results: Number of similar positions to return

    Returns:
        Dict with similar positions and similarity scores
    """
    try:
        retriever = get_retriever()
        result = retriever.find_similar_to_ticker(ticker, n_results=n_results)

        logger.info(f"Found similar holdings to {ticker}")
        return result

    except Exception as e:
        logger.error(f"Error in find_similar_holdings: {e}")
        return {"error": str(e), "similar_positions": []}


def refresh_embeddings() -> Dict[str, Any]:
    """
    Refresh all portfolio embeddings (call after portfolio changes)

    Returns:
        Dict with success status
    """
    try:
        portfolio_mgr = PortfolioManager()
        portfolio = portfolio_mgr.get_portfolio()

        embedder = PortfolioEmbedder()
        success = embedder.embed_portfolio(portfolio, include_current_data=True)

        # Reset retriever to pick up new embeddings
        global _retriever
        _retriever = None

        if success:
            return {
                "success": True,
                "message": f"Refreshed embeddings for {portfolio.total_positions()} positions"
            }
        else:
            return {
                "success": False,
                "message": "Failed to refresh embeddings"
            }

    except Exception as e:
        logger.error(f"Error refreshing embeddings: {e}")
        return {"success": False, "error": str(e)}


def get_all_sectors() -> Dict[str, Any]:
    """
    Get list of all sectors in portfolio

    Returns:
        Dict with list of sectors and their counts
    """
    try:
        portfolio_mgr = PortfolioManager()
        portfolio = portfolio_mgr.get_portfolio()

        from tools.stock_data import get_stock_fundamentals

        sectors = {}
        for position in portfolio.positions:
            fundamentals = get_stock_fundamentals(position.ticker)
            if "error" not in fundamentals:
                sector = fundamentals.get('sector', 'Unknown')
                if sector not in sectors:
                    sectors[sector] = {"count": 0, "tickers": []}
                sectors[sector]["count"] += 1
                sectors[sector]["tickers"].append(position.ticker)

        return {
            "sectors": sectors,
            "total_sectors": len(sectors)
        }

    except Exception as e:
        logger.error(f"Error getting all sectors: {e}")
        return {"error": str(e), "sectors": {}}
