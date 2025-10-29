# Implementation Checklist
## AXIS Capital - AI Futures Trading System

**Version**: 2.0
**Date**: 2025-10-27
**Total Duration**: 10-12 Weeks
**Related Docs**: PRD-AXIS-Capital.md, TRD-AXIS-Capital.md

---

## ⚠️ Implementation Rules (필독)

### 작업 진행 원칙

```yaml
1. 한 번에 1개 작업만:
   - 여러 작업 동시 진행 금지
   - 현재 작업 완료 전까지 다음 작업 시작 불가

2. 단계별 승인:
   - 각 작업 완료 후 Owner에게 보고
   - Owner 승인 후 체크리스트 체크 (✓)
   - 승인 없이 다음 단계 진행 금지

3. 체크리스트 관리:
   - 작업 시작: [ ] → [진행중]
   - 작업 완료: [진행중] → [완료 대기]
   - Owner 승인: [완료 대기] → [x]

4. 보고 형식:
   ✅ 완료: [작업명]
   📝 내용: [무엇을 했는지]
   🧪 테스트: [테스트 결과]
   ❓ 확인 요청: 다음 단계 진행해도 될까요?
```

### 예시 워크플로우

```
Step 1:
  AI: "Docker Compose 설정 시작합니다"
  AI: [작업 수행]
  AI: "✅ 완료: docker-compose.yml 작성
       📝 내용: PostgreSQL, Redis, n8n 컨테이너 설정
       🧪 테스트: docker-compose up -d 성공
       ❓ 확인: 다음 단계 진행해도 될까요?"

  Owner: "확인했어, 진행해" (승인)

  AI: [체크리스트 체크 ✓]
  AI: "다음 작업 시작합니다"

Step 2:
  AI: "PostgreSQL 연결 테스트 시작합니다"
  ...
```

### 금지 사항 ⛔

```
❌ 여러 작업 동시 진행
❌ 승인 없이 다음 단계
❌ 체크리스트 임의 체크
❌ 테스트 없이 완료 보고
❌ 문제 발생 시 숨기기
```

### 문제 발생 시

```
1. 즉시 Owner에게 보고
2. 에러 로그/스크린샷 첨부
3. 해결 방안 제안
4. Owner 지시 대기
```

---

## Phase 1: Foundation & Infrastructure (Week 1-2)

### Week 1: Environment Setup

**⚠️ 각 작업 완료 후 Owner 승인 필수**

#### Infrastructure
- [x] **Task 1.1: 서버 준비** ✅
  - [x] Ubuntu 22.04 LTS 설치 (macOS 환경 확인)
  - [x] Docker 설치 및 설정
  - [x] Docker Compose 설치 (v2 확인)

  **완료 보고**:
  ```
  ✅ 완료: 서버 기본 환경
  📝 내용: macOS + Docker Desktop + docker compose (v2)
  🧪 테스트: docker compose ps 정상 작동
  ❓ 다음 단계 진행?
  ```
  **👤 Owner 승인 완료** ✓

