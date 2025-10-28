# API Key 관리 방식

**Version**: 1.0
**Date**: 2025-10-27

---

## 🔐 Multi-User API Key Architecture

### 핵심 원칙

**각 유저의 거래소 API Key는 DB에 암호화되어 저장됩니다.**

- 환경변수 (`.env`)에는 **시스템 레벨 테스트용 키만** (Optional)
- 실제 유저 키는 **users 테이블에 암호화 저장**
- 거래 시 **동적으로 복호화하여 사용**

---

## 데이터 흐름

```
[유저 등록 시]
1. 유저가 웹/API로 Binance API Key 입력
   POST /api/v2/users/register
   {
     "username": "user1",
     "email": "user1@example.com",
     "binance_api_key": "USER_KEY_123",
     "binance_api_secret": "USER_SECRET_456"
   }

2. FastAPI에서 ENCRYPTION_KEY로 암호화
   from cryptography.fernet import Fernet
   cipher = Fernet(ENCRYPTION_KEY)
   encrypted_key = cipher.encrypt(api_key.encode())

3. DB에 저장 (users 테이블)
   INSERT INTO users (
     username,
     api_key_encrypted,
     api_secret_encrypted
   ) VALUES (
     'user1',
     'gAAAAABh...',  -- 암호화됨
     'gAAAAABi...'   -- 암호화됨
   )

[거래 실행 시]
1. n8n에서 거래 요청
   POST /api/v2/positions/open
   {
     "user_id": 1,
     "symbol": "BTCUSDT",
     "side": "LONG",
     ...
   }

2. FastAPI에서 유저 조회
   user = db.query(User).filter_by(user_id=1).first()

3. API Key 복호화 (메모리에서만)
   cipher = Fernet(ENCRYPTION_KEY)
   api_key = cipher.decrypt(user.api_key_encrypted).decode()
   api_secret = cipher.decrypt(user.api_secret_encrypted).decode()

4. Binance 거래 실행
   binance = ccxt.binance({
     'apiKey': api_key,
     'secret': api_secret
   })
   order = binance.create_order(...)

5. 메모리에서 즉시 폐기
   del api_key, api_secret
```

---

## DB 스키마

### users 테이블

```sql
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,

    -- 암호화된 API Key 저장
    api_key_encrypted TEXT NOT NULL,       -- Fernet 암호화
    api_secret_encrypted TEXT NOT NULL,    -- Fernet 암호화

    -- 거래소 설정
    exchange VARCHAR(20) DEFAULT 'binance',
    is_testnet BOOLEAN DEFAULT true,       -- 테스트넷 사용 여부

    -- 기타
    risk_profile VARCHAR(20) DEFAULT 'balanced',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

---

## 보안 코드 예시

### 1. API Key 암호화 (등록 시)

```python
# api/core/security.py

from cryptography.fernet import Fernet
import os

class APIKeyManager:
    def __init__(self):
        encryption_key = os.getenv('ENCRYPTION_KEY')
        if not encryption_key:
            raise ValueError("ENCRYPTION_KEY not set!")

        self.cipher = Fernet(encryption_key.encode())

    def encrypt(self, api_key: str) -> str:
        """API Key 암호화"""
        return self.cipher.encrypt(api_key.encode()).decode()

    def decrypt(self, encrypted: str) -> str:
        """API Key 복호화"""
        return self.cipher.decrypt(encrypted.encode()).decode()

# 사용 예시
api_key_manager = APIKeyManager()

# 저장 시
encrypted_key = api_key_manager.encrypt("USER_BINANCE_KEY")
user.api_key_encrypted = encrypted_key

# 사용 시
real_api_key = api_key_manager.decrypt(user.api_key_encrypted)
```

### 2. 유저별 거래소 클라이언트 생성

```python
# api/services/binance.py

import ccxt
from api.core.security import APIKeyManager

class BinanceService:
    def __init__(self):
        self.api_key_manager = APIKeyManager()

    def get_user_exchange(self, user: User) -> ccxt.binance:
        """유저별 Binance 클라이언트 생성"""

        # DB에서 암호화된 키 가져오기
        encrypted_key = user.api_key_encrypted
        encrypted_secret = user.api_secret_encrypted

        # 복호화 (메모리에서만)
        api_key = self.api_key_manager.decrypt(encrypted_key)
        api_secret = self.api_key_manager.decrypt(encrypted_secret)

        # Binance 클라이언트 생성
        exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': api_secret,
            'options': {
                'defaultType': 'future',  # 선물 거래
                'testnet': user.is_testnet  # 테스트넷 여부
            }
        })

        # 민감 정보 즉시 삭제
        del api_key, api_secret

        return exchange

    def execute_trade(self, user_id: int, symbol: str, side: str, amount: float):
        """거래 실행"""
        user = db.query(User).filter_by(user_id=user_id).first()

        # 유저 전용 클라이언트로 거래
        exchange = self.get_user_exchange(user)

        order = exchange.create_market_order(
            symbol=symbol,
            side=side,
            amount=amount
        )

        return order
