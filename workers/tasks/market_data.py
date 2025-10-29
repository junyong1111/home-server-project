"""
시장 데이터 수집 태스크
"""
from celery import shared_task
from datetime import datetime
import requests
import ccxt
import os
from typing import List

# Database 연결
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from api.core.database import SessionLocal
from api.models.market_data import MarketData, FundingRateHistory


@shared_task(name="workers.tasks.market_data.collect_candle_data")
def collect_candle_data(symbols: List[str], timeframe: str = "5m", limit: int = 100):
    """
    캔들 데이터 수집 및 DB 저장

    Args:
        symbols: 심볼 리스트 (예: ["BTCUSDT", "ETHUSDT"])
        timeframe: 시간봉 (예: "5m", "15m", "1h")
        limit: 수집할 캔들 개수
    """
    print(f"▲ 캔들 데이터 수집 시작: {symbols}, {timeframe}")

    try:
        # CCXT Binance 인스턴스 (Public API, 인증 불필요)
        exchange = ccxt.binance({
            'enableRateLimit': True,
            'options': {'defaultType': 'future'}
        })

        db = SessionLocal()
        total_saved = 0

        for symbol in symbols:
            try:
                # OHLCV 데이터 조회
                ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)

                for candle in ohlcv:
                    timestamp, open_price, high, low, close, volume = candle

                    # DB에 저장 (upsert)
                    market_data = MarketData(
                        time=datetime.fromtimestamp(timestamp / 1000),
                        exchange="binance",
                        symbol=symbol,
                        timeframe=timeframe,
                        open=open_price,
                        high=high,
                        low=low,
                        close=close,
                        volume=volume
                    )

                    # Upsert (중복 시 업데이트)
                    db.merge(market_data)

                db.commit()
                total_saved += len(ohlcv)
                print(f"  ✓ {symbol}: {len(ohlcv)}개 저장")

            except Exception as e:
                print(f"  ✗ {symbol} 실패: {e}")
                db.rollback()

        db.close()

        print(f"✓ 캔들 데이터 수집 완료: 총 {total_saved}개")
        return {"success": True, "total_saved": total_saved}

    except Exception as e:
        print(f"✗ 캔들 데이터 수집 실패: {e}")
        return {"success": False, "error": str(e)}


@shared_task(name="workers.tasks.market_data.collect_funding_rates")
def collect_funding_rates(symbols: List[str] = ["BTCUSDT", "ETHUSDT"]):
    """
    Funding Rate 수집 및 DB 저장

    Args:
        symbols: 심볼 리스트
    """
    print(f"▲ Funding Rate 수집 시작: {symbols}")

    try:
        exchange = ccxt.binance({
            'enableRateLimit': True,
            'options': {'defaultType': 'future'}
        })

        db = SessionLocal()
        total_saved = 0

        for symbol in symbols:
            try:
                # Funding Rate 조회
                funding = exchange.fetch_funding_rate(symbol)

                funding_data = FundingRateHistory(
                    time=datetime.fromtimestamp(funding['timestamp'] / 1000),
                    exchange="binance",
                    symbol=symbol,
                    funding_rate=funding['fundingRate'],
                    mark_price=funding.get('markPrice', 0),
                    index_price=funding.get('indexPrice', 0)
                )

                db.merge(funding_data)
                db.commit()
                total_saved += 1

                print(f"  ✓ {symbol}: {funding['fundingRate']:.6f}")

            except Exception as e:
                print(f"  ✗ {symbol} 실패: {e}")
                db.rollback()

        db.close()

        print(f"✓ Funding Rate 수집 완료: {total_saved}개")
        return {"success": True, "total_saved": total_saved}

    except Exception as e:
        print(f"✗ Funding Rate 수집 실패: {e}")
        return {"success": False, "error": str(e)}


@shared_task(name="workers.tasks.market_data.trigger_n8n_workflow")
def trigger_n8n_workflow():
    """
    n8n 워크플로우 트리거 (AI 의사결정)

    조건:
    - 15분마다 실행
    - Quick Filter 통과 시에만 n8n 호출
    """
    print("▲ AI 의사결정 워크플로우 트리거 시도")

    try:
        # Quick Filter: 간단한 조건 체크
        # 예: 최근 15분간 가격 변동 > 1%

        # TODO: 실제 Quick Filter 로직 구현
        should_trigger = True  # 임시

        if not should_trigger:
            print("  → Quick Filter 통과 실패, 건너뜀")
            return {"success": True, "triggered": False, "reason": "quick_filter_failed"}

        # n8n Webhook URL
        n8n_webhook_url = os.getenv("N8N_WEBHOOK_URL", "")

        if not n8n_webhook_url:
            print("  ! N8N_WEBHOOK_URL이 설정되지 않음")
            return {"success": False, "error": "N8N_WEBHOOK_URL not configured"}

        # n8n 워크플로우 호출
        response = requests.post(
            n8n_webhook_url,
            json={
                "trigger_time": datetime.now().isoformat(),
                "trigger_source": "celery_beat"
            },
            timeout=10
        )

        if response.status_code == 200:
            print(f"  ✓ n8n 워크플로우 트리거 성공")
            return {"success": True, "triggered": True}
        else:
            print(f"  ✗ n8n 워크플로우 트리거 실패: {response.status_code}")
            return {"success": False, "error": f"HTTP {response.status_code}"}

    except Exception as e:
        print(f"✗ n8n 워크플로우 트리거 실패: {e}")
        return {"success": False, "error": str(e)}
