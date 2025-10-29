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


# =============================================
# Wallet Transfer Schemas
# =============================================

class AssetBalance(BaseModel):
    """자산 잔고"""
    asset: str
    free: float
    used: float
    total: float


class WalletBalances(BaseModel):
    """현물/선물 통합 잔고"""
    spot: dict[str, AssetBalance]
    futures: dict[str, AssetBalance]
    timestamp: datetime


class TransferRequest(BaseModel):
    """자금 이체 요청"""
    asset: str
    amount: float
    direction: str  # 'spot_to_futures' or 'futures_to_spot'

    class Config:
        json_schema_extra = {
            "example": {
                "asset": "USDT",
                "amount": 100.0,
                "direction": "spot_to_futures"
            }
        }


class TransferResponse(BaseModel):
    """자금 이체 응답"""
    success: bool
    tranId: int | str | None = None
    asset: str
    amount: float
    from_wallet: str
    to_wallet: str
    timestamp: int
    message: str | None = None

