# Product Requirements Document (PRD)
## AXIS Capital - AI Futures Trading System

**Version**: 2.0 (Final)
**Date**: 2025-10-27
**Author**: AXIS Development Team
**Status**: Ready for Implementation

---

## Executive Summary

### Vision
**"Profit in any market direction through AI-driven futures trading"**

세계 최고 수준의 퀀트 트레이딩 회사처럼 운영되는 완전 자율 AI 시스템. 상승장에서는 롱(Long), 하락장에서는 숏(Short)으로 양방향 수익 창출.

### Core Principles

```
1. Simplicity over Complexity
   → BTC 중심 (80%), ETH 보조 (20%)
   → 복잡한 다중 자산 포트폴리오 지양

2. Momentum over Mean Reversion
   → 크립토는 추세 시장
   → Let Winners Run (승자를 자르지 않음)

3. Direction over Leverage
   → 방향(Long/Short) 판단이 가장 중요
   → 레버리지는 보조 수단

4. Cost Efficiency
   → 15분마다 분석, 고품질 시그널만 거래
   → 리밸런싱은 필수 상황만

5. Regime-Adaptive
   → Bull/Bear/Consolidation 별 전략 전환
   → 시장 환경에 동적 대응
```

---

## 1. Market Analysis

### 1.1 Cryptocurrency Market Characteristics

| 특성 | 설명 | 전략 시사점 |
|------|------|-------------|
| **High Volatility** | 일 변동성 3-5% | 높은 레버리지 가능 |
| **Momentum-Driven** | 추세 지속성 강함 | 리밸런싱 최소화 |
| **24/7 Trading** | 무휴 거래 | 자동화 필수 |
| **High Correlation** | BTC-Alts 0.85+ | 진짜 분산 효과 < 5% |
| **Leverage Available** | 1x ~ 125x | 신중한 레버리지 관리 |

### 1.2 Why Futures Only?

```
현물의 한계:
  ✗ 상승장에만 수익 (하락장 무력)
  ✗ 레버리지 없음 (자본 효율 낮음)
  ✗ 수익률 제한적

선물의 장점:
  ✅ 양방향 거래 (Long + Short)
  ✅ 레버리지 (자본 효율 극대화)
  ✅ Funding Rate 차익거래 가능
  ✅ 1배 레버리지 = 현물과 동일
```

---

## 2. User Personas

### Primary User: Individual Trader (개인 투자자)

**Goals**:
- 일 0.3-0.5% 안정적 수익 (월 10-15%)
- 24시간 자동 거래 (잠자는 동안에도)
- 하락장에서도 수익 (Short)

**Pain Points**:
- 감정 개입 (공포, 탐욕)
- 24시간 모니터링 불가능
- 기술적 분석 부족
- 하락장 속수무책

**Solution**:
- AI가 감정 없이 거래
- 완전 자동화 (Celery + n8n)
- 200+ 지표 자동 분석
- Short 전략으로 하락장 공략

---

## 3. Product Goals

### 3.1 Business Goals

| Metric | Target | Stretch |
|--------|--------|---------|
| **월 수익률** | 10% | 15% |
| **Sharpe Ratio** | 2.0 | 2.5 |
| **Max Drawdown** | < -15% | < -10% |
| **Win Rate** | 60% | 70% |
| **청산 발생률** | < 2% | 0% |

### 3.2 Technical Goals

| Metric | Target |
|--------|--------|
| **시스템 가동률** | 99.5% |
| **API 응답 시간** | < 500ms |
| **데이터 지연** | < 5초 |
| **LLM 응답 시간** | < 30초 |
| **거래 실행 시간** | < 10초 |

---

## 4. Core Features

### 4.1 Market Regime Detection

**가장 중요한 기능**: 지금 어떤 장인가?

#### 3가지 Regime

| Regime | Detection Criteria | Strategy |
|--------|-------------------|----------|
| **Bull Trend** | ADX > 25, Price > MA(50,200), RSI > 50 | LONG 중심, 높은 레버리지 |
| **Bear Trend** | ADX > 25, Price < MA(50,200), RSI < 50 | SHORT 중심, 중간 레버리지 |
| **Consolidation** | ADX < 25, 박스권 | 양방향 스윙 or HOLD |