```

---

## 환경변수 설정

### .env 파일

```bash
# ========================================
# 보안 키 (필수!)
# ========================================
# 유저 API Key 암호화용 (32자)
ENCRYPTION_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6

# JWT 토큰 생성용 (64자)
JWT_SECRET_KEY=your_jwt_secret_key_here

# ========================================
# 시스템 레벨 테스트용 (Optional)
# ========================================
# 개발/테스트용으로만 사용
BINANCE_TESTNET_KEY=system_test_key
BINANCE_TESTNET_SECRET=system_test_secret
```

### ENCRYPTION_KEY 생성

```bash
# 방법 1: OpenSSL
openssl rand -hex 16

# 방법 2: Python
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# 출력 예시
a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6==
```

---

## 보안 체크리스트

### ✅ 해야 할 것

- [x] ENCRYPTION_KEY를 `.env`에 저장 (Git에 커밋 안됨)
- [x] API Key는 항상 암호화하여 DB 저장
- [x] 복호화는 메모리에서만, 사용 후 즉시 삭제
- [x] 로그에 API Key 절대 출력 금지
- [x] HTTPS 사용 (프로덕션)
- [x] Rate Limiting (무차별 대입 공격 방지)

### ❌ 하지 말아야 할 것

- [ ] API Key를 평문으로 DB 저장
- [ ] API Key를 Git에 커밋
- [ ] API Key를 로그에 출력
- [ ] 여러 유저가 하나의 API Key 공유
- [ ] ENCRYPTION_KEY를 코드에 하드코딩

---

## 마이그레이션 (기존 유저 키 암호화)

만약 이미 평문으로 저장된 API Key가 있다면:

```python
# scripts/encrypt_existing_keys.py

from api.core.database import get_db
from api.models.user import User
from api.core.security import APIKeyManager

def encrypt_existing_keys():
    """기존 평문 API Key를 암호화"""
    db = next(get_db())
    api_key_manager = APIKeyManager()

    users = db.query(User).filter(
        User.api_key_encrypted == None
    ).all()

    for user in users:
        if user.api_key_plain:  # 평문 필드
            # 암호화
            encrypted = api_key_manager.encrypt(user.api_key_plain)
            user.api_key_encrypted = encrypted

            # 평문 삭제
            user.api_key_plain = None

    db.commit()
    print(f"✓ {len(users)}명의 API Key 암호화 완료")

if __name__ == "__main__":
    encrypt_existing_keys()
```

---

## FAQ

### Q1. ENCRYPTION_KEY를 잃어버리면?

**A**: 모든 유저의 API Key를 복호화할 수 없습니다.
→ 유저들이 다시 등록해야 합니다.
→ **반드시 백업 보관!** (안전한 Secret Manager)

### Q2. 여러 서버에서 같은 ENCRYPTION_KEY를 사용해도 되나요?

**A**: 네, 같은 DB를 공유하는 서버들은 같은 키를 사용해야 합니다.
→ Kubernetes Secret, AWS Secrets Manager 등 사용 권장

### Q3. 유저가 API Key를 변경하려면?

**A**: 새로운 키를 받아서 다시 암호화 후 DB 업데이트

```python
@app.put("/api/v2/users/{user_id}/api-key")
async def update_api_key(user_id: int, new_key: str, new_secret: str):
    user = db.query(User).filter_by(user_id=user_id).first()

    # 새로운 키 암호화
    user.api_key_encrypted = api_key_manager.encrypt(new_key)
    user.api_secret_encrypted = api_key_manager.encrypt(new_secret)

    db.commit()
    return {"status": "updated"}
```

### Q4. 시스템 레벨 테스트용 키는 언제 사용하나요?

**A**:
- 개발 중 유저 등록 없이 빠른 테스트
- CI/CD 파이프라인 자동 테스트
- 실제 프로덕션에서는 사용 안함

---

**참고 문서**: TRD-AXIS-Capital.md 섹션 8.1 (API Key Management)

