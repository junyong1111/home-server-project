"""
Celery 설정
"""
import os
from datetime import timedelta

# Redis 설정 (from .env)
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
REDIS_DB = int(os.getenv("REDIS_DB", 0))

# Redis URL 생성
if REDIS_PASSWORD:
    REDIS_URL = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
else:
    REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

# Celery Broker & Backend
broker_url = REDIS_URL
result_backend = REDIS_URL

# Task 설정
task_serializer = "json"
result_serializer = "json"
accept_content = ["json"]
timezone = "Asia/Seoul"
enable_utc = True

# Task 실행 설정
task_track_started = True
task_time_limit = 300  # 5분 타임아웃
task_soft_time_limit = 240  # 4분 소프트 타임아웃
task_acks_late = True  # Worker가 죽으면 태스크 재시작
worker_prefetch_multiplier = 1  # 한 번에 1개씩만 가져오기

# Beat 스케줄 (주기적 작업)
beat_schedule = {
    # ===== 고빈도 데이터 수집 (5분) =====
    "collect-candle-data-5m": {
        "task": "workers.tasks.market_data.collect_candle_data",
        "schedule": timedelta(minutes=5),
        "args": (["BTCUSDT", "ETHUSDT"], "5m"),
    },

    # ===== 중빈도 데이터 수집 (30분) =====
    "collect-news-30m": {
        "task": "workers.tasks.news.collect_crypto_news",
        "schedule": timedelta(minutes=30),
    },

    # ===== AI 의사결정 트리거 (15분) =====
    "trigger-ai-decision-15m": {
        "task": "workers.tasks.market_data.trigger_n8n_workflow",
        "schedule": timedelta(minutes=15),
    },

    # ===== Funding Rate 수집 (1시간) =====
    "collect-funding-rate-1h": {
        "task": "workers.tasks.market_data.collect_funding_rates",
        "schedule": timedelta(hours=1),
    },
}

# 로깅 설정
worker_log_format = "[%(asctime)s: %(levelname)s/%(processName)s] %(message)s"
worker_task_log_format = "[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s"

