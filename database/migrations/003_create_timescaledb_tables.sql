-- =============================================
-- 003_create_timescaledb_tables.sql
-- TimescaleDB 시계열 데이터 테이블 생성
-- =============================================
-- 생성일: 2025-10-28
-- 설명: 시장 데이터, 포트폴리오 스냅샷, 펀딩 레이트 이력
-- =============================================

-- TimescaleDB extension 활성화 확인
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- =============================================
-- 1. market_data (시장 데이터 - OHLCV)
-- =============================================
-- 거래소별 심볼별 시간프레임별 캔들 데이터
CREATE TABLE market_data (
    time TIMESTAMPTZ NOT NULL,
    exchange VARCHAR(20) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    timeframe VARCHAR(10) NOT NULL,  -- 1m, 5m, 15m, 1h, 4h, 1d

    -- OHLCV
    open DECIMAL(20,8) NOT NULL,
    high DECIMAL(20,8) NOT NULL,
    low DECIMAL(20,8) NOT NULL,
    close DECIMAL(20,8) NOT NULL,
    volume DECIMAL(20,8) NOT NULL,

    PRIMARY KEY (time, exchange, symbol, timeframe)
);

-- Hypertable 변환 (시계열 최적화)
SELECT create_hypertable('market_data', 'time');

-- 인덱스 생성 (심볼 + 타임프레임 기반 조회 최적화)
CREATE INDEX idx_market_symbol_time ON market_data(symbol, timeframe, time DESC);
CREATE INDEX idx_market_exchange ON market_data(exchange, symbol);

-- 코멘트
COMMENT ON TABLE market_data IS '시장 데이터 (OHLCV 캔들) - TimescaleDB Hypertable';
COMMENT ON COLUMN market_data.timeframe IS '시간프레임: 1m, 5m, 15m, 1h, 4h, 1d';
COMMENT ON COLUMN market_data.time IS 'UTC 타임존 기준 캔들 시작 시간';

-- =============================================
-- 2. portfolio_snapshots (포트폴리오 스냅샷)
-- =============================================
-- 사용자별 포트폴리오 가치 및 구성 스냅샷 (10분마다 저장)
CREATE TABLE portfolio_snapshots (
    time TIMESTAMPTZ NOT NULL,
    user_id INT NOT NULL,

    -- 총 가치
    total_value_usdt DECIMAL(20,2) NOT NULL,

    -- 자산별 가치
    btc_value DECIMAL(20,2),
    eth_value DECIMAL(20,2),
    usdt_value DECIMAL(20,2),

    -- 자산 배분 비율
    btc_allocation_pct DECIMAL(5,2),
    eth_allocation_pct DECIMAL(5,2),

    -- 리스크 메트릭
    total_leverage DECIMAL(10,2),
    margin_ratio DECIMAL(10,4),
    unrealized_pnl DECIMAL(20,2),

    PRIMARY KEY (time, user_id)
);

-- Hypertable 변환
SELECT create_hypertable('portfolio_snapshots', 'time');

-- 인덱스 생성 (사용자별 시계열 조회)
CREATE INDEX idx_portfolio_user_time ON portfolio_snapshots(user_id, time DESC);

-- 코멘트
COMMENT ON TABLE portfolio_snapshots IS '포트폴리오 스냅샷 (10분마다) - TimescaleDB Hypertable';
COMMENT ON COLUMN portfolio_snapshots.total_value_usdt IS '총 포트폴리오 가치 (USDT)';
COMMENT ON COLUMN portfolio_snapshots.margin_ratio IS '마진 비율 (0~1, 청산 리스크 지표)';
COMMENT ON COLUMN portfolio_snapshots.unrealized_pnl IS '미실현 손익 (USDT)';

-- =============================================
-- 3. funding_rate_history (펀딩 레이트 이력)
-- =============================================
-- 선물 거래소의 펀딩 레이트 이력 (8시간마다 or 실시간)
CREATE TABLE funding_rate_history (
    time TIMESTAMPTZ NOT NULL,
    exchange VARCHAR(20) NOT NULL,
    symbol VARCHAR(20) NOT NULL,

    -- 펀딩 레이트 데이터
    funding_rate DECIMAL(10,8) NOT NULL,
    mark_price DECIMAL(20,8) NOT NULL,
    index_price DECIMAL(20,8) NOT NULL,

    PRIMARY KEY (time, exchange, symbol)
);

-- Hypertable 변환
SELECT create_hypertable('funding_rate_history', 'time');

-- 인덱스 생성 (심볼별 펀딩 레이트 조회)
CREATE INDEX idx_funding_symbol_time ON funding_rate_history(symbol, time DESC);
CREATE INDEX idx_funding_exchange ON funding_rate_history(exchange, symbol);

-- 코멘트
COMMENT ON TABLE funding_rate_history IS '펀딩 레이트 이력 - TimescaleDB Hypertable';
COMMENT ON COLUMN funding_rate_history.funding_rate IS '펀딩 레이트 (0.01% = 0.0001)';
COMMENT ON COLUMN funding_rate_history.mark_price IS '마크 가격 (청산 기준 가격)';
COMMENT ON COLUMN funding_rate_history.index_price IS '인덱스 가격 (현물 가격 기준)';

-- =============================================
-- Data Retention 정책 (선택사항)
-- =============================================
-- 오래된 데이터 자동 삭제 (디스크 공간 관리)

-- 1분봉: 7일 보관
-- SELECT add_retention_policy('market_data', INTERVAL '7 days');

-- 포트폴리오 스냅샷: 90일 보관
-- SELECT add_retention_policy('portfolio_snapshots', INTERVAL '90 days');

-- 펀딩 레이트: 180일 보관
-- SELECT add_retention_policy('funding_rate_history', INTERVAL '180 days');

-- =============================================
-- 완료 메시지
-- =============================================
DO $$
BEGIN
    RAISE NOTICE '✅ TimescaleDB Tables 생성 완료:';
    RAISE NOTICE '  - market_data: OHLCV 캔들 데이터 (Hypertable)';
    RAISE NOTICE '  - portfolio_snapshots: 포트폴리오 스냅샷 (Hypertable)';
    RAISE NOTICE '  - funding_rate_history: 펀딩 레이트 이력 (Hypertable)';
    RAISE NOTICE '  - 총 인덱스: 6개';
END $$;

