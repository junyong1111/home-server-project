"""
AXIS Capital - 홈
AI 기반 선물 트레이딩 시스템
"""
import streamlit as st
from utils.api_client import APIClient

# 페이지 설정
st.set_page_config(
    page_title="AXIS Capital",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Client 초기화
if "api_client" not in st.session_state:
    st.session_state.api_client = APIClient()

# 로그인 상태
if "token" not in st.session_state:
    st.session_state.token = None
if "user_info" not in st.session_state:
    st.session_state.user_info = None

# 커스텀 CSS
st.markdown("""
<style>
    h1 { font-weight: 300; letter-spacing: -1px; }
    h2 { font-weight: 300; font-size: 1.8rem; margin-top: 2rem; }
    h3 { font-weight: 400; font-size: 1.3rem; color: #00D9FF; }
    [data-testid="stMetricValue"] { font-size: 2rem; font-weight: 300; }
    .block-container { padding-top: 2rem; }
</style>
""", unsafe_allow_html=True)

# 헤더
st.title("AXIS Capital")
st.caption("AI 기반 선물 트레이딩 시스템")

st.divider()

# 시스템 상태
col1, col2, col3 = st.columns(3)

with col1:
    health = st.session_state.api_client.health_check()
    status = "정상" if health.get("status") == "healthy" else "오프라인"
    st.metric("시스템 상태", status)

with col2:
    if st.session_state.token:
        st.metric("세션", "활성", st.session_state.user_info.get("username", ""))
    else:
        st.metric("세션", "비활성", "로그인 필요")

with col3:
    backend_status = "연결됨" if health.get("status") == "healthy" else "연결 안 됨"
    st.metric("백엔드 API", backend_status)

st.divider()

# 메인 콘텐츠
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("개요")
    st.markdown("""
    AXIS Capital은 AI 기반의 자동화된 암호화폐 선물 트레이딩 시스템입니다.

    **핵심 기능**
    - AI 기반 시장 분석 및 의사결정
    - 자동화된 데이터 수집 및 처리
    - 동적 레버리지를 활용한 선물 거래
    - 실시간 리스크 관리
    - 증거 기반 의사결정 시스템
    """)

    st.subheader("기술 스택")
    tech_col1, tech_col2 = st.columns(2)

    with tech_col1:
        st.markdown("""
        **백엔드**
        - FastAPI (REST API)
        - PostgreSQL + TimescaleDB
        - Redis (캐시)
        - Celery (작업 큐)
        """)

    with tech_col2:
        st.markdown("""
        **AI & 자동화**
        - GPT-4o, GPT-o1 (분석)
        - n8n (워크플로우)
        - CCXT (거래소 API)
        """)

with col_right:
    st.subheader("빠른 시작")

    if not st.session_state.token:
        if st.button("회원가입", use_container_width=True, type="primary"):
            st.switch_page("pages/1_회원가입.py")

        if st.button("로그인", use_container_width=True):
            st.switch_page("pages/2_로그인.py")
    else:
        if st.button("대시보드", use_container_width=True, type="primary"):
            st.switch_page("pages/3_대시보드.py")

        if st.button("API 키 관리", use_container_width=True):
            st.switch_page("pages/4_API키관리.py")

    st.divider()

    st.caption("**버전** 1.0.0")
    st.caption("**최종 업데이트** 2025-10-28")
