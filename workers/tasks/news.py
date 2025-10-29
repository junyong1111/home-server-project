"""
뉴스 및 소셜 데이터 수집 태스크
실제 API: Perplexity, Reddit, Google Search
"""
from celery import shared_task
from datetime import datetime
import requests
import os
import praw  # Reddit API


@shared_task(name="workers.tasks.news.collect_crypto_news")
def collect_crypto_news():
    """
    암호화폐 뉴스 수집

    사용 API:
    1. Perplexity AI - AI 기반 실시간 검색
    2. Google Custom Search API - 실시간 뉴스 검색
    """
    print("▲ 뉴스 데이터 수집 시작")

    all_news = []

    # ===== 1. Perplexity AI 검색 =====
    try:
        perplexity_key = os.getenv("PERPLEXITY_API_KEY", "")
        if perplexity_key:
            print("  → Perplexity AI 검색 중...")

            # Perplexity API로 최신 Bitcoin 뉴스 및 트렌드 검색
            response = requests.post(
                "https://api.perplexity.ai/chat/completions",
                headers={
                    "Authorization": f"Bearer {perplexity_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "sonar",  # Perplexity 온라인 검색 모델
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a crypto news analyst. Provide the latest Bitcoin and cryptocurrency news in a structured format."
                        },
                        {
                            "role": "user",
                            "content": "What are the top 5 most important Bitcoin and cryptocurrency news from the last 24 hours? Include title, brief summary, and impact (positive/negative/neutral)."
                        }
                    ],
                    "temperature": 0.2,
                    "max_tokens": 1000
                },
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                perplexity_result = data.get("choices", [{}])[0].get("message", {}).get("content", "")

                all_news.append({
                    "source": "Perplexity AI",
                    "content": perplexity_result,
                    "type": "ai_analysis",
                    "timestamp": datetime.now().isoformat()
                })
                print(f"  ✓ Perplexity AI: 분석 완료 ({len(perplexity_result)} 글자)")
            else:
                print(f"  ✗ Perplexity API 오류: {response.status_code}")
        else:
            print("  - Perplexity API 키 없음 (건너뜀)")
    except Exception as e:
        print(f"  ✗ Perplexity 오류: {e}")

    # ===== 2. Google Custom Search API =====
    try:
        google_key = os.getenv("GOOGLE_API_KEY", "")
        google_cx = os.getenv("GOOGLE_SEARCH_ENGINE_ID", "")

        if google_key and google_cx:
            print("  → Google Search API 검색 중...")

            response = requests.get(
                "https://www.googleapis.com/customsearch/v1",
                params={
                    "key": google_key,
                    "cx": google_cx,
                    "q": "Bitcoin cryptocurrency news",
                    "dateRestrict": "d1",  # 최근 1일
                    "num": 5,  # 상위 5개
                    "sort": "date"  # 날짜순 정렬
                },
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])

                for item in items:
                    all_news.append({
                        "source": "Google Search",
                        "title": item.get("title"),
                        "url": item.get("link"),
                        "snippet": item.get("snippet"),
                        "timestamp": datetime.now().isoformat()
                    })

                print(f"  ✓ Google Search: {len(items)}개 뉴스 검색")
            else:
                print(f"  ✗ Google Search API 오류: {response.status_code}")
        else:
            print("  - Google Search API 키 없음 (건너뜀)")
    except Exception as e:
        print(f"  ✗ Google Search 오류: {e}")

    print(f"✓ 뉴스 수집 완료: 총 {len(all_news)}개")
    return {"success": True, "count": len(all_news), "news": all_news}