**Output Example**:
```json
{
  "regime": "bull_trend",
  "confidence": 0.85,
  "duration": "3 days",
  "strength": "strong",
  "evidence": {
    "adx": 42,
    "price_vs_ma50": "+8.5%",
    "trend_consistency": "high"
  }
}
```

---

### 4.2 Core-Satellite Portfolio

#### Portfolio Structure

```
Core (80%): BTC
  - Primary bet
  - Dynamic Leverage (3x ~ 20x)
  - Long or Short based on Regime

Satellite (20%): ETH
  - Secondary bet
  - Only when diverges from BTC
  - Lower Leverage (2x ~ 12x)
```

#### Why This Structure?

```
BTC 중심 이유:
  ✅ 시장 대표성 (Dominance 50%+)
  ✅ 최고 유동성 (슬리피지 최소)
  ✅ 가장 안정적 (러그풀 위험 0)

ETH 보조 이유:
  ✅ 2위 시총 (안전성)
  ✅ 다른 내러티브 (L2, DeFi)
  ✅ BTC와 다를 때 기회 (드물지만)

Alts 제외 이유:
  ✗ 높은 변동성 → 청산 위험
  ✗ 유동성 부족 → 슬리피지
  ✗ 러그풀/해킹 리스크
```

---

### 4.3 Minimal Rebalancing Strategy

#### Philosophy: "Don't Cut Your Winners"

크립토는 **Momentum Market** (추세 시장):
- Bull Run: 50% → 100% → 200% 상승
- 너무 자주 리밸런싱 = 승자를 자름 = 기회비용

#### Rebalancing Rules (Only 3 Cases)

```yaml
Case 1: Regime Change (월 1-3회)
  Bull → Bear 전환:
    - Close all LONG positions
    - Open SHORT positions
    - Portfolio 완전 전환

  Trigger: Regime 확정 (Confidence > 0.8)

Case 2: Extreme Concentration (거의 없음)
  Single Asset > 95%:
    - 위험 분산 필요
    - 5-10% 매도

  Trigger: 비정상적 급등

Case 3: Black Swan (연 1-2회?)
  BTC ±20% in 1 hour:
    - 비정상 변동
    - 50% 포지션 청산
    - 24시간 관망

  Trigger: 극단적 변동성

일반 상황:
  BTC +10% → DO NOTHING (Let it run)
  BTC -5% → DO NOTHING (Stop loss가 처리)
```

#### Cost Comparison

| Strategy | 분석 빈도 | 실제 거래 | 수수료 비용 | 슬리피지 |
|----------|---------|---------|------------|---------|
| Manual | 부정기 | 월 20-30회 | 2-3% | 1-2% |
| **AI Automated** | **15분마다** | **월 20-30회** | **2-3%** | **0.5-1%** |

**장점**: 사람 불가능한 24/7 모니터링, 감정 배제, 슬리피지 최소화

---

### 4.4 Hierarchical Data Collection

#### Philosophy: "Right Data, Right Time, Right Cost"

암호화폐 시장은 **다양한 시간 주기**의 데이터가 필요:
- 가격: 실시간 변화 (5분)
- 뉴스: 중간 빈도 (30-60분)
- 이벤트: 발생 시점 (CPI, FOMC 등)

#### 3-Layer Architecture

```yaml
Layer 1: High-Frequency (5분)
  목적: 시장 변화 포착
  데이터:
    - OHLCV (BTC/ETH)
    - Price, Volume
    - Funding Rate
    - Open Interest
  저장: Redis (원본)
  비용: 무료 (Binance API)

Layer 2: Medium-Frequency (30-60분)
  목적: 맥락 파악
  데이터:
    - 뉴스 (CryptoPanic, CoinTelegraph)
    - 소셜 미디어 (Twitter, Reddit)
    - 온체인 데이터 (거래소 입출금, 고래 움직임)
  처리: GPT-4o-mini 요약 (1-2문장)
  저장: Redis (요약본)
  비용: ~$2/월

Layer 3: Event-Driven (이벤트 발생 시)
  목적: 급변 대응
  이벤트:
    - CPI 발표 (월 1회)
    - FOMC 금리 결정 (연 8회)
    - 거래소 해킹, BTC Halving
  처리: 실시간 수집 + 즉시 요약
  트리거: n8n 긴급 호출
  비용: ~$5/월
```

