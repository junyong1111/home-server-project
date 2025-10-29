"""
AXIS Capital - 회원가입
"""
import streamlit as st
from utils.api_client import APIClient

st.set_page_config(
    page_title="회원가입 - AXIS Capital",
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
    .stButton>button { font-weight: 500; }
</style>
""", unsafe_allow_html=True)

# 헤더
st.title("계정 생성")
st.caption("AXIS Capital 트레이딩 플랫폼 가입")

st.divider()

# 회원가입 폼
with st.form("register_form"):
    st.subheader("계정 정보")

    col1, col2 = st.columns(2)

    with col1:
        username = st.text_input(
            "사용자명",
            placeholder="최소 3자 이상",
            help="고유한 사용자명을 입력하세요"
        )

    with col2:
        email = st.text_input(
            "이메일",
            placeholder="your@email.com",
            help="알림을 받을 이메일 주소"
        )

    password = st.text_input(
        "비밀번호",
        type="password",
        placeholder="최소 4자 이상",
        help="안전한 비밀번호를 사용하세요"
    )

    password_confirm = st.text_input(
        "비밀번호 확인",
        type="password",
        placeholder="비밀번호를 다시 입력하세요"
    )

    st.divider()

    st.subheader("Binance API 인증 정보")
    st.info("API 키는 암호화되어 안전하게 저장됩니다.")

    binance_api_key = st.text_input(
        "Binance API Key",
        type="password",
        placeholder="Binance API Key 입력"
    )

    binance_api_secret = st.text_input(
        "Binance API Secret",
        type="password",
        placeholder="Binance API Secret 입력"
    )

    st.divider()

    st.subheader("리스크 프로필")

    risk_profile = st.selectbox(
        "거래 스타일",
        options=["conservative", "balanced", "aggressive"],
        index=1,
        help="레버리지와 리스크 허용도를 결정합니다"
    )

    risk_descriptions = {
        "conservative": "보수적: 레버리지 1-3x, 낮은 리스크",
        "balanced": "균형: 레버리지 3-7x, 중간 리스크",
        "aggressive": "공격적: 레버리지 7-15x, 높은 리스크"
    }
    st.caption(risk_descriptions[risk_profile])

    st.divider()

    # 제출 버튼
    submitted = st.form_submit_button("계정 생성", type="primary", use_container_width=True)

    if submitted:
        # 유효성 검사
        errors = []

        if not username or len(username) < 3:
            errors.append("사용자명은 최소 3자 이상이어야 합니다.")

        if not email or "@" not in email:
            errors.append("올바른 이메일 주소를 입력하세요.")

        if not password or len(password) < 4:
            errors.append("비밀번호는 최소 4자 이상이어야 합니다.")

        if password != password_confirm:
            errors.append("비밀번호가 일치하지 않습니다.")

        if not binance_api_key:
            errors.append("Binance API Key가 필요합니다.")

        if not binance_api_secret:
            errors.append("Binance API Secret이 필요합니다.")

        if errors:
            for error in errors:
                st.error(error)
        else:
            # API 호출
            with st.spinner("계정 생성 중..."):
                result = st.session_state.api_client.register(
                    username=username,
                    email=email,
                    password=password,
                    binance_api_key=binance_api_key,
                    binance_api_secret=binance_api_secret,
                    risk_profile=risk_profile
                )

            if result["success"]:
                st.success("계정이 성공적으로 생성되었습니다!")
                user_data = result["data"]

                with st.expander("계정 상세정보"):
                    st.write(f"**사용자명:** {user_data['username']}")
                    st.write(f"**이메일:** {user_data['email']}")
                    st.write(f"**리스크 프로필:** {user_data['risk_profile']}")
                    st.write(f"**API Key (마스킹):** {user_data['binance_api_key_masked']}")

                st.info("로그인 페이지로 이동하여 로그인하세요.")
            else:
                st.error(f"회원가입 실패: {result['error']}")

st.divider()
st.caption("이미 계정이 있으신가요? → 로그인 페이지로 이동")
