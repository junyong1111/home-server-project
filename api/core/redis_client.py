"""
AXIS Capital - Redis Client
Redis 연결 및 캐싱
"""
import redis
from typing import Optional

from core.config import settings


# ===== Redis Client =====
redis_client = redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,  # 문자열로 반환
    socket_connect_timeout=5,
    socket_timeout=5,
)


# ===== Helper Functions =====
def get_redis_client() -> redis.Redis:
    """Redis 클라이언트 반환"""
    return redis_client


def check_redis_connection() -> bool:
    """
    Redis 연결 확인

    Returns:
        bool: 연결 성공 여부
    """
    try:
        redis_client.ping()
        return True
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False


# ===== Cache Functions =====
def set_cache(key: str, value: str, ttl: Optional[int] = None) -> bool:
    """
    Redis 캐시 저장

    Args:
        key: 캐시 키
        value: 캐시 값
        ttl: TTL (초), None이면 무제한

    Returns:
        bool: 성공 여부
    """
    try:
        if ttl:
            redis_client.setex(key, ttl, value)
        else:
            redis_client.set(key, value)
        return True
    except Exception as e:
        print(f"❌ Redis set failed: {e}")
        return False


def get_cache(key: str) -> Optional[str]:
    """
    Redis 캐시 조회

    Args:
        key: 캐시 키

    Returns:
        Optional[str]: 캐시 값 (없으면 None)
    """
    try:
        return redis_client.get(key)
    except Exception as e:
        print(f"❌ Redis get failed: {e}")
        return None


def delete_cache(key: str) -> bool:
    """
    Redis 캐시 삭제

    Args:
        key: 캐시 키

    Returns:
        bool: 성공 여부
    """
    try:
        redis_client.delete(key)
        return True
    except Exception as e:
        print(f"❌ Redis delete failed: {e}")
        return False

