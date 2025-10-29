"""
API 키 복호화 테스트
"""
import sys
from sqlalchemy.orm import Session
from core.database import SessionLocal
from core.security import decrypt_api_key
from models.user import User

def test_api_keys():
    """devjun API 키 복호화 테스트"""
    db = SessionLocal()

    try:
        # devjun 사용자 조회
        user = db.query(User).filter(User.username == "devjun").first()

        if not user:
            print("❌ devjun 사용자를 찾을 수 없습니다.")
            return

        print(f"✅ 사용자 찾음: {user.username} (user_id: {user.user_id})")
        print(f"📝 암호화된 API Key 길이: {len(user.api_key_encrypted)}")
        print(f"📝 암호화된 API Secret 길이: {len(user.api_secret_encrypted)}")
        print("")

        # 복호화 시도
        try:
            api_key = decrypt_api_key(user.api_key_encrypted)
            api_secret = decrypt_api_key(user.api_secret_encrypted)

            print("✅ 복호화 성공!")
            print(f"🔑 API Key: {api_key[:10]}...{api_key[-10:]}")
            print(f"🔑 API Secret: {api_secret[:10]}...{api_secret[-10:]}")
            print(f"📏 API Key 길이: {len(api_key)}")
            print(f"📏 API Secret 길이: {len(api_secret)}")

            # Binance API 키 형식 확인
            if len(api_key) == 64 and len(api_secret) == 64:
                print("✅ Binance API 키 형식 일치 (64자)")
            else:
                print(f"⚠️ Binance API 키 형식과 다름 (기대: 64자, 실제: key={len(api_key)}, secret={len(api_secret)})")

        except Exception as e:
            print(f"❌ 복호화 실패: {e}")
            import traceback
            traceback.print_exc()

    finally:
        db.close()

if __name__ == "__main__":
    test_api_keys()

