"""
AXIS Capital - User Service
사용자 관련 비즈니스 로직
"""
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional

from api.models.user import User
from api.schemas.user import UserCreate, UserUpdate, UserUpdateAPIKeys
from api.core.security import (
    hash_password,
    verify_password,
    encrypt_api_key,
    decrypt_api_key,
    mask_api_key,
)


class UserService:
    """사용자 서비스"""

    @staticmethod
    def create_user(db: Session, user_create: UserCreate) -> User:
        """
        사용자 생성

        Args:
            db: DB 세션
            user_create: 사용자 생성 데이터

        Returns:
            User: 생성된 사용자

        Raises:
            ValueError: 사용자명 or 이메일 중복
        """
        # 비밀번호 해싱
        hashed_pw = hash_password(user_create.password)

        # API 키 암호화
        encrypted_key = encrypt_api_key(user_create.binance_api_key)
        encrypted_secret = encrypt_api_key(user_create.binance_api_secret)

        # User 생성
        db_user = User(
            username=user_create.username,
            email=user_create.email,
            hashed_password=hashed_pw,
            api_key_encrypted=encrypted_key,
            api_secret_encrypted=encrypted_secret,
            risk_profile=user_create.risk_profile,
        )

        try:
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            return db_user
        except IntegrityError as e:
            db.rollback()
            if "username" in str(e):
                raise ValueError("이미 존재하는 사용자명입니다.")
            elif "email" in str(e):
                raise ValueError("이미 존재하는 이메일입니다.")
            else:
                raise ValueError(f"사용자 생성 실패: {e}")

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """사용자명으로 사용자 조회"""
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """user_id로 사용자 조회"""
        return db.query(User).filter(User.user_id == user_id).first()

    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
        """
        사용자 인증

        Args:
            db: DB 세션
            username: 사용자명
            password: 평문 비밀번호

        Returns:
            Optional[User]: 인증 성공 시 User, 실패 시 None
        """
        user = UserService.get_user_by_username(db, username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        if not user.is_active:
            return None
        return user

    @staticmethod
    def update_user(db: Session, user_id: int, user_update: UserUpdate) -> User:
        """
        사용자 정보 수정

        Args:
            db: DB 세션
            user_id: 사용자 ID
            user_update: 수정할 데이터

        Returns:
            User: 수정된 사용자

        Raises:
            ValueError: 사용자 없음 or 이메일 중복
        """
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            raise ValueError("사용자를 찾을 수 없습니다.")

        if user_update.email:
            user.email = user_update.email
        if user_update.risk_profile:
            user.risk_profile = user_update.risk_profile

        try:
            db.commit()
            db.refresh(user)
            return user
        except IntegrityError:
            db.rollback()
            raise ValueError("이미 존재하는 이메일입니다.")

    @staticmethod
    def update_api_keys(db: Session, user_id: int, keys: UserUpdateAPIKeys) -> User:
        """
        API 키 수정

        Args:
            db: DB 세션
            user_id: 사용자 ID
            keys: 새 API 키

        Returns:
            User: 수정된 사용자

        Raises:
            ValueError: 사용자 없음
        """
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            raise ValueError("사용자를 찾을 수 없습니다.")

        # API 키 암호화
        user.api_key_encrypted = encrypt_api_key(keys.binance_api_key)
        user.api_secret_encrypted = encrypt_api_key(keys.binance_api_secret)

        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def get_decrypted_api_keys(user: User) -> tuple[str, str]:
        """
        복호화된 API 키 반환

        Args:
            user: User 모델

        Returns:
            tuple[str, str]: (api_key, api_secret)
        """
        api_key = decrypt_api_key(user.api_key_encrypted)
        api_secret = decrypt_api_key(user.api_secret_encrypted)
        return api_key, api_secret

    @staticmethod
    def get_masked_api_key(user: User) -> str:
        """
        마스킹된 API 키 반환

        Args:
            user: User 모델

        Returns:
            str: 마스킹된 API 키 (****abc123)
        """
        api_key = decrypt_api_key(user.api_key_encrypted)
        return mask_api_key(api_key)

