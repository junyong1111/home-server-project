"""
Market Data Models (TimescaleDB)
"""
from sqlalchemy import Column, String, Integer, DECIMAL, TIMESTAMP, PrimaryKeyConstraint
from core.database import Base


class MarketData(Base):
    """시장 데이터 (OHLCV) - TimescaleDB Hypertable"""
    __tablename__ = "market_data"
    __table_args__ = {"extend_existing": True}

    time = Column(TIMESTAMP(timezone=True), nullable=False)
    exchange = Column(String(20), nullable=False)
    symbol = Column(String(20), nullable=False)
    timeframe = Column(String(10), nullable=False)

    open = Column(DECIMAL(20, 8), nullable=False)
    high = Column(DECIMAL(20, 8), nullable=False)
    low = Column(DECIMAL(20, 8), nullable=False)
    close = Column(DECIMAL(20, 8), nullable=False)
    volume = Column(DECIMAL(20, 8), nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint('time', 'exchange', 'symbol', 'timeframe'),
    )


class PortfolioSnapshot(Base):
    """포트폴리오 스냅샷 - TimescaleDB Hypertable"""
    __tablename__ = "portfolio_snapshots"
    __table_args__ = {"extend_existing": True}

    time = Column(TIMESTAMP(timezone=True), nullable=False)
    user_id = Column(Integer, nullable=False)

    total_value_usdt = Column(DECIMAL(20, 2), nullable=False)
    btc_value = Column(DECIMAL(20, 2))
    eth_value = Column(DECIMAL(20, 2))
    usdt_value = Column(DECIMAL(20, 2))

    btc_allocation_pct = Column(DECIMAL(5, 2))
    eth_allocation_pct = Column(DECIMAL(5, 2))

    total_leverage = Column(DECIMAL(10, 2))
    margin_ratio = Column(DECIMAL(10, 4))
    unrealized_pnl = Column(DECIMAL(20, 2))

    __table_args__ = (
        PrimaryKeyConstraint('time', 'user_id'),
    )


class FundingRateHistory(Base):
    """Funding Rate 히스토리 - TimescaleDB Hypertable"""
    __tablename__ = "funding_rate_history"
    __table_args__ = {"extend_existing": True}

    time = Column(TIMESTAMP(timezone=True), nullable=False)
    exchange = Column(String(20), nullable=False)
    symbol = Column(String(20), nullable=False)

    funding_rate = Column(DECIMAL(10, 8), nullable=False)
    mark_price = Column(DECIMAL(20, 8), nullable=False)
    index_price = Column(DECIMAL(20, 8), nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint('time', 'exchange', 'symbol'),
    )