@shared_task(name="workers.tasks.news.collect_social_sentiment")
def collect_social_sentiment():
    """
    소셜 미디어 감성 분석 수집

    사용 API:
    1. Reddit API - r/cryptocurrency, r/bitcoin
    2. Crypto Fear & Greed Index (무료, API 키 불필요)
    """
    print("▲ 소셜 감성 데이터 수집 시작")

    sentiment_data = {}

    # ===== 1. Reddit API =====
    try:
        reddit_client_id = os.getenv("REDDIT_CLIENT_ID", "")
        reddit_secret = os.getenv("REDDIT_CLIENT_SECRET", "")

        if reddit_client_id and reddit_secret:
            print("  → Reddit API 호출 중...")

            reddit = praw.Reddit(
                client_id=reddit_client_id,
                client_secret=reddit_secret,
                user_agent="AXIS Capital Trading Bot 1.0"
            )

            # r/cryptocurrency에서 최신 hot 포스트 수집
            subreddit = reddit.subreddit("cryptocurrency")
            hot_posts = list(subreddit.hot(limit=20))

            # 간단한 감성 분석 (제목과 점수 기반)
            positive_keywords = [
                "bull", "bullish", "moon", "pump", "surge", "rally", "up", "gain",
                "profit", "win", "green", "ath", "breakout", "long"
            ]
            negative_keywords = [
                "bear", "bearish", "dump", "crash", "drop", "down", "loss", "red",
                "fear", "sell", "panic", "short", "liquidation"
            ]

            positive_count = 0
            negative_count = 0
            neutral_count = 0
            total_score = 0

            for post in hot_posts:
                title_lower = post.title.lower()
                total_score += post.score

                is_positive = any(word in title_lower for word in positive_keywords)
                is_negative = any(word in title_lower for word in negative_keywords)

                if is_positive and not is_negative:
                    positive_count += 1
                elif is_negative and not is_positive:
                    negative_count += 1
                else:
                    neutral_count += 1

            # 감성 비율 계산
            total_posts = len(hot_posts)
            sentiment_score = (positive_count - negative_count) / total_posts if total_posts > 0 else 0

            sentiment_data["reddit"] = {
                "positive": positive_count,
                "negative": negative_count,
                "neutral": neutral_count,
                "total_posts": total_posts,
                "avg_score": total_score / total_posts if total_posts > 0 else 0,
                "sentiment_score": round(sentiment_score, 2),  # -1(매우 부정) ~ 1(매우 긍정)
                "classification": (
                    "Very Bullish" if sentiment_score > 0.3 else
                    "Bullish" if sentiment_score > 0.1 else
                    "Neutral" if sentiment_score > -0.1 else
                    "Bearish" if sentiment_score > -0.3 else
                    "Very Bearish"
                )
            }

            print(f"  ✓ Reddit: {total_posts}개 포스트 분석 ({sentiment_data['reddit']['classification']})")
        else:
            print("  - Reddit API 키 없음 (건너뜀)")
            sentiment_data["reddit"] = {"status": "API key not configured"}
    except Exception as e:
        print(f"  ✗ Reddit 오류: {e}")
        sentiment_data["reddit"] = {"error": str(e)}

    # ===== 2. Crypto Fear & Greed Index (무료, API 키 불필요) =====
    try:
        print("  → Fear & Greed Index 조회 중...")
        response = requests.get(
            "https://api.alternative.me/fng/",
            params={"limit": 7},  # 최근 7일
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            if "data" in data and len(data["data"]) > 0:
                latest = data["data"][0]

                # 7일 평균 계산
                values = [int(d.get("value", 50)) for d in data["data"]]
                avg_7d = sum(values) / len(values)

                sentiment_data["fear_greed"] = {
                    "value": int(latest.get("value", 50)),
                    "classification": latest.get("value_classification", "Neutral"),
                    "timestamp": latest.get("timestamp"),
                    "avg_7d": round(avg_7d, 1),
                    "trend": "Increasing" if values[0] > values[-1] else "Decreasing"
                }
                print(f"  ✓ Fear & Greed: {latest.get('value')} ({latest.get('value_classification')})")
        else:
            print(f"  ✗ Fear & Greed API 오류: {response.status_code}")
    except Exception as e:
        print(f"  ✗ Fear & Greed 오류: {e}")
        sentiment_data["fear_greed"] = {"error": str(e)}

    # ===== 3. Perplexity AI로 소셜 트렌드 분석 (선택) =====
    try:
        perplexity_key = os.getenv("PERPLEXITY_API_KEY", "")
        if perplexity_key:
            print("  → Perplexity AI 소셜 트렌드 분석 중...")

            response = requests.post(
                "https://api.perplexity.ai/chat/completions",
                headers={
                    "Authorization": f"Bearer {perplexity_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "sonar",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a crypto social media analyst."
                        },
                        {
                            "role": "user",
                            "content": "What is the current sentiment on social media (Twitter, Reddit) about Bitcoin? Is it bullish, bearish, or neutral? Provide a brief 2-sentence summary."
                        }
                    ],
                    "temperature": 0.2,
                    "max_tokens": 200
                },
                timeout=20
            )

            if response.status_code == 200:
                data = response.json()
                social_summary = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                sentiment_data["perplexity_social"] = {
                    "summary": social_summary,
                    "timestamp": datetime.now().isoformat()
                }
                print(f"  ✓ Perplexity AI: 소셜 트렌드 분석 완료")
    except Exception as e:
        print(f"  ✗ Perplexity 소셜 분석 오류: {e}")

    print(f"✓ 소셜 감성 데이터 수집 완료")
    return {"success": True, "data": sentiment_data}