#### 요약 예시 (토큰 절감)

**원본 뉴스** (2,000 토큰):
```
Title: Bitcoin ETF Approval Decision Delayed Again by SEC
Content: The U.S. Securities and Exchange Commission has once again delayed
its decision on several spot Bitcoin ETF applications, pushing the deadline
to December 2024. This marks the third delay for BlackRock's iShares Bitcoin
Trust application... [1,800 more words]
```

**GPT-4o-mini 요약** (100 토큰):
```json
{
  "headline": "SEC, 비트코인 ETF 승인 12월로 연기",
  "sentiment": "neutral_to_bearish",
  "impact_score": 0.65,
  "key_facts": [
    "BlackRock 포함 3개 ETF 신청 심사 연기",
    "최종 결정 12월 예정",
    "시장 단기 실망감 예상"
  ],
  "reasoning": "세 번째 연기로 시장 피로감 증가. 단기 부정적이나 장기 승인 가능성 여전히 높음."
}
```

**토큰 절감**: 95% ↓ (2,000 → 100)

---

### 4.5 Evidence-Based Decision System

#### Philosophy: "No Decision Without Evidence"

모든 의사결정은 **검증 가능한 근거**가 있어야:
- 백테스팅 시 "왜 틀렸는지" 분석 가능
- 프롬프트 개선의 기초
- 지속적 학습 루프

#### Evidence 구조

```json
{
  "decision": {
    "action": "LONG",
    "confidence": 0.85,
    "evidence": {
      "technical": {
        "adx": 42.1,
        "rsi": 65.3,
        "price_vs_ma50": "+8.5%",
        "macd_histogram": 120,
        "support_level": 67500,
        "reasoning": "강한 상승 추세. ADX 42로 추세 확실. RSI 과매수 아님. 지지선 확인됨."
      },
      "fundamental": {
        "news_impact": 0.85,
        "news_summary": "ETF 승인 임박, SEC 최종 검토",
        "social_sentiment": 0.75,
        "social_reasoning": "긍정 멘션 4배 증가. 고래 축적 신호.",
        "onchain_signal": "accumulation",
        "onchain_reasoning": "거래소 순유출 5,000 BTC. 매수 압력."
      },
      "risk": {
        "liquidation_distance": 0.067,
        "margin_ratio": 0.72,
        "max_loss": -3000,
        "approval": "APPROVED"
      }
    },
    "final_reasoning": "기술적/펀더멘털 모두 긍정. 리스크 허용 범위 내. 진입 타이밍 좋음."
  }
}
```

#### Backtesting 검증

```python
# 24시간 후 분석
if actual_price_change > 0 and decision == "LONG":
    result = "CORRECT"

    # Evidence 세부 검증
    if evidence['technical']['adx'] > 40:
        evidence_quality['adx'] = "USEFUL"

    if evidence['social_sentiment'] > 0.7 and actual_change > 0.05:
        evidence_quality['social'] = "HIGHLY_USEFUL"

    # 프롬프트 개선 힌트
    if evidence['news_impact'] > 0.8 but actual_change < 0.01:
        improvement = "뉴스 임팩트 가중치 낮춤"
```

---

### 4.6 Quick Filter Strategy

#### Problem: 불필요한 LLM 호출

```
시나리오: 15분마다 n8n 실행
         일 96회 AI 분석
         실제 거래: 일 1-2회
         → 불필요한 호출 94-95회

비용: 일 96회 × $0.02 = $1.92/일 = $57/월
      (실제 필요: $3/월)
```

#### Solution: 2단계 필터링

