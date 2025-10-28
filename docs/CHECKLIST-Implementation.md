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
- [ ] **Task 1.1: 서버 준비**
  - [ ] Ubuntu 22.04 LTS 설치
  - [ ] Docker 설치 및 설정
  - [ ] Docker Compose 설치

  **완료 보고**:
  ```
  ✅ 완료: 서버 기본 환경
  📝 내용: Ubuntu 22.04 + Docker + Docker Compose
  🧪 테스트: docker --version, docker-compose --version
  ❓ 다음 단계 진행?
  ```
  **👤 Owner 승인 대기** ⏸️

- [ ] **Task 1.2: 방화벽 설정**
  - [ ] 방화벽 설정 (포트 8000, 5678, 3000)
  - [ ] SSL 인증서 발급 (Let's Encrypt)

  **완료 보고 후 승인 대기** ⏸️

- [ ] **Task 1.3: Docker Compose 설정**
  - [ ] `docker-compose.yml` 작성
  - [ ] PostgreSQL 컨테이너 설정
  - [ ] Redis 컨테이너 설정
  - [ ] TimescaleDB extension 활성화
  - [ ] 환경변수 파일 `.env` 작성
  - [ ] 볼륨 매핑 확인

  **완료 보고**:
  ```
  ✅ 완료: Docker Compose 설정
  📝 내용: PostgreSQL, Redis, n8n 컨테이너 설정
  🧪 테스트: docker-compose up -d 성공, 모든 컨테이너 RUNNING
  📂 파일: docker-compose.yml, .env
  ❓ 다음 단계 진행?
  ```
  **👤 Owner 승인 대기** ⏸️

- [ ] **Task 1.4: Database 초기화**
  - [ ] PostgreSQL 연결 테스트
  - [ ] TimescaleDB extension 설치
  - [ ] 데이터베이스 생성 (`axis_capital`)
  - [ ] 사용자 생성 및 권한 설정

  **완료 보고 후 승인 대기** ⏸️

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
- [ ] **Task 2.1: Core Tables 생성**
  - [ ] `users` 테이블 생성
  - [ ] `positions` 테이블 생성
  - [ ] `trades` 테이블 생성

  **완료 보고 후 승인 대기** ⏸️

- [ ] **Task 2.2: AI Tables 생성**
  - [ ] `ai_decisions` 테이블 생성 (evidence, reasoning 포함)
  - [ ] `decision_analysis` 테이블 생성
  - [ ] `regime_history` 테이블 생성

  **완료 보고 후 승인 대기** ⏸️

- [ ] **Task 2.3: 인덱스 & 제약조건**
  - [ ] 모든 인덱스 생성 (TRD 참고)
  - [ ] 제약조건 확인 (FK, NOT NULL)

  **완료 보고 후 승인 대기** ⏸️

- [ ] **TimescaleDB Tables**
  - [ ] `market_data` 테이블 생성
  - [ ] Hypertable 변환
  - [ ] `portfolio_snapshots` 테이블 생성
  - [ ] Hypertable 변환
  - [ ] `funding_rate_history` 테이블 생성
  - [ ] 인덱스 최적화

#### FastAPI 기본 구조
- [ ] **프로젝트 구조 생성**
  ```
  api/
  ├── main.py
  ├── requirements.txt
  ├── routers/
  ├── services/
  ├── models/
  └── core/
  ```
  - [ ] `main.py` FastAPI 앱 초기화
  - [ ] `requirements.txt` 작성
  - [ ] `core/config.py` 설정 파일
  - [ ] `core/database.py` DB 연결
  - [ ] `core/redis_client.py` Redis 연결

- [ ] **Health Check API**
  - [ ] `GET /health` 엔드포인트
  - [ ] Database 연결 확인
  - [ ] Redis 연결 확인
  - [ ] 응답 시간 < 500ms 확인

#### 테스트
```bash
# FastAPI 실행
cd api
pip install -r requirements.txt
uvicorn main:app --reload

# Health Check
curl http://localhost:8000/health
# Expected: {"status": "healthy", "database": "ok", "redis": "ok"}
```

---

## Phase 2: Exchange Integration (Week 3)

### Binance Futures API

#### 기본 연동
- [ ] **CCXT 설정**
  - [ ] `services/binance.py` 생성
  - [ ] API Key 암호화 모듈 (`core/security.py`)
  - [ ] Binance 테스트넷 연결
  - [ ] API 요청 성공 확인

- [ ] **Market Data APIs**
  - [ ] OHLCV 조회 (`fetch_ohlcv`)
  - [ ] Ticker 조회 (`fetch_ticker`)
  - [ ] Funding Rate 조회 (`fetch_funding_rate`)
  - [ ] Order Book 조회 (`fetch_order_book`)
  - [ ] 캐싱 로직 (Redis)

- [ ] **Account APIs**
  - [ ] 선물 계좌 잔고 조회
  - [ ] 오픈 포지션 조회
  - [ ] 미체결 주문 조회
  - [ ] 거래 내역 조회

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
- [ ] **Celery App 설정**
  - [ ] `workers/celery_app.py` 작성
  - [ ] Redis Broker 설정
  - [ ] Result Backend 설정
  - [ ] Task 자동 발견 설정

- [ ] **Celery Beat 스케줄 (3-Layer)**
  - [ ] `workers/scheduler.py` 작성
  - [ ] Layer 1: High-Frequency (5분)
  - [ ] Layer 2: Medium-Frequency (30분)
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
- [ ] **collect_and_summarize_news Task**
  - [ ] 뉴스 소스 연동 (CryptoPanic, CoinTelegraph)
  - [ ] GPT-4o-mini 요약 API
  - [ ] Evidence 구조 생성
  - [ ] Redis 캐싱 (TTL 45분)
  - [ ] Failure Fallback (이전 요약 or Neutral)

- [ ] **collect_and_analyze_social Task**
  - [ ] Twitter API 연동
  - [ ] Reddit API 연동
  - [ ] 감성 분석 로직
  - [ ] 요약 생성
  - [ ] Redis 캐싱 (TTL 45분)

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

