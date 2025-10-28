# Technical Requirements Document (TRD)
## AXIS Capital - AI Futures Trading System

**Version**: 2.0 (Final)
**Date**: 2025-10-27
**Related**: PRD-AXIS-Capital.md
**Status**: Ready for Implementation

---

## 1. System Architecture

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                 Load Balancer (Nginx)                   │
│                 SSL/TLS Termination                     │
└─────────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   FastAPI    │  │     n8n      │  │   Celery     │
│  (Backend)   │  │  (Workflows) │  │  (Workers)   │
│  Port: 8000  │  │  Port: 5678  │  │  Queue: Redis│
└──────────────┘  └──────────────┘  └──────────────┘
        │                 │                 │
        └─────────────────┴─────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ PostgreSQL   │  │    Redis     │  │ TimescaleDB  │
│ (Main DB)    │  │   (Cache)    │  │ (Timeseries) │
│ Port: 5432   │  │  Port: 6379  │  │ Port: 5433   │
└──────────────┘  └──────────────┘  └──────────────┘
```

### 1.2 Component Responsibilities

| Component | Purpose | Technology |
|-----------|---------|------------|
| **FastAPI** | REST API, 비즈니스 로직 | Python 3.11, FastAPI |
| **n8n** | AI Agent workflows | n8n (Docker) |
| **Celery** | 백그라운드 작업, 스케줄링 | Celery + Redis |
| **PostgreSQL** | 거래 기록, 설정 저장 | PostgreSQL 15 |
| **Redis** | 캐싱, Celery Broker | Redis 7 |
| **TimescaleDB** | OHLCV 시계열 데이터 | TimescaleDB (PostgreSQL extension) |
| **Grafana** | 대시보드, 모니터링 | Grafana + Prometheus |

---

## 2. Technology Stack

### 2.1 Backend (FastAPI)

```yaml
Language: Python 3.11+
Framework: FastAPI 0.104+

Core Libraries:
  - ccxt: 거래소 API 통합
  - pandas: 데이터 처리
  - numpy: 수치 계산
  - ta-lib: 기술 지표
  - pydantic: 데이터 검증
  - sqlalchemy: ORM
  - redis: 캐싱

Structure:
  api/
    ├── main.py              # FastAPI 앱
    ├── routers/
    │   ├── trading.py       # 거래 실행
    │   ├── portfolio.py     # 포트폴리오 조회
    │   └── data.py          # 데이터 API
    ├── services/
    │   ├── binance.py       # 바이낸스 API
    │   ├── risk.py          # 리스크 계산
    │   └── indicators.py    # 지표 계산
    ├── models/
    │   ├── position.py      # Position 모델
    │   └── trade.py         # Trade 모델
    └── core/
        ├── config.py        # 설정
        └── database.py      # DB 연결
```

### 2.2 Workflow Engine (n8n)

```yaml
Version: n8n 1.0+

Workflows:
  1. Main-Trading-Workflow.json
     - CEO → Analysts → Risk → Execution

  2. BTC-Analysis-Workflow.json
     - BTC 전문 분석

  3. ETH-Analysis-Workflow.json
     - ETH 전문 분석 (조건부)

AI Integration:
  - OpenAI API (GPT-4o, GPT-o1)
  - Custom HTTP Request nodes
  - Python Code nodes
```

### 2.3 Background Tasks (Celery)

```yaml
Version: Celery 5.3+
Broker: Redis
Result Backend: Redis

Task Categories:
  1. Data Collection (높은 빈도)
     - collect_btc_ohlcv (5분)
     - collect_funding_rates (5분)
     - collect_eth_ohlcv (5분)

  2. Monitoring (중간 빈도)
     - monitor_positions (1분)
     - check_liquidation_risk (1분)
     - update_portfolio_value (10분)

  3. Trading Cycle (낮은 빈도)
     - trigger_trading_cycle (CEO 결정)
     - check_regime_change (1시간)
```

---

## 3. Database Schema

### 3.1 PostgreSQL Schema

#### users
```sql
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    api_key_encrypted TEXT NOT NULL,
    api_secret_encrypted TEXT NOT NULL,
    risk_profile VARCHAR(20) DEFAULT 'balanced',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- risk_profile: conservative, balanced, aggressive
```

#### positions
```sql
CREATE TABLE positions (
    position_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id),
    exchange VARCHAR(20) DEFAULT 'binance',
    symbol VARCHAR(20) NOT NULL,
    side VARCHAR(10) NOT NULL,  -- LONG or SHORT
    leverage DECIMAL(5,2) NOT NULL,

    -- Entry
    entry_price DECIMAL(20,8) NOT NULL,
    entry_time TIMESTAMP NOT NULL,
    quantity DECIMAL(20,8) NOT NULL,
    notional_value DECIMAL(20,2) NOT NULL,
    margin DECIMAL(20,2) NOT NULL,

    -- Risk
    stop_loss_price DECIMAL(20,8),
    take_profit_price DECIMAL(20,8),
    liquidation_price DECIMAL(20,8) NOT NULL,

    -- Exit
    exit_price DECIMAL(20,8),
    exit_time TIMESTAMP,
    realized_pnl DECIMAL(20,2),
    pnl_pct DECIMAL(10,4),

    -- Meta
    regime VARCHAR(20),  -- bull_trend, bear_trend, consolidation
    confidence DECIMAL(5,4),
    ai_rationale TEXT,
    status VARCHAR(20) DEFAULT 'open',  -- open, closed, liquidated

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_positions_user_status ON positions(user_id, status);
CREATE INDEX idx_positions_symbol_status ON positions(symbol, status);
```

#### trades
```sql
CREATE TABLE trades (
    trade_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id),
    position_id INT REFERENCES positions(position_id),

    timestamp TIMESTAMP NOT NULL,
    exchange VARCHAR(20) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    side VARCHAR(10) NOT NULL,  -- BUY or SELL (execution side)
    order_type VARCHAR(20) NOT NULL,  -- MARKET, LIMIT

    price DECIMAL(20,8) NOT NULL,
    quantity DECIMAL(20,8) NOT NULL,
    total_usdt DECIMAL(20,2) NOT NULL,
    fee DECIMAL(20,8) NOT NULL,
    fee_currency VARCHAR(10) NOT NULL,

    exchange_order_id VARCHAR(100),
    status VARCHAR(20) DEFAULT 'executed',

    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_trades_user_time ON trades(user_id, timestamp DESC);
