"""
Portfolio manager for CRUD operations on portfolio JSON file
"""
import json
from pathlib import Path
from typing import Optional
from datetime import datetime

import config
from portfolio.models import Portfolio, Position
from utils.logger import get_logger

logger = get_logger(__name__)


class PortfolioManager:
    """Manages portfolio persistence and operations"""

    def __init__(self, portfolio_file: Path = config.PORTFOLIO_FILE):
        self.portfolio_file = portfolio_file
        self.portfolio: Optional[Portfolio] = None

    def load_portfolio(self) -> Portfolio:
        """Load portfolio from JSON file"""
        if not self.portfolio_file.exists():
            logger.warning(f"Portfolio file not found at {self.portfolio_file}, creating new portfolio")
            self.portfolio = Portfolio(positions=[])
            self.save_portfolio()
            return self.portfolio

        try:
            with open(self.portfolio_file, 'r') as f:
                data = json.load(f)
            self.portfolio = Portfolio(**data)
            logger.info(f"Loaded portfolio with {self.portfolio.total_positions()} positions")
            return self.portfolio
        except Exception as e:
            logger.error(f"Error loading portfolio: {e}")
            raise

    def save_portfolio(self) -> bool:
        """Save portfolio to JSON file"""
        try:
            if self.portfolio is None:
                raise ValueError("No portfolio loaded to save")

            self.portfolio.update_timestamp()

            with open(self.portfolio_file, 'w') as f:
                json.dump(self.portfolio.model_dump(), f, indent=2)

            logger.info(f"Saved portfolio with {self.portfolio.total_positions()} positions")
            return True
        except Exception as e:
            logger.error(f"Error saving portfolio: {e}")
            return False

    def add_position(self, ticker: str, shares: float, purchase_price: float,
                     purchase_date: Optional[str] = None) -> Position:
        """
        Add a new position or update existing one

        If position exists, this will average the cost basis
        """
        if self.portfolio is None:
            self.load_portfolio()

        ticker = ticker.upper().strip()

        if purchase_date is None:
            purchase_date = datetime.now().strftime("%Y-%m-%d")

        existing_position = self.portfolio.get_position(ticker)

        if existing_position:
            # Calculate new average cost
            total_shares = existing_position.shares + shares
            total_cost = (existing_position.shares * existing_position.purchase_price +
                         shares * purchase_price)
            new_avg_price = total_cost / total_shares

            # Update existing position
            existing_position.shares = total_shares
            existing_position.purchase_price = new_avg_price
            # Keep original purchase date for existing position

            logger.info(f"Updated {ticker}: {total_shares} shares @ ${new_avg_price:.2f} avg")
            position = existing_position
        else:
            # Create new position
            position = Position(
                ticker=ticker,
                shares=shares,
                purchase_price=purchase_price,
                purchase_date=purchase_date
            )
            self.portfolio.positions.append(position)
            logger.info(f"Added new position: {ticker} {shares} shares @ ${purchase_price:.2f}")

        self.save_portfolio()
        return position

    def remove_position(self, ticker: str, shares: Optional[float] = None) -> bool:
        """
        Remove shares from a position or entire position

        If shares is None or >= total shares, removes entire position
        If shares < total shares, reduces the position
        """
        if self.portfolio is None:
            self.load_portfolio()

        ticker = ticker.upper().strip()
        position = self.portfolio.get_position(ticker)

        if not position:
            logger.warning(f"Position {ticker} not found in portfolio")
            return False

        if shares is None or shares >= position.shares:
            # Remove entire position
            self.portfolio.positions = [p for p in self.portfolio.positions if p.ticker != ticker]
            logger.info(f"Removed entire position: {ticker}")
        else:
            # Reduce shares
            position.shares -= shares
            logger.info(f"Reduced {ticker} by {shares} shares, {position.shares} remaining")

        self.save_portfolio()
        return True

    def get_portfolio(self) -> Portfolio:
        """Get the current portfolio (loads if not already loaded)"""
        if self.portfolio is None:
            self.load_portfolio()
        return self.portfolio

    def update_position(self, ticker: str, **kwargs) -> bool:
        """Update specific fields of a position"""
        if self.portfolio is None:
            self.load_portfolio()

        ticker = ticker.upper().strip()
        position = self.portfolio.get_position(ticker)

        if not position:
            logger.warning(f"Position {ticker} not found in portfolio")
            return False

        for key, value in kwargs.items():
            if hasattr(position, key):
                setattr(position, key, value)

        self.save_portfolio()
        logger.info(f"Updated {ticker} with {kwargs}")
        return True
