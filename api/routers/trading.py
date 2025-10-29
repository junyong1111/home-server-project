"""
Trading Router - Binance API 연동
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from api.core.database import get_db
from api.models.user import User
from api.models.market_data import MarketData
from api.routers.users import get_current_user
from api.services.binance_service import BinanceService
from api.schemas.market_data import (
    WalletBalances,
    AssetBalance,
    TransferRequest,
    TransferResponse
)

router = APIRouter(prefix="/api/v1/trading", tags=["Trading"])


# =============================================
# Market Data Endpoints
# =============================================

@router.get("/ohlcv/{symbol}")
def get_ohlcv_from_binance(
    symbol: str,
    timeframe: str = Query(default="15m", description="1m, 5m, 15m, 1h, 4h, 1d"),
    limit: int = Query(default=100, le=1000),
    save_to_db: bool = Query(default=False, description="DB에 저장 여부"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Binance에서 OHLCV 캔들 데이터 조회 (실시간)

    - **symbol**: 심볼 (예: BTC/USDT)
    - **timeframe**: 시간프레임 (1m, 5m, 15m, 1h, 4h, 1d)
    - **limit**: 캔들 개수 (최대 1000)
    - **save_to_db**: True이면 market_data 테이블에 저장
    """
    try:
        # BinanceService 초기화
        binance = BinanceService(current_user, testnet=False)

        # OHLCV 조회
        ohlcv = binance.fetch_ohlcv(symbol, timeframe, limit)

        # DB 저장
        if save_to_db:
            saved_count = 0
            for candle in ohlcv:
                timestamp, open_price, high, low, close, volume = candle

                # 중복 확인 (Primary Key: time, exchange, symbol, timeframe)
                existing = db.query(MarketData).filter(
                    MarketData.time == datetime.fromtimestamp(timestamp / 1000),
                    MarketData.exchange == 'binance',
                    MarketData.symbol == symbol,
                    MarketData.timeframe == timeframe
                ).first()

                if not existing:
                    market_data = MarketData(
                        time=datetime.fromtimestamp(timestamp / 1000),
                        exchange='binance',
                        symbol=symbol,
                        timeframe=timeframe,
                        open=open_price,
                        high=high,
                        low=low,
                        close=close,
                        volume=volume
                    )
                    db.add(market_data)
                    saved_count += 1

            db.commit()
            print(f"✅ DB 저장 완료: {saved_count}개 (중복 제외)")

        # 응답 포맷팅
        candles = []
        for candle in ohlcv:
            timestamp, open_price, high, low, close, volume = candle
            candles.append({
                "time": datetime.fromtimestamp(timestamp / 1000).isoformat(),
                "open": open_price,
                "high": high,
                "low": low,
                "close": close,
                "volume": volume
            })

        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "count": len(candles),
            "saved_to_db": save_to_db,
            "data": candles
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OHLCV 조회 실패: {str(e)}"
        )


@router.get("/ticker/{symbol}")
def get_ticker_from_binance(
    symbol: str,
    current_user: User = Depends(get_current_user)
):
    """
    Binance에서 현재 가격 및 24시간 통계 조회

    - **symbol**: 심볼 (예: BTC/USDT)
    """
    try:
        binance = BinanceService(current_user, testnet=False)
        ticker = binance.fetch_ticker(symbol)

        return {
            "symbol": ticker['symbol'],
            "last": ticker['last'],
            "bid": ticker['bid'],
            "ask": ticker['ask'],
            "high": ticker['high'],
            "low": ticker['low'],
            "volume": ticker['baseVolume'],
            "quoteVolume": ticker['quoteVolume'],
            "change": ticker['change'],
            "percentage": ticker['percentage'],
            "timestamp": datetime.fromtimestamp(ticker['timestamp'] / 1000).isoformat()
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ticker 조회 실패: {str(e)}"
        )


@router.get("/funding-rate/{symbol}")
def get_funding_rate_from_binance(
    symbol: str,
    current_user: User = Depends(get_current_user)
):
    """
    Binance에서 펀딩 레이트 조회 (선물 전용)

    - **symbol**: 심볼 (예: BTC/USDT)
    """
    try:
        binance = BinanceService(current_user, testnet=False)
        funding = binance.fetch_funding_rate(symbol)

        return {
            "symbol": funding['symbol'],
            "fundingRate": funding.get('fundingRate'),
            "fundingTimestamp": datetime.fromtimestamp(funding.get('fundingTimestamp', 0) / 1000).isoformat() if funding.get('fundingTimestamp') else None,
            "markPrice": funding.get('markPrice'),
            "indexPrice": funding.get('indexPrice'),
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Funding Rate 조회 실패: {str(e)}"
        )


# =============================================
# Account Endpoints
# =============================================