**Stage 1: Quick Filter** (Celery, 무료)
```python
def should_trigger_ai_analysis():
    """AI 분석이 필요한가?"""

    # 1. 이미 포지션 보유 중 → SKIP
    if has_open_position():
        log("포지션 보유 중, 스킵")
        return False

    # 2. Regime 불확실 → TRIGGER
    regime = redis.get('regime:current')
    if regime['confidence'] < 0.8:
        log("Regime 불확실, AI 분석 필요")
        return True

    # 3. 가격 급변 (15분 내 ±1.5%) → TRIGGER
    price_change = get_price_change_15m()
    if abs(price_change) > 1.5:
        log(f"가격 급변 {price_change:.2f}%, AI 분석")
        return True

    # 4. 중요 뉴스 → TRIGGER
    news = redis.get('news:summary')
    if news and news['impact_score'] > 0.8:
        log("중요 뉴스 감지, AI 분석")
        return True

    # 5. 소셜 감성 급변 → TRIGGER
    social = redis.get('social:summary')
    if social and abs(social['score_change_1h']) > 0.3:
        log("소셜 감성 급변, AI 분석")
        return True

    # 6. 4시간 경과 → TRIGGER (정기 체크)
    last_analysis = redis.get('last_analysis_time')
    if time.time() - last_analysis > 4 * 3600:
        log("4시간 경과, 정기 체크")
        return True

    # 나머지: SKIP
    log("조건 미충족, 스킵")
    return False
```

**Stage 2: AI Analysis** (n8n, 유료)
```
Quick Filter 통과 시:
  → n8n Workflow 트리거
  → CEO/BTC-Analyst/Risk 분석
  → 거래 결정
```

#### 효과

| 항목 | Before | After | 개선 |
|-----|--------|-------|------|
| **AI 호출** | 96회/일 | 15회/일 | 84% ↓ |
| **LLM 비용** | $57/월 | $9/월 | 84% ↓ |
| **실제 거래** | 일 1-2회 | 일 1-2회 | 동일 |

**절감**: $48/월 (연 $576)

---

### 4.7 Dynamic Leverage System

#### Leverage = f(Regime, Confidence, Volatility)

```python
def calculate_optimal_leverage(regime, confidence, btc_volatility):
    """
    동적 레버리지 계산
    """
    base_leverage = {
        'bull_trend': 15,
        'bear_trend': 10,
        'consolidation': 3
    }[regime]

    # Confidence 조정
    leverage = base_leverage * confidence

    # Volatility 조정 (높을수록 낮춤)
    if btc_volatility > 80:
        leverage *= 0.7
    elif btc_volatility > 60:
        leverage *= 0.85

    # 한도
    return min(leverage, 20)

# Example:
# Bull Trend, Confidence 0.9, Volatility 50
# → 15 * 0.9 * 1.0 = 13.5x
```

---

### 4.5 Risk Management

#### Position-Level Risk

```yaml
Entry Rules:
  - 추세 확인 (ADX > 25 for trend)
  - 지지/저항 근처 진입
  - 청산 가격 거리 > 15%

Stop Loss (자동):
  - Trend: Entry 대비 -3%
  - Consolidation: Entry 대비 -1.5%
  - 절대 청산 방어선 (Entry 대비 -5%)

Take Profit (단계별):
  - 1차: +5% (30% 청산)
  - 2차: +10% (40% 청산)
  - 3차: Trailing Stop (30% 보유)

Liquidation Protection:
  - 거리 < 15% → 경고
  - 거리 < 10% → 포지션 50% 축소
  - 거리 < 5% → 긴급 전체 청산
```

#### Portfolio-Level Risk

```yaml
Circuit Breaker:
  - 일일 손실 > -5% → 24시간 거래 중단
  - 주간 손실 > -15% → CEO 긴급 리뷰

Max Exposure:
  - BTC: < 90% (과도한 집중 방지)
  - Total Leverage: < 15x (평균)
  - Single Position Size: < 50%

Margin Management:
  - Margin Ratio 항상 > 60%
  - 50% 이하 → 자동 증거금 추가 or 청산
```

---

## 5. AI Agent Organization

### 5.1 Executive Level

#### AXIS-CEO (GPT-o1)

**Role**: 최고 경영자, 전략 방향 결정

**Input**:
- 전일 성과
- 현재 시장 환경
- 각 Agent 리포트 요약

**Output**:
```json
{
  "regime": "bull_trend",
  "confidence": 0.85,
  "risk_tolerance": "aggressive",
  "rebalancing_mode": "minimal",
  "global_leverage_limit": 15,
  "trading_directive": "Focus on BTC LONG, ETH secondary"
}
```

