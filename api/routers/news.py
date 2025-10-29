"""
AXIS Capital - 뉴스 & 소셜 감성 API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
from datetime import datetime
import os
import sys

# Celery 태스크 임포트 준비
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Redis 캐싱용
from api.core.redis_client import get_redis_client

router = APIRouter(prefix="/api/v1/news", tags=["News"])


@router.get("/crypto", response_model=Dict[str, Any])
def get_crypto_news():
    """
    암호화폐 뉴스 조회 (Perplexity + Google Search)
    - Redis 캐시 우선 조회 (TTL: 30분)
    - 캐시 없으면 Celery 태스크 즉시 실행
    """
    try:
        redis_client = get_redis_client()
        cache_key = "axis:news:crypto"

        # Redis 캐시 확인
        cached = redis_client.get(cache_key)
        if cached:
            import json
            data = json.loads(cached)
            data["from_cache"] = True
            data["cached_at"] = data.get("timestamp", datetime.now().isoformat())
            return data

        # 캐시 없으면 Celery 태스크 즉시 실행
        from workers.tasks.news import collect_crypto_news
        result = collect_crypto_news()

        # Redis에 캐싱 (TTL: 30분)
        result["timestamp"] = datetime.now().isoformat()
        result["from_cache"] = False

        import json
        redis_client.setex(
            cache_key,
            1800,  # 30분
            json.dumps(result, ensure_ascii=False)
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"뉴스 조회 실패: {str(e)}"
        )


@router.get("/social", response_model=Dict[str, Any])
def get_social_sentiment():
    """
    소셜 감성 분석 조회 (Reddit + Fear & Greed + Perplexity)
    - Redis 캐시 우선 조회 (TTL: 30분)
    - 캐시 없으면 Celery 태스크 즉시 실행
    """
    try:
        redis_client = get_redis_client()
        cache_key = "axis:news:social"

        # Redis 캐시 확인
        cached = redis_client.get(cache_key)
        if cached:
            import json
            data = json.loads(cached)
            data["from_cache"] = True
            data["cached_at"] = data.get("timestamp", datetime.now().isoformat())
            return data

        # 캐시 없으면 Celery 태스크 즉시 실행
        from workers.tasks.news import collect_social_sentiment
        result = collect_social_sentiment()

        # Redis에 캐싱 (TTL: 30분)
        result["timestamp"] = datetime.now().isoformat()
        result["from_cache"] = False

        import json
        redis_client.setex(
            cache_key,
            1800,  # 30분
            json.dumps(result, ensure_ascii=False)
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"소셜 감성 조회 실패: {str(e)}"
        )


@router.post("/refresh")
def refresh_news():
    """
    뉴스 및 소셜 감성 데이터 강제 새로고침
    - Redis 캐시 삭제
    - 다음 조회 시 자동으로 새 데이터 수집
    """
    try:
        redis_client = get_redis_client()
        redis_client.delete("axis:news:crypto")
        redis_client.delete("axis:news:social")

        return {
            "success": True,
            "message": "뉴스 캐시가 삭제되었습니다. 다음 조회 시 새 데이터가 수집됩니다.",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"캐시 삭제 실패: {str(e)}"
        )

