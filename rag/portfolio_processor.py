"""
Convert portfolio positions to rich text documents for embedding
"""
from typing import List, Dict
from datetime import datetime

from portfolio.models import Position
from tools.stock_data import get_stock_fundamentals, get_current_stock_price, get_company_info
from utils.logger import get_logger

logger = get_logger(__name__)


def position_to_document(position: Position, include_current_data: bool = True) -> str:
    """
    Convert a portfolio position to a rich text document

    Args:
        position: Position object
        include_current_data: Whether to fetch current price and fundamentals

    Returns:
        Rich text document string
    """
    doc_parts = []

    # Basic position info
    doc_parts.append(f"Position: {position.ticker}")

    if include_current_data:
        # Fetch current data
        current_price_data = get_current_stock_price(position.ticker)
        fundamentals = get_stock_fundamentals(position.ticker)
        company_info = get_company_info(position.ticker)

        if "error" not in current_price_data and "error" not in fundamentals:
            # Company name and description
            doc_parts.append(f"Company: {fundamentals.get('company_name', position.ticker)}")

            # Sector and industry
            sector = fundamentals.get('sector', 'Unknown')
            industry = fundamentals.get('industry', 'Unknown')
            doc_parts.append(f"Sector: {sector} | Industry: {industry}")

            # Position details
            current_price = current_price_data['price']
            current_value = position.current_value(current_price)
            gain_loss_pct = position.gain_loss_pct(current_price)
            gain_loss = position.gain_loss(current_price)

            doc_parts.append(
                f"Holdings: {position.shares} shares @ ${position.purchase_price:.2f} "
                f"purchased on {position.purchase_date}"
            )
            doc_parts.append(
                f"Current Value: ${current_value:,.2f} ({position.shares} shares @ ${current_price:.2f}) | "
                f"Gain/Loss: {'+' if gain_loss >= 0 else ''}{gain_loss_pct:.2f}% (${gain_loss:,.2f})"
            )

            # Holding period
            holding_days = position.holding_period_days()
            doc_parts.append(f"Holding Period: {holding_days} days ({holding_days // 365} years, {(holding_days % 365) // 30} months)")

            # Fundamentals
            pe_ratio = fundamentals.get('pe_ratio', 'N/A')
            dividend_yield = fundamentals.get('dividend_yield', 'N/A')
            market_cap = fundamentals.get('market_cap', 'N/A')

            fundamentals_str = f"Fundamentals: P/E Ratio: {pe_ratio}"
            if dividend_yield != 'N/A':
                fundamentals_str += f" | Dividend Yield: {dividend_yield}%"
            if market_cap != 'N/A':
                market_cap_str = f"${market_cap / 1e9:.2f}B" if market_cap > 1e9 else f"${market_cap / 1e6:.2f}M"
                fundamentals_str += f" | Market Cap: {market_cap_str}"

            doc_parts.append(fundamentals_str)

            # Company description (shortened)
            if "error" not in company_info:
                description = company_info.get('description', '')
                if description and description != 'No description available':
                    # Truncate to first 200 chars
                    description = description[:200] + "..." if len(description) > 200 else description
                    doc_parts.append(f"Description: {description}")
        else:
            # Fallback if current data not available
            doc_parts.append(f"Holdings: {position.shares} shares @ ${position.purchase_price:.2f}")
            doc_parts.append(f"Purchased: {position.purchase_date}")
    else:
        # Simple version without current data
        doc_parts.append(f"Holdings: {position.shares} shares @ ${position.purchase_price:.2f}")
        doc_parts.append(f"Purchased: {position.purchase_date}")

    return "\n".join(doc_parts)


def positions_to_documents(positions: List[Position], include_current_data: bool = True) -> List[Dict[str, str]]:
    """
    Convert multiple positions to documents with metadata

    Args:
        positions: List of Position objects
        include_current_data: Whether to fetch current data for each position

    Returns:
        List of dicts with 'document', 'metadata', and 'id' keys
    """
    documents = []

    for position in positions:
        try:
            doc_text = position_to_document(position, include_current_data)

            # Create metadata
            metadata = {
                "ticker": position.ticker,
                "shares": position.shares,
                "purchase_price": position.purchase_price,
                "purchase_date": position.purchase_date,
            }

            # Add current data to metadata if available
            if include_current_data:
                fundamentals = get_stock_fundamentals(position.ticker)
                if "error" not in fundamentals:
                    metadata["sector"] = fundamentals.get("sector", "Unknown")
                    metadata["industry"] = fundamentals.get("industry", "Unknown")

            documents.append({
                "document": doc_text,
                "metadata": metadata,
                "id": f"pos_{position.ticker}"
            })

            logger.info(f"Processed position document for {position.ticker}")

        except Exception as e:
            logger.error(f"Error processing position {position.ticker}: {e}")
            continue

    return documents
