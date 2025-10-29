"""
Market Data Schemas
"""
from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal


class MarketDataResponse(BaseModel):
    """Market Data 응답"""
    time: datetime
    exchange: str
    symbol: str
    timeframe: str
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal

    class Config:
        from_attributes = True


class PortfolioSnapshotResponse(BaseModel):
    """Portfolio Snapshot 응답"""
    time: datetime
    user_id: int
    total_value_usdt: Decimal
    btc_value: Decimal | None = None
    eth_value: Decimal | None = None
    usdt_value: Decimal | None = None
    btc_allocation_pct: Decimal | None = None
    eth_allocation_pct: Decimal | None = None
    total_leverage: Decimal | None = None
    margin_ratio: Decimal | None = None
    unrealized_pnl: Decimal | None = None

    class Config:
        from_attributes = True

