"""
AXIS Capital - 대시보드
"""
import streamlit as st
from datetime import datetime
from utils.api_client import APIClient
import pandas as pd
import altair as alt
import requests

st.set_page_config(
    page_title="대시보드 - AXIS Capital",
    page_icon="📈",
    layout="wide"
)

# API Client
if "api_client" not in st.session_state:
    st.session_state.api_client = APIClient()

# 인증 확인
if not st.session_state.get("token"):
    st.warning("로그인이 필요합니다.")
    if st.button("로그인하러 가기"):
        st.switch_page("pages/2_로그인.py")
    st.stop()

st.session_state.api_client.set_token(st.session_state.token)

# 커스텀 CSS
st.markdown("""
<style>
    h1 { font-weight: 300; letter-spacing: -1px; }
    h2 { font-weight: 300; font-size: 1.5rem; color: #00D9FF; }
    [data-testid="stMetricValue"] { font-size: 2.5rem; font-weight: 300; }
</style>
""", unsafe_allow_html=True)

# 사용자 데이터 조회
with st.spinner("데이터 로딩 중..."):
    result = st.session_state.api_client.get_me()

if not result["success"]:
    st.error(f"데이터 로드 실패: {result['error']}")
    if "token" in result['error'].lower():
        if st.button("로그아웃 후 다시 로그인"):
            st.session_state.token = None
            st.session_state.user_info = None
            st.session_state.api_client.set_token(None)
            st.switch_page("pages/2_로그인.py")
    st.stop()

user_data = result["data"]

# 헤더
st.title("대시보드")
st.caption(f"안녕하세요, **{user_data['username']}**님")

st.divider()

# 계정 개요
st.subheader("계정 개요")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("사용자명", user_data["username"])

with col2:
    status = "활성" if user_data["is_active"] else "비활성"
    st.metric("상태", status)

with col3:
    risk_map = {
        "conservative": "보수적",
        "balanced": "균형",
        "aggressive": "공격적"
    }
    st.metric("리스크 프로필", risk_map.get(user_data["risk_profile"], user_data["risk_profile"]))

with col4:
    st.metric("사용자 ID", user_data["user_id"])

st.divider()

# 시장 데이터
st.subheader("시장 데이터")

# 외부 API로 실시간 데이터 조회
def get_binance_price():
    """Binance Public API로 BTC 가격 조회"""
    try:
        response = requests.get("https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT", timeout=5)
        response.raise_for_status()
        data = response.json()
        return {
            "price": float(data['lastPrice']),
            "change_24h": float(data['priceChangePercent']),
            "high_24h": float(data['highPrice']),
            "low_24h": float(data['lowPrice']),
            "volume_24h": float(data['volume'])
        }
    except:
        return None

def get_exchange_rate():
    """환율 조회 (USD/KRW)"""
    try:
        # exchangerate-api.com 무료 API
        response = requests.get("https://open.er-api.com/v6/latest/USD", timeout=5)
        response.raise_for_status()
        data = response.json()
        return data['rates'].get('KRW', 1300)  # 기본값 1300
    except:
        return 1300  # 실패 시 대략적인 환율

def get_gold_price():
    """금값 조회 (USD/oz)"""
    try:
        # goldapi.io 대체 - 간단하게 고정값 사용 또는 다른 API
        # 실제 운영에서는 goldapi.io 또는 metals-api.com 사용
        return 2050.0  # USD/oz (대략적인 값)
    except:
        return 2050.0

# 데이터 조회
btc_data = get_binance_price()
usd_krw = get_exchange_rate()
gold_price = get_gold_price()

# 4개 컬럼으로 표시
col1, col2, col3, col4 = st.columns(4)

with col1:
    if btc_data:
        btc_price_usd = btc_data['price']
        btc_price_krw = btc_price_usd * usd_krw
        st.metric(
            "BTC 가격 (USD)",
            f"${btc_price_usd:,.2f}",
            f"{btc_data['change_24h']:+.2f}%"
        )
        st.caption(f"₩{btc_price_krw:,.0f}")
    else:
        st.metric("BTC 가격", "N/A")

with col2:
    st.metric(
        "환율 (USD/KRW)",
        f"₩{usd_krw:,.2f}"
    )
    st.caption("1 USD = ₩ KRW")

