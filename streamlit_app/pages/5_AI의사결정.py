"""
AXIS Capital - AI 의사결정
"""
import streamlit as st
from datetime import datetime
from utils.api_client import APIClient
import json

st.set_page_config(
    page_title="AI 의사결정 - AXIS Capital",
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
    .evidence-card {
        background-color: #1A1D24;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #00D9FF;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# 헤더
st.title("AI 의사결정")
st.caption("AI 에이전트의 의사결정 기록 및 분석")

st.divider()

# 탭
tab1, tab2, tab3 = st.tabs(["최근 의사결정", "시장 레짐", "통계"])

# ===== Tab 1: 최근 의사결정 =====
with tab1:
    # 조회 개수 선택
    limit = st.selectbox("조회 개수", [5, 10, 20, 50], index=1)

    # AI 의사결정 조회
    with st.spinner("데이터 로딩 중..."):
        result = st.session_state.api_client.get_my_decisions(limit=limit)

    if not result["success"]:
        st.error(f"데이터 로드 실패: {result['error']}")
        st.stop()

    decisions = result["data"]

    if not decisions:
        st.info("아직 AI 의사결정 기록이 없습니다.")
    else:
        st.success(f"총 {len(decisions)}개의 의사결정 기록")

        # 의사결정 목록
        for decision in decisions:
            with st.expander(
                f"**{decision['agent_name']}** - {decision['decision']} ({float(decision['confidence']) * 100:.1f}%) - "
                f"{datetime.fromisoformat(decision['created_at'].replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M')}"
            ):
                # 기본 정보
                info_col1, info_col2, info_col3, info_col4 = st.columns(4)

                with info_col1:
                    st.metric("에이전트", decision['agent_name'].replace("AXIS-", ""))

                with info_col2:
                    st.metric("역할", decision['agent_role'])

                with info_col3:
                    st.metric("결정 유형", decision['decision_type'])

                with info_col4:
                    st.metric("확신도", f"{float(decision['confidence']) * 100:.1f}%")

                st.divider()

                # Reasoning (AI의 설명)
                st.subheader("AI의 판단 근거")
                st.write(decision['reasoning'])

                st.divider()

                # Evidence (증거)
                st.subheader("Evidence")

                evidence_list = decision.get('evidence', [])
                if evidence_list:
                    for idx, ev in enumerate(evidence_list):
                        ev_type = ev.get('type', 'Unknown')

                        st.markdown(f"""
                        <div class="evidence-card">
                            <strong>#{idx + 1} - {ev_type.upper()}</strong>
                        </div>
                        """, unsafe_allow_html=True)

                        ev_cols = st.columns(4)

                        # Evidence 상세 정보 표시
                        col_idx = 0
                        for key, value in ev.items():
                            if key != 'type' and col_idx < 4:
                                with ev_cols[col_idx]:
                                    st.caption(f"**{key}**: {value}")
                                    col_idx += 1
                else:
                    st.info("Evidence 정보가 없습니다.")

                st.divider()

                # LLM 정보
                st.subheader("LLM 정보")

                llm_col1, llm_col2, llm_col3, llm_col4 = st.columns(4)

                with llm_col1:
                    if decision.get('llm_model'):
                        st.metric("모델", decision['llm_model'])

                with llm_col2:
                    if decision.get('prompt_tokens') and decision.get('completion_tokens'):
                        total_tokens = decision['prompt_tokens'] + decision['completion_tokens']
                        st.metric("총 토큰", f"{total_tokens:,}")

                with llm_col3:
                    if decision.get('llm_cost'):
                        st.metric("비용 (USD)", f"${float(decision['llm_cost']):.4f}")

                with llm_col4:
                    if decision.get('execution_time_ms'):
                        st.metric("실행 시간", f"{decision['execution_time_ms']}ms")

# ===== Tab 2: 시장 레짐 =====
with tab2:
    st.subheader("현재 시장 레짐")

    # 최신 레짐 조회
    regime_result = st.session_state.api_client.get_latest_regime()

    if regime_result["success"]:
        regime_data = regime_result["data"]

        # 레짐 표시
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

        st.markdown(
            f"<h1 style='text-align: center; color: {regime_color.get(regime_text, '#FFFFFF')}'>"
            f"{regime_emoji.get(regime_text, '📊')} {regime_text}</h1>",
            unsafe_allow_html=True
        )

        st.divider()

        # 메트릭
        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

        with metric_col1:
            st.metric("확신도", f"{float(regime_data['confidence']) * 100:.1f}%")

        with metric_col2:
            if regime_data.get("adx"):
                st.metric("ADX", f"{float(regime_data['adx']):.1f}")

        with metric_col3:
            if regime_data.get("rsi"):
                st.metric("RSI", f"{float(regime_data['rsi']):.1f}")

        with metric_col4:
            if regime_data.get("price_vs_ma50"):
                st.metric("Price/MA50", f"{float(regime_data['price_vs_ma50']):.2f}")

        st.divider()

        # AI 판단 근거
        if regime_data.get("ai_rationale"):
            st.subheader("AI 판단 근거")
            st.write(regime_data["ai_rationale"])

        st.divider()

        # 레짐 변경 이력
        st.subheader("레짐 변경 이력")

        history_result = st.session_state.api_client.get_regime_history(limit=10)

        if history_result["success"] and history_result["data"]:
            history_data = history_result["data"]

            for regime in history_data:
                regime_icon = regime_emoji.get(regime["regime"], "📊")
                regime_name = regime["regime"]
                confidence = float(regime["confidence"]) * 100
                timestamp = datetime.fromisoformat(regime["created_at"].replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M")

                st.write(f"{regime_icon} **{regime_name}** ({confidence:.1f}%) - {timestamp}")
    else:
        st.info("시장 레짐 정보가 없습니다.")

# ===== Tab 3: 통계 =====
with tab3:
    st.subheader("AI 의사결정 통계")

    # 의사결정 조회
    result = st.session_state.api_client.get_my_decisions(limit=100)

    if result["success"] and result["data"]:
        decisions = result["data"]

        # 에이전트별 의사결정 수
        st.write("**에이전트별 의사결정 수**")

        agent_counts = {}
        for decision in decisions:
            agent = decision['agent_name']
            agent_counts[agent] = agent_counts.get(agent, 0) + 1

        for agent, count in sorted(agent_counts.items(), key=lambda x: x[1], reverse=True):
            st.write(f"- {agent}: {count}개")

        st.divider()

        # 총 LLM 비용
        total_cost = sum(float(d.get('llm_cost', 0)) for d in decisions if d.get('llm_cost'))
        total_tokens = sum(
            (d.get('prompt_tokens', 0) + d.get('completion_tokens', 0))
            for d in decisions
        )

        cost_col1, cost_col2 = st.columns(2)

        with cost_col1:
            st.metric("총 LLM 비용", f"${total_cost:.4f}")

        with cost_col2:
            st.metric("총 토큰 사용량", f"{total_tokens:,}")

        st.divider()

        # LLM 모델별 사용량
        st.write("**LLM 모델별 사용량**")

        model_counts = {}
        for decision in decisions:
            model = decision.get('llm_model', 'Unknown')
            model_counts[model] = model_counts.get(model, 0) + 1

        for model, count in sorted(model_counts.items(), key=lambda x: x[1], reverse=True):
            st.write(f"- {model}: {count}회")
    else:
        st.info("통계를 표시할 데이터가 없습니다.")

st.divider()

# 하단 액션
if st.button("대시보드로 돌아가기"):
    st.switch_page("pages/3_대시보드.py")

