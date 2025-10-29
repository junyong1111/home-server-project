"""
AXIS Capital - 뉴스 & 소셜 감성
"""
import streamlit as st
from datetime import datetime
from utils.api_client import APIClient

st.set_page_config(
    page_title="뉴스 - AXIS Capital",
    page_icon="▲",
    layout="wide"
)

# API Client
if "api_client" not in st.session_state:
    st.session_state.api_client = APIClient()

# 로그인 확인 (뉴스는 로그인 없이도 볼 수 있도록 할 수도 있음)
# 여기서는 로그인 필요 없이 누구나 볼 수 있도록 설정

# 커스텀 CSS
st.markdown("""
<style>
    h1 { font-weight: 300; letter-spacing: -1px; }
    h2 { font-weight: 300; font-size: 1.8rem; color: #00D9FF; }
    h3 { font-weight: 400; font-size: 1.3rem; }
    [data-testid="stMetricValue"] { font-size: 2.5rem; font-weight: 300; }
    .news-card {
        background: rgba(0, 217, 255, 0.05);
        border-left: 3px solid #00D9FF;
        padding: 1rem;
        margin-bottom: 1rem;
        border-radius: 4px;
    }
    .sentiment-positive { color: #00FF88; font-weight: 600; }
    .sentiment-negative { color: #FF4444; font-weight: 600; }
    .sentiment-neutral { color: #888888; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# 헤더
col1, col2 = st.columns([4, 1])
with col1:
    st.title("News & Social Sentiment")
    st.caption("실시간 암호화폐 뉴스 및 소셜 감성 분석")

with col2:
    if st.button("🔄 새로고침", use_container_width=True):
        result = st.session_state.api_client.refresh_news()
        if result["success"]:
            st.success("새로고침 완료!")
            st.rerun()
        else:
            st.error(f"새로고침 실패: {result['error']}")

st.divider()

# 탭 구성
tab1, tab2 = st.tabs(["📰 Crypto News", "💬 Social Sentiment"])

# ===== Tab 1: 뉴스 =====
with tab1:
    st.subheader("Cryptocurrency News")

    with st.spinner("뉴스 로딩 중..."):
        news_result = st.session_state.api_client.get_crypto_news()

    if news_result["success"]:
        news_data = news_result["data"]

        # 캐시 정보
        if news_data.get("from_cache"):
            st.info(f"캐시된 데이터 (수집 시간: {news_data.get('cached_at', 'N/A')})")
        else:
            st.success(f"실시간 수집 완료 (수집 시간: {news_data.get('timestamp', 'N/A')})")

        st.markdown(f"**총 {news_data.get('count', 0)}개 뉴스**")
        st.divider()

        # 뉴스 목록
        news_list = news_data.get("news", [])

        if news_list:
            for idx, news_item in enumerate(news_list, 1):
                source = news_item.get("source", "Unknown")

                if source == "Perplexity AI":
                    st.markdown(f"### 🤖 {source} Analysis")
                    content = news_item.get("content", "No content")
                    st.markdown(content)
                    st.caption(f"Type: {news_item.get('type', 'N/A')} | Time: {news_item.get('timestamp', 'N/A')}")

                elif source == "Google Search":
                    title = news_item.get("title", "No title")
                    url = news_item.get("url", "#")
                    snippet = news_item.get("snippet", "No description")

                    st.markdown(f"### 🔍 [{title}]({url})")
                    st.markdown(snippet)
                    st.caption(f"Source: Google Search | Time: {news_item.get('timestamp', 'N/A')}")

                if idx < len(news_list):
                    st.divider()
        else:
            st.info("수집된 뉴스가 없습니다.")

    else:
        st.error(f"뉴스 로드 실패: {news_result['error']}")

# ===== Tab 2: 소셜 감성 =====
with tab2:
    st.subheader("Social Media Sentiment Analysis")

    with st.spinner("소셜 감성 로딩 중..."):
        social_result = st.session_state.api_client.get_social_sentiment()

    if social_result["success"]:
        social_data = social_result["data"]

        # 캐시 정보
        if social_data.get("from_cache"):
            st.info(f"캐시된 데이터 (수집 시간: {social_data.get('cached_at', 'N/A')})")
        else:
            st.success(f"실시간 수집 완료 (수집 시간: {social_data.get('timestamp', 'N/A')})")

        st.divider()

        sentiment_data = social_data.get("data", {})

        # Reddit 감성 분석
        if "reddit" in sentiment_data:
            reddit = sentiment_data["reddit"]

            if "error" in reddit:
                st.warning(f"Reddit: {reddit['error']}")
            elif "status" in reddit:
                st.info(f"Reddit: {reddit['status']}")
            else:
                st.markdown("### 📱 Reddit (r/cryptocurrency)")

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric(
                        "Classification",
                        reddit.get("classification", "N/A")
                    )

                with col2:
                    score = reddit.get("sentiment_score", 0)
                    score_color = "positive" if score > 0 else "negative" if score < 0 else "neutral"
                    st.metric(
                        "Sentiment Score",
                        f"{score:+.2f}",
                        delta=None
                    )

                with col3:
                    st.metric(
                        "Total Posts",
                        reddit.get("total_posts", 0)
                    )

                with col4:
                    st.metric(
                        "Avg Score",
                        f"{reddit.get('avg_score', 0):.1f}"
                    )

                st.divider()

                # 감성 분포
                positive = reddit.get("positive", 0)
                negative = reddit.get("negative", 0)
                neutral = reddit.get("neutral", 0)

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("▲ Bullish", positive)
                with col2:
                    st.metric("─ Neutral", neutral)
                with col3:
                    st.metric("▼ Bearish", negative)

        st.divider()

        # Fear & Greed Index
        if "fear_greed" in sentiment_data:
            fg = sentiment_data["fear_greed"]

            if "error" in fg:
                st.warning(f"Fear & Greed Index: {fg['error']}")
            else:
                st.markdown("### 📊 Crypto Fear & Greed Index")

                col1, col2, col3 = st.columns(3)

                with col1:
                    value = fg.get("value", 50)
                    classification = fg.get("classification", "Neutral")

                    # 색상 결정
                    if value >= 75:
                        color = "#00FF88"  # Extreme Greed
                    elif value >= 55:
                        color = "#88FF88"  # Greed
                    elif value >= 45:
                        color = "#FFFF88"  # Neutral
                    elif value >= 25:
                        color = "#FF8888"  # Fear
                    else:
                        color = "#FF4444"  # Extreme Fear

                    st.markdown(f"<h1 style='color: {color}; text-align: center;'>{value}</h1>", unsafe_allow_html=True)
                    st.markdown(f"<p style='text-align: center; font-size: 1.2rem;'>{classification}</p>", unsafe_allow_html=True)

                with col2:
                    st.metric(
                        "7-Day Average",
                        f"{fg.get('avg_7d', 0):.1f}"
                    )

                with col3:
                    trend = fg.get("trend", "N/A")
                    trend_emoji = "📈" if trend == "Increasing" else "📉" if trend == "Decreasing" else "─"
                    st.metric(
                        "Trend",
                        f"{trend_emoji} {trend}"
                    )

        st.divider()

        # Perplexity 소셜 트렌드
        if "perplexity_social" in sentiment_data:
            perp = sentiment_data["perplexity_social"]

            st.markdown("### 🤖 Perplexity AI Social Trend Analysis")
            st.markdown(perp.get("summary", "No summary available"))
            st.caption(f"Time: {perp.get('timestamp', 'N/A')}")

    else:
        st.error(f"소셜 감성 로드 실패: {social_result['error']}")

# 푸터
st.divider()
st.caption(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Data sources: Perplexity AI, Google Search, Reddit, Fear & Greed Index")

