"""
AXIS Capital - Auth Router
회원가입, 로그인 API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.core.database import get_db
from api.core.security import create_access_token
from api.schemas.auth import LoginRequest, TokenResponse
from api.schemas.user import UserCreate, UserResponse
from api.services.user_service import UserService


router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    user_create: UserCreate,
    db: Session = Depends(get_db)
):
    """
    회원가입

    - **username**: 사용자명 (3-50자, 고유)
    - **email**: 이메일 (고유)
    - **password**: 비밀번호 (최소 8자)
    - **binance_api_key**: Binance API Key
    - **binance_api_secret**: Binance API Secret
    - **risk_profile**: conservative, balanced, aggressive (기본: balanced)

    Returns:
        UserResponse: 생성된 사용자 정보
    """
    try:
        user = UserService.create_user(db, user_create)

        # 응답에 마스킹된 API 키 추가
        masked_key = UserService.get_masked_api_key(user)

        return UserResponse(
            user_id=user.user_id,
            username=user.username,
            email=user.email,
            risk_profile=user.risk_profile,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
            binance_api_key_masked=masked_key,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"회원가입 실패: {str(e)}"
        )


@router.post("/login", response_model=TokenResponse)
def login(
    login_request: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    로그인

    - **username**: 사용자명
    - **password**: 비밀번호

    Returns:
        TokenResponse: JWT Access Token
    """
    # 사용자 인증
    user = UserService.authenticate_user(
        db,
        login_request.username,
        login_request.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="사용자명 또는 비밀번호가 잘못되었습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # JWT 토큰 생성
    access_token = create_access_token(data={"sub": user.username})

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=user.user_id,
        username=user.username,
    )