**Execution**: 1일 1회 (09:00)

---

### 5.2 Research Division

#### AXIS-BTC-Analyst (GPT-4o)

**Role**: BTC 전문 분석가

**Input**:
- OHLCV (200 candles, 15m)
- 200+ 기술 지표
- 온체인 데이터 (거래소 유출입)
- Funding Rate

**Output**:
```json
{
  "asset": "BTC",
  "direction": "LONG",
  "strength_score": 0.85,
  "optimal_leverage": 15,
  "entry_zone": "67500-68000",
  "target": 74800,
  "stop_loss": 66000,
  "rationale": "Strong uptrend, ADX 42, support confirmed at $67.5k"
}
```

---

#### AXIS-ETH-Analyst (GPT-4o)

**Role**: ETH 전문 분석가

**Activation**:
- ETH/BTC 비율이 BTC와 다른 움직임 보일 때만
- 예: BTC 약세지만 ETH 강세 (L2 호재 등)

**Output**: BTC Analyst와 동일 포맷

---

### 5.3 Risk Management

#### AXIS-Risk-Chief (GPT-4o)

**Role**: 리스크 검증, Veto 권한

**Checks**:
```yaml
Pre-Trade Validation:
  - 청산 가격 거리 > 15% ✓
  - Total Leverage < 15x ✓
  - Portfolio concentration < 95% ✓
  - Margin Ratio > 60% ✓

Real-time Monitoring (1분마다):
  - 청산 거리 < 10% → 알림
  - 청산 거리 < 5% → 긴급 청산
  - 일일 손실 > -5% → Circuit Breaker
```

**Veto Conditions**:
- 레버리지 > 20x
- 청산 거리 < 15%
- Margin Ratio < 50%
- 일일 거래 횟수 > 5회 (과도한 거래)

---

### 5.4 Operations

#### AXIS-Performance-Analyst (GPT-4o-mini)

**Role**: 성과 분석 및 리포팅

**Daily Report**:
```markdown
# Daily Performance Report
Date: 2025-01-27

## Summary
- Daily Return: +1.8%
- MTD Return: +12.5%
- Win Rate: 65%
- Sharpe Ratio: 2.3

## Today's Trades
1. BTC LONG @ $68,000 → $70,400 (+3.5%, +52.5% with 15x)
2. ETH HOLD (no opportunity)

## Best Decision
- Entry timing 완벽 (지지선 근처)
- Leverage 적절 (15x)

## What to Improve
- 익절 너무 빠름 (목표 +10%였으나 +3.5%에 청산)
```

---

## 6. Trading Workflow

### 6.1 15-Minute Trading Cycle

#### 전체 플로우

```
[매 5분] Celery: 시장 데이터 수집
  ↓
  OHLCV, Funding Rate, Indicators 수집
  → Redis 캐싱 (TTL 6분)

[매 30분] Celery: 뉴스/소셜 요약
  ↓
  1. 뉴스 수집 → GPT-4o-mini 요약
  2. 소셜 수집 → 감성 분석 + 요약
  3. 온체인 데이터 → 요약
  → Redis 캐싱 (TTL 45분)

[매 15분] Celery: Quick Filter
  ↓
  포지션 체크, 가격 변동, 뉴스 임팩트 확인

  조건 충족? (15% 확률)
    ↓ YES
    n8n Webhook 트리거

    ↓ NO (85% 케이스)
    스킵 (15분 후 재확인)

[조건 충족 시] n8n Workflow (일 10-20회)
  ↓
  00:00 - Load Cached Data (Redis)
    - 시장 데이터 (OHLCV, 지표)
    - 뉴스 요약
    - 소셜 요약
    - 온체인 요약

  00:01 - CEO Agent (GPT-o1)
    - Regime 판단
    - Evidence 수집

  00:02 - BTC Analyst (GPT-4o)
    - 거래 방향 결정
    - 진입 가격, 레버리지
    - Evidence 수집

  00:03 - Risk Chief (GPT-4o)
    - 리스크 검증
    - Approve or Veto

  00:04 - Execute or Skip
    - Approved → FastAPI 거래 실행
    - Vetoed → 스킵
    - Evidence 저장 (백테스팅용)
```

