"""
Pydantic models for portfolio data structures
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class Position(BaseModel):
    """Represents a single stock position in the portfolio"""
    ticker: str = Field(..., description="Stock ticker symbol (e.g., AAPL)")
    shares: float = Field(..., gt=0, description="Number of shares owned")
    purchase_price: float = Field(..., gt=0, description="Average purchase price per share")
    purchase_date: str = Field(..., description="Date of purchase (YYYY-MM-DD)")

    @field_validator('ticker')
    @classmethod
    def ticker_must_be_uppercase(cls, v: str) -> str:
        """Ensure ticker is uppercase"""
        return v.upper().strip()

    @field_validator('purchase_date')
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        """Validate date format is YYYY-MM-DD"""
        try:
            datetime.strptime(v, "%Y-%m-%d")
            return v
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")

    def current_value(self, current_price: float) -> float:
        """Calculate current value of position"""
        return self.shares * current_price

    def gain_loss(self, current_price: float) -> float:
        """Calculate dollar gain/loss"""
        return (current_price - self.purchase_price) * self.shares

    def gain_loss_pct(self, current_price: float) -> float:
        """Calculate percentage gain/loss"""
        return ((current_price - self.purchase_price) / self.purchase_price) * 100

    def holding_period_days(self) -> int:
        """Calculate days since purchase"""
        purchase_dt = datetime.strptime(self.purchase_date, "%Y-%m-%d")
        return (datetime.now() - purchase_dt).days


class Portfolio(BaseModel):
    """Represents the entire portfolio"""
    positions: List[Position] = Field(default_factory=list, description="List of stock positions")
    last_updated: Optional[str] = Field(default=None, description="Last update timestamp")

    def get_position(self, ticker: str) -> Optional[Position]:
        """Get a specific position by ticker"""
        ticker = ticker.upper().strip()
        for position in self.positions:
            if position.ticker == ticker:
                return position
        return None

    def has_position(self, ticker: str) -> bool:
        """Check if ticker exists in portfolio"""
        return self.get_position(ticker) is not None

    def total_positions(self) -> int:
        """Count total number of positions"""
        return len(self.positions)

    def total_shares(self, ticker: str) -> float:
        """Get total shares for a ticker"""
        position = self.get_position(ticker)
        return position.shares if position else 0.0

    def update_timestamp(self):
        """Update the last_updated timestamp"""
        self.last_updated = datetime.now().isoformat()