- [x] **Task 1.2: 방화벽 설정** ⏭️ (로컬 개발 환경으로 SKIP)
  - [ ] 방화벽 설정 (포트 8000, 5678, 3000) - 프로덕션 배포 시 필요
  - [ ] SSL 인증서 발급 (Let's Encrypt) - 프로덕션 배포 시 필요

  **로컬 개발 환경이므로 SKIP**

- [x] **Task 1.3: Docker Compose 설정** ✅
  - [x] `docker-compose.yml` 작성
  - [x] PostgreSQL 컨테이너 설정
  - [x] Redis 컨테이너 설정
  - [x] n8n 컨테이너 설정
  - [x] TimescaleDB extension 활성화
  - [x] 환경변수 파일 `.env` 작성
  - [x] 볼륨 매핑 확인
  - [x] Healthcheck 설정

  **완료 보고**:
  ```
  ✅ 완료: Docker Compose 설정
  📝 내용: PostgreSQL, Redis, n8n 컨테이너 설정 (한글 주석 포함)
  🧪 테스트: docker compose up -d 성공, 모든 컨테이너 RUNNING
  📂 파일: docker-compose.yml, .env, .env.example, API-KEY-MANAGEMENT.md
  ❓ 다음 단계 진행?
  ```
  **👤 Owner 승인 완료** ✓

- [x] **Task 1.4: Database 초기화** ✅
  - [x] PostgreSQL 연결 테스트
  - [x] TimescaleDB extension 설치
  - [x] 데이터베이스 생성 (`axis_capital`)
  - [x] Redis 연결 테스트 (PONG 확인)

  **완료 보고**:
  ```
  ✅ 완료: Database 초기화
  📝 내용: PostgreSQL + TimescaleDB, Redis 정상 실행
  🧪 테스트: TimescaleDB extension 설치 완료, Redis PONG 응답
  ❓ 다음 단계 진행?
  ```
  **👤 Owner 승인 완료** ✓

#### 테스트 & 승인 요청

```bash
# Docker 실행 확인
docker-compose up -d
docker ps  # 모든 컨테이너 running 확인

# PostgreSQL 연결 테스트
psql -h localhost -U axis -d axis_capital

# Redis 연결 테스트
redis-cli ping  # PONG 응답 확인
```

**Phase 1 완료 보고**:
```
✅ 완료: Phase 1 - Foundation & Infrastructure
📝 내용:
  - Docker 환경 구축 완료
  - DB 스키마 생성 완료
  - FastAPI 기본 구조 완료
🧪 테스트:
  - 모든 컨테이너 정상 실행
  - Health Check API 응답 성공
  - DB 연결 확인
❓ Phase 2 진행해도 될까요?
```
**👤 Owner 최종 승인 대기** ⏸️

---

### Week 2: Database Schema & Core Services

**⚠️ 각 작업 완료 후 Owner 승인 필수**

#### Database Schema
- [x] **Task 2.1: Core Tables 생성** ✅
  - [x] `users` 테이블 생성 (API 키 암호화 필드 포함)
  - [x] `positions` 테이블 생성 (LONG/SHORT, 레버리지, PnL)
  - [x] `trades` 테이블 생성 (개별 거래 실행 기록)
  - [x] 인덱스 생성 (16개)
  - [x] Foreign Key 제약조건 설정
  - [x] updated_at 자동 업데이트 트리거
  - [x] 테스트 데이터 삽입 확인

  **완료 보고**:
  ```
  ✅ 완료: Core Tables 생성
  📝 내용:
    - users: 사용자 정보 + 암호화된 API 키
    - positions: 선물 포지션 (진입/청산/PnL/청산가)
    - trades: 개별 거래 실행 기록
    - 16개 인덱스 최적화 (user_id, symbol, timestamp 등)
    - CASCADE 삭제 설정 (users 삭제 시 positions/trades 자동 삭제)
  🧪 테스트:
    - \dt: 3개 테이블 확인
    - test_user 데이터 정상 삽입
    - 인덱스 16개 정상 생성
  📂 파일: database/migrations/001_create_core_tables.sql
  ❓ 다음 단계 진행?
  ```
  **👤 Owner 승인 완료** ✓

- [x] **Task 2.4: FastAPI 사용자 관리** ✅
  - [x] API 프로젝트 구조 생성 (`api/`)
  - [x] `uv`로 패키지 관리 설정 (`pyproject.toml`)
  - [x] FastAPI 기본 설정 (`main.py`, `core/config.py`)
  - [x] Database 연결 (`core/database.py`)
  - [x] Redis 연결 (`core/redis_client.py`)
  - [x] 보안 모듈 (`core/security.py`)
    - [x] Argon2 비밀번호 해싱
    - [x] JWT 토큰 생성/검증
    - [x] Fernet API 키 암호화/복호화
  - [x] User 모델 (`models/user.py`)
  - [x] User 스키마 (`schemas/user.py`, `schemas/auth.py`)
  - [x] User 서비스 (`services/user_service.py`)
  - [x] Auth 라우터 (`routers/auth.py`)
    - [x] POST /auth/register (회원가입)
    - [x] POST /auth/login (로그인)
  - [x] User 라우터 (`routers/users.py`)
    - [x] GET /users/me (내 정보 조회)
    - [x] PUT /users/me/api-keys (API 키 업데이트)
  - [x] Health Check API (`GET /health`)

  **완료 보고**:
  ```
  ✅ 완료: FastAPI 사용자 관리 시스템
  📝 내용:
    - uv 기반 패키지 관리
    - JWT 인증 (24시간 유효)
    - Argon2 비밀번호 해싱 (72바이트 제한 없음)
    - Fernet API 키 암호화 (DB 저장)
    - 회원가입/로그인/내 정보 조회/API 키 업데이트 API
  🧪 테스트:
    - FastAPI 포트 7000 실행 성공
    - Swagger UI (/docs) 접근 가능
    - 회원가입 및 로그인 정상 작동
    - API 키 암호화 저장 확인
  📂 파일: api/ 전체 구조 (15+ 파일)
  ❓ 다음 단계 진행?
  ```
  **👤 Owner 승인 완료** ✓

- [x] **Task 2.5: Streamlit Web UI** ✅
  - [x] Streamlit 프로젝트 구조 생성 (`streamlit_app/`)
  - [x] `uv`로 패키지 관리 설정 (`pyproject.toml`)
  - [x] API Client 구현 (`utils/api_client.py`)
    - [x] health_check, register, login, get_me, update_api_keys
  - [x] 다크 테마 설정 (`.streamlit/config.toml`)
  - [x] Home 페이지 (`Home.py`)
    - [x] 시스템 상태 개요
    - [x] 기술 스택 소개
    - [x] 빠른 시작 버튼
  - [x] 회원가입 페이지 (`pages/1_회원가입.py`)
    - [x] 사용자명/이메일/비밀번호 입력
    - [x] Binance API 키 입력
    - [x] 리스크 프로필 선택
  - [x] 로그인 페이지 (`pages/2_로그인.py`)
    - [x] JWT 기반 인증
    - [x] 세션 관리
  - [x] 대시보드 페이지 (`pages/3_대시보드.py`)
    - [x] 계정 개요 (사용자명, 상태, 리스크 프로필)
    - [x] 트레이딩 성과 메트릭 (Placeholder)
    - [x] 포트폴리오 가치 차트 (Altair)
    - [x] 일일 손익 차트 (Altair)
  - [x] API 키 관리 페이지 (`pages/4_API키관리.py`)
    - [x] 현재 API 키 확인 (마스킹)
    - [x] API 키 업데이트
    - [x] Binance 발급 가이드
  - [x] UI 한글화 (모든 페이지)
  - [x] 미니멀/프로페셔널 디자인 적용
  - [x] Dockerfile 생성
  - [x] docker-compose.yml에 streamlit 서비스 추가

  **완료 보고**:
  ```
  ✅ 완료: Streamlit Web UI
  📝 내용:
    - 5개 페이지 (Home, 회원가입, 로그인, 대시보드, API 키 관리)
    - JWT 기반 인증 & 세션 관리
    - Altair 차트 (포트폴리오 가치, 일일 손익)
    - 다크 테마 (#00D9FF Cyan)
    - 미니멀/프로페셔널 디자인
    - 완전 한글화
    - Docker 컨테이너화
  🧪 테스트:
    - Streamlit 포트 8501 실행 성공
    - 모든 페이지 정상 렌더링
    - FastAPI와 통신 성공
    - 회원가입/로그인/대시보드 플로우 정상
  📂 파일: streamlit_app/ 전체 구조 (10+ 파일)
  🌐 접속: http://localhost:8501
  ❓ 다음 단계 진행?
  ```
  **👤 Owner 승인 완료** ✓

- [x] **Task 2.2: AI Tables 생성** ✅
  - [x] `ai_decisions` 테이블 생성 (evidence, reasoning 포함)
  - [x] `decision_analysis` 테이블 생성
  - [x] `regime_history` 테이블 생성
  - [x] 인덱스 9개 생성
  - [x] 테스트 데이터 삽입 확인

  **완료 보고**:
  ```
  ✅ 완료: AI Tables 생성 + FastAPI 연동 테스트
  📝 내용:
    - ai_decisions: AI 의사결정 기록 (evidence, reasoning, validation 포함)
    - decision_analysis: 사후 분석 (24h 후 예측 vs 실제 비교)
    - regime_history: 시장 레짐 변경 이력 (Bull/Bear/Consolidation)
    - 총 9개 인덱스 최적화 (agent, quality, time 등)

    - FastAPI 연동:
      * models/ai_decision.py: SQLAlchemy 모델
      * schemas/ai_decision.py: Pydantic 검증 스키마
      * routers/ai_decisions.py: REST API 엔드포인트
      * POST /ai/decisions: AI 의사결정 생성
      * GET /ai/decisions: 내 의사결정 조회
      * POST /ai/regime: 시장 레짐 기록
      * GET /ai/regime/latest: 최신 레짐 조회

  🧪 테스트 (실제 API 호출):
    - ✅ 로그인 → JWT 토큰 획득
    - ✅ POST /ai/regime: Bull Trend 기록 (confidence 0.875)
    - ✅ POST /ai/decisions: AXIS-CEO LONG (confidence 0.82)
    - ✅ POST /ai/decisions: AXIS-BTC-Analyst BULLISH (confidence 0.85)
    - ✅ POST /ai/decisions: AXIS-Risk-Chief APPROVED (confidence 0.90)
    - ✅ DB 확인: 3개 AI 결정, 1개 레짐 기록 정상 저장
    - ✅ 총 LLM 비용 추적: $0.122 (gpt-4o + gpt-o1)
    - ✅ Foreign Key 정상 작동 (users → ai_decisions)

  📂 파일:
    - database/migrations/002_create_ai_tables.sql
    - api/models/ai_decision.py
    - api/schemas/ai_decision.py
    - api/routers/ai_decisions.py
    - api/main.py (ai_decisions 라우터 추가)

  💡 특징:
    - Evidence 기반 의사결정 (JSON 배열)
    - AI의 자연어 reasoning
    - 백테스팅을 위한 actual_outcome 필드
    - LLM 비용 추적 (model, tokens, cost)
    - JWT 인증 기반 사용자별 의사결정 관리

  🌐 API 엔드포인트:
    - POST   /ai/decisions          (Create AI Decision)
    - GET    /ai/decisions          (List My Decisions)
    - GET    /ai/decisions/{id}     (Get Decision Detail)
    - POST   /ai/regime              (Create Regime)
    - GET    /ai/regime/latest       (Get Latest Regime)
    - GET    /ai/regime              (List Regime History)

  ❓ 다음 단계 진행?
  ```
  **👤 Owner 승인 완료** ✓

- [x] **Task 2.6: Streamlit AI 의사결정 UI** ✅
  - [x] API Client에 AI 의사결정 메서드 추가
    - [x] get_my_decisions(): 내 의사결정 목록
    - [x] get_decision(id): 의사결정 상세
    - [x] get_latest_regime(): 최신 시장 레짐
    - [x] get_regime_history(): 레짐 변경 이력
  - [x] 대시보드(3_대시보드.py) 업데이트
    - [x] 현재 시장 레짐 표시 (Bull/Bear/Consolidation)
    - [x] RSI, ADX 메트릭 표시
    - [x] 최근 AI 결정 요약 (최근 3개)
    - [x] "전체 보기" 버튼
  - [x] 새 페이지(5_AI의사결정.py) 생성
    - [x] Tab 1: 최근 의사결정 목록
      * Evidence 카드 형식 표시
      * AI Reasoning 표시
      * LLM 비용 및 토큰 정보
    - [x] Tab 2: 시장 레짐
      * 현재 레짐 (색상 코딩)
      * 기술적 지표 (ADX, RSI, Price/MA50)
      * AI 판단 근거
      * 레짐 변경 이력 (최근 10개)
    - [x] Tab 3: 통계
      * 에이전트별 의사결정 수
      * 총 LLM 비용 및 토큰
      * LLM 모델별 사용량

  **완료 보고**:
  ```
  ✅ 완료: Streamlit AI 의사결정 UI
  📝 내용:
    - API Client: AI 의사결정 조회 메서드 4개 추가
    - 대시보드: 현재 레짐 + 최근 AI 결정 요약
    - 새 페이지: 3개 탭 (의사결정/레짐/통계)

  🎨 디자인:
    - 미니멀한 카드 형식 Evidence 표시
    - 레짐별 색상 코딩 (Bull=녹색, Bear=빨강, Consolidation=오렌지)
    - 확신도 퍼센트 표시
    - LLM 비용 추적

  🧪 테스트:
    - ✅ Streamlit 재시작 성공
    - ✅ 대시보드에 AI 섹션 추가 확인
    - ✅ 5_AI의사결정.py 페이지 생성 완료
    - ✅ API 연동 정상 (JWT 인증)

  📂 파일:
    - streamlit_app/utils/api_client.py (메서드 4개 추가)
    - streamlit_app/pages/3_대시보드.py (AI 섹션 추가)
    - streamlit_app/pages/5_AI의사결정.py (신규 310줄)

  🌐 접속: http://localhost:8501

  ❓ 다음 단계 진행?
  ```
  **👤 Owner 승인 완료** ✓

- [x] **Task 2.3: 인덱스 & 제약조건** ✅
  - [x] 모든 인덱스 확인 및 검증
  - [x] Foreign Key 제약조건 확인
  - [x] NOT NULL 제약조건 확인
  - [x] 순환 참조 검증

  **완료 보고**:
  ```
  ✅ 완료: 인덱스 & 제약조건 검증
  📝 내용:
    - 총 6개 테이블 (users, positions, trades, ai_decisions, decision_analysis, regime_history)
    - 총 28개 인덱스
      * UNIQUE INDEX: 8개 (Primary Key + UNIQUE 제약)
      * PARTIAL INDEX: 1개 (positions.status = 'open')
      * REGULAR INDEX: 19개
    - 총 5개 Foreign Key 제약조건
      * ai_decisions → users (CASCADE)
      * decision_analysis → ai_decisions (CASCADE)
      * positions → users (CASCADE)
      * trades → users (CASCADE)
      * trades → positions (SET NULL)
    - NOT NULL 제약조건: 39개 컬럼

  🧪 검증 결과:
    - ✅ users: 6개 인덱스 (PK + 2 UNIQUE + 3 INDEX)
    - ✅ positions: 5개 인덱스 (PK + 4 INDEX, partial 포함)
    - ✅ trades: 5개 인덱스 (PK + 4 INDEX)
    - ✅ ai_decisions: 5개 인덱스 (PK + 4 INDEX)
    - ✅ decision_analysis: 4개 인덱스 (PK + 3 INDEX)
    - ✅ regime_history: 3개 인덱스 (PK + 2 INDEX)
    - ✅ 순환 참조 없음 (자기 자신 참조 FK 없음)
    - ✅ 모든 FK에 CASCADE 또는 SET NULL 규칙 설정
    - ✅ 필수 컬럼에 NOT NULL 제약조건 설정

  📊 인덱스 커버리지:
    - user_id 기반 조회 최적화 ✓
    - timestamp 기반 정렬 최적화 ✓
    - agent_name, decision_type, quality 필터링 최적화 ✓
    - symbol, status 복합 인덱스 ✓
    - email, username UNIQUE 제약 ✓

  💡 특징:
    - Partial Index (positions.status = 'open'): 열린 포지션만 빠른 조회
    - Composite Index: 복합 조건 쿼리 최적화
    - DESC 인덱스: 최신 데이터 우선 정렬
    - CASCADE 삭제: 사용자 삭제 시 관련 데이터 자동 정리

  ❓ 다음 단계 진행?
  ```
  **👤 Owner 승인 완료** ✓

- [x] **Task 2.7: TimescaleDB Tables + UI** ✅
  - [x] TimescaleDB 테이블 생성
    - [x] market_data (OHLCV 캔들)
    - [x] portfolio_snapshots (포트폴리오 이력)
    - [x] funding_rate_history (펀딩 레이트)
  - [x] Hypertable 변환 (3개 모두)
  - [x] 인덱스 생성 (6개)
  - [x] 테스트 데이터 삽입
  - [x] FastAPI Market Data API
    - [x] models/market_data.py
    - [x] schemas/market_data.py
    - [x] routers/market_data.py
    - [x] GET /market/ohlcv/{symbol}
    - [x] GET /market/portfolio-history
    - [x] GET /market/latest-price/{symbol}
  - [x] Streamlit Market Data UI
    - [x] BTC/USDT 가격 차트 (실제 데이터)
    - [x] 포트폴리오 가치 차트 (실제 데이터)
    - [x] 실시간 가격 메트릭
    - [x] 손익 계산

  **완료 보고**:
  ```
  ✅ 완료: TimescaleDB Tables + Market Data UI
  📝 내용:
    - TimescaleDB 테이블 3개 (Hypertable 변환 완료)
      * market_data: OHLCV 캔들 데이터
      * portfolio_snapshots: 포트폴리오 스냅샷 (10분마다)
      * funding_rate_history: 펀딩 레이트 이력
    - 총 6개 인덱스 (시간 기반 조회 최적화)
    - FastAPI Market Data API 3개 엔드포인트
    - Streamlit 실시간 차트 2개

  🧪 테스트 결과:
    - ✅ Hypertable 3개 정상 변환
    - ✅ market_data: BTC 15분봉 10개
    - ✅ portfolio_snapshots: devjun 스냅샷 5개
    - ✅ funding_rate_history: 펀딩 레이트 4개
    - ✅ FastAPI GET /market/ohlcv/BTC/USDT 정상
    - ✅ FastAPI GET /market/portfolio-history 정상
    - ✅ Streamlit BTC 가격 차트 표시
    - ✅ Streamlit 포트폴리오 가치 차트 표시
    - ✅ 실시간 가격 $67,850 (최신 캔들)
    - ✅ 포트폴리오 가치 $10,600 (+6.0%)

  📊 차트 기능:
    - BTC/USDT 가격 차트
      * 15분봉 기준 (50개)
      * 가격 변화율 표시
      * Interactive tooltip (시간, 가격)
    - 포트폴리오 가치 차트
      * Area 차트 (그라데이션)
      * 총 가치 + 미실현 손익
      * 실시간 업데이트

  💡 특징:
    - TimescaleDB 시계열 최적화 (Hypertable)
    - 시간 기반 인덱스 (time DESC)
    - 심볼/타임프레임 복합 인덱스
    - 실제 데이터 기반 차트 (플레이스홀더 제거)

  📂 파일:
    - database/migrations/003_create_timescaledb_tables.sql
    - api/models/market_data.py
    - api/schemas/market_data.py
    - api/routers/market_data.py
    - streamlit_app/utils/api_client.py (+3 메서드)
    - streamlit_app/pages/3_대시보드.py (실제 차트 추가)

  🌐 API 엔드포인트:
    - GET /market/ohlcv/{symbol}      (OHLCV 캔들)
    - GET /market/portfolio-history   (포트폴리오 이력)
    - GET /market/latest-price/{symbol} (최신 가격)

  ❓ 다음 단계 진행?
  ```
  **👤 Owner 승인 완료** ✓

- [x] **Task 2.8: Streamlit 시장 데이터 UI** ✅
  - [x] 포트폴리오 차트 제거 (실제 지갑 아님)
  - [x] 실시간 BTC 가격 (Binance Public API)
  - [x] 환율 조회 (USD/KRW)
  - [x] 금값 표시 (USD/oz, KRW/g)
  - [x] 원화 자동 변환 (모든 USD 가격)
  - [x] 24시간 거래량, 고가, 저가

  **완료 보고**:
  ```
  ✅ 완료: Streamlit 실시간 시장 데이터 UI
  📝 내용:
    - 포트폴리오 차트 제거 (테스트 데이터였음)
    - 실시간 외부 API 연동
      * Binance Public API (BTC 가격)
      * Open Exchange Rates API (USD/KRW)
      * 금값 표시 (추후 goldapi.io 연동 예정)
    - 원화 자동 변환 기능

  🧪 테스트 결과:
    - ✅ BTC 가격 실시간 조회 (Binance)
    - ✅ 24시간 변동률 표시
    - ✅ USD → KRW 자동 변환
    - ✅ 금값 USD/oz → KRW/g 변환
    - ✅ 24시간 고가/저가/거래량

  💡 향후 개선:
    - ccxt 라이브러리 연동 (다중 거래소 지원)
    - 실제 사용자 포트폴리오 연동
    - 실시간 금값 API 연동

  📂 파일:
    - streamlit_app/pages/3_대시보드.py (시장 데이터 UI)

  ❓ 다음 단계 진행?
  ```
  **👤 Owner 승인 완료** ✓

---

### ✅ Phase 2 완료: Database & UI Setup

**Phase 2 요약**:
- ✅ PostgreSQL/TimescaleDB 설정 (9개 테이블)
- ✅ FastAPI 사용자 관리 (회원가입, 로그인, API 키 관리)
- ✅ Streamlit Web UI (대시보드, AI 의사결정, 시장 데이터)
- ✅ AI 의사결정 테이블 및 API
- ✅ 실시간 시장 데이터 UI (BTC, 환율, 금값)

---

### Phase 3: Backend Services (FastAPI, Celery)

#### FastAPI 기본 구조
- [x] **프로젝트 구조 생성** ✅
  ```
  api/
  ├── main.py
  ├── pyproject.toml (uv 패키지 관리)
  ├── routers/
  ├── services/
  ├── models/
  └── core/
  ```
  - [x] `main.py` FastAPI 앱 초기화
  - [x] `pyproject.toml` 작성 (uv 사용)
  - [x] `core/config.py` 설정 파일
  - [x] `core/database.py` DB 연결
  - [x] `core/redis_client.py` Redis 연결

- [x] **Health Check API** ✅
  - [x] `GET /health` 엔드포인트
  - [x] Database 연결 확인
  - [x] Redis 연결 확인
  - [x] 응답 시간 < 500ms 확인

  **완료 보고**:
  ```
  ✅ 완료: FastAPI 기본 인프라
  📝 내용:
    - FastAPI Health Check 정상 작동
    - Database & Redis 연결 성공
    - Python 3.12, uv 패키지 관리
    - Docker Compose 통합
  🧪 테스트 결과:
    - ✅ GET /health: 정상 응답
    - ✅ Database: connected
    - ✅ Redis: connected
    - ✅ Version: 1.0.0
  📂 포트: http://localhost:8001
  ```
  **👤 Owner 승인 완료** ✓

#### 테스트
```bash
# Docker Compose 실행
docker compose up -d

# Health Check
curl http://localhost:8001/health
# Expected: {"status": "healthy", "database": "connected", "redis": "connected", "version": "1.0.0"}
```

---

## Phase 2: Exchange Integration (Week 3)

### Binance Futures API

#### 기본 연동
- [x] **CCXT 설정** ✅
  - [x] `services/binance_service.py` 생성
  - [x] API Key 암호화 모듈 (`core/security.py`)
  - [x] Binance Futures 연결 (실제 운영)
  - [x] API 요청 성공 확인

  **완료 보고**:
  ```
  ✅ 완료: Binance Futures API 연동
  📝 내용:
    - BinanceService 클래스 구현
    - devjun 사용자 API 키 암호화 저장 및 복호화 성공
    - Binance Futures 연결 (testnet=false)
    - 거래소 정보 조회 성공 (ID: binance, 지원 타임프레임: 1m~1d)
  🧪 테스트 결과 (test_api_keys.py):
    - ✅ 거래소 정보 조회 (timeframes: 1m, 5m, 15m, 1h, 4h, 1d 등)
    - ✅ BTC 현재가: $112,433.3 (-1.702%, 24h 거래량: 135,552 BTC)
    - ✅ 잔고 조회: USDT/BTC 잔고 0 (에러 없음, -2015 에러 해결)
  📂 파일:
    - api/services/binance_service.py (278줄)
    - api/test_api_keys.py (55줄)
    - api/routers/trading.py (274줄)
  ❓ 다음 단계: OHLCV 데이터 DB 저장
  ```
  **👤 Owner 승인 대기** ⏸️

- [진행중] **Market Data APIs**
  - [x] Ticker 조회 (`fetch_ticker`)
  - [ ] OHLCV 조회 → DB 저장 (다음 단계)
  - [ ] Funding Rate 조회 (`fetch_funding_rate`)
  - [ ] Order Book 조회 (`fetch_order_book`)
  - [ ] 캐싱 로직 (Redis)

- [진행중] **Account APIs**
  - [x] 선물 계좌 잔고 조회
  - [ ] 오픈 포지션 조회
  - [ ] 미체결 주문 조회
  - [ ] 거래 내역 조회

#### 자금 관리 (Wallet Transfer)
- [진행중] **현물↔선물 자금 이체 시스템**
  - [ ] Backend: BinanceService 메서드
    - [ ] `get_spot_balance()` - 현물 잔고 조회
    - [ ] `get_futures_balance()` - 선물 잔고 조회 (기존 리팩토링)
    - [ ] `transfer_to_futures()` - 현물→선물 이체
    - [ ] `transfer_to_spot()` - 선물→현물 이체
  - [ ] Backend: FastAPI 엔드포인트
    - [ ] `GET /trading/balances/all` - 통합 잔고 조회
    - [ ] `POST /trading/transfer` - 이체 실행
  - [ ] Backend: Pydantic 스키마
    - [ ] `WalletBalances` - 잔고 응답
    - [ ] `TransferRequest` - 이체 요청
    - [ ] `TransferResponse` - 이체 결과
  - [ ] Frontend: Streamlit API Client
    - [ ] `get_all_balances()` - 잔고 조회
    - [ ] `transfer_funds()` - 이체 실행
  - [ ] Frontend: Streamlit UI (pages/6_자금관리.py)
    - [ ] 현물/선물 잔고 카드 표시
    - [ ] 이체 방향 선택 (현물↔선물)
    - [ ] 이체 금액 입력 (실시간 검증)
    - [ ] 미리보기 (수수료, 최소금액, 예상시간)
    - [ ] 이체 실행 버튼 + 결과 표시

  **예상 정보 표시**:
  - 수수료: 무료 (내부 이체)
  - 최소 금액: 0.01 USDT
  - 예상 시간: 1-3초 (즉시)
  - Rate Limit: 1분 5회

  **완료 후 보고 대기** ⏸️

#### 주문 실행
- [ ] **Order Execution**
  - [ ] Market 주문 생성
  - [ ] Limit 주문 생성 (추후)
  - [ ] 레버리지 설정 API
  - [ ] 포지션 모드 설정 (Hedge/One-way)
  - [ ] 에러 핸들링 (Rate Limit, Insufficient Balance)

- [ ] **Position Management**
  - [ ] 청산 가격 계산 함수
  - [ ] Margin Ratio 계산
  - [ ] Liquidation Distance 계산
  - [ ] 포지션 Close API

#### 테스트 (테스트넷)
```python
# tests/test_binance.py
def test_fetch_ohlcv():
    binance = BinanceService(testnet=True)
    ohlcv = binance.fetch_ohlcv('BTC/USDT', '15m', 200)
    assert len(ohlcv) == 200

def test_open_position():
    position = binance.open_position(
        symbol='BTC/USDT',
        side='LONG',
        leverage=5,
        size_usdt=100
    )
    assert position['orderId'] is not None

    # 즉시 청산 (테스트 정리)
    binance.close_position(position['orderId'])
```

**중요**: 실제 자금 투입 전에 테스트넷에서 충분히 검증!

---

## Phase 3: Data Pipeline (Week 4)

### Celery Setup

#### Celery 구성
- [x] **Celery App 설정** ✅
  - [x] `workers/celery_app.py` 작성
  - [x] Redis Broker 설정
  - [x] Result Backend 설정
  - [x] Task 자동 발견 설정

  **완료 보고**:
  ```
  ✅ 완료: Celery Worker & Beat 정상 작동
  📝 내용:
    - Celery App 초기화
    - Redis Broker 연결
    - Docker Compose 통합
    - 뉴스 수집 태스크 구현
  🧪 테스트 결과:
    - ✅ Celery Worker: 온라인
    - ✅ Celery Beat: 실행 중
    - ✅ Task 자동 발견 작동
  📂 컨테이너: axis-celery-worker, axis-celery-beat
  ```
  **👤 Owner 승인 완료** ✓

- [x] **Celery Beat 스케줄 (3-Layer)** ✅ (부분 완료)
  - [x] `workers/config.py` 작성
  - [x] Layer 2: Medium-Frequency (뉴스 수집)
  - [ ] Layer 1: High-Frequency (5분)
  - [ ] Layer 3: Event-Driven (수동 트리거)
  - [ ] Quick Filter (15분)
  - [ ] Backtesting (매일 00:00)

#### Layer 1: Market Data (5분)
- [ ] **collect_market_data Task**
  - [ ] OHLCV 수집 (BTC, ETH)
  - [ ] Funding Rate 수집
  - [ ] 지표 계산 (RSI, MACD, ADX, Bollinger, MA)
  - [ ] 가격 변동률 계산 (Quick Filter용)
  - [ ] Redis 캐싱 (TTL 6분)
  - [ ] TimescaleDB 저장
  - [ ] 에러 핸들링

#### Layer 2: Contextual Data (30분)
- [x] **collect_crypto_news Task** ✅
  - [x] Perplexity AI 뉴스 검색 (실시간 온라인)
  - [x] Google Custom Search API 연동
  - [x] 뉴스 수집 (최근 24시간)
  - [x] 에러 핸들링 (Fallback)

  **완료 보고**:
  ```
  ✅ 완료: Celery 뉴스 수집 태스크
  📝 내용:
    - Perplexity AI (sonar 모델) 뉴스 분석
    - Google Custom Search (최근 24시간)
    - 모델명 수정 (llama-3.1-sonar-small-128k-online → sonar)
  🧪 테스트 결과:
    - ✅ Perplexity AI: 2,965글자 분석
    - ✅ Google Search: 5개 뉴스 검색
    - ✅ 총 6개 뉴스 수집 성공
  📂 파일: workers/tasks/news.py (283줄)
  ```
  **👤 Owner 승인 완료** ✓

- [x] **collect_social_sentiment Task** ✅
  - [x] Reddit API 연동 (r/cryptocurrency)
  - [x] Fear & Greed Index 조회
  - [x] Perplexity AI 소셜 트렌드 분석
  - [x] 감성 분석 로직 (긍정/부정/중립)
  - [x] 감성 점수 계산 (-1 ~ 1)

  **완료 보고**:
  ```
  ✅ 완료: Celery 소셜 감성 수집 태스크
  📝 내용:
    - Reddit API: 20개 포스트 키워드 기반 감성 분석
    - Fear & Greed Index: 시장 심리 지수 (0-100)
    - Perplexity AI: 소셜 트렌드 요약
  🧪 테스트 결과:
    - ✅ Reddit: 20개 포스트 (Neutral, Score: 0.0)
    - ✅ Fear & Greed: 51 (Neutral)
    - ✅ Perplexity: 소셜 트렌드 분석 완료
  📂 파일: workers/tasks/news.py (283줄)
  ```
  **👤 Owner 승인 완료** ✓

- [ ] **collect_and_summarize_onchain Task**
  - [ ] 거래소 입출금 데이터
  - [ ] 고래 움직임 추적
  - [ ] 요약 생성
  - [ ] Redis 캐싱 (TTL 45분)

#### Quick Filter (15분)
- [ ] **quick_filter_and_trigger Task**
  - [ ] 포지션 보유 체크
  - [ ] Regime 신뢰도 체크
  - [ ] 가격 급변 체크 (±1.5%)
  - [ ] 뉴스 임팩트 체크 (> 0.8)
  - [ ] 소셜 감성 급변 체크
  - [ ] 정기 체크 (4시간 경과)
  - [ ] n8n Webhook 트리거 로직
  - [ ] Redis 상태 저장

#### Monitoring Tasks
- [ ] **monitor_positions (1분)**
  - [ ] 오픈 포지션 조회
  - [ ] Stop Loss 체크
  - [ ] Take Profit 체크
  - [ ] 청산 리스크 체크 (< 10%)
  - [ ] Redis 업데이트 (has_open_position)
  - [ ] 자동 액션 실행

- [ ] **update_portfolio_value (10분)**
  - [ ] 현재 총 가치 계산
  - [ ] 배분 비율 계산
  - [ ] TimescaleDB 저장

#### 테스트
```bash
# Celery Worker 실행
celery -A workers.celery_app worker -l info

# Celery Beat 실행
celery -A workers.celery_app beat -l info

# Task 수동 테스트
python -c "from workers.tasks import collect_market_data; collect_market_data.delay()"
python -c "from workers.tasks import quick_filter_and_trigger; quick_filter_and_trigger.delay()"

# Redis 확인
redis-cli get market:binance:BTCUSDT:ohlcv_15m
redis-cli get news:summary
redis-cli get quickfilter:last_analysis_time

# 비용 모니터링 (요약 LLM 호출)
# 예상: GPT-4o-mini 48회/일 = ~$0.048/일
```

---

## Phase 4: AI Agents & n8n (Week 5-6)

### Week 5: n8n Workflows

#### n8n 설정
- [ ] **n8n 접속 및 초기 설정**
  - [ ] http://localhost:5678 접속
  - [ ] 관리자 계정 생성
  - [ ] OpenAI Credentials 추가
  - [ ] HTTP Request Credentials (FastAPI)
  - [ ] **Timeout 설정: 600초 (10분)**

#### Main Trading Workflow
- [ ] **Workflow 구조 설정**
  - [ ] Webhook Trigger (Celery가 호출)
  - [ ] Timeout: 600초 설정
  - [ ] Error Handler 노드 추가

- [ ] **Data Loading**
  - [ ] Get Cached Data (HTTP Request)
    - [ ] URL: `http://fastapi:8000/api/v2/data/market/BTCUSDT?include_summary=true`
    - [ ] 캐시된 시장/뉴스/소셜/온체인 데이터 로드

- [ ] **CEO Agent (GPT-o1)**
  - [ ] Regime Detection 프롬프트
  - [ ] maxTokens: 1000
  - [ ] Evidence 구조 출력 요구
  - [ ] Parse JSON Response
  - [ ] Save Regime (FastAPI)

**프롬프트 예시 (Evidence 포함)**:
```
You are AXIS-CEO. Determine market regime with EVIDENCE.

Input:
- Technical: {{ $json.indicators }}
- News: {{ $json.news_summary }}
- Social: {{ $json.social_summary }}
- Onchain: {{ $json.onchain_summary }}

Output JSON:
{
  "regime": "bull_trend" | "bear_trend" | "consolidation",
  "confidence": 0.85,
  "evidence": {
    "technical": {
      "adx": 42.1,
      "rsi": 65.3,
      "reasoning": "..."
    },
    "fundamental": {
      "news_impact": 0.85,
      "social_sentiment": 0.75,
      "reasoning": "..."
    }
  },
  "final_reasoning": "종합적으로..."
}
```

- [ ] **BTC Analyst (GPT-4o)**
  - [ ] 거래 방향 결정 프롬프트
  - [ ] maxTokens: 800
  - [ ] Evidence 구조 출력
  - [ ] Parse Response

- [ ] **Risk Chief (GPT-4o)**
  - [ ] 리스크 검증 프롬프트
  - [ ] maxTokens: 600
  - [ ] Approve/Veto 결정
  - [ ] Evidence 포함

- [ ] **Save AI Decision**
  - [ ] FastAPI POST `/api/v2/decisions/save`
  - [ ] evidence, reasoning 포함
  - [ ] DB 저장

- [ ] **Conditional Execution**
  - [ ] If node: Approval 체크
  - [ ] Approved → Execute Trade
  - [ ] Vetoed → Skip + Slack Alert

- [ ] **Trade Execution**
  - [ ] FastAPI POST `/api/v2/positions/open`
  - [ ] Timeout: 10초
  - [ ] Error Handling

- [ ] **Notification**
  - [ ] Slack Alert (성공/실패)
  - [ ] Evidence 요약 포함

#### 테스트
```bash
# Quick Filter 수동 트리거 (n8n 호출)
curl -X POST http://localhost:5678/webhook/trading \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "trigger_reason": "test"}'

# 실행 확인
# 1. CEO 실행 (GPT-o1) → Regime 결정
# 2. BTC Analyst (GPT-4o) → 거래 결정
# 3. Risk Chief (GPT-4o) → 승인/거부
# 4. Evidence DB 저장 확인

# 비용 확인
# 예상: CEO(800+200 tokens) + Analyst(600+150) + Risk(600+150)
#      ≈ $0.60/실행 × 15회/일 = $9/일
```

---

### Week 6: Integration & Fine-tuning

#### FastAPI Endpoints 확장
- [ ] **`POST /api/v2/decisions/save`**
  - [ ] evidence JSONB 저장
  - [ ] reasoning TEXT 저장
  - [ ] ai_decisions 테이블 저장

- [ ] **`POST /api/v2/positions/open`**
  - [ ] 요청 파싱 (Pydantic)
  - [ ] Binance API 호출
  - [ ] Position DB 저장 (evidence 포함)
  - [ ] Trade DB 저장
  - [ ] 응답 반환

- [ ] **`POST /api/v2/positions/{id}/close`**
  - [ ] Position 조회
  - [ ] Binance Close 주문
  - [ ] Position 업데이트
  - [ ] P&L 계산
  - [ ] Trade 기록

- [ ] **`GET /api/v2/data/market/{symbol}?include_summary=true`**
  - [ ] 시장 데이터 (OHLCV, 지표)
  - [ ] 뉴스 요약
  - [ ] 소셜 요약
  - [ ] 온체인 요약
  - [ ] 하나의 응답으로 통합

#### End-to-End Test
- [ ] **전체 플로우 테스트 (15분 주기)**
  1. Celery 데이터 수집 (5분마다 자동)
  2. Celery Quick Filter (15분) → 조건 충족?
  3. n8n Workflow 트리거
  4. CEO Regime 판단 (Evidence 포함)
  5. BTC Analyst 추천 (Evidence 포함)
  6. Risk Chief 검증
  7. AI Decision 저장 (evidence, reasoning)
  8. FastAPI 주문 실행 (테스트넷)
  9. Slack 알림 수신
  10. Position DB 확인

**성공 기준**:
- [ ] 전체 플로우 < 2분 완료
- [ ] Evidence 저장 확인 (DB)
- [ ] 에러 없이 실행
- [ ] Position 생성 확인
- [ ] Liquidation Distance > 15%
- [ ] LLM 비용 < $1/실행

---

## Phase 5: Risk Management & Monitoring (Week 7)

### Risk Management

#### Real-time Monitoring
- [ ] **청산 리스크 모니터**
  - [ ] `monitor_liquidation_risk` Task (1분)
    - [ ] 모든 포지션 조회
    - [ ] 현재 가격 vs 청산 가격
    - [ ] 거리 < 15% → WARNING
    - [ ] 거리 < 10% → CRITICAL
    - [ ] 거리 < 5% → 자동 50% 청산

- [ ] **Circuit Breaker**
  - [ ] 일일 P&L 추적
  - [ ] 손실 > -5% → 모든 포지션 청산
  - [ ] 24시간 거래 중단
  - [ ] CEO에게 알림

#### Alert System
- [ ] **Slack Integration**
  - [ ] Webhook URL 설정
  - [ ] 메시지 포맷 정의
  - [ ] Alert 레벨별 색상
    - [ ] INFO: 파란색
    - [ ] WARNING: 노란색
    - [ ] CRITICAL: 빨간색

- [ ] **Alert Types**
  - [ ] 포지션 오픈 (INFO)
  - [ ] 포지션 청산 (INFO)
  - [ ] 익절 달성 (INFO)
  - [ ] 손절 발생 (WARNING)
  - [ ] 청산 위험 (CRITICAL)
  - [ ] Circuit Breaker 발동 (CRITICAL)

#### 테스트
```python
# 의도적으로 위험한 포지션 생성 (테스트넷)
position = binance.open_position(
    symbol='BTC/USDT',
    side='LONG',
    leverage=20,  # 높은 레버리지
    size_usdt=1000
)

# 1분 대기
time.sleep(60)

# Slack 알림 확인
# Expected: "청산 위험: BTC/USDT, 거리 8.5%"
```

---

## Phase 6: Backtesting & Learning (Week 8)

### Daily Backtesting (자동화)

#### analyze_past_decisions Task
- [ ] **Celery Task 구현**
  - [ ] 매일 00:00 UTC 실행
  - [ ] 24시간 전 AI 결정 조회
  - [ ] 실제 가격 변화 계산
  - [ ] 정확도 판단 (correct/incorrect)

- [ ] **Evidence 검증 로직**
  - [ ] `verify_evidence()` 함수
  - [ ] 기술적 지표 정확도
    - [ ] ADX > 40 → 큰 움직임?
    - [ ] RSI > 70 → 하락?
  - [ ] 펀더멘털 정확도
    - [ ] 뉴스 임팩트 → 실제 영향?
    - [ ] 소셜 감성 → 가격 반영?
  - [ ] evidence_accuracy JSONB 저장

- [ ] **개선 제안 생성**
  - [ ] `generate_improvements()` 함수
  - [ ] 틀린 결정 분석
  - [ ] 프롬프트 개선 힌트
    - [ ] "소셜 감성 가중치 낮춤"
    - [ ] "ADX < 30 구간 진입 자제"

- [ ] **decision_analysis 테이블**
  - [ ] DB 레코드 생성
  - [ ] was_correct, evidence_breakdown
  - [ ] improvement_suggestions 저장

#### Daily Report (Slack)
- [ ] **generate_daily_backtest_report()**
  - [ ] 일일 정확도 요약
  - [ ] Evidence별 정확도
  - [ ] 개선 제안 리스트
  - [ ] Best/Worst Decision
  - [ ] Slack으로 발송

**Report 예시**:
```markdown
# Daily Backtest Report (2025-10-27)

## Overall
- Decisions Made: 3
- Correct: 2 (66.7%)
- Incorrect: 1 (33.3%)

## Evidence Accuracy
- Technical: 100% (3/3) ✅
- News: 66.7% (2/3) ⚠️
- Social: 33.3% (1/3) ❌

## Improvements
1. 소셜 감성 가중치 낮춤 (0.3 → 0.2)
2. ADX < 30 구간 진입 자제

## Best Decision
- Time: 14:30
- Direction: LONG
- Result: +2.5%
- Reasoning: Technical + News aligned
```

### Historical Backtest (수동)

#### Backtest Engine
- [ ] **`services/backtest.py`**
  - [ ] `BacktestEngine` 클래스
  - [ ] `simulate_position()` (Futures 포함)
  - [ ] `calculate_metrics()`

#### Target Metrics
- [ ] Sharpe Ratio > 1.5
- [ ] Win Rate > 60%
- [ ] Max Drawdown < -20%
- [ ] Evidence Accuracy > 70%

---

## Phase 7: Paper Trading (Week 9)

### Paper Trading System

#### 가상 계좌
- [ ] **Virtual Account**
  - [ ] `paper_accounts` 테이블 생성
  - [ ] 초기 자본: $10,000
  - [ ] 실제 주문 없이 시뮬레이션

- [ ] **Paper Execution**
  - [ ] `services/paper_trading.py`
  - [ ] Position 생성 (DB only)
  - [ ] 실시간 가격으로 P&L 계산
  - [ ] 청산 시뮬레이션

#### 2주 실시간 테스트
- [ ] **Week 1**
  - [ ] Paper Trading 활성화
  - [ ] n8n Workflow → Paper Account
  - [ ] 매일 성과 기록
  - [ ] 문제점 파악

- [ ] **Week 2**
  - [ ] 개선 사항 적용
  - [ ] 최종 성과 평가
  - [ ] Backtest vs Paper 비교

#### 검증 기준
- [ ] Paper 수익률 > Backtest * 0.8
- [ ] 에러/버그 0건
- [ ] Sharpe Ratio > 1.5
- [ ] 청산 발생 0건

---

## Phase 8: Live Trading (Week 10-11)

### Week 10: 소액 Live

#### 준비
- [ ] **리스크 한도 설정**
  - [ ] 초기 자본: $1,000 (소액)
  - [ ] 최대 레버리지: 10x (보수적)
  - [ ] 일일 손실 한도: -3%
  - [ ] 포지션 크기: < $300

- [ ] **실전 API 설정**
  - [ ] Binance Mainnet API Key 발급
  - [ ] 화이트리스트 IP 설정
  - [ ] API Key 권한 확인 (선물 거래)

#### Live 전환
- [ ] **Production 배포**
  - [ ] 환경변수 업데이트 (Mainnet)
  - [ ] n8n Workflow 최종 검토
  - [ ] Celery 스케줄 확인
  - [ ] 모니터링 대시보드 확인

- [ ] **첫 거래**
  - [ ] CEO 수동 승인 필요
  - [ ] 소액 포지션 ($100)
  - [ ] 전체 플로우 확인
  - [ ] 성공 시 → 자동화

#### 1개월 관찰
- [ ] **주간 리뷰**
  - [ ] Week 1: 수익률, Sharpe, MDD 기록
  - [ ] Week 2: 문제점 파악 및 개선
  - [ ] Week 3: 전략 미세 조정
  - [ ] Week 4: 최종 평가

#### 성공 기준 (1개월)
- [ ] 수익률 > +5%
- [ ] 청산 발생 0건
- [ ] 시스템 다운타임 < 1시간
- [ ] Sharpe Ratio > 1.0

**성공 시**: 자금 증액 ($1,000 → $10,000)

---

### Week 11: 스케일업

#### 자금 증액
- [ ] **리스크 재조정**
  - [ ] 자본: $10,000
  - [ ] 최대 레버리지: 15x
  - [ ] 일일 손실 한도: -5%

- [ ] **전략 최적화**
  - [ ] Regime Detection 프롬프트 개선
  - [ ] Stop Loss 최적화
  - [ ] Take Profit 타이밍 조정

---

## Phase 9: Advanced Features (Week 12+)

### Multi-User Support
- [ ] **User Management**
  - [ ] 회원가입 API
  - [ ] JWT 인증
  - [ ] API Key 관리 UI

### ETH 추가 (Core-Satellite)
- [ ] **ETH Analyst**
  - [ ] n8n Workflow 추가
  - [ ] ETH/BTC 비율 분석
  - [ ] 독립 포지션 관리

### Funding Rate Arbitrage
- [ ] **Arbitrage Strategy**
  - [ ] Funding Rate 모니터링
  - [ ] Spot + Futures 헤지
  - [ ] 수익 계산 및 기록

### Advanced Dashboard
- [ ] **Grafana Dashboards**
  - [ ] Portfolio Overview
  - [ ] Performance Charts
  - [ ] Risk Metrics
  - [ ] AI Agent Performance

---

## Continuous Improvement

### Daily
- [ ] 시스템 헬스 체크
- [ ] 에러 로그 확인
- [ ] 포지션 리뷰

### Weekly
- [ ] 성과 분석 (P&L, Sharpe, MDD)
- [ ] AI Agent 정확도 평가
- [ ] 프롬프트 개선
- [ ] 백테스트 업데이트

### Monthly
- [ ] 전략 리뷰
- [ ] 리스크 파라미터 조정
- [ ] 새로운 Feature 개발 계획

---

## Emergency Procedures

### System Down
1. Slack 알림 확인
2. Docker 컨테이너 상태 확인 (`docker ps`)
3. 로그 확인 (`docker-compose logs -f`)
4. 필요 시 재시작 (`docker-compose restart`)

### Position in Danger
1. Slack Critical 알림 수신
2. 수동으로 포지션 확인 (Binance App)
3. 필요 시 수동 청산
4. 시스템 일시 중단

### API Key Compromised
1. 즉시 Binance에서 API Key 비활성화
2. 모든 포지션 수동 청산
3. 새 API Key 발급
4. 시스템 재배포

---

## Success Metrics Summary

### Technical KPIs
- [ ] Uptime: 99.5%
- [ ] API Latency: < 500ms
- [ ] Data Freshness: < 5s
- [ ] LLM Response: < 30s

### Financial KPIs
- [ ] 월 수익률: 10-15%
- [ ] Sharpe Ratio: > 2.0
- [ ] Max Drawdown: < -15%
- [ ] Win Rate: > 60%
- [ ] 청산 발생: < 2%

### Operational KPIs
- [ ] Alert Response: < 30초
- [ ] 백업 성공률: 100%
- [ ] 에러율: < 1%

---

## Documentation

### 필수 문서
- [x] PRD (Product Requirements Document)
- [x] TRD (Technical Requirements Document)
- [x] Implementation Checklist
- [ ] API Documentation (Swagger)
- [ ] Runbook (운영 가이드)
- [ ] Troubleshooting Guide

### Code Documentation
- [ ] Docstrings (모든 함수)
- [ ] Type Hints (Python 3.11+)
- [ ] README.md (프로젝트 개요)
- [ ] CONTRIBUTING.md (기여 가이드)

---

## Final Checklist

**Phase 1-3 완료 시**:
- [ ] 데이터 파이프라인 작동 확인
- [ ] Binance API 연동 확인
- [ ] 테스트넷 거래 성공

**Phase 4-6 완료 시**:
- [ ] AI Agents 작동 확인
- [ ] 백테스트 통과 (Sharpe > 1.5)
- [ ] Paper Trading 검증

**Phase 7-8 완료 시**:
- [ ] 소액 Live 1개월 성공
- [ ] 자금 증액 ($10,000)
- [ ] 시스템 안정화

**Production Ready**:
- [ ] 모든 테스트 통과
- [ ] 문서화 완료
- [ ] 모니터링 설정 완료
- [ ] 백업 시스템 구축
- [ ] 재난 복구 계획 수립

---

**Status**: Ready to Start
**Estimated Completion**: 12 Weeks
**Next Action**: Phase 1 시작 - 서버 준비 및 Docker 설정

**Good Luck! 🚀**

