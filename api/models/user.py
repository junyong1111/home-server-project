"""
AXIS Capital - User Model
SQLAlchemy User 모델
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import relationship

from core.database import Base


class User(Base):
    """사용자 모델"""

    __tablename__ = "users"
    __table_args__ = {"extend_existing": True}

    # ===== Primary Key =====
    user_id = Column(Integer, primary_key=True, index=True)

    # ===== 기본 정보 =====
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)  # bcrypt 해시

    # ===== API 키 (암호화 저장) =====
    api_key_encrypted = Column(String, nullable=False)
    api_secret_encrypted = Column(String, nullable=False)

    # ===== 리스크 프로필 =====
    risk_profile = Column(
        String(20),
        default="balanced",
        nullable=False
    )  # conservative, balanced, aggressive

    # ===== 활성화 상태 =====
    is_active = Column(Boolean, default=True, nullable=False)

    # ===== 타임스탬프 =====
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # ===== Relationships =====
    # positions = relationship("Position", back_populates="user", cascade="all, delete-orphan")
    # trades = relationship("Trade", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(user_id={self.user_id}, username='{self.username}', email='{self.email}')>"