#### 시간별 예시 (하루)

```
00:00 ✓ 데이터 수집
00:05 ✓ 데이터 수집
00:10 ✓ 데이터 수집
00:15 ✓ 데이터 수집 + Quick Filter → 스킵
00:20 ✓ 데이터 수집
00:25 ✓ 데이터 수집
00:30 ✓ 데이터 수집 + 뉴스 요약 + Quick Filter → 스킵
...

06:45 ✓ 데이터 수집 + Quick Filter → 🔥 조건 충족!
      → n8n 트리거 → AI 분석 → LONG 진입

07:00 ✓ 데이터 수집 + Quick Filter → 스킵 (이미 포지션)
07:15 ✓ 포지션 모니터링 중 → 스킵
...

14:30 ✓ Stop Loss 발동 → 자동 청산
14:45 ✓ Quick Filter → 🔥 조건 충족!
      → n8n 트리거 → AI 분석 → 시기상조, 패스
```

#### 하루 통계 (평균)

| 작업 | 빈도 | 비용 |
|-----|-----|-----|
| 데이터 수집 | 288회 | 무료 |
| 뉴스/소셜 요약 | 48회 | $0.07 |
| Quick Filter | 96회 | 무료 |
| AI 분석 (n8n) | 15회 | $0.30 |
| 실제 거래 | 1-2회 | 수수료 별도 |

**월 비용**: ~$10 (LLM only)

### 6.2 Regime Change Scenario

```
Scenario: Bull → Bear 전환

Detection:
  - 3일 연속 하락
  - MA(50) Death Cross MA(200)
  - ADX 여전히 > 25 (추세 강함)
  - RSI < 40

CEO Decision:
  "Regime changed to Bear Trend"
  Confidence: 0.82

Action:
  1. Close all LONG positions (익절 or 손절)
  2. Wait 1 hour (급반등 대비)
  3. Open SHORT positions
     - BTC SHORT 70% @ 8x
     - ETH SHORT 30% @ 6x or HOLD

Result:
  Portfolio 완전 전환 (LONG → SHORT)
```

---

## 7. User Interface Requirements

### 7.1 Real-time Dashboard

**Must-Have Metrics**:
```
Portfolio Overview:
  - Total Value (USD)
  - Today P&L (% and $)
  - Current Positions (BTC/ETH)
  - Effective Leverage

Performance:
  - Daily/Weekly/Monthly Returns
  - Sharpe Ratio (30d)
  - Max Drawdown (Current)
  - Win Rate

Risk Indicators:
  - Liquidation Distance (closest)
  - Margin Ratio
  - Daily Loss Limit Remaining

System Health:
  - Last Update Time
  - Data Latency
  - Celery Queue Length
```

### 7.2 Notification System

**Slack/Telegram Alerts**:

```yaml
INFO (매일):
  - 09:00 전략 브리핑
  - 21:00 일일 성과 리포트

WARNING (즉시):
  - 청산 거리 < 15%
  - 일일 손실 > -3%
  - Regime 변경 감지

CRITICAL (즉시 + SMS):
  - 청산 거리 < 10%
  - 일일 손실 > -5% (Circuit Breaker)
  - API 연결 실패
```

---

## 8. Cost Analysis

### 8.1 LLM Cost Breakdown

#### GPT-4o-mini (요약용)
```
사용: 뉴스/소셜 요약
빈도: 48회/일 (30분마다)
토큰: 500 input + 100 output
비용: $0.15/1M input, $0.60/1M output
계산: 48 × (500×0.15 + 100×0.60) / 1,000,000 × 30일
    = $1.44/월
```

#### GPT-o1 (CEO Agent)
```
사용: Regime Detection
빈도: 15회/일 (Quick Filter 통과 시)
토큰: 800 input + 200 output
비용: $15/1M input, $60/1M output
계산: 15 × (800×15 + 200×60) / 1,000,000 × 30일
    = $5.40 + $5.40 = $10.80/월
```

#### GPT-4o (Analyst, Risk)
```
사용: BTC 분석, Risk 검증
빈도: 30회/일 (CEO 후 각 1회)
토큰: 600 input + 150 output
비용: $2.5/1M input, $10/1M output
계산: 30 × (600×2.5 + 150×10) / 1,000,000 × 30일
    = $1.35 + $1.35 = $2.70/월
```

