"""
Binance Service - CCXT Integration
"""
import ccxt
from typing import Dict, List, Any, Optional
from datetime import datetime
from decimal import Decimal

from api.core.security import decrypt_api_key
from api.models.user import User


class BinanceService:
    """Binance 거래소 연동 서비스 (CCXT)"""

    def __init__(self, user: User, testnet: bool = False):
        """
        BinanceService 초기화

        Args:
            user: User 모델 인스턴스 (암호화된 API 키 포함)
            testnet: 테스트넷 사용 여부 (기본: True)
        """
        self.user = user
        self.testnet = testnet

        # API 키 복호화
        api_key = decrypt_api_key(user.api_key_encrypted)
        api_secret = decrypt_api_key(user.api_secret_encrypted)

        # CCXT Binance 초기화
        self.exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'future',  # 선물 거래
            }
        })

        # 테스트넷 설정
        if testnet:
            self.exchange.set_sandbox_mode(True)
            print(f"✅ Binance Testnet 모드 활성화 (user_id: {user.user_id})")
        else:
            print(f"⚠️ Binance 실전 모드 (user_id: {user.user_id})")

    # =============================================
    # Market Data APIs
    # =============================================

    def fetch_ohlcv(
        self,
        symbol: str = 'BTC/USDT',
        timeframe: str = '15m',
        limit: int = 100
    ) -> List[List]:
        """
        OHLCV 캔들 데이터 조회

        Args:
            symbol: 심볼 (기본: BTC/USDT)
            timeframe: 시간프레임 (1m, 5m, 15m, 1h, 4h, 1d)
            limit: 캔들 개수 (최대 1000)

        Returns:
            List[List]: [[timestamp, open, high, low, close, volume], ...]
        """
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            print(f"✅ OHLCV 조회 성공: {symbol} {timeframe} ({len(ohlcv)}개)")
            return ohlcv
        except Exception as e:
            print(f"❌ OHLCV 조회 실패: {e}")
            raise

    def fetch_ticker(self, symbol: str = 'BTC/USDT') -> Dict[str, Any]:
        """
        현재 가격 및 24시간 통계 조회

        Args:
            symbol: 심볼

        Returns:
            Dict: {
                'symbol': 'BTC/USDT',
                'last': 67850.0,
                'bid': 67849.0,
                'ask': 67850.5,
                'high': 68000.0,
                'low': 67000.0,
                'volume': 12345.6,
                'percentage': 1.25,
                ...
            }
        """
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            print(f"✅ Ticker 조회 성공: {symbol} = ${ticker['last']}")
            return ticker
        except Exception as e:
            print(f"❌ Ticker 조회 실패: {e}")
            raise

    def fetch_funding_rate(self, symbol: str = 'BTC/USDT') -> Dict[str, Any]:
        """
        펀딩 레이트 조회 (선물 전용)

        Args:
            symbol: 심볼

        Returns:
            Dict: {
                'symbol': 'BTC/USDT',
                'fundingRate': 0.0001,
                'fundingTimestamp': 1234567890,
                'markPrice': 67850.0,
                'indexPrice': 67845.0,
                ...
            }
        """
        try:
            funding = self.exchange.fetch_funding_rate(symbol)
            print(f"✅ Funding Rate 조회 성공: {symbol} = {funding.get('fundingRate', 'N/A')}")
            return funding
        except Exception as e:
            print(f"❌ Funding Rate 조회 실패: {e}")
            raise

    def fetch_order_book(self, symbol: str = 'BTC/USDT', limit: int = 10) -> Dict[str, Any]:
        """
        오더북 조회

        Args:
            symbol: 심볼
            limit: 호가 개수 (기본: 10)

        Returns:
            Dict: {
                'bids': [[price, amount], ...],
                'asks': [[price, amount], ...],
                'timestamp': 1234567890,
                ...
            }
        """
        try:
            order_book = self.exchange.fetch_order_book(symbol, limit)
            print(f"✅ Order Book 조회 성공: {symbol} (bids: {len(order_book['bids'])}, asks: {len(order_book['asks'])})")
            return order_book
        except Exception as e:
            print(f"❌ Order Book 조회 실패: {e}")
            raise

    # =============================================
    # Account APIs
    # =============================================

    def fetch_balance(self) -> Dict[str, Any]:
        """
        선물 계좌 잔고 조회

        Returns:
            Dict: {
                'USDT': {'free': 1000.0, 'used': 500.0, 'total': 1500.0},
                'BTC': {...},
                ...
            }
        """
        try:
            balance = self.exchange.fetch_balance()
            print(f"✅ 잔고 조회 성공: USDT {balance.get('USDT', {}).get('total', 0)}")
            return balance
        except Exception as e:
            print(f"❌ 잔고 조회 실패: {e}")
            raise

    def get_spot_balance(self) -> Dict[str, Any]:
        """
        현물 지갑 잔고 조회

        Returns:
            Dict: {
                'USDT': {'free': 1000.0, 'used': 500.0, 'total': 1500.0},
                'BTC': {...},
                ...
            }
        """
        try:
            balance = self.exchange.fetch_balance({'type': 'spot'})
            print(f"✅ 현물 잔고 조회 성공: USDT {balance.get('USDT', {}).get('total', 0)}")
            return balance
        except Exception as e:
            print(f"❌ 현물 잔고 조회 실패: {e}")
            raise

    def get_futures_balance(self) -> Dict[str, Any]:
        """
        선물 지갑 잔고 조회 (fetch_balance의 명시적 별칭)

        Returns:
            Dict: {
                'USDT': {'free': 1000.0, 'used': 500.0, 'total': 1500.0},
                'BTC': {...},
                ...
            }
        """
        try:
            balance = self.exchange.fetch_balance({'type': 'future'})
            print(f"✅ 선물 잔고 조회 성공: USDT {balance.get('USDT', {}).get('total', 0)}")
            return balance
        except Exception as e:
            print(f"❌ 선물 잔고 조회 실패: {e}")
            raise

    def transfer_to_futures(self, asset: str, amount: float) -> Dict[str, Any]:
        """
        현물 → 선물 지갑 이체

        Args:
            asset: 자산 코드 (예: 'USDT', 'BTC')
            amount: 이체 금액

        Returns:
            Dict: {
                'success': True,
                'tranId': 12345,
                'asset': 'USDT',
                'amount': 100.0,
                'from': 'spot',
                'to': 'future',
                'timestamp': 1234567890
            }
        """
        try:
            result = self.exchange.transfer(
                code=asset,
                amount=amount,
                fromAccount='spot',
                toAccount='future'
            )
            print(f"✅ 현물→선물 이체 성공: {amount} {asset}")
            return {
                'success': True,
                'tranId': result.get('id') or result.get('tranId'),
                'asset': asset,
                'amount': amount,
                'from': 'spot',
                'to': 'future',
                'timestamp': result.get('timestamp') or int(datetime.now().timestamp() * 1000)
            }
        except Exception as e:
            print(f"❌ 현물→선물 이체 실패: {e}")
            raise

    def transfer_to_spot(self, asset: str, amount: float) -> Dict[str, Any]:
        """
        선물 → 현물 지갑 이체

        Args:
            asset: 자산 코드 (예: 'USDT', 'BTC')
            amount: 이체 금액

        Returns:
            Dict: {
                'success': True,
                'tranId': 12345,
                'asset': 'USDT',
                'amount': 100.0,
                'from': 'future',
                'to': 'spot',
                'timestamp': 1234567890
            }
        """
        try:
            result = self.exchange.transfer(
                code=asset,
                amount=amount,
                fromAccount='future',
                toAccount='spot'
            )
            print(f"✅ 선물→현물 이체 성공: {amount} {asset}")
            return {
                'success': True,
                'tranId': result.get('id') or result.get('tranId'),
                'asset': asset,
                'amount': amount,
                'from': 'future',
                'to': 'spot',
                'timestamp': result.get('timestamp') or int(datetime.now().timestamp() * 1000)
            }
        except Exception as e:
            print(f"❌ 선물→현물 이체 실패: {e}")
            raise

    def fetch_positions(self, symbols: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        오픈 포지션 조회

        Args:
            symbols: 조회할 심볼 리스트 (None이면 전체)

        Returns:
            List[Dict]: [
                {
                    'symbol': 'BTC/USDT',
                    'side': 'long',
                    'contracts': 0.1,
                    'entryPrice': 67000.0,
                    'markPrice': 67850.0,
                    'liquidationPrice': 60000.0,
                    'unrealizedPnl': 85.0,
                    'leverage': 5,
                    ...
                },
                ...
            ]
        """
        try:
            positions = self.exchange.fetch_positions(symbols)
            # 포지션이 있는 것만 필터링 (contracts > 0)
            open_positions = [p for p in positions if float(p.get('contracts', 0)) > 0]
            print(f"✅ 포지션 조회 성공: {len(open_positions)}개 오픈")
            return open_positions
        except Exception as e:
            print(f"❌ 포지션 조회 실패: {e}")
            raise

    def fetch_open_orders(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        미체결 주문 조회

        Args:
            symbol: 심볼 (None이면 전체)

        Returns:
            List[Dict]: 미체결 주문 목록
        """
        try:
            orders = self.exchange.fetch_open_orders(symbol)
            print(f"✅ 미체결 주문 조회 성공: {len(orders)}개")
            return orders
        except Exception as e:
            print(f"❌ 미체결 주문 조회 실패: {e}")
            raise

    # =============================================
    # Trading APIs (추후 구현)
    # =============================================

    def create_market_order(
        self,
        symbol: str,
        side: str,
        amount: float,
        leverage: int = 1
    ) -> Dict[str, Any]:
        """
        Market 주문 생성 (추후 구현)

        Args:
            symbol: 심볼
            side: 'buy' or 'sell'
            amount: 수량
            leverage: 레버리지
        """
        raise NotImplementedError("Trading APIs는 추후 구현 예정")

    # =============================================
    # Utility Methods
    # =============================================

    def get_exchange_info(self) -> Dict[str, Any]:
        """
        거래소 정보 조회

        Returns:
            Dict: {
                'id': 'binance',
                'name': 'Binance',
                'has': {...},
                'timeframes': {...},
                ...
            }
        """
        return {
            'id': self.exchange.id,
            'name': self.exchange.name,
            'version': self.exchange.version,
            'testnet': self.testnet,
            'has_fetch_ohlcv': self.exchange.has['fetchOHLCV'],
            'has_fetch_ticker': self.exchange.has['fetchTicker'],
            'has_fetch_funding_rate': self.exchange.has.get('fetchFundingRate', False),
            'timeframes': list(self.exchange.timeframes.keys()),
        }

