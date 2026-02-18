"""
Portfolio analysis for diversification and sector allocation
"""
from typing import Dict, Any, List
from collections import defaultdict

import config
from portfolio.manager import PortfolioManager
from tools.stock_data import get_stock_fundamentals, get_current_stock_price
from utils.logger import get_logger

logger = get_logger(__name__)


def calculate_portfolio_metrics() -> Dict[str, Any]:
    """
    Calculate comprehensive portfolio metrics

    Returns:
        Dict with diversification score, sector allocation, etc.
    """
    try:
        portfolio_mgr = PortfolioManager()
        portfolio = portfolio_mgr.get_portfolio()

        if portfolio.total_positions() == 0:
            return {
                "error": "Portfolio is empty",
                "total_positions": 0
            }

        # Calculate sector allocation
        sector_data = defaultdict(lambda: {"value": 0.0, "positions": []})
        total_value = 0.0
        position_values = []

        for position in portfolio.positions:
            # Get current price
            price_data = get_current_stock_price(position.ticker)
            if "error" in price_data:
                continue

            current_value = position.shares * price_data['price']
            total_value += current_value
            position_values.append({
                "ticker": position.ticker,
                "value": current_value
            })

            # Get sector
            fundamentals = get_stock_fundamentals(position.ticker)
            if "error" not in fundamentals:
                sector = fundamentals.get('sector', 'Unknown')
                sector_data[sector]["value"] += current_value
                sector_data[sector]["positions"].append(position.ticker)

        # Calculate sector percentages
        sector_allocation = {}
        for sector, data in sector_data.items():
            pct = (data["value"] / total_value * 100) if total_value > 0 else 0
            sector_allocation[sector] = {
                "value": round(data["value"], 2),
                "percentage": round(pct, 2),
                "count": len(data["positions"]),
                "tickers": data["positions"]
            }

        # Sort by percentage
        sector_allocation = dict(sorted(
            sector_allocation.items(),
            key=lambda x: x[1]["percentage"],
            reverse=True
        ))

        # Calculate diversification score (0-100)
        # Based on: number of stocks, sector distribution, position concentration
        num_positions = portfolio.total_positions()
        num_sectors = len(sector_data)

        # Component 1: Number of positions (0-40 points)
        position_score = min(num_positions / config.MIN_DIVERSIFICATION_STOCKS * 40, 40)

        # Component 2: Sector distribution (0-30 points)
        sector_score = min(num_sectors / 8 * 30, 30)  # 8 major sectors

        # Component 3: Position concentration (0-30 points)
        # Lower concentration = higher score
        if total_value > 0:
            position_percentages = [(pv["value"] / total_value * 100) for pv in position_values]
            max_position_pct = max(position_percentages) if position_percentages else 100
            concentration_score = max(30 - (max_position_pct - 10) * 2, 0)  # Penalty if any position > 10%
        else:
            concentration_score = 0

        diversification_score = round(position_score + sector_score + concentration_score, 1)

        # Check for concentration risks
        concentration_risks = []
        if num_positions < 5:
            concentration_risks.append("Too few positions (< 5)")

        for sector, data in sector_allocation.items():
            if data["percentage"] > config.HIGH_SECTOR_CONCENTRATION_PCT:
                concentration_risks.append(f"{sector} sector overweight ({data['percentage']:.1f}%)")

        if total_value > 0:
            for pv in position_values:
                pct = pv["value"] / total_value * 100
                if pct > 25:
                    concentration_risks.append(f"{pv['ticker']} overweight ({pct:.1f}%)")

        result = {
            "total_value": round(total_value, 2),
            "total_positions": num_positions,
            "total_sectors": num_sectors,
            "diversification_score": diversification_score,
            "sector_allocation": sector_allocation,
            "concentration_risks": concentration_risks,
            "is_well_diversified": diversification_score >= 60 and len(concentration_risks) == 0
        }

        logger.info(f"Portfolio metrics: {num_positions} positions, diversification score {diversification_score}")
        return result

    except Exception as e:
        logger.error(f"Error calculating portfolio metrics: {e}")
        return {"error": str(e)}


