"""
AXIS Capital - Users Router
사용자 관리 API (JWT 인증 필요)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from api.core.database import get_db
from api.core.security import decode_access_token
from api.schemas.user import UserMe, UserUpdate, UserUpdateAPIKeys
from api.services.user_service import UserService


router = APIRouter(prefix="/api/v1/users", tags=["Users"])
security = HTTPBearer()


# ===== Dependency: 현재 사용자 =====
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    JWT 토큰에서 현재 사용자 추출

    Args:
        credentials: HTTP Bearer 토큰
        db: DB 세션

    Returns:
        User: 현재 사용자

    Raises:
        HTTPException: 토큰 무효 또는 사용자 없음
    """
    token = credentials.credentials

    # JWT 디코딩
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰입니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰에 사용자 정보가 없습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 사용자 조회
    user = UserService.get_user_by_username(db, username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="사용자를 찾을 수 없습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="비활성화된 사용자입니다."
        )

    return user


# ===== API Endpoints =====
@router.get("/me", response_model=UserMe)
def get_my_info(
    current_user = Depends(get_current_user)
):
    """
    내 정보 조회

    **인증 필요**: Bearer Token

    Returns:
        UserMe: 현재 사용자 정보 (API 키 마스킹)
    """
    masked_key = UserService.get_masked_api_key(current_user)

    return UserMe(
        user_id=current_user.user_id,
        username=current_user.username,
        email=current_user.email,
        risk_profile=current_user.risk_profile,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
        binance_api_key_masked=masked_key,
    )


@router.put("/me", response_model=UserMe)
def update_my_info(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    내 정보 수정

    **인증 필요**: Bearer Token

    - **email**: 새 이메일 (선택)
    - **risk_profile**: 새 리스크 프로필 (선택)

    Returns:
        UserMe: 수정된 사용자 정보
    """
    try:
        updated_user = UserService.update_user(db, current_user.user_id, user_update)
        masked_key = UserService.get_masked_api_key(updated_user)

        return UserMe(
            user_id=updated_user.user_id,
            username=updated_user.username,
            email=updated_user.email,
            risk_profile=updated_user.risk_profile,
            is_active=updated_user.is_active,
            created_at=updated_user.created_at,
            updated_at=updated_user.updated_at,
            binance_api_key_masked=masked_key,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/me/api-keys", response_model=dict)
def update_my_api_keys(
    keys: UserUpdateAPIKeys,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    API 키 수정

    **인증 필요**: Bearer Token

    - **binance_api_key**: 새 Binance API Key
    - **binance_api_secret**: 새 Binance API Secret

    Returns:
        dict: 성공 메시지 및 마스킹된 API 키
    """
    try:
        updated_user = UserService.update_api_keys(db, current_user.user_id, keys)
        masked_key = UserService.get_masked_api_key(updated_user)

        return {
            "message": "API 키가 성공적으로 업데이트되었습니다.",
            "binance_api_key_masked": masked_key,
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