### 8.2 Total Monthly Cost

| 항목 | 월 비용 |
|-----|--------|
| GPT-4o-mini (요약) | $1.44 |
| GPT-o1 (CEO) | $10.80 |
| GPT-4o (분석/리스크) | $2.70 |
| **LLM 합계** | **$14.94** |
| Redis Cloud (256MB) | $7.00 |
| VPS (8GB RAM) | $30.00 |
| **총 운영비** | **$51.94** |

### 8.3 거래 비용 (별도)

| 항목 | 예시 (월 20회 거래) |
|-----|------------------|
| Binance 수수료 (0.04%) | $8,000 × 20 × 0.0004 = $64 |
| 펀딩 비용 (평균) | ~$30 |
| 슬리피지 (0.05%) | ~$8 |
| **거래 비용 합계** | **~$102** |

### 8.4 ROI 계산

```
초기 자본: $10,000
목표 수익률: 월 10%
월 수익: $1,000

운영비: $52
거래비: $102
순수익: $846

ROI: 846 / 10,000 = 8.46%/월 (연 171%)
```

### 8.5 Comparison: AI vs Manual

| 항목 | Manual | AI System | 차이 |
|-----|--------|-----------|-----|
| **모니터링** | 불가능 (수면) | 24/7 자동 | ∞ |
| **분석 빈도** | 일 2-3회 | 일 96회 체크 | 30배 ↑ |
| **감정 개입** | 높음 | 없음 | - |
| **백테스팅** | 수동 | 자동 | - |
| **개선 속도** | 느림 | 매일 학습 | - |
| **LLM 비용** | - | $15/월 | 추가 |
| **시간 절약** | - | 월 40시간 | $1,000+ |

**결론**: 비용 대비 가치 압도적

---

## 9. Success Metrics

### 8.1 Financial KPIs

| Metric | Month 1 | Month 3 | Month 6 |
|--------|---------|---------|---------|
| **Return** | 8-12% | 10-15% | 12-18% |
| **Sharpe** | > 1.5 | > 2.0 | > 2.5 |
| **MDD** | < -20% | < -15% | < -12% |
| **Win Rate** | > 55% | > 60% | > 65% |
| **청산 발생** | < 5% | < 3% | < 2% |

### 8.2 Operational KPIs

| Metric | Target |
|--------|--------|
| **Uptime** | 99.5% |
| **Data Quality** | 99.9% |
| **Alert Response** | < 30초 |
| **Order Execution** | < 10초 |

### 9.3 AI Performance KPIs

| Metric | Target |
|--------|--------|
| **Regime 정확도** | > 75% |
| **Direction 정확도** | > 65% |
| **Evidence 정확도** | > 70% |
| **Quick Filter 정확도** | > 80% |
| **LLM 토큰 비용** | < $20/월 |

### 9.4 Daily Backtesting

**목적**: 지속적 개선

**프로세스**:
```yaml
매일 00:00 (UTC):
  1. 24시간 전 결정들 조회
  2. 실제 결과 비교
  3. Evidence 검증
     - 기술적 지표 정확도
     - 뉴스 임팩트 정확도
     - 소셜 감성 정확도
  4. 정확도 계산
  5. 개선 제안 생성
  6. Slack 리포트 발송

주간 리뷰 (일요일):
  1. 주간 정확도 분석
  2. 프롬프트 개선 제안
  3. 파라미터 조정 제안
```

**Output Example**:
```markdown
# Daily Backtest Report (2025-10-27)

## Overall
- Decisions Made: 3
- Correct: 2 (66.7%)
- Incorrect: 1 (33.3%)

## Evidence Accuracy
- Technical Indicators: 100% (3/3)
- News Impact: 66.7% (2/3)
- Social Sentiment: 33.3% (1/3) ⚠️

## Improvement Suggestions
1. 소셜 감성 가중치 낮춤 (0.3 → 0.2)
2. 뉴스는 신뢰도 높은 소스만 (credibility > 0.8)
3. ADX < 30 구간에서는 진입 자제

## Best Decision
- Time: 14:30
- Action: LONG @ $68,000
- Result: +2.5% (24h)
- Why: 기술적 + 펀더멘털 모두 정확
```

