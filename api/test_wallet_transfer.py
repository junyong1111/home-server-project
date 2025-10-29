"""
자금 이체 기능 테스트
"""
import asyncio
from sqlalchemy.orm import Session
from api.core.database import get_db
from api.models.user import User
from api.services.binance_service import BinanceService


async def test_wallet_transfer():
    """현물/선물 잔고 조회 및 이체 테스트"""

    print("=" * 60)
    print("자금 이체 기능 테스트 시작")
    print("=" * 60)

    # DB 세션
    db = next(get_db())

    # devjun 사용자 조회
    user = db.query(User).filter(User.username == "devjun").first()
    if not user:
        print("❌ devjun 사용자를 찾을 수 없습니다.")
        return

    print(f"✅ 사용자: {user.username} (ID: {user.user_id})")
    print()

    # BinanceService 초기화
    binance = BinanceService(user, testnet=False)

    # =============================================
    # 1. 현물 잔고 조회
    # =============================================
    print("1️⃣ 현물 잔고 조회")
    print("-" * 60)

    try:
        spot_balance = binance.get_spot_balance()

        # USDT
        usdt_spot = spot_balance.get('USDT', {})
        print(f"USDT (현물)")
        print(f"  - 사용 가능: {usdt_spot.get('free', 0):,.2f}")
        print(f"  - 사용 중: {usdt_spot.get('used', 0):,.2f}")
        print(f"  - 총합: {usdt_spot.get('total', 0):,.2f}")

        # BTC
        btc_spot = spot_balance.get('BTC', {})
        if btc_spot.get('total', 0) > 0:
            print(f"BTC (현물)")
            print(f"  - 사용 가능: {btc_spot.get('free', 0):.6f}")
            print(f"  - 사용 중: {btc_spot.get('used', 0):.6f}")
            print(f"  - 총합: {btc_spot.get('total', 0):.6f}")

        print()

    except Exception as e:
        print(f"❌ 현물 잔고 조회 실패: {e}")
        print()

    # =============================================
    # 2. 선물 잔고 조회
    # =============================================
    print("2️⃣ 선물 잔고 조회")
    print("-" * 60)

    try:
        futures_balance = binance.get_futures_balance()

        # USDT
        usdt_futures = futures_balance.get('USDT', {})
        print(f"USDT (선물)")
        print(f"  - 사용 가능: {usdt_futures.get('free', 0):,.2f}")
        print(f"  - 사용 중: {usdt_futures.get('used', 0):,.2f}")
        print(f"  - 총합: {usdt_futures.get('total', 0):,.2f}")

        # BTC
        btc_futures = futures_balance.get('BTC', {})
        if btc_futures.get('total', 0) > 0:
            print(f"BTC (선물)")
            print(f"  - 사용 가능: {btc_futures.get('free', 0):.6f}")
            print(f"  - 사용 중: {btc_futures.get('used', 0):.6f}")
            print(f"  - 총합: {btc_futures.get('total', 0):.6f}")

        print()

    except Exception as e:
        print(f"❌ 선물 잔고 조회 실패: {e}")
        print()

    # =============================================
    # 3. 이체 테스트 (선택적)
    # =============================================
    print("3️⃣ 이체 테스트 (수동 확인 필요)")
    print("-" * 60)
    print("⚠️ 실제 자금 이체는 Streamlit UI에서 수행하세요.")
    print()
    print("테스트 방법:")
    print("1. Streamlit 실행: cd streamlit_app && streamlit run Home.py")
    print("2. 로그인 → 자금관리 페이지 이동")
    print("3. 현물 → 선물 (또는 반대) 이체 실행")
    print()

    # 이체 가능 여부 확인
    spot_usdt = usdt_spot.get('free', 0)
    futures_usdt = usdt_futures.get('free', 0)

    if spot_usdt > 10:
        print(f"✅ 현물 → 선물 이체 가능 (현물: {spot_usdt:,.2f} USDT)")
    elif futures_usdt > 10:
        print(f"✅ 선물 → 현물 이체 가능 (선물: {futures_usdt:,.2f} USDT)")
    else:
        print("⚠️ 이체 가능한 잔고가 부족합니다 (최소 10 USDT)")

    print()
    print("=" * 60)
    print("테스트 완료")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_wallet_transfer())

