"""
Market Data Router
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from core.database import get_db
from models.market_data import MarketData, PortfolioSnapshot
from models.user import User
from routers.users import get_current_user
from schemas.market_data import MarketDataResponse, PortfolioSnapshotResponse

router = APIRouter(prefix="/api/v1/market", tags=["Market Data"])


@router.get("/ohlcv/{symbol}", response_model=List[MarketDataResponse])
def get_ohlcv(
    symbol: str,
    timeframe: str = "15m",
    exchange: str = "binance",
    limit: int = Query(default=100, le=1000),
    db: Session = Depends(get_db)
):
    """
    OHLCV 캔들 데이터 조회

    - **symbol**: 심볼 (예: BTC/USDT)
    - **timeframe**: 시간프레임 (1m, 5m, 15m, 1h, 4h, 1d)
    - **exchange**: 거래소 (기본: binance)
    - **limit**: 조회 개수 (최대 1000)
    """
    candles = db.query(MarketData).filter(
        MarketData.symbol == symbol,
        MarketData.timeframe == timeframe,
        MarketData.exchange == exchange
    ).order_by(MarketData.time.desc()).limit(limit).all()

    if not candles:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No data found for {symbol} {timeframe}"
        )

    # 시간 오름차순 정렬 (차트 표시용)
    return list(reversed(candles))


@router.get("/portfolio-history", response_model=List[PortfolioSnapshotResponse])
def get_portfolio_history(
    hours: int = Query(default=24, le=720),  # 최대 30일
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    내 포트폴리오 가치 이력 조회 (인증 필요)

    - **hours**: 조회 기간 (시간 단위, 최대 720시간 = 30일)
    """
    since = datetime.utcnow() - timedelta(hours=hours)

    snapshots = db.query(PortfolioSnapshot).filter(
        PortfolioSnapshot.user_id == current_user.user_id,
        PortfolioSnapshot.time >= since
    ).order_by(PortfolioSnapshot.time.asc()).all()

    return snapshots


@router.get("/latest-price/{symbol}")
def get_latest_price(
    symbol: str,
    exchange: str = "binance",
    db: Session = Depends(get_db)
):
    """
    최신 가격 조회

    - **symbol**: 심볼 (예: BTC/USDT)
    - **exchange**: 거래소 (기본: binance)
    """
    latest = db.query(MarketData).filter(
        MarketData.symbol == symbol,
        MarketData.exchange == exchange
    ).order_by(MarketData.time.desc()).first()

    if not latest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No data found for {symbol}"
        )

    return {
        "symbol": latest.symbol,
        "price": float(latest.close),
        "time": latest.time,
        "change_24h": None  # TODO: 24시간 변화율 계산
    }

