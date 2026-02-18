"""
Stock analysis functions for valuation, growth, and risk assessment
"""
from typing import Dict, Any, Optional
import config
from tools.stock_data import get_stock_fundamentals, get_current_stock_price, get_historical_data
from utils.logger import get_logger

logger = get_logger(__name__)


def analyze_valuation(ticker: str) -> Dict[str, Any]:
    """
    Analyze stock valuation metrics

    Args:
        ticker: Stock ticker symbol

    Returns:
        Dict with valuation analysis
    """
    try:
        fundamentals = get_stock_fundamentals(ticker)

        if "error" in fundamentals:
            return {"error": fundamentals["error"]}

        pe_ratio = fundamentals.get('pe_ratio')
        forward_pe = fundamentals.get('forward_pe')
        sector = fundamentals.get('sector', 'Unknown')

        # Determine if overvalued based on P/E ratio
        is_overvalued = None
        valuation_summary = "N/A"

        if pe_ratio and pe_ratio != "N/A":
            if pe_ratio > config.OVERVALUED_PE_THRESHOLD:
                is_overvalued = True
                valuation_summary = f"Premium valuation with P/E of {pe_ratio:.2f}"
            elif pe_ratio < 15:
                is_overvalued = False
                valuation_summary = f"Value valuation with P/E of {pe_ratio:.2f}"
            else:
                is_overvalued = False
                valuation_summary = f"Fair valuation with P/E of {pe_ratio:.2f}"

        # Add forward P/E context
        if forward_pe and forward_pe != "N/A":
            valuation_summary += f" (Forward P/E: {forward_pe:.2f})"

        # Analyze profit margin
        profit_margin = fundamentals.get('profit_margin')
        profitability = "N/A"
        if profit_margin and profit_margin != "N/A":
            if profit_margin > 20:
                profitability = f"High profitability ({profit_margin:.1f}% margin)"
            elif profit_margin > 10:
                profitability = f"Moderate profitability ({profit_margin:.1f}% margin)"
            else:
                profitability = f"Low profitability ({profit_margin:.1f}% margin)"

        result = {
            "ticker": ticker,
            "company_name": fundamentals.get('company_name'),
            "sector": sector,
            "pe_ratio": pe_ratio,
            "forward_pe": forward_pe,
            "is_overvalued": is_overvalued,
            "valuation_summary": valuation_summary,
            "profitability": profitability,
            "profit_margin": profit_margin,
            "debt_to_equity": fundamentals.get('debt_to_equity'),
        }

        logger.info(f"Valuation analysis for {ticker}: {valuation_summary}")
        return result

    except Exception as e:
        logger.error(f"Error analyzing valuation for {ticker}: {e}")
        return {"error": str(e)}


def analyze_growth(ticker: str) -> Dict[str, Any]:
    """
    Analyze growth metrics and momentum

    Args:
        ticker: Stock ticker symbol

    Returns:
        Dict with growth analysis
    """
    try:
        fundamentals = get_stock_fundamentals(ticker)
        historical = get_historical_data(ticker, period="1y")

        if "error" in fundamentals:
            return {"error": fundamentals["error"]}

        revenue_growth = fundamentals.get('revenue_growth')
        earnings_growth = fundamentals.get('earnings_growth')

        # Categorize growth
        growth_category = "N/A"
        if revenue_growth and revenue_growth != "N/A":
            if revenue_growth > 20:
                growth_category = "High Growth"
            elif revenue_growth > 10:
                growth_category = "Moderate Growth"
            elif revenue_growth > 0:
                growth_category = "Low Growth"
            else:
                growth_category = "Declining"

        # Analyze momentum from historical data
        momentum = "N/A"
        if "error" not in historical:
            total_return = historical.get('total_return_pct', 0)
            if total_return > 30:
                momentum = f"Strong positive momentum (+{total_return:.1f}% YoY)"
            elif total_return > 10:
                momentum = f"Positive momentum (+{total_return:.1f}% YoY)"
            elif total_return > 0:
                momentum = f"Slight positive momentum (+{total_return:.1f}% YoY)"
            elif total_return > -10:
                momentum = f"Slight negative momentum ({total_return:.1f}% YoY)"
            else:
                momentum = f"Negative momentum ({total_return:.1f}% YoY)"

        result = {
            "ticker": ticker,
            "company_name": fundamentals.get('company_name'),
            "revenue_growth": revenue_growth,
            "earnings_growth": earnings_growth,
            "growth_category": growth_category,
            "year_return_pct": historical.get('total_return_pct') if "error" not in historical else "N/A",
            "momentum": momentum,
            "growth_summary": f"{growth_category} company with {momentum}"
        }

        logger.info(f"Growth analysis for {ticker}: {growth_category}")
        return result

    except Exception as e:
        logger.error(f"Error analyzing growth for {ticker}: {e}")
        return {"error": str(e)}


