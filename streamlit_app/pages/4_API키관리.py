"""
AXIS Capital - API 키 관리
"""
import streamlit as st
from utils.api_client import APIClient

st.set_page_config(
    page_title="API 키 관리 - AXIS Capital",
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
</style>
""", unsafe_allow_html=True)

# 헤더
st.title("API 키 관리")
st.caption("Binance API 인증 정보 관리")

st.divider()

# 현재 API 키 조회
with st.spinner("현재 API 키 로딩 중..."):
    result = st.session_state.api_client.get_me()

if not result["success"]:
    st.error(f"데이터 로드 실패: {result['error']}")
    st.stop()

user_data = result["data"]

st.subheader("현재 API 키")
st.code(user_data['binance_api_key_masked'], language=None)
st.caption("보안을 위해 마지막 6자리만 표시됩니다.")

st.divider()

# 업데이트 폼
st.subheader("API 인증 정보 업데이트")

st.warning("⚠️ API 키가 정확한지 확인하세요. 잘못된 키는 거래를 방해할 수 있습니다.")

with st.form("update_api_keys_form"):
    new_api_key = st.text_input(
        "새 Binance API Key",
        type="password",
        placeholder="새 Binance API Key를 입력하세요"
    )

    new_api_secret = st.text_input(
        "새 Binance API Secret",
        type="password",
        placeholder="새 Binance API Secret을 입력하세요"
    )

    st.divider()

    col1, col2 = st.columns([1, 3])

    with col1:
        submitted = st.form_submit_button("API 키 업데이트", type="primary", use_container_width=True)

    with col2:
        if st.form_submit_button("취소", use_container_width=True):
            st.switch_page("pages/3_대시보드.py")

    if submitted:
        if not new_api_key:
            st.error("API Key가 필요합니다.")
        elif not new_api_secret:
            st.error("API Secret이 필요합니다.")
        else:
            with st.spinner("API 키 업데이트 중..."):
                result = st.session_state.api_client.update_api_keys(
                    binance_api_key=new_api_key,
                    binance_api_secret=new_api_secret
                )

            if result["success"]:
                st.success("API 키가 성공적으로 업데이트되었습니다!")
                response_data = result["data"]

                st.code(response_data['binance_api_key_masked'], language=None)
                st.caption("새 API 키가 암호화되어 안전하게 저장되었습니다.")

                import time
                time.sleep(2)
                st.switch_page("pages/3_대시보드.py")
            else:
                st.error(f"업데이트 실패: {result['error']}")

st.divider()

# 가이드
st.subheader("Binance API 키 발급 방법")

with st.expander("가이드 보기"):
    st.markdown("""
    ### Binance API 키 생성 단계

    1. **Binance 로그인**
       - https://www.binance.com 접속
       - 계정에 로그인

    2. **API 관리 페이지 이동**
       - 프로필 아이콘 클릭 (우측 상단)
       - "API Management" 선택

    3. **새 API 키 생성**
       - "Create API" 클릭
       - 라벨 입력 (예: "AXIS 트레이딩 봇")
       - 보안 인증 완료

    4. **권한 설정**
       - Reading 활성화 (필수)
       - Futures 활성화 (필수)
       - Spot & Margin Trading 활성화 (선택)
       - 출금(Withdrawals) 권한은 비활성화

    5. **키 저장**
       - API Key와 Secret Key 복사
       - 안전한 곳에 보관
       - Secret Key는 한 번만 표시됩니다

    6. **IP 화이트리스트 (선택사항)**
       - 추가 보안을 위해 서버 IP 추가

    ### 보안 팁

    - API 키를 절대 공유하지 마세요
    - 정기적으로 키를 교체하세요
    - 출금 권한은 비활성화하세요
    - Binance에서 API 사용량을 모니터링하세요
    - 유출 시 즉시 키를 취소하세요
    """)

st.divider()

if st.button("대시보드로 돌아가기"):
    st.switch_page("pages/3_대시보드.py")