with col3:
    gold_price_krw = gold_price * usd_krw / 31.1035  # oz → gram 변환
    st.metric(
        "금 시세 (USD)",
        f"${gold_price:,.2f}/oz"
    )
    st.caption(f"₩{gold_price_krw:,.0f}/g")

with col4:
    if btc_data:
        st.metric(
            "24시간 거래량",
            f"{btc_data['volume_24h']:,.0f} BTC"
        )
        st.caption(f"고점: ${btc_data['high_24h']:,.0f}")
    else:
        st.metric("거래량", "N/A")

# BTC 상세 정보
if btc_data:
    st.write("")
    detail_col1, detail_col2, detail_col3 = st.columns(3)

    with detail_col1:
        st.write("**24시간 고가**")
        st.write(f"${btc_data['high_24h']:,.2f}")
        st.caption(f"₩{btc_data['high_24h'] * usd_krw:,.0f}")

    with detail_col2:
        st.write("**24시간 저가**")
        st.write(f"${btc_data['low_24h']:,.2f}")
        st.caption(f"₩{btc_data['low_24h'] * usd_krw:,.0f}")

    with detail_col3:
        st.write("**가격 변동폭**")
        price_range = btc_data['high_24h'] - btc_data['low_24h']
        st.write(f"${price_range:,.2f}")
        st.caption(f"₩{price_range * usd_krw:,.0f}")

st.divider()

# AI 의사결정
st.subheader("AI 의사결정")

ai_col1, ai_col2 = st.columns([2, 1])

with ai_col1:
    # 최신 시장 레짐 조회
    regime_result = st.session_state.api_client.get_latest_regime()

    if regime_result["success"]:
        regime_data = regime_result["data"]
        regime_emoji = {
            "Bull Trend": "📈",
            "Bear Trend": "📉",
            "Consolidation": "➡️"
        }

        regime_color = {
            "Bull Trend": "#00FF00",
            "Bear Trend": "#FF0000",
            "Consolidation": "#FFA500"
        }

        regime_text = regime_data["regime"]
        st.markdown(f"### {regime_emoji.get(regime_text, '📊')} 현재 레짐: <span style='color:{regime_color.get(regime_text, '#FFFFFF')}'>{regime_text}</span>", unsafe_allow_html=True)

        regime_metric_col1, regime_metric_col2, regime_metric_col3 = st.columns(3)
        with regime_metric_col1:
            st.metric("확신도", f"{float(regime_data['confidence']) * 100:.1f}%")
        with regime_metric_col2:
            if regime_data.get("rsi"):
                st.metric("RSI", f"{float(regime_data['rsi']):.1f}")
        with regime_metric_col3:
            if regime_data.get("adx"):
                st.metric("ADX", f"{float(regime_data['adx']):.1f}")
    else:
        st.info("시장 레짐 정보가 없습니다.")

with ai_col2:
    # 최근 AI 의사결정
    decisions_result = st.session_state.api_client.get_my_decisions(limit=3)

    if decisions_result["success"] and decisions_result["data"]:
        st.write("**최근 AI 결정**")
        for decision in decisions_result["data"][:3]:
            agent_name = decision["agent_name"].replace("AXIS-", "")
            decision_text = decision["decision"]
            confidence = float(decision["confidence"]) * 100

            st.caption(f"**{agent_name}**: {decision_text} ({confidence:.0f}%)")

        if st.button("전체 보기", use_container_width=True, type="primary"):
            st.switch_page("pages/5_AI의사결정.py")
    else:
        st.info("AI 의사결정 기록이 없습니다.")

st.divider()

# API 설정
st.subheader("API 설정")

api_col1, api_col2 = st.columns([2, 1])

with api_col1:
    st.write(f"**Binance API Key (마스킹):** `{user_data['binance_api_key_masked']}`")
    st.caption("마지막 업데이트: " + datetime.fromisoformat(user_data["updated_at"].replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M"))

with api_col2:
    if st.button("API 키 업데이트", use_container_width=True):
        st.switch_page("pages/4_API키관리.py")

st.divider()

# 액션
action_col1, action_col2 = st.columns([3, 1])

with action_col2:
    if st.button("로그아웃", use_container_width=True):
        st.session_state.token = None
        st.session_state.user_info = None
        st.session_state.api_client.set_token(None)
        st.switch_page("Home.py")
