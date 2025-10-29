"""
자금 관리 - 현물/선물 잔고 조회 및 이체
"""
import streamlit as st
from utils.api_client import APIClient
from datetime import datetime

st.set_page_config(page_title="Wallet", page_icon="▲", layout="wide")

# API Client 초기화
api_client = APIClient()

# 로그인 확인
if "access_token" not in st.session_state:
    st.warning("로그인이 필요합니다.")
    st.page_link("pages/2_로그인.py", label="로그인하러 가기")
    st.stop()

st.title("Wallet Management")
st.markdown("현물 지갑과 선물 지갑 간 자금을 이체합니다.")

# =============================================
# 1. 잔고 조회
# =============================================

st.header("Balance")

with st.spinner("잔고 조회 중..."):
    balance_result = api_client.get_all_balances(st.session_state.access_token)

if not balance_result["success"]:
    st.error(f"잔고 조회 실패: {balance_result.get('error', '알 수 없는 오류')}")
    st.stop()

balances = balance_result["data"]
spot_balances = balances.get("spot", {})
futures_balances = balances.get("futures", {})

# 2개 컬럼으로 현물/선물 표시
col1, col2 = st.columns(2)

with col1:
    st.subheader("Spot Wallet")

    # USDT 잔고
    usdt_spot = spot_balances.get("USDT", {})
    if usdt_spot:
        st.metric(
            label="USDT",
            value=f"{usdt_spot.get('total', 0):,.2f}",
            delta=f"사용 가능: {usdt_spot.get('free', 0):,.2f}"
        )
    else:
        st.info("USDT 잔고 없음")

    # BTC 잔고
    btc_spot = spot_balances.get("BTC", {})
    if btc_spot and btc_spot.get('total', 0) > 0:
        st.metric(
            label="BTC",
            value=f"{btc_spot.get('total', 0):.6f}",
            delta=f"사용 가능: {btc_spot.get('free', 0):.6f}"
        )

with col2:
    st.subheader("Futures Wallet")

    # USDT 잔고
    usdt_futures = futures_balances.get("USDT", {})
    if usdt_futures:
        st.metric(
            label="USDT",
            value=f"{usdt_futures.get('total', 0):,.2f}",
            delta=f"사용 가능: {usdt_futures.get('free', 0):,.2f}"
        )
    else:
        st.info("USDT 잔고 없음")

    # BTC 잔고
    btc_futures = futures_balances.get("BTC", {})
    if btc_futures and btc_futures.get('total', 0) > 0:
        st.metric(
            label="BTC",
            value=f"{btc_futures.get('total', 0):.6f}",
            delta=f"사용 가능: {btc_futures.get('free', 0):.6f}"
        )

st.markdown("---")

# =============================================
# 2. 자금 이체
# =============================================

st.header("Transfer")

# 이체 정보 표시
with st.expander("Transfer Information", expanded=False):
    st.markdown("""
    **수수료**: 무료 (내부 이체)
    **최소 금액**: 0.01 USDT
    **예상 시간**: 1-3초 (즉시)
    **Rate Limit**: 1분에 5회까지

    ⚠️ **주의사항**:
    - 현물 지갑에서 선물 지갑으로 이체해야 선물 거래가 가능합니다
    - 이체 후 즉시 반영됩니다 (새로고침 필요)
    """)

col_left, col_right = st.columns([1, 1])

with col_left:
    # 이체 방향 선택
    direction = st.selectbox(
        "이체 방향",
        options=["현물 → 선물", "선물 → 현물"],
        index=0,
        help="자금을 이동할 방향을 선택하세요"
    )

    # 자산 선택
    asset = st.selectbox(
        "자산",
        options=["USDT", "BTC"],
        index=0,
        help="이체할 자산을 선택하세요"
    )

    # 사용 가능 금액 표시
    if direction == "현물 → 선물":
        available = spot_balances.get(asset, {}).get('free', 0)
        direction_code = "spot_to_futures"
    else:
        available = futures_balances.get(asset, {}).get('free', 0)
        direction_code = "futures_to_spot"

    st.info(f"사용 가능: {available:,.6f} {asset}")

    # 이체 금액 입력
    amount = st.number_input(
        "이체 금액",
        min_value=0.01,
        max_value=float(available) if available > 0 else 0.01,
        value=min(10.0, float(available)) if available >= 10 else 0.01,
        step=0.01 if asset == "USDT" else 0.0001,
        help=f"최소 0.01 {asset}"
    )

with col_right:
    st.subheader("Preview")

    # 미리보기 박스
    preview_container = st.container()

    with preview_container:
        if direction == "현물 → 선물":
            st.markdown(f"""
            **From**: Spot Wallet
            **To**: Futures Wallet

            **Amount**: `{amount:,.6f} {asset}`
            **Fee**: `FREE`
            **Receive**: `{amount:,.6f} {asset}`

            **Est. Time**: 1-3 sec
            """)
        else:
            st.markdown(f"""
            **From**: Futures Wallet
            **To**: Spot Wallet

            **Amount**: `{amount:,.6f} {asset}`
            **Fee**: `FREE`
            **Receive**: `{amount:,.6f} {asset}`

            **Est. Time**: 1-3 sec
            """)

    # 이체 후 잔고 예상
    st.markdown("---")
    st.caption("**이체 후 예상 잔고**")

    if direction == "현물 → 선물":
        spot_after = available - amount
        futures_after = futures_balances.get(asset, {}).get('free', 0) + amount
        st.caption(f"현물: {spot_after:,.6f} {asset}")
        st.caption(f"선물: {futures_after:,.6f} {asset}")
    else:
        spot_after = spot_balances.get(asset, {}).get('free', 0) + amount
        futures_after = available - amount
        st.caption(f"현물: {spot_after:,.6f} {asset}")
        st.caption(f"선물: {futures_after:,.6f} {asset}")

# 이체 실행 버튼
st.markdown("---")

col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])

with col_btn2:
    if st.button("EXECUTE TRANSFER", type="primary", use_container_width=True):
        # 검증
        if amount < 0.01:
            st.error(f"최소 이체 금액은 0.01 {asset}입니다.")
        elif amount > available:
            st.error(f"잔고가 부족합니다. (사용 가능: {available:,.6f} {asset})")
        else:
            with st.spinner("이체 처리 중..."):
                transfer_result = api_client.transfer_funds(
                    token=st.session_state.access_token,
                    asset=asset,
                    amount=amount,
                    direction=direction_code
                )

            if transfer_result["success"]:
                data = transfer_result["data"]
                st.success(f"""
                Transfer Completed

                **Transaction ID**: {data.get('tranId', 'N/A')}
                **Amount**: {data.get('amount', 0):,.6f} {data.get('asset', asset)}
                **Direction**: {data.get('from_wallet', '')} → {data.get('to_wallet', '')}
                """)

                # 3초 후 자동 새로고침
                st.info("3초 후 자동으로 새로고침됩니다...")
                import time
                time.sleep(3)
                st.rerun()
            else:
                st.error(f"이체 실패: {transfer_result.get('error', '알 수 없는 오류')}")

# =============================================
# 3. 이체 내역 (추후 구현)
# =============================================

st.markdown("---")

with st.expander("Transfer History (Coming Soon)", expanded=False):
    st.info("이체 내역 조회 기능은 추후 업데이트 예정입니다.")
    st.markdown("""
    **향후 기능**:
    - 최근 10건 이체 내역 표시
    - 날짜별 필터링
    - CSV 다운로드
    """)

# Footer
st.markdown("---")
st.caption(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