def analyze_sector_exposure(sector: str) -> Dict[str, Any]:
    """
    Analyze exposure to a specific sector

    Args:
        sector: Sector name

    Returns:
        Dict with sector exposure analysis
    """
    try:
        metrics = calculate_portfolio_metrics()

        if "error" in metrics:
            return metrics

        sector_allocation = metrics.get("sector_allocation", {})

        if sector not in sector_allocation:
            return {
                "sector": sector,
                "exposure": 0.0,
                "positions": [],
                "message": f"No exposure to {sector} sector"
            }

        sector_data = sector_allocation[sector]

        # Determine if overweight
        is_overweight = sector_data["percentage"] > config.HIGH_SECTOR_CONCENTRATION_PCT

        result = {
            "sector": sector,
            "value": sector_data["value"],
            "percentage": sector_data["percentage"],
            "position_count": sector_data["count"],
            "tickers": sector_data["tickers"],
            "is_overweight": is_overweight,
            "recommendation": f"Reduce {sector} exposure" if is_overweight else f"{sector} exposure is balanced"
        }

        logger.info(f"Sector exposure for {sector}: {sector_data['percentage']:.1f}%")
        return result

    except Exception as e:
        logger.error(f"Error analyzing sector exposure for {sector}: {e}")
        return {"error": str(e)}


def get_portfolio_summary() -> Dict[str, Any]:
    """
    Get high-level portfolio summary

    Returns:
        Dict with summary statistics
    """
    try:
        portfolio_mgr = PortfolioManager()
        portfolio = portfolio_mgr.get_portfolio()

        if portfolio.total_positions() == 0:
            return {
                "total_value": 0.0,
                "total_positions": 0,
                "total_gain_loss": 0.0,
                "total_gain_loss_pct": 0.0,
                "positions": []
            }

        total_value = 0.0
        total_cost = 0.0
        position_summaries = []

        for position in portfolio.positions:
            # Get current price
            price_data = get_current_stock_price(position.ticker)
            if "error" in price_data:
                continue

            current_price = price_data['price']
            current_value = position.current_value(current_price)
            cost_basis = position.shares * position.purchase_price
            gain_loss = position.gain_loss(current_price)
            gain_loss_pct = position.gain_loss_pct(current_price)

            total_value += current_value
            total_cost += cost_basis

            # Get fundamentals for sector
            fundamentals = get_stock_fundamentals(position.ticker)
            sector = fundamentals.get('sector', 'Unknown') if "error" not in fundamentals else 'Unknown'

            position_summaries.append({
                "ticker": position.ticker,
                "shares": position.shares,
                "purchase_price": position.purchase_price,
                "current_price": current_price,
                "current_value": round(current_value, 2),
                "cost_basis": round(cost_basis, 2),
                "gain_loss": round(gain_loss, 2),
                "gain_loss_pct": round(gain_loss_pct, 2),
                "sector": sector,
                "holding_days": position.holding_period_days()
            })

        total_gain_loss = total_value - total_cost
        total_gain_loss_pct = (total_gain_loss / total_cost * 100) if total_cost > 0 else 0

        result = {
            "total_value": round(total_value, 2),
            "total_cost": round(total_cost, 2),
            "total_positions": len(position_summaries),
            "total_gain_loss": round(total_gain_loss, 2),
            "total_gain_loss_pct": round(total_gain_loss_pct, 2),
            "positions": position_summaries
        }

        logger.info(f"Portfolio summary: ${total_value:,.2f} value, {total_gain_loss_pct:+.2f}% return")
        return result

    except Exception as e:
        logger.error(f"Error getting portfolio summary: {e}")
        return {"error": str(e)}
