"""
AXIS Capital - Auth Schemas
인증 관련 Pydantic 스키마
"""
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """로그인 요청"""
    username: str = Field(..., description="사용자명")
    password: str = Field(..., description="비밀번호")


class TokenResponse(BaseModel):
    """토큰 응답"""
    access_token: str = Field(..., description="JWT Access Token")
    token_type: str = Field(default="bearer", description="토큰 타입")
    user_id: int = Field(..., description="사용자 ID")
    username: str = Field(..., description="사용자명")


class TokenData(BaseModel):
    """토큰 데이터 (디코딩 후)"""
    username: str

