"""
Celery 애플리케이션 인스턴스
"""
from celery import Celery
from dotenv import load_dotenv
import os

# .env 로드
load_dotenv()

# Celery 앱 생성
app = Celery("axis_capital")

# 설정 로드
app.config_from_object("workers.config")

# 태스크 자동 발견
app.autodiscover_tasks(["workers.tasks"])

if __name__ == "__main__":
    app.start()