---

## 9. Risk Assessment

### 9.1 Major Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **청산 발생** | Medium | Critical | 청산 거리 15% 강제, 실시간 모니터링 |
| **Regime 오판** | High | High | Confidence > 0.8만 실행, 3일 연속 확인 |
| **Flash Crash** | Low | Critical | Circuit Breaker, 비정상 변동 감지 |
| **API 다운** | Medium | High | Failover (Bybit 백업), 5분 내 전환 |
| **LLM 오판** | Medium | Medium | Risk Chief 검증, 백테스트 사전 확인 |

---

## 10. Development Process

### 10.1 Step-by-Step Approval Workflow

**핵심 원칙**: "한 번에 하나씩, 확인 후 진행"

```yaml
작업 단위:
  - 1개 기능 = 1개 작업
  - 예: "Docker Compose 설정" (OK)
  - 예: "전체 인프라 구축" (Too Big, 쪼개기)

진행 프로세스:
  1. AI가 작업 시작 선언
  2. 작업 수행
  3. 테스트 실행
  4. Owner에게 보고
  5. Owner 승인 대기
  6. 승인 시 체크리스트 체크 ✓
  7. 다음 작업 시작

보고 포맷:
  ✅ 완료: [작업명]
  📝 내용: [상세 설명]
  🧪 테스트: [테스트 결과]
  📂 파일: [변경된 파일 목록]
  ❓ 확인: 다음 단계 진행해도 될까요?
```

### 10.2 Quality Gates

각 Phase 완료 시 필수 체크:

```yaml
Phase 1-2 완료 시:
  ✓ 모든 컨테이너 정상 실행
  ✓ Database 연결 성공
  ✓ Health Check API 응답
  ✓ Owner 최종 승인

Phase 3-4 완료 시:
  ✓ Celery 모든 Task 실행
  ✓ Redis 캐시 동작
  ✓ 데이터 수집 확인
  ✓ Owner 최종 승인

Phase 5-6 완료 시:
  ✓ n8n Workflow 실행
  ✓ AI Agents 응답
  ✓ Evidence 저장 확인
  ✓ 테스트넷 거래 성공
  ✓ Owner 최종 승인

Phase 7-8 완료 시:
  ✓ Backtesting 자동화
  ✓ Daily Report 수신
  ✓ 정확도 > 목표치
  ✓ Owner 최종 승인
```

---

## 11. Roadmap

### Phase 1: MVP (Week 1-4)
- [ ] BTC 선물 거래 (Long/Short)
- [ ] 3개 Regime Detection
- [ ] 기본 Risk Management
- [ ] Minimal Rebalancing

### Phase 2: Optimization (Week 5-8)
- [ ] ETH 추가 (Core-Satellite)
- [ ] 백테스팅 시스템
- [ ] Paper Trading 검증
- [ ] Performance Analytics

### Phase 3: Scale (Week 9-12)
- [ ] 소액 Live Trading ($1,000)
- [ ] Multi-user Support
- [ ] Advanced Dashboard
- [ ] 자금 증액 ($10,000)

### Phase 4: Advanced (Month 4+)
- [ ] Funding Rate Arbitrage
- [ ] Multi-exchange (Bybit)
- [ ] Auto-tuning System
- [ ] Mobile App

---

## 11. Appendix

### 11.1 Glossary

- **Regime**: 시장 상태 (Bull/Bear/Consolidation)
- **Leverage**: 레버리지 (1x = 현물과 동일)
- **Liquidation**: 청산 (증거금 소진 시 강제 청산)
- **Funding Rate**: 선물 프리미엄 (8시간마다 지불/수취)
- **Core-Satellite**: 핵심 자산(BTC) + 보조 자산(ETH)

### 11.2 References

- Binance Futures API Documentation
- Modern Portfolio Theory (Markowitz)
- Momentum Investing (Jegadeesh & Titman)
- Risk Parity Approach (Bridgewater)

---

**Document Approval**: Pending Implementation

**Next Step**: TRD (Technical Requirements Document) 작성

