"""
Celery 태스크 모듈
"""
from workers.tasks.market_data import (
    collect_candle_data,
    collect_funding_rates,
    trigger_n8n_workflow
)

from workers.tasks.news import (
    collect_crypto_news,
    collect_social_sentiment
)

__all__ = [
    "collect_candle_data",
    "collect_funding_rates",
    "trigger_n8n_workflow",
    "collect_crypto_news",
    "collect_social_sentiment",
]

