"""
AXIS Capital - FastAPI Main Application
AI Futures Trading System API
"""
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from core.config import settings
from core.database import Base, engine, check_database_connection
from core.redis_client import check_redis_connection
from routers import auth, users, ai_decisions, market_data


# ===== FastAPI App =====
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI 기반 선물 트레이딩 시스템 API",
    docs_url="/docs",
    redoc_url="/redoc",
)


# ===== CORS Middleware =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===== Routers =====
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(ai_decisions.router)
app.include_router(market_data.router)


# ===== Startup Event =====
@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 실행"""
    print("=" * 60)
    print(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} Starting...")
    print("=" * 60)

    # DB 테이블 생성 (없으면)
    # 주의: 프로덕션에서는 Alembic 사용 권장
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created (if not exists)")

    # 연결 확인
    if check_database_connection():
        print("✅ PostgreSQL connected")
    else:
        print("❌ PostgreSQL connection failed")

    if check_redis_connection():
        print("✅ Redis connected")
    else:
        print("❌ Redis connection failed")

    print("=" * 60)
    print(f"📖 API Docs: http://localhost:8000/docs")
    print("=" * 60)


# ===== Health Check =====
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health Check API

    - PostgreSQL 연결 확인
    - Redis 연결 확인

    Returns:
        dict: 시스템 상태
    """
    db_status = check_database_connection()
    redis_status = check_redis_connection()

    if db_status and redis_status:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "healthy",
                "database": "connected",
                "redis": "connected",
                "version": settings.APP_VERSION,
            }
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "database": "connected" if db_status else "disconnected",
                "redis": "connected" if redis_status else "disconnected",
                "version": settings.APP_VERSION,
            }
        )


# ===== Root =====
@app.get("/", tags=["Root"])
async def root():
    """
    Root API

    Returns:
        dict: 기본 정보
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