CREATE INDEX idx_trades_position ON trades(position_id);
```

#### ai_decisions
```sql
CREATE TABLE ai_decisions (
    decision_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id),

    timestamp TIMESTAMP NOT NULL,
    agent_name VARCHAR(50) NOT NULL,

    -- Input
    input_data JSONB NOT NULL,

    -- Output
    output_data JSONB NOT NULL,

    -- Evidence (신규!)
    evidence JSONB NOT NULL,  -- 근거 저장
    reasoning TEXT NOT NULL,   -- AI의 논리적 설명

    -- Validation (백테스팅용, 신규!)
    actual_outcome DECIMAL(10,4),  -- 실제 결과 (24h 후 업데이트)
    decision_quality VARCHAR(20),  -- correct, incorrect, neutral
    evidence_accuracy JSONB,       -- 각 evidence 정확도

    -- LLM Meta
    llm_model VARCHAR(50),
    prompt_tokens INT,
    completion_tokens INT,
    llm_cost DECIMAL(10,6),
    execution_time_ms INT,

    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_decisions_user_time ON ai_decisions(user_id, timestamp DESC);
CREATE INDEX idx_decisions_agent ON ai_decisions(agent_name, timestamp DESC);
CREATE INDEX idx_decisions_quality ON ai_decisions(decision_quality, timestamp DESC);
```

#### decision_analysis (신규)
```sql
CREATE TABLE decision_analysis (
    analysis_id SERIAL PRIMARY KEY,
    decision_id INT REFERENCES ai_decisions(decision_id),

    -- 분석 시점 (거래 후 24시간)
    analysis_timestamp TIMESTAMP NOT NULL,

    -- 결과
    predicted_direction VARCHAR(10),  -- LONG, SHORT, HOLD
    actual_direction VARCHAR(10),
    was_correct BOOLEAN,

    -- 성과
    predicted_return DECIMAL(10,4),
    actual_return DECIMAL(10,4),
    error_pct DECIMAL(10,4),

    -- 근거 검증
    evidence_breakdown JSONB,  -- 각 evidence가 맞았는지

    -- 개선 제안
    improvement_suggestions TEXT,

    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_analysis_decision ON decision_analysis(decision_id);
CREATE INDEX idx_analysis_time ON decision_analysis(analysis_timestamp DESC);
```

#### regime_history
```sql
CREATE TABLE regime_history (
    regime_id SERIAL PRIMARY KEY,

    timestamp TIMESTAMP NOT NULL,
    regime VARCHAR(20) NOT NULL,
    confidence DECIMAL(5,4) NOT NULL,

    -- Evidence
    adx DECIMAL(10,4),
    rsi DECIMAL(10,4),
    price_vs_ma50 DECIMAL(10,4),
    trend_strength VARCHAR(20),

    ai_rationale TEXT,

    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_regime_time ON regime_history(timestamp DESC);
```

---

### 3.2 TimescaleDB Schema

#### market_data
```sql
CREATE TABLE market_data (
    time TIMESTAMPTZ NOT NULL,
    exchange VARCHAR(20) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    timeframe VARCHAR(10) NOT NULL,  -- 1m, 5m, 15m, 1h, 4h, 1d

    open DECIMAL(20,8) NOT NULL,
    high DECIMAL(20,8) NOT NULL,
    low DECIMAL(20,8) NOT NULL,
    close DECIMAL(20,8) NOT NULL,
    volume DECIMAL(20,8) NOT NULL,

    PRIMARY KEY (time, exchange, symbol, timeframe)
);

SELECT create_hypertable('market_data', 'time');
CREATE INDEX idx_market_symbol_time ON market_data(symbol, timeframe, time DESC);
```

#### portfolio_snapshots
```sql
CREATE TABLE portfolio_snapshots (
    time TIMESTAMPTZ NOT NULL,
    user_id INT NOT NULL,

    total_value_usdt DECIMAL(20,2) NOT NULL,
    btc_value DECIMAL(20,2),
    eth_value DECIMAL(20,2),
    usdt_value DECIMAL(20,2),

    btc_allocation_pct DECIMAL(5,2),
    eth_allocation_pct DECIMAL(5,2),

    total_leverage DECIMAL(10,2),
    margin_ratio DECIMAL(10,4),
    unrealized_pnl DECIMAL(20,2),

    PRIMARY KEY (time, user_id)
);

SELECT create_hypertable('portfolio_snapshots', 'time');
```

#### funding_rate_history
```sql
CREATE TABLE funding_rate_history (
    time TIMESTAMPTZ NOT NULL,
    exchange VARCHAR(20) NOT NULL,
    symbol VARCHAR(20) NOT NULL,

    funding_rate DECIMAL(10,8) NOT NULL,
    mark_price DECIMAL(20,8) NOT NULL,
    index_price DECIMAL(20,8) NOT NULL,

    PRIMARY KEY (time, exchange, symbol)
);

SELECT create_hypertable('funding_rate_history', 'time');
```

---

### 3.3 Redis Cache Structure

#### Key Naming Convention
```
{category}:{exchange}:{symbol}:{data_type}
{category}:user:{user_id}:{data_type}
```

#### TTL Strategy
```
실시간 데이터: TTL = 수집 주기 × 1.2 (20% 여유)
요약 데이터: TTL = 수집 주기 × 1.5 (50% 여유)
포지션 데이터: TTL = 1분 (자주 변경)
```

#### Cache Keys

```yaml
# Layer 1: Market Data (High-Frequency, TTL: 6분)
market:binance:BTCUSDT:ohlcv_15m       → JSON (200 candles)
market:binance:BTCUSDT:indicators      → JSON (RSI, MACD, ADX, etc.)
market:binance:BTCUSDT:funding         → FLOAT
market:binance:BTCUSDT:price_change_15m → FLOAT

market:binance:ETHUSDT:ohlcv_15m       → JSON
market:binance:ETHUSDT:indicators      → JSON

# Layer 2: Contextual Data (Medium-Frequency, TTL: 45분)
news:summary                           → JSON {headline, sentiment, impact, evidence}
social:summary                         → JSON {score, trend, evidence, keywords}
onchain:summary                        → JSON {signal, strength, evidence}

# Layer 3: User Data (TTL: 1분)
user:1:positions                       → JSON Array
user:1:margin_ratio                    → FLOAT
user:1:total_value                     → FLOAT
user:1:has_open_position               → BOOLEAN

# System State (TTL: 1시간)
regime:current                         → JSON {regime, confidence, timestamp, evidence}
regime:history:24h                     → JSON Array

# Quick Filter (TTL: 15분)
quickfilter:last_analysis_time         → TIMESTAMP
quickfilter:last_trigger_reason        → STRING

# Locks (TTL: 10분)
trading:lock:user:1                    → STRING (execution_id)
```

---

## 4. API Specification

### 4.1 Trading APIs

#### Open Position
```http
POST /api/v2/positions/open
Content-Type: application/json

Request:
{
  "user_id": 1,
  "symbol": "BTCUSDT",
  "side": "LONG",
  "leverage": 15,
  "size_usdt": 8000,
  "stop_loss_pct": 0.03,
  "take_profit_pct": 0.10,
  "regime": "bull_trend",
  "confidence": 0.85,
  "ai_rationale": "Strong uptrend..."
}

Response (200):
{
  "success": true,
  "position_id": 1234,
  "entry_price": 68000.50,
  "quantity": 0.117647,
  "notional_value": 120000,
  "margin": 8000,
  "liquidation_price": 63235.44,
  "liquidation_distance_pct": 7.01,
  "exchange_order_id": "1234567890"
}

Response (400):
{
  "success": false,
  "error": "Liquidation distance < 15%",
  "details": {...}
}
```

#### Close Position
```http
POST /api/v2/positions/{position_id}/close
Content-Type: application/json

Request:
{
  "user_id": 1,
  "close_pct": 1.0,  // 1.0 = 전체, 0.5 = 50%
  "reason": "take_profit" | "stop_loss" | "manual" | "liquidation"
}

Response (200):
{
  "success": true,
  "position_id": 1234,
  "exit_price": 74800.00,
  "realized_pnl": 4000.00,
  "pnl_pct": 0.50,
  "holding_hours": 36
}
```

---

### 4.2 Data APIs

#### Get Cached Market Data
```http
GET /api/v2/data/market/{symbol}
Query Params:
  - timeframe: 15m (default), 1h, 4h
  - include_indicators: true (default)

Response (200):
{
  "symbol": "BTCUSDT",
  "timeframe": "15m",
  "cached_at": "2025-01-27T14:30:00Z",
  "ohlcv": [
    {
      "timestamp": "2025-01-27T14:15:00Z",
      "open": 68000,
      "high": 68200,
      "low": 67900,
      "close": 68100,
      "volume": 1250.5
    },
    ...
  ],
  "indicators": {
    "rsi": 65.3,
    "macd": {"macd": 120, "signal": 100, "histogram": 20},
    "adx": 42.1,
    "bollinger": {"upper": 69500, "middle": 68000, "lower": 66500}
  }
}
```

#### Get Current Regime
```http
GET /api/v2/regime/current

Response (200):
{
  "regime": "bull_trend",
  "confidence": 0.85,
  "timestamp": "2025-01-27T14:30:00Z",
  "duration_hours": 72,
  "evidence": {
    "adx": 42.1,
    "rsi": 65.3,
    "price_vs_ma50": "+8.5%"
  }
}
```

---

### 4.3 Portfolio APIs

#### Get Portfolio Summary
```http
GET /api/v2/users/{user_id}/portfolio

Response (200):
{
  "user_id": 1,
  "timestamp": "2025-01-27T14:30:00Z",
  "total_value_usdt": 10850.00,
  "unrealized_pnl": 850.00,
  "unrealized_pnl_pct": 8.5,

  "allocations": {
    "BTC": {
      "pct": 85.0,
      "value_usdt": 9222.50,
      "position_side": "LONG",
      "leverage": 15,
      "pnl": 750.00
    },
    "ETH": {
      "pct": 15.0,
      "value_usdt": 1627.50,
      "position_side": "HOLD",
      "leverage": 1,
      "pnl": 100.00
    }
  },

  "risk_metrics": {
    "total_leverage": 13.5,
    "margin_ratio": 0.68,
    "closest_liquidation_distance": 0.067
  }
}
```

---

## 5. Celery Task Specifications

### 5.1 Data Collection Tasks

#### Layer 1: High-Frequency (5분)

```python
@app.task(name='collect_market_data')
def collect_market_data():
    """
    시장 데이터 수집 (OHLCV, Funding, Indicators)

    Schedule: */5 * * * * (5분마다)
    Priority: High
    """
    exchange = ccxt.binance()

    for symbol in ['BTC/USDT', 'ETH/USDT']:
        # 1. OHLCV 수집
        ohlcv = exchange.fetch_ohlcv(symbol, '15m', limit=200)
        redis_client.setex(
            f'market:binance:{symbol.replace("/", "")}:ohlcv_15m',
            360,  # 6분 TTL (20% 여유)
            json.dumps(ohlcv)
        )

        # 2. 지표 계산
        indicators = calculate_indicators(ohlcv)
        redis_client.setex(
            f'market:binance:{symbol.replace("/", "")}:indicators',
            360,
            json.dumps(indicators)
        )

        # 3. Funding Rate
        funding = exchange.fetch_funding_rate(symbol)
        redis_client.setex(
            f'market:binance:{symbol.replace("/", "")}:funding',
            360,
            funding['fundingRate']
        )

        # 4. 가격 변동률 (Quick Filter용)
        price_change_15m = calculate_price_change(ohlcv, minutes=15)
        redis_client.setex(
            f'market:binance:{symbol.replace("/", "")}:price_change_15m',
            360,
            price_change_15m
        )

        # 5. TimescaleDB 저장 (백테스팅용)
        save_to_timescaledb(symbol, ohlcv)

    return {'status': 'success', 'timestamp': time.time()}
```

#### Layer 2: Medium-Frequency (30분)

```python
@app.task(name='collect_and_summarize_news')
def collect_and_summarize_news():
    """
    뉴스 수집 및 GPT-4o-mini 요약

    Schedule: 0,30 * * * * (30분마다)
    Priority: Medium
    """
    # 1. 뉴스 수집
    news_list = fetch_news_from_sources([
        'CryptoPanic',
        'CoinTelegraph',
        'CoinDesk'
    ])

    if not news_list:
        logger.warning("No news fetched")
        return {'status': 'no_news'}

    # 2. GPT-4o-mini 요약
    summary = gpt4o_mini_summarize(news_list)

    # Expected output:
    # {
    #   "headline": "BTC ETF 승인 임박",
    #   "sentiment": "bullish",
    #   "impact_score": 0.85,
    #   "key_facts": [...],
    #   "evidence": {
    #     "sources": [...],
    #     "reasoning": "..."
    #   }
    # }

    # 3. Redis 저장
    redis_client.setex(
        'news:summary',
        2700,  # 45분 TTL (50% 여유)
        json.dumps(summary)
    )

    return {'status': 'success', 'impact_score': summary['impact_score']}

@app.task(name='collect_and_analyze_social')
def collect_and_analyze_social():
    """
    소셜 미디어 수집 및 감성 분석

    Schedule: 15,45 * * * * (30분마다, 뉴스와 교대)
    Priority: Medium
    """
    # 1. 소셜 데이터 수집
    tweets = fetch_crypto_tweets(keywords=['BTC', 'Bitcoin'])
    reddit_posts = fetch_reddit_posts(subreddit='cryptocurrency')

    # 2. 감성 분석 + 요약
    social_summary = analyze_and_summarize_social(tweets, reddit_posts)

    # Expected output:
    # {
    #   "score": 0.75,
    #   "trend": "bullish",
    #   "score_change_1h": 0.15,
    #   "evidence": {
    #     "sentiment_breakdown": {...},
    #     "key_signals": [...],
    #     "reasoning": "..."
    #   }
    # }

    # 3. Redis 저장
    redis_client.setex(
        'social:summary',
        2700,  # 45분 TTL
        json.dumps(social_summary)
    )

    return {'status': 'success', 'score': social_summary['score']}

@app.task(name='collect_and_summarize_onchain')
def collect_and_summarize_onchain():
    """
    온체인 데이터 수집 및 요약

    Schedule: 10,40 * * * * (30분마다)
    Priority: Medium
    """
    # 1. 온체인 데이터 수집
    exchange_flow = get_exchange_netflow()
    whale_txs = get_whale_transactions()

    # 2. 요약 생성
    onchain_summary = summarize_onchain_data(exchange_flow, whale_txs)

    # Expected output:
    # {
    #   "signal": "accumulation",
    #   "strength": 0.78,
    #   "evidence": {
    #     "exchange_flow": {...},
    #     "whale_activity": [...],
    #     "reasoning": "..."
    #   }
    # }

    # 3. Redis 저장
    redis_client.setex(
        'onchain:summary',
        2700,  # 45분 TTL
        json.dumps(onchain_summary)
    )

    return {'status': 'success', 'signal': onchain_summary['signal']}
```

### 5.2 Quick Filter & Trigger Tasks

#### quick_filter_and_trigger
```python
@app.task(name='quick_filter_and_trigger')
def quick_filter_and_trigger():
    """
    Quick Filter: AI 분석이 필요한지 판단

    Schedule: 0,15,30,45 * * * * (15분마다)
    Priority: High
    """
    # 1. 포지션 체크
    if has_open_position():
        logger.info("포지션 보유 중, AI 분석 스킵")
        return {'status': 'skipped', 'reason': 'has_position'}

    # 2. Regime 신뢰도 체크
    regime = redis_client.get('regime:current')
    if regime and regime['confidence'] < 0.8:
        logger.info("Regime 불확실, AI 분석 트리거")
        trigger_n8n_workflow(reason='regime_uncertain')
        return {'status': 'triggered', 'reason': 'regime_uncertain'}

    # 3. 가격 급변 체크
    price_change = redis_client.get('market:binance:BTCUSDT:price_change_15m')
    if abs(price_change) > 1.5:
        logger.info(f"가격 급변 {price_change:.2f}%, AI 분석 트리거")
        trigger_n8n_workflow(reason='price_spike')
        return {'status': 'triggered', 'reason': 'price_spike'}

    # 4. 중요 뉴스 체크
    news = redis_client.get('news:summary')
    if news and news.get('impact_score', 0) > 0.8:
        logger.info("중요 뉴스 감지, AI 분석 트리거")
        trigger_n8n_workflow(reason='major_news')
        return {'status': 'triggered', 'reason': 'major_news'}

    # 5. 소셜 감성 급변 체크
    social = redis_client.get('social:summary')
    if social and abs(social.get('score_change_1h', 0)) > 0.3:
        logger.info("소셜 감성 급변, AI 분석 트리거")
        trigger_n8n_workflow(reason='social_shift')
        return {'status': 'triggered', 'reason': 'social_shift'}

    # 6. 정기 체크 (4시간 경과)
    last_analysis = redis_client.get('quickfilter:last_analysis_time')
    if time.time() - last_analysis > 4 * 3600:
        logger.info("4시간 경과, 정기 AI 분석 트리거")
        trigger_n8n_workflow(reason='scheduled_check')
        return {'status': 'triggered', 'reason': 'scheduled_check'}

    # 조건 미충족
    logger.info("Quick Filter 조건 미충족, 스킵")
    return {'status': 'skipped', 'reason': 'no_trigger_condition'}

def trigger_n8n_workflow(reason: str):
    """n8n Webhook 호출"""
    redis_client.set('quickfilter:last_analysis_time', time.time())
    redis_client.setex('quickfilter:last_trigger_reason', 900, reason)

    response = requests.post(
        'http://n8n:5678/webhook/trading',
        json={
            'user_id': 1,
            'trigger_reason': reason,
            'timestamp': datetime.now().isoformat()
        },
        timeout=600  # 10분
    )

    return response.json()
```

#### monitor_positions
```python
@app.task(name='monitor_positions')
def monitor_positions():
    """
    포지션 실시간 모니터링 (Stop Loss/Take Profit/청산 리스크)

    Schedule: * * * * * (1분마다)
    Priority: Critical
    """
    all_users = get_active_users()

    for user in all_users:
        positions = get_open_positions(user.user_id)

        # Redis 업데이트
        redis_client.setex(
            f'user:{user.user_id}:has_open_position',
            60,
            len(positions) > 0
        )

        for pos in positions:
            current_price = get_current_price(pos.symbol)

            # 1. Stop Loss 체크
            if should_stop_loss(pos, current_price):
                close_position(pos.position_id, reason='stop_loss')
                send_alert(f"🔴 Stop Loss: {pos.symbol} @ ${current_price}")

            # 2. Take Profit 체크
            elif should_take_profit(pos, current_price):
                close_position(pos.position_id, close_pct=0.5, reason='take_profit')
                send_alert(f"🟢 Take Profit: {pos.symbol} @ ${current_price}")

            # 3. 청산 리스크 체크
            liq_distance = calculate_liquidation_distance(pos, current_price)
            if liq_distance < 0.10:
                send_critical_alert(
                    f"⚠️ 청산 위험: {pos.symbol}\n"
                    f"거리: {liq_distance:.2%}\n"
                    f"청산가: ${pos.liquidation_price}"
                )

                if liq_distance < 0.05:
                    # 긴급 50% 청산
                    close_position(pos.position_id, close_pct=0.5, reason='emergency')
                    send_critical_alert(f"🚨 긴급 청산 실행: {pos.symbol}")
```

### 5.3 Backtesting & Analysis Tasks

#### analyze_past_decisions
```python
@app.task(name='analyze_past_decisions')
def analyze_past_decisions():
    """
    24시간 전 AI 결정들을 분석하고 정확도 평가

    Schedule: 0 0 * * * (매일 00:00 UTC)
    Priority: Medium
    """
    # 1. 24시간 전 결정 조회
    yesterday = datetime.now() - timedelta(days=1)
    decisions = db.query(AIDecision).filter(
        AIDecision.timestamp >= yesterday,
        AIDecision.timestamp < yesterday + timedelta(hours=1)
    ).all()

    results = []

    for decision in decisions:
        # 2. 실제 가격 변화 조회
        actual_price_change = get_price_change_24h(
            decision.timestamp,
            decision.output_data['symbol']
        )

        # 3. 정확도 판단
        predicted = decision.output_data.get('direction')
        was_correct = (
            (predicted == 'LONG' and actual_price_change > 0) or
            (predicted == 'SHORT' and actual_price_change < 0) or
            (predicted == 'HOLD' and abs(actual_price_change) < 0.01)
        )

        # 4. Evidence 검증
        evidence_accuracy = verify_evidence(
            decision.evidence,
            actual_price_change
        )

        # 5. DB 업데이트
        decision.actual_outcome = actual_price_change
        decision.decision_quality = 'correct' if was_correct else 'incorrect'
        decision.evidence_accuracy = evidence_accuracy

        # 6. DecisionAnalysis 레코드 생성
        analysis = DecisionAnalysis(
            decision_id=decision.decision_id,
            analysis_timestamp=datetime.now(),
            predicted_direction=predicted,
            actual_direction='UP' if actual_price_change > 0 else 'DOWN',
            was_correct=was_correct,
            actual_return=actual_price_change,
            evidence_breakdown=evidence_accuracy,
            improvement_suggestions=generate_improvements(decision, was_correct)
        )
        db.add(analysis)

        results.append({
            'decision_id': decision.decision_id,
            'was_correct': was_correct,
            'evidence_accuracy': evidence_accuracy
        })

    db.commit()

    # 7. 일일 리포트 생성 및 Slack 발송
    report = generate_daily_backtest_report(results)
    send_slack_report(report)

    return {'status': 'success', 'analyzed': len(results)}

def verify_evidence(evidence: dict, actual_outcome: float) -> dict:
    """각 evidence 요소가 실제로 유효했는지 검증"""
    accuracy = {}

    # 기술적 지표
    tech = evidence.get('technical', {})
    if tech.get('adx', 0) > 40:
        # ADX > 40이면 강한 추세 → 실제로 큰 움직임 있었나?
        accuracy['adx'] = abs(actual_outcome) > 0.02

    if tech.get('rsi', 50) > 70:
        # RSI 과매수 → 실제로 하락했나?
        accuracy['rsi'] = actual_outcome < 0

    # 펀더멘털
    fund = evidence.get('fundamental', {})
    if fund.get('news_impact', 0) > 0.8:
        # 높은 뉴스 임팩트 → 실제로 큰 움직임?
        accuracy['news'] = abs(actual_outcome) > 0.03

    if fund.get('social_sentiment', 0.5) > 0.7:
        # 긍정 소셜 → 실제로 상승?
        accuracy['social'] = actual_outcome > 0

    return accuracy

def generate_improvements(decision: AIDecision, was_correct: bool) -> str:
    """개선 제안 생성"""
    if was_correct:
        return "Decision was correct. No improvement needed."

    suggestions = []

    # Evidence 분석
    evidence = decision.evidence

    if evidence.get('fundamental', {}).get('social_sentiment', 0) > 0.7:
        if decision.actual_outcome < 0:
            suggestions.append("소셜 감성 가중치 낮춤 (0.3 → 0.2)")

    if evidence.get('technical', {}).get('adx', 0) < 30:
        suggestions.append("ADX < 30 구간에서는 진입 자제")

    return "; ".join(suggestions) if suggestions else "Further analysis needed"
```

#### Celery Beat Schedule
```python
# workers/celery_app.py

from celery.schedules import crontab

app.conf.beat_schedule = {
    # Layer 1: High-Frequency (5분)
    'collect-market-data': {
        'task': 'collect_market_data',
        'schedule': crontab(minute='*/5'),
    },

    # Layer 2: Medium-Frequency (30분)
    'summarize-news': {
        'task': 'collect_and_summarize_news',
        'schedule': crontab(minute='0,30'),
    },
    'analyze-social': {
        'task': 'collect_and_analyze_social',
        'schedule': crontab(minute='15,45'),
    },
    'summarize-onchain': {
        'task': 'collect_and_summarize_onchain',
        'schedule': crontab(minute='10,40'),
    },

    # Quick Filter & Trigger (15분)
    'quick-filter': {
        'task': 'quick_filter_and_trigger',
        'schedule': crontab(minute='0,15,30,45'),
    },

    # Position Monitoring (1분)
    'monitor-positions': {
        'task': 'monitor_positions',
        'schedule': crontab(minute='*'),
    },

    # Portfolio Update (10분)
    'update-portfolio': {
        'task': 'update_portfolio_value',
        'schedule': crontab(minute='*/10'),
    },

    # Backtesting (매일 00:00)
    'analyze-decisions': {
        'task': 'analyze_past_decisions',
        'schedule': crontab(hour=0, minute=0),
    },
}
```

---

## 6. n8n Workflow Specifications

### 6.1 Main Trading Workflow

#### Workflow Settings
```yaml
Name: Main-Trading-Workflow
Timeout: 600초 (10분)
Error Handling: Continue on Fail (로깅)
Retry: 없음 (LLM은 재시도 불필요)
```

#### Workflow Structure
```json
{
  "name": "Main-Trading-Workflow",
  "settings": {
    "executionTimeout": 600,
    "saveExecutionProgress": true
  },
  "nodes": [
    {
      "name": "Webhook Trigger",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "path": "trading",
        "httpMethod": "POST"
      }
    },
    {
      "name": "Get Cached Data",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "http://fastapi:8000/api/v2/data/market/BTCUSDT?include_summary=true",
        "timeout": 5000
      },
      "notes": "Redis에서 캐시된 데이터 로드 (시장/뉴스/소셜/온체인)"
    },
    {
      "name": "CEO Agent",
      "type": "@n8n/n8n-nodes-langchain.agent",
      "parameters": {
        "model": "gpt-o1",
        "prompt": "Regime Detection Prompt...",
        "maxTokens": 1000
      },
      "notes": "Regime 판단 + Evidence 수집"
    },
    {
      "name": "Save Regime",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "POST",
        "url": "http://fastapi:8000/api/v2/regime/update"
      }
    },
    {
      "name": "BTC Analyst",
      "type": "@n8n/n8n-nodes-langchain.agent",
      "parameters": {
        "model": "gpt-4o",
        "prompt": "BTC Analysis Prompt...",
        "maxTokens": 800
      },
      "notes": "거래 방향 결정 + Evidence"
    },
    {
      "name": "Risk Chief",
      "type": "@n8n/n8n-nodes-langchain.agent",
      "parameters": {
        "model": "gpt-4o",
        "prompt": "Risk Validation Prompt...",
        "maxTokens": 600
      },
      "notes": "리스크 검증 + Approve/Veto"
    },
    {
      "name": "Save AI Decision",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "POST",
        "url": "http://fastapi:8000/api/v2/decisions/save"
      },
      "notes": "evidence, reasoning 포함하여 저장"
    },
    {
      "name": "If Approved",
      "type": "n8n-nodes-base.if",
      "parameters": {
        "conditions": {
          "approved": "{{ $json.risk_chief.approval === 'APPROVED' }}"
        }
      }
    },
    {
      "name": "Execute Trade",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "POST",
        "url": "http://fastapi:8000/api/v2/positions/open",
        "timeout": 10000
      }
    },
    {
      "name": "Send Slack Alert",
      "type": "n8n-nodes-base.slack",
      "parameters": {
        "channel": "#trading-alerts",
        "text": "{{ $json.trade_result }}"
      }
    }
  ]
}
```

#### Timeout Handling
```javascript
// Error Handler Node (Workflow 실패 시)
if (error.type === 'TIMEOUT') {
  send_critical_alert({
    title: "⚠️ n8n Workflow Timeout",
    message: "10분 초과. AI 응답 지연 의심.",
    action: "수동 확인 필요"
  });

  // Slack에 알림 후 종료
  return { status: 'timeout', timestamp: Date.now() };
}
```

---

## 7. Infrastructure Requirements

### 7.1 Hardware Requirements (Minimum)

| Component | Spec |
|-----------|------|
| **CPU** | 4 cores |
| **RAM** | 8GB |
| **Disk** | 100GB SSD |
| **Network** | 100Mbps |

### 7.2 Docker Compose

```yaml
version: '3.8'

