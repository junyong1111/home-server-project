"""
AXIS Capital - Security
비밀번호 해싱, JWT, API 키 암호화/복호화
"""
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from cryptography.fernet import Fernet

from core.config import settings


# ===== 비밀번호 해싱 =====
# argon2 사용 (bcrypt의 72 bytes 제한 없음, 더 안전)
pwd_context = CryptContext(
    schemes=["argon2", "bcrypt"],  # argon2 우선, bcrypt는 fallback
    deprecated="auto",
)


def hash_password(password: str) -> str:
    """
    비밀번호 해싱

    Args:
        password: 평문 비밀번호

    Returns:
        str: 해시된 비밀번호
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    비밀번호 검증

    Args:
        plain_password: 평문 비밀번호
        hashed_password: 해시된 비밀번호

    Returns:
        bool: 일치 여부
    """
    return pwd_context.verify(plain_password, hashed_password)


# ===== JWT 토큰 =====
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    JWT Access Token 생성

    Args:
        data: 토큰에 포함할 데이터 (예: {"sub": "username"})
        expires_delta: 만료 시간 (기본: 24시간)

    Returns:
        str: JWT 토큰
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    JWT Access Token 검증 및 디코딩

    Args:
        token: JWT 토큰

    Returns:
        Optional[dict]: 디코딩된 데이터 (실패 시 None)
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        return None


# ===== API 키 암호화/복호화 =====
# Fernet 인스턴스 생성 (ENCRYPTION_KEY 사용)
try:
    import base64
    # ENCRYPTION_KEY는 64 hex chars (32 bytes)
    # hex string을 bytes로 변환
    encryption_key_bytes = bytes.fromhex(settings.ENCRYPTION_KEY)
    # Fernet은 정확히 32 bytes의 URL-safe base64-encoded key를 요구
    fernet_key = base64.urlsafe_b64encode(encryption_key_bytes)
    cipher_suite = Fernet(fernet_key)
    print("✅ API Key encryption initialized")
except Exception as e:
    print(f"⚠️ Fernet 초기화 실패: {e}")
    print(f"⚠️ ENCRYPTION_KEY 길이: {len(settings.ENCRYPTION_KEY)}, 필요: 64")
    cipher_suite = None


def encrypt_api_key(api_key: str) -> str:
    """
    API 키 암호화

    Args:
        api_key: 평문 API 키

    Returns:
        str: 암호화된 API 키 (base64 encoded)

    Raises:
        ValueError: cipher_suite가 초기화되지 않은 경우
    """
    if cipher_suite is None:
        raise ValueError("Encryption cipher not initialized. Check ENCRYPTION_KEY.")

    encrypted = cipher_suite.encrypt(api_key.encode())
    return encrypted.decode()  # bytes를 str로 변환


def decrypt_api_key(encrypted_api_key: str) -> str:
    """
    API 키 복호화

    Args:
        encrypted_api_key: 암호화된 API 키

    Returns:
        str: 평문 API 키

    Raises:
        ValueError: cipher_suite가 초기화되지 않은 경우
        Exception: 복호화 실패
    """
    if cipher_suite is None:
        raise ValueError("Encryption cipher not initialized. Check ENCRYPTION_KEY.")

    decrypted = cipher_suite.decrypt(encrypted_api_key.encode())
    return decrypted.decode()


def mask_api_key(api_key: str, visible_chars: int = 6) -> str:
    """
    API 키 마스킹 (보안을 위해 일부만 표시)

    Args:
        api_key: 평문 API 키
        visible_chars: 표시할 문자 수 (끝부분)

    Returns:
        str: 마스킹된 API 키 (예: "****abc123")
    """
    if len(api_key) <= visible_chars:
        return "****" + api_key

    return "****" + api_key[-visible_chars:]

