"""
AXIS Capital - Database Connection
PostgreSQL 연결 및 세션 관리
"""
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from .config import settings


# ===== SQLAlchemy Engine =====
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # 연결 유효성 확인
    pool_size=10,  # 연결 풀 크기
    max_overflow=20,  # 최대 추가 연결
    echo=settings.DEBUG,  # SQL 로깅 (디버그 모드에서만)
)

# ===== Session Factory =====
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# ===== Base Model =====
Base = declarative_base()


# ===== Dependency: DB Session =====
def get_db() -> Generator[Session, None, None]:
    """
    FastAPI Dependency: DB 세션 생성 및 종료

    Usage:
        @app.get("/")
        def read_root(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ===== Health Check =====
def check_database_connection() -> bool:
    """
    데이터베이스 연결 확인

    Returns:
        bool: 연결 성공 여부
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

