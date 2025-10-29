"""
Celery 태스크 테스트 스크립트
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from workers.celery_app import app
from workers.tasks.market_data import collect_candle_data, collect_funding_rates

# Celery 앱 설정 확인
print("=== Celery 설정 확인 ===")
print(f"Broker: {app.conf.broker_url}")
print(f"Backend: {app.conf.result_backend}")
print(f"Timezone: {app.conf.timezone}")
print()

# 등록된 태스크 확인
print("=== 등록된 태스크 ===")
for task_name in sorted(app.tasks.keys()):
    if not task_name.startswith('celery.'):
        print(f"  ▲ {task_name}")
print()

# 태스크 직접 실행 테스트 (비동기 아님)
print("=== 태스크 직접 실행 테스트 ===")
print("캔들 데이터 수집 테스트...")
result = collect_candle_data(["BTCUSDT"], "5m", 10)
print(f"결과: {result}")
print()

print("✅ Celery 테스트 완료!")

