"""
AXIS Capital - User Schemas
Pydantic 스키마 (요청/응답)
"""
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    """사용자 기본 스키마"""
    username: str = Field(..., min_length=3, max_length=50, description="사용자명")
    email: EmailStr = Field(..., description="이메일")


class UserCreate(UserBase):
    """사용자 생성 요청"""
    password: str = Field(..., min_length=4, description="비밀번호 (최소 4자)")
    binance_api_key: str = Field(..., description="Binance API Key")
    binance_api_secret: str = Field(..., description="Binance API Secret")
    risk_profile: str = Field(
        default="balanced",
        pattern="^(conservative|balanced|aggressive)$",
        description="리스크 프로필"
    )


class UserUpdate(BaseModel):
    """사용자 정보 수정 요청"""
    email: Optional[EmailStr] = None
    risk_profile: Optional[str] = Field(
        None,
        pattern="^(conservative|balanced|aggressive)$"
    )


class UserUpdateAPIKeys(BaseModel):
    """API 키 수정 요청"""
    binance_api_key: str = Field(..., description="새 Binance API Key")
    binance_api_secret: str = Field(..., description="새 Binance API Secret")


class UserResponse(UserBase):
    """사용자 응답 (공개 정보)"""
    user_id: int
    risk_profile: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    # API 키는 마스킹 처리
    binance_api_key_masked: str = Field(..., description="마스킹된 API Key (****abc123)")

    class Config:
        from_attributes = True  # Pydantic v2에서 orm_mode 대체


class UserMe(UserResponse):
    """현재 사용자 정보 (더 상세)"""
    pass