def analyze_risk(ticker: str) -> Dict[str, Any]:
    """
    Analyze risk factors

    Args:
        ticker: Stock ticker symbol

    Returns:
        Dict with risk analysis
    """
    try:
        fundamentals = get_stock_fundamentals(ticker)

        if "error" in fundamentals:
            return {"error": fundamentals["error"]}

        beta = fundamentals.get('beta')
        debt_to_equity = fundamentals.get('debt_to_equity')

        # Analyze volatility risk from beta
        volatility_risk = "N/A"
        if beta and beta != "N/A":
            if beta > 1.5:
                volatility_risk = "High volatility (Beta > 1.5)"
            elif beta > 1.0:
                volatility_risk = "Moderate volatility (Beta > 1.0)"
            else:
                volatility_risk = "Low volatility (Beta < 1.0)"

        # Analyze financial risk from debt
        financial_risk = "N/A"
        if debt_to_equity and debt_to_equity != "N/A":
            if debt_to_equity > 2.0:
                financial_risk = "High debt (D/E > 2.0)"
            elif debt_to_equity > 1.0:
                financial_risk = "Moderate debt (D/E > 1.0)"
            else:
                financial_risk = "Low debt (D/E < 1.0)"

        # Overall risk assessment
        risk_factors = []
        if volatility_risk != "N/A" and "High" in volatility_risk:
            risk_factors.append("high price volatility")
        if financial_risk != "N/A" and "High" in financial_risk:
            risk_factors.append("high financial leverage")

        overall_risk = "Moderate risk"
        if len(risk_factors) >= 2:
            overall_risk = "High risk"
        elif len(risk_factors) == 0:
            overall_risk = "Low risk"

        result = {
            "ticker": ticker,
            "company_name": fundamentals.get('company_name'),
            "beta": beta,
            "debt_to_equity": debt_to_equity,
            "volatility_risk": volatility_risk,
            "financial_risk": financial_risk,
            "overall_risk": overall_risk,
            "risk_factors": risk_factors,
            "risk_summary": f"{overall_risk} - {', '.join(risk_factors) if risk_factors else 'No major risk factors identified'}"
        }

        logger.info(f"Risk analysis for {ticker}: {overall_risk}")
        return result

    except Exception as e:
        logger.error(f"Error analyzing risk for {ticker}: {e}")
        return {"error": str(e)}


def get_comprehensive_analysis(ticker: str) -> Dict[str, Any]:
    """
    Get comprehensive stock analysis combining all factors

    Args:
        ticker: Stock ticker symbol

    Returns:
        Dict with complete analysis
    """
    try:
        valuation = analyze_valuation(ticker)
        growth = analyze_growth(ticker)
        risk = analyze_risk(ticker)
        current_price = get_current_stock_price(ticker)

        if any("error" in x for x in [valuation, growth, risk, current_price]):
            errors = [x.get("error") for x in [valuation, growth, risk, current_price] if "error" in x]
            return {"error": "; ".join(errors)}

        result = {
            "ticker": ticker,
            "company_name": valuation.get('company_name'),
            "current_price": current_price.get('price'),
            "sector": valuation.get('sector'),
            "valuation": {
                "summary": valuation.get('valuation_summary'),
                "is_overvalued": valuation.get('is_overvalued'),
                "pe_ratio": valuation.get('pe_ratio'),
                "profitability": valuation.get('profitability')
            },
            "growth": {
                "category": growth.get('growth_category'),
                "momentum": growth.get('momentum'),
                "revenue_growth": growth.get('revenue_growth'),
                "year_return": growth.get('year_return_pct')
            },
            "risk": {
                "overall": risk.get('overall_risk'),
                "factors": risk.get('risk_factors'),
                "beta": risk.get('beta'),
                "volatility": risk.get('volatility_risk')
            }
        }

        logger.info(f"Comprehensive analysis completed for {ticker}")
        return result

    except Exception as e:
        logger.error(f"Error in comprehensive analysis for {ticker}: {e}")
        return {"error": str(e)}
