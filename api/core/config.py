"""
AXIS Capital - Configuration
환경변수 설정 및 애플리케이션 설정
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """애플리케이션 설정"""

    # ===== 애플리케이션 =====
    APP_NAME: str = "AXIS Capital API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # ===== PostgreSQL =====
    DATABASE_URL: str
    POSTGRES_PASSWORD: str  # healthcheck 등에서 필요

    # ===== Redis =====
    REDIS_URL: str
    REDIS_PASSWORD: str  # healthcheck 등에서 필요

    # ===== Security =====
    ENCRYPTION_KEY: str  # API 키 암호화용 (32 bytes hex)
    JWT_SECRET_KEY: str  # JWT 토큰 시크릿
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24시간

    # ===== Binance (테스트용, 선택사항) =====
    BINANCE_TESTNET_KEY: Optional[str] = None
    BINANCE_TESTNET_SECRET: Optional[str] = None

    # ===== CORS =====
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5679"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # .env의 추가 필드 무시
    )


# 전역 설정 인스턴스
settings = Settings()