@router.get("/balance")
def get_balance_from_binance(
    current_user: User = Depends(get_current_user)
):
    """
    Binance 선물 계좌 잔고 조회
    """
    try:
        binance = BinanceService(current_user, testnet=False)
        balance = binance.fetch_balance()

        # USDT 잔고만 추출 (주요 화폐)
        usdt_balance = balance.get('USDT', {})
        btc_balance = balance.get('BTC', {})

        return {
            "USDT": {
                "free": usdt_balance.get('free', 0),
                "used": usdt_balance.get('used', 0),
                "total": usdt_balance.get('total', 0)
            },
            "BTC": {
                "free": btc_balance.get('free', 0),
                "used": btc_balance.get('used', 0),
                "total": btc_balance.get('total', 0)
            },
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"잔고 조회 실패: {str(e)}"
        )


@router.get("/positions")
def get_positions_from_binance(
    current_user: User = Depends(get_current_user)
):
    """
    Binance 오픈 포지션 조회
    """
    try:
        binance = BinanceService(current_user, testnet=False)
        positions = binance.fetch_positions()

        # 응답 포맷팅
        formatted_positions = []
        for pos in positions:
            formatted_positions.append({
                "symbol": pos.get('symbol'),
                "side": pos.get('side'),
                "contracts": pos.get('contracts'),
                "contractSize": pos.get('contractSize'),
                "entryPrice": pos.get('entryPrice'),
                "markPrice": pos.get('markPrice'),
                "liquidationPrice": pos.get('liquidationPrice'),
                "unrealizedPnl": pos.get('unrealizedPnl'),
                "leverage": pos.get('leverage'),
                "marginType": pos.get('marginType'),
                "timestamp": datetime.fromtimestamp(pos.get('timestamp', 0) / 1000).isoformat() if pos.get('timestamp') else None
            })

        return {
            "count": len(formatted_positions),
            "positions": formatted_positions,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"포지션 조회 실패: {str(e)}"
        )


# =============================================
# Exchange Info
# =============================================

@router.get("/exchange-info")
def get_exchange_info(
    current_user: User = Depends(get_current_user)
):
    """
    Binance 거래소 정보 조회
    """
    try:
        binance = BinanceService(current_user, testnet=False)
        info = binance.get_exchange_info()

        return info

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"거래소 정보 조회 실패: {str(e)}"
        )


# =============================================
# Wallet Transfer Endpoints
# =============================================

@router.get("/balances/all", response_model=WalletBalances)
def get_all_balances(
    current_user: User = Depends(get_current_user)
):
    """
    현물/선물 통합 잔고 조회

    - **spot**: 현물 지갑 잔고
    - **futures**: 선물 지갑 잔고
    - **timestamp**: 조회 시각
    """
    try:
        binance = BinanceService(current_user, testnet=False)

        # 현물 잔고
        spot_balance = binance.get_spot_balance()
        # 선물 잔고
        futures_balance = binance.get_futures_balance()

        # AssetBalance 형식으로 변환
        def convert_balance(balance_dict: dict) -> dict:
            result = {}
            for asset, data in balance_dict.items():
                if isinstance(data, dict) and 'free' in data:
                    result[asset] = AssetBalance(
                        asset=asset,
                        free=float(data.get('free', 0)),
                        used=float(data.get('used', 0)),
                        total=float(data.get('total', 0))
                    )
            return result

        return WalletBalances(
            spot=convert_balance(spot_balance),
            futures=convert_balance(futures_balance),
            timestamp=datetime.now()
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"잔고 조회 실패: {str(e)}"
        )


@router.post("/transfer", response_model=TransferResponse)
def transfer_funds(
    request: TransferRequest,
    current_user: User = Depends(get_current_user)
):
    """
    현물 ↔ 선물 자금 이체

    - **asset**: 자산 코드 (USDT, BTC 등)
    - **amount**: 이체 금액
    - **direction**: 'spot_to_futures' 또는 'futures_to_spot'

    ### 정보
    - 수수료: 무료 (내부 이체)
    - 최소 금액: 0.01 USDT
    - 예상 시간: 1-3초
    - Rate Limit: 1분 5회
    """
    try:
        binance = BinanceService(current_user, testnet=False)

        # 방향 검증
        if request.direction not in ['spot_to_futures', 'futures_to_spot']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="direction은 'spot_to_futures' 또는 'futures_to_spot'이어야 합니다"
            )

        # 최소 금액 검증
        if request.amount < 0.01:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="최소 이체 금액은 0.01입니다"
            )

        # 이체 실행
        if request.direction == 'spot_to_futures':
            result = binance.transfer_to_futures(request.asset, request.amount)
            from_wallet = 'spot'
            to_wallet = 'futures'
        else:
            result = binance.transfer_to_spot(request.asset, request.amount)
            from_wallet = 'futures'
            to_wallet = 'spot'

        return TransferResponse(
            success=result['success'],
            tranId=result.get('tranId'),
            asset=request.asset,
            amount=request.amount,
            from_wallet=from_wallet,
            to_wallet=to_wallet,
            timestamp=result['timestamp'],
            message=f"{request.amount} {request.asset} 이체 완료 ({from_wallet} → {to_wallet})"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"자금 이체 실패: {str(e)}"
        )