services:
  postgres:
    image: timescale/timescaledb:latest-pg15
    environment:
      POSTGRES_DB: axis_capital
      POSTGRES_USER: axis
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  fastapi:
    build: ./api
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://axis:${POSTGRES_PASSWORD}@postgres:5432/axis_capital
      REDIS_URL: redis://redis:6379/0
      BINANCE_API_KEY: ${BINANCE_API_KEY}
      BINANCE_API_SECRET: ${BINANCE_API_SECRET}
      OPENAI_API_KEY: ${OPENAI_API_KEY}
    depends_on:
      - postgres
      - redis

  celery-worker:
    build: ./api
    command: celery -A workers.celery_app worker -l info
    environment:
      DATABASE_URL: postgresql://axis:${POSTGRES_PASSWORD}@postgres:5432/axis_capital
      REDIS_URL: redis://redis:6379/0
    depends_on:
      - redis
      - postgres

  celery-beat:
    build: ./api
    command: celery -A workers.celery_app beat -l info
    environment:
      REDIS_URL: redis://redis:6379/0
    depends_on:
      - redis

  n8n:
    image: n8nio/n8n:latest
    ports:
      - "5678:5678"
    environment:
      N8N_BASIC_AUTH_USER: admin
      N8N_BASIC_AUTH_PASSWORD: ${N8N_PASSWORD}
    volumes:
      - n8n_data:/home/node/.n8n
    depends_on:
      - fastapi

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana

