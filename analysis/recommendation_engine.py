"""
Recommendation engine for buy/sell/hold decisions
"""
from typing import Dict, Any, Optional

from analysis.stock_analyzer import get_comprehensive_analysis
from analysis.portfolio_analyzer import calculate_portfolio_metrics, analyze_sector_exposure
from portfolio.manager import PortfolioManager
from utils.logger import get_logger

logger = get_logger(__name__)


def recommend_action(ticker: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Generate buy/sell/hold recommendation based on analysis and portfolio context

    Args:
        ticker: Stock ticker symbol
        context: Optional context from RAG or user query

    Returns:
        Dict with action, confidence, and detailed reasoning
    """
    try:
        # Get comprehensive stock analysis
        analysis = get_comprehensive_analysis(ticker)

        if "error" in analysis:
            return {"error": analysis["error"]}

        # Get portfolio context
        portfolio_mgr = PortfolioManager()
        portfolio = portfolio_mgr.get_portfolio()
        has_position = portfolio.has_position(ticker)

        portfolio_metrics = calculate_portfolio_metrics()

        # Extract key factors
        valuation = analysis["valuation"]
        growth = analysis["growth"]
        risk = analysis["risk"]
        sector = analysis["sector"]

        # Decision factors
        factors = []
        positive_signals = 0
        negative_signals = 0

        # Factor 1: Valuation
        if valuation["is_overvalued"]:
            negative_signals += 1
            factors.append(f"❌ Overvalued: {valuation['summary']}")
        elif valuation["is_overvalued"] is False:
            positive_signals += 1
            factors.append(f"✓ Fair/Value pricing: {valuation['summary']}")

        # Factor 2: Growth
        growth_category = growth["category"]
        if growth_category in ["High Growth", "Moderate Growth"]:
            positive_signals += 1
            factors.append(f"✓ {growth_category}: {growth.get('revenue_growth', 'N/A')}% revenue growth")
        elif growth_category == "Declining":
            negative_signals += 1
            factors.append(f"❌ Declining revenues")

        # Factor 3: Momentum
        momentum = growth.get("momentum", "")
        if "Strong positive" in momentum or "Positive momentum" in momentum:
            positive_signals += 1
            factors.append(f"✓ {momentum}")
        elif "Negative" in momentum:
            negative_signals += 1
            factors.append(f"❌ {momentum}")

        # Factor 4: Risk
        overall_risk = risk["overall"]
        if overall_risk == "High risk":
            negative_signals += 1
            factors.append(f"❌ High risk: {', '.join(risk['factors'])}")
        elif overall_risk == "Low risk":
            positive_signals += 1
            factors.append(f"✓ Low risk profile")

        # Factor 5: Portfolio context
        if "error" not in portfolio_metrics:
            sector_allocation = portfolio_metrics.get("sector_allocation", {})

            if sector in sector_allocation:
                sector_pct = sector_allocation[sector]["percentage"]
                if sector_pct > 40:
                    negative_signals += 1
                    factors.append(f"❌ {sector} sector overweight in portfolio ({sector_pct:.1f}%)")
                elif sector_pct < 20:
                    positive_signals += 1
                    factors.append(f"✓ {sector} sector underweight in portfolio ({sector_pct:.1f}%)")

        # Factor 6: Existing position
        if has_position:
            position = portfolio.get_position(ticker)
            from tools.stock_data import get_current_stock_price
            price_data = get_current_stock_price(ticker)

            if "error" not in price_data:
                gain_loss_pct = position.gain_loss_pct(price_data['price'])

                if gain_loss_pct > 50:
                    factors.append(f"ℹ️ Strong gain on existing position (+{gain_loss_pct:.1f}%) - consider taking profits")
                elif gain_loss_pct < -20:
                    factors.append(f"ℹ️ Significant loss on existing position ({gain_loss_pct:.1f}%) - review holding")

        # Generate recommendation
        signal_ratio = positive_signals / max(positive_signals + negative_signals, 1)

        if has_position:
            # HOLD or SELL decision for existing positions
            if negative_signals >= 3 or signal_ratio < 0.3:
                action = "SELL"
                confidence = "MODERATE" if negative_signals == 3 else "HIGH"
                summary = f"Consider selling {ticker}. Multiple negative factors suggest it may underperform."
            elif signal_ratio < 0.5:
                action = "HOLD"
                confidence = "MODERATE"
                summary = f"Hold {ticker} for now. Mixed signals suggest waiting for clearer direction."
            else:
                action = "HOLD"
                confidence = "MODERATE"
                summary = f"Continue holding {ticker}. Positive fundamentals support the position."

        else:
            # BUY or PASS decision for new positions
            if signal_ratio >= 0.7 and positive_signals >= 3:
                action = "BUY"
                confidence = "HIGH"
                summary = f"Strong buy signal for {ticker}. Multiple positive factors align."
            elif signal_ratio >= 0.5 and positive_signals >= 2:
                action = "BUY"
                confidence = "MODERATE"
                summary = f"Cautious buy for {ticker}. Consider a small position (5-10%)."
            else:
                action = "PASS"
                confidence = "MODERATE"
                summary = f"Pass on {ticker} for now. Wait for better entry point or clearer fundamentals."

        # Construct reasoning
        reasoning_parts = [summary, ""]
        reasoning_parts.append("Key Factors:")
        reasoning_parts.extend([f"  {factor}" for factor in factors])

        # Add portfolio context if relevant
        if "error" not in portfolio_metrics:
            reasoning_parts.append("")
            reasoning_parts.append(f"Portfolio Context:")
            reasoning_parts.append(f"  Total positions: {portfolio_metrics['total_positions']}")
            reasoning_parts.append(f"  Diversification score: {portfolio_metrics['diversification_score']}/100")

            if portfolio_metrics.get("concentration_risks"):
                reasoning_parts.append("  Concentration risks:")
                for risk in portfolio_metrics["concentration_risks"][:3]:  # Top 3
                    reasoning_parts.append(f"    - {risk}")

        result = {
            "ticker": ticker,
            "action": action,
            "confidence": confidence,
            "summary": summary,
            "reasoning": "\n".join(reasoning_parts),
            "positive_signals": positive_signals,
            "negative_signals": negative_signals,
            "has_existing_position": has_position,
            "current_price": analysis.get("current_price")
        }

        logger.info(f"Recommendation for {ticker}: {action} ({confidence} confidence)")
        return result

    except Exception as e:
        logger.error(f"Error generating recommendation for {ticker}: {e}")
        return {"error": str(e)}


def compare_stocks(tickers: list) -> Dict[str, Any]:
    """
    Compare multiple stocks and rank them

    Args:
        tickers: List of stock ticker symbols

    Returns:
        Dict with comparison results and rankings
    """
    try:
        comparisons = []

        for ticker in tickers:
            recommendation = recommend_action(ticker)

            if "error" not in recommendation:
                score = recommendation["positive_signals"] - recommendation["negative_signals"]
                comparisons.append({
                    "ticker": ticker,
                    "action": recommendation["action"],
                    "confidence": recommendation["confidence"],
                    "score": score,
                    "summary": recommendation["summary"]
                })

        # Sort by score
        comparisons.sort(key=lambda x: x["score"], reverse=True)

        result = {
            "comparisons": comparisons,
            "top_pick": comparisons[0]["ticker"] if comparisons else None,
            "recommendation": f"Based on analysis, {comparisons[0]['ticker']} is the top pick" if comparisons else "No clear winner"
        }

        logger.info(f"Compared {len(tickers)} stocks")
        return result

    except Exception as e:
        logger.error(f"Error comparing stocks: {e}")
        return {"error": str(e)}
