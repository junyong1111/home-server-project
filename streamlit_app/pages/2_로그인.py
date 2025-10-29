"""
AXIS Capital - 로그인
"""
import streamlit as st
from utils.api_client import APIClient

st.set_page_config(
    page_title="로그인 - AXIS Capital",
    page_icon="📈",
    layout="wide"
)

# API Client
if "api_client" not in st.session_state:
    st.session_state.api_client = APIClient()

# 커스텀 CSS
st.markdown("""
<style>
    h1 { font-weight: 300; letter-spacing: -1px; }
</style>
""", unsafe_allow_html=True)

# 헤더
st.title("로그인")
st.caption("AXIS Capital 계정에 접속하세요")

st.divider()

# 이미 로그인한 경우
if st.session_state.get("token"):
    st.success(f"**{st.session_state.user_info['username']}**님으로 이미 로그인되어 있습니다")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("대시보드로 이동", type="primary", use_container_width=True):
            st.switch_page("pages/3_대시보드.py")
    with col2:
        if st.button("로그아웃", use_container_width=True):
            st.session_state.token = None
            st.session_state.user_info = None
            st.session_state.api_client.set_token(None)
            st.rerun()

    st.stop()

# 로그인 폼
with st.form("login_form"):
    username = st.text_input(
        "사용자명",
        placeholder="사용자명을 입력하세요"
    )

    password = st.text_input(
        "비밀번호",
        type="password",
        placeholder="비밀번호를 입력하세요"
    )

    st.divider()

    submitted = st.form_submit_button("로그인", type="primary", use_container_width=True)

    if submitted:
        if not username:
            st.error("사용자명이 필요합니다.")
        elif not password:
            st.error("비밀번호가 필요합니다.")
        else:
            with st.spinner("인증 중..."):
                result = st.session_state.api_client.login(username, password)

            if result["success"]:
                token_data = result["data"]
                st.session_state.token = token_data["access_token"]
                st.session_state.user_info = {
                    "user_id": token_data["user_id"],
                    "username": token_data["username"]
                }

                st.success("로그인 성공!")
                st.info("대시보드로 이동 중...")
                st.rerun()
            else:
                st.error(f"로그인 실패: {result['error']}")

st.divider()

# 추가 정보
col1, col2 = st.columns(2)

with col1:
    st.info("""
    **보안**
    - JWT 토큰 기반 인증
    - 24시간 세션 유효기간
    - HTTPS 연결 권장
    """)

with col2:
    st.warning("""
    **계정이 없으신가요?**
    회원가입 페이지에서
    새 계정을 만드세요.
    """)