volumes:
  postgres_data:
  redis_data:
  n8n_data:
  grafana_data:
```

---

## 8. Security Requirements

### 8.1 API Key Management

```python
# api/core/security.py
from cryptography.fernet import Fernet

class APIKeyManager:
    def __init__(self):
        self.cipher = Fernet(os.getenv('ENCRYPTION_KEY'))

    def encrypt(self, api_key: str) -> str:
        return self.cipher.encrypt(api_key.encode()).decode()

    def decrypt(self, encrypted: str) -> str:
        return self.cipher.decrypt(encrypted.encode()).decode()

# Usage
api_key = "user_binance_api_key"
encrypted = api_key_manager.encrypt(api_key)
# DB에 저장: encrypted

# 사용 시
decrypted = api_key_manager.decrypt(encrypted)
binance = ccxt.binance({'apiKey': decrypted, ...})
```

### 8.2 Rate Limiting

```python
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

@app.post("/api/v2/positions/open")
@limiter(times=10, seconds=60)  # 10 requests per minute
async def open_position(...):
    pass
```

### 8.3 Authentication

```python
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials):
    token = credentials.credentials
    # JWT 검증
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    return payload['user_id']

@app.get("/api/v2/users/{user_id}/portfolio")
async def get_portfolio(
    user_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    verified_user_id = verify_token(credentials)
    if verified_user_id != user_id:
        raise HTTPException(403, "Forbidden")
    ...
```

---

## 9. Monitoring & Observability

### 9.1 Prometheus Metrics

```python
from prometheus_client import Counter, Histogram, Gauge

# Metrics
trades_total = Counter('trades_total', 'Total trades executed', ['side', 'symbol'])
trade_pnl = Histogram('trade_pnl', 'Trade P&L distribution')
open_positions = Gauge('open_positions', 'Number of open positions', ['user_id'])
liquidation_distance = Gauge('liquidation_distance', 'Closest liquidation distance', ['user_id'])

# Usage
trades_total.labels(side='LONG', symbol='BTCUSDT').inc()
trade_pnl.observe(pnl_value)
```

### 9.2 Logging

```python
import structlog

logger = structlog.get_logger()

logger.info(
    "position_opened",
    user_id=1,
    symbol="BTCUSDT",
    side="LONG",
    leverage=15,
    entry_price=68000
)

logger.error(
    "position_liquidated",
    user_id=1,
    position_id=1234,
    symbol="BTCUSDT",
    loss=-8000
)
```

---

## 10. Cost Analysis & Optimization

### 10.1 LLM Cost Breakdown

#### GPT-4o-mini (Summarization)
```
Purpose: 뉴스/소셜/온체인 요약
Frequency: 48회/일 (30분마다)
Input: 500 tokens avg
Output: 100 tokens avg
Cost: $0.15/1M input, $0.60/1M output

Daily: 48 × (500×0.15 + 100×0.60) / 1,000,000
     = $0.048/일
Monthly: $1.44
```

#### GPT-o1 (CEO Agent)
```
Purpose: Regime Detection
Frequency: 15회/일 (Quick Filter 통과 시)
Input: 800 tokens avg
Output: 200 tokens avg
Cost: $15/1M input, $60/1M output

Daily: 15 × (800×15 + 200×60) / 1,000,000
     = $0.36/일
Monthly: $10.80
```

#### GPT-4o (Analysts & Risk)
```
Purpose: BTC Analyst + Risk Chief
Frequency: 30회/일 (각 15회)
Input: 600 tokens avg
Output: 150 tokens avg
Cost: $2.5/1M input, $10/1M output

Daily: 30 × (600×2.5 + 150×10) / 1,000,000
     = $0.09/일
Monthly: $2.70
```

### 10.2 Infrastructure Cost

| 항목 | 스펙 | 월 비용 |
|-----|-----|--------|
| VPS (DigitalOcean) | 8GB RAM, 4 vCPU | $30 |
| Redis Cloud | 256MB | $7 |
| PostgreSQL (VPS 포함) | - | $0 |
| Bandwidth | ~100GB | $0 (포함) |
| **합계** | | **$37** |

### 10.3 Total Monthly Cost

| Category | 항목 | 월 비용 |
|----------|-----|--------|
| **LLM** | GPT-4o-mini | $1.44 |
| | GPT-o1 | $10.80 |
| | GPT-4o | $2.70 |
| **인프라** | VPS | $30.00 |
| | Redis | $7.00 |
| **총 운영비** | | **$51.94** |

### 10.4 Trading Cost (별도)

```
자본: $10,000
거래: 월 20회 (Quick Filter 통과 + AI 승인)
포지션 크기: $8,000 avg
레버리지: 평균 12x

Binance 수수료: 0.04% (Maker)
  $8,000 × 20회 × 0.0004 = $64

펀딩 비용: 8시간마다 ±0.01%
  평균 보유 24시간 × 3회 × 0.01% × $96,000 = ~$30

슬리피지: 0.05% (시장가)
  $8,000 × 20회 × 0.0005 = $8

총 거래 비용: ~$102/월
```

### 10.5 ROI Analysis

```yaml
초기 자본: $10,000
목표 수익률: 월 10% ($1,000)

비용:
  - 운영비: $52
  - 거래비: $102
  - 합계: $154

순수익: $1,000 - $154 = $846

실제 ROI: 8.46%/월 (연 170%)
```

### 10.6 Cost Optimization

#### Quick Filter 효과
```
Without Quick Filter:
  - n8n 실행: 96회/일
  - LLM 비용: ~$600/월

With Quick Filter:
  - n8n 실행: 15회/일
  - LLM 비용: ~$15/월

절감: $585/월 (97%)
```

#### Caching 효과
```
Without Cache:
  - n8n이 직접 API 호출
  - 지연: ~5-10초
  - API Rate Limit 위험

With Cache:
  - Redis에서 즉시 로드
  - 지연: ~100ms
  - API 호출 0회 (n8n에서)

절감: 시간 98%, 안정성 향상
```

---

## 11. Performance Requirements

| Metric | Target | Critical |
|--------|--------|----------|
| **API P95 Latency** | < 500ms | < 2s |
| **Order Execution** | < 10s | < 30s |
| **Data Freshness** | < 5s | < 30s |
| **LLM Response** | < 20s | < 60s |
| **Cache Hit Rate** | > 90% | > 80% |
| **DB Query Time** | < 100ms | < 500ms |
| **n8n Workflow** | < 2분 | < 10분 (timeout) |

---

## 12. Failure Handling

### 12.1 Data Collection Failures

#### News API Down
```python
@app.task(name='collect_and_summarize_news')
def collect_and_summarize_news():
    try:
        news_list = fetch_news_from_sources()
    except Exception as e:
        logger.error(f"News fetch failed: {e}")

        # Fallback: 이전 요약 사용
        previous = redis_client.get('news:summary')
        if previous:
            logger.warning("Using previous news summary")
            return {'status': 'fallback', 'source': 'previous'}

        # 이전 것도 없으면: Neutral 상태
        redis_client.setex(
            'news:summary',
            2700,
            json.dumps({
                'headline': 'Data unavailable',
                'sentiment': 'neutral',
                'impact_score': 0.5,
                'evidence': {'reasoning': 'News API failed'}
            })
        )

        send_alert("⚠️ News API 실패, Fallback 사용")
        return {'status': 'failed_fallback'}
```

#### Summarization LLM Failed
```python
def gpt4o_mini_summarize(news_list):
    try:
        summary = openai_client.summarize(news_list)
        return summary
    except Exception as e:
        logger.error(f"GPT-4o-mini failed: {e}")

        # Fallback: 간단한 규칙 기반 요약
        summary = rule_based_summarize(news_list)
        summary['evidence']['reasoning'] += " (Fallback: Rule-based)"

        send_alert("⚠️ LLM 요약 실패, 규칙 기반 사용")
        return summary
```

### 12.2 n8n Workflow Failures

#### Timeout
```python
# Celery trigger
try:
    response = requests.post(
        'http://n8n:5678/webhook/trading',
        json={...},
        timeout=600  # 10분
    )
except requests.Timeout:
    logger.critical("n8n workflow timeout")
    send_critical_alert("🚨 n8n Timeout (10분 초과)")

    # Redis에 실패 기록
    redis_client.setex(
        'quickfilter:last_failure',
        3600,
        json.dumps({'reason': 'timeout', 'time': time.time()})
    )

    return {'status': 'timeout'}
```

#### LLM Error in Workflow
```javascript
// n8n Error Handler
if (error.type === 'AI_ERROR') {
  // CEO가 실패하면 전체 중단
  if (node === 'CEO Agent') {
    send_alert("⚠️ CEO Agent 실패, 거래 스킵");
    return { status: 'aborted', reason: 'ceo_failed' };
  }

  // Analyst 실패 → HOLD
  if (node === 'BTC Analyst') {
    return {
      decision: 'HOLD',
      reason: 'analyst_failed',
      evidence: { error: error.message }
    };
  }
}
```

### 12.3 Redis Failure

```python
def get_cached_data_safe(key: str):
    """Redis 실패 시 DB Fallback"""
    try:
        data = redis_client.get(key)
        if data:
            return data
    except Exception as e:
        logger.error(f"Redis failed: {e}")
        send_critical_alert("🚨 Redis 연결 실패")

    # Fallback to PostgreSQL
    logger.warning("Falling back to PostgreSQL")
    return get_from_postgresql(key)
```

---

## 13. Disaster Recovery

### 11.1 Backup Strategy

```yaml
PostgreSQL:
  - Full Backup: 매일 03:00 (S3)
  - Incremental: 매시간 (로컬)
  - Retention: 30일

Redis:
  - RDB Snapshot: 매시간
  - AOF: 실시간 (appendfsync everysec)
  - Retention: 7일

Code:
  - Git: 모든 변경사항
  - Docker Images: Tagged versions
```

### 11.2 Failover Plan

```yaml
Binance API Down:
  1. 자동 감지 (5분 내)
  2. Bybit API로 전환
  3. 포지션 미러링
  4. 알림 발송

Database Failure:
  1. Read Replica로 전환 (읽기 전용)
  2. 백업에서 복구 (최대 1시간 데이터 손실)

Redis Failure:
  1. PostgreSQL로 Fallback (느리지만 작동)
  2. Redis 재시작
  3. 캐시 Warm-up
```

---

## 12. Testing Strategy

### 12.1 Unit Tests

```python
# tests/test_risk.py
def test_liquidation_distance_calculation():
    position = Position(
        side='LONG',
        entry_price=68000,
        leverage=15,
        mark_price=70000
    )

    distance = calculate_liquidation_distance(position)

    assert distance > 0.10  # > 10%
    assert distance < 0.15  # < 15%
```

### 12.2 Integration Tests

```python
# tests/test_trading_flow.py
async def test_full_trading_cycle():
    # 1. Trigger workflow
    response = await client.post("/api/v2/trading/trigger", json={'user_id': 1})
    assert response.status_code == 200

    # 2. Wait for execution
    await asyncio.sleep(60)

    # 3. Check position opened
    positions = await get_open_positions(user_id=1)
    assert len(positions) > 0

    # 4. Verify risk limits
    for pos in positions:
        assert pos.liquidation_distance > 0.15
```

### 12.3 Load Tests

```bash
# locust 사용
locust -f tests/load_test.py --users 100 --spawn-rate 10
```

---

## 13. Deployment

### 13.1 CI/CD Pipeline

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Tests
        run: |
          pip install -r requirements.txt
          pytest tests/

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Server
        run: |
          ssh user@server 'cd /app && git pull && docker-compose up -d --build'
```

---

## 14. Implementation Workflow

### 14.1 Step-by-Step Approval Process

#### Workflow Rules

```python
class ImplementationWorkflow:
    """구현 워크플로우 관리"""

    def __init__(self):
        self.current_task = None
        self.approval_required = True

    def start_task(self, task_name: str):
        """작업 시작"""
        if self.current_task:
            raise Exception("이전 작업 완료 후 시작 가능")

        self.current_task = task_name
        print(f"🚀 작업 시작: {task_name}")

    def complete_task(self, details: dict):
        """작업 완료 보고"""
        report = f"""
        ✅ 완료: {self.current_task}
        📝 내용: {details['description']}
        🧪 테스트: {details['test_result']}
        📂 파일: {details['files_changed']}
        ❓ 확인: 다음 단계 진행해도 될까요?
        """
        print(report)

        # Owner 승인 대기
        self.wait_for_approval()

    def wait_for_approval(self):
        """승인 대기"""
        print("⏳ Owner 승인 대기 중...")
        # Owner가 승인하면 체크리스트 체크

    def approve(self):
        """승인 (Owner만 가능)"""
        print(f"✓ 체크리스트 체크: {self.current_task}")
        self.current_task = None

    def reject(self, reason: str):
        """거부"""
        print(f"❌ 재작업 필요: {reason}")
        # 현재 작업 재시도
```

#### Task Granularity (작업 단위)

```yaml
Good (적절한 크기):
  - "Docker Compose 파일 작성"
  - "PostgreSQL 테이블 1개 생성"
  - "Celery Task 1개 구현"
  - "n8n 노드 3개 추가"

Bad (너무 큼):
  - "전체 인프라 구축" → 10개 작업으로 쪼개기
  - "데이터 파이프라인 완성" → 각 Task별로 쪼개기
  - "n8n Workflow 전체" → 노드별로 쪼개기

Bad (너무 작음):
  - "변수 1개 추가" → 의미 있는 단위로 묶기
  - "주석 작성" → 코드 작성과 함께
```

#### Example: Phase 1 Execution

```bash
# Task 1
AI: "작업 시작: Docker Compose 설정"
AI: [docker-compose.yml 작성]
AI: [테스트 실행: docker-compose up -d]
AI:
  ✅ 완료: Docker Compose 설정
  📝 내용: PostgreSQL, Redis, n8n 컨테이너 설정 완료
  🧪 테스트: 모든 컨테이너 RUNNING 상태 확인
  📂 파일: docker-compose.yml
  ❓ 확인: 다음 단계 진행해도 될까요?

Owner: "확인했어, 진행해"

AI: [체크리스트 체크 ✓]

# Task 2
AI: "작업 시작: PostgreSQL 연결 테스트"
...
```

#### Error Handling

```yaml
문제 발생 시:
  1. 즉시 Owner에게 보고
     "⚠️ 에러 발생: [에러 내용]"

  2. 에러 상세 정보
     - 에러 메시지
     - 스택 트레이스
     - 재현 방법

  3. 해결 방안 제안
     - Option A: [방안 1]
     - Option B: [방안 2]

  4. Owner 지시 대기
     - 재시도
     - 다른 방법
     - 스킵 (나중에)

예시:
  ⚠️ 에러: PostgreSQL 연결 실패
  원인: Password 불일치
  해결안:
    A) .env 파일 수정
    B) docker-compose 재시작
  어떻게 할까요?
```

---

## 15. Appendix

### 15.1 Environment Variables

```bash
# .env.example
DATABASE_URL=postgresql://axis:password@localhost:5432/axis_capital
REDIS_URL=redis://localhost:6379/0

BINANCE_API_KEY=your_binance_api_key
BINANCE_API_SECRET=your_binance_api_secret

OPENAI_API_KEY=your_openai_api_key

ENCRYPTION_KEY=your_encryption_key_for_api_keys

JWT_SECRET_KEY=your_jwt_secret

SLACK_WEBHOOK_URL=your_slack_webhook
```

---

**Document Status**: Ready for Implementation
**Next Step**: Implementation Checklist 작성

