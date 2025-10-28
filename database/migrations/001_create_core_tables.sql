-- ============================================================
-- AXIS Capital - Core Tables Migration
-- ============================================================
-- Version: 1.0
-- Created: 2025-10-28
-- Description: users, positions, trades 테이블 생성
-- ============================================================

-- ============================================================
-- 1. users 테이블
-- ============================================================
-- 설명: 사용자 정보 및 암호화된 API 키 저장
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,

    -- API 키 (암호화 저장)
    api_key_encrypted TEXT NOT NULL,
    api_secret_encrypted TEXT NOT NULL,

    -- 리스크 프로필: conservative, balanced, aggressive
    risk_profile VARCHAR(20) DEFAULT 'balanced',

    -- 활성화 상태
    is_active BOOLEAN DEFAULT true,

    -- 타임스탬프
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 인덱스
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);

-- 코멘트
COMMENT ON TABLE users IS '사용자 정보 및 API 키 (암호화)';
COMMENT ON COLUMN users.api_key_encrypted IS 'ENCRYPTION_KEY로 암호화된 Binance API Key';
COMMENT ON COLUMN users.api_secret_encrypted IS 'ENCRYPTION_KEY로 암호화된 Binance API Secret';
COMMENT ON COLUMN users.risk_profile IS 'conservative(레버리지 1-3x), balanced(3-7x), aggressive(7-15x)';

-- ============================================================
-- 2. positions 테이블
-- ============================================================
-- 설명: 선물 포지션 정보 (진입/청산/PnL)
-- ============================================================
CREATE TABLE IF NOT EXISTS positions (
    position_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,

    -- 거래소 및 심볼
    exchange VARCHAR(20) DEFAULT 'binance',
    symbol VARCHAR(20) NOT NULL,

    -- 포지션 타입
    side VARCHAR(10) NOT NULL CHECK (side IN ('LONG', 'SHORT')),
    leverage DECIMAL(5,2) NOT NULL CHECK (leverage > 0 AND leverage <= 125),

    -- ===== Entry (진입) =====
    entry_price DECIMAL(20,8) NOT NULL,
    entry_time TIMESTAMP NOT NULL,
    quantity DECIMAL(20,8) NOT NULL CHECK (quantity > 0),
    notional_value DECIMAL(20,2) NOT NULL,  -- quantity * entry_price
    margin DECIMAL(20,2) NOT NULL,  -- notional_value / leverage

    -- ===== Risk (리스크 관리) =====
    stop_loss_price DECIMAL(20,8),
    take_profit_price DECIMAL(20,8),
    liquidation_price DECIMAL(20,8) NOT NULL,

    -- ===== Exit (청산) =====
    exit_price DECIMAL(20,8),
    exit_time TIMESTAMP,
    realized_pnl DECIMAL(20,2),  -- 실현 손익 (USDT)
    pnl_pct DECIMAL(10,4),  -- 손익률 (%)

    -- ===== Meta (AI 판단 근거) =====
    regime VARCHAR(20),  -- bull_trend, bear_trend, consolidation
    confidence DECIMAL(5,4),  -- AI 신뢰도 (0-1)
    ai_rationale TEXT,  -- AI 결정 이유

    -- ===== Status =====
    status VARCHAR(20) DEFAULT 'open' CHECK (status IN ('open', 'closed', 'liquidated')),

    -- 타임스탬프
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 인덱스
CREATE INDEX IF NOT EXISTS idx_positions_user_status ON positions(user_id, status);
CREATE INDEX IF NOT EXISTS idx_positions_symbol_status ON positions(symbol, status);
CREATE INDEX IF NOT EXISTS idx_positions_entry_time ON positions(entry_time DESC);
CREATE INDEX IF NOT EXISTS idx_positions_status ON positions(status) WHERE status = 'open';

-- 코멘트
COMMENT ON TABLE positions IS '선물 포지션 정보 (LONG/SHORT)';
COMMENT ON COLUMN positions.side IS 'LONG: 롱 포지션, SHORT: 숏 포지션';
COMMENT ON COLUMN positions.leverage IS '레버리지 배율 (1x ~ 125x)';
COMMENT ON COLUMN positions.margin IS '실제 투입 자금 (notional_value / leverage)';
COMMENT ON COLUMN positions.liquidation_price IS '청산 가격 (진입 시 계산)';
COMMENT ON COLUMN positions.regime IS 'bull_trend, bear_trend, consolidation';

-- ============================================================
-- 3. trades 테이블
-- ============================================================
-- 설명: 개별 거래 실행 기록 (진입/청산 주문)
-- ============================================================
CREATE TABLE IF NOT EXISTS trades (
    trade_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    position_id INT REFERENCES positions(position_id) ON DELETE SET NULL,

    -- 실행 시간
    timestamp TIMESTAMP NOT NULL,

    -- 거래소 및 심볼
    exchange VARCHAR(20) NOT NULL,
    symbol VARCHAR(20) NOT NULL,

    -- 주문 타입
    side VARCHAR(10) NOT NULL CHECK (side IN ('BUY', 'SELL')),  -- 실행 side
    order_type VARCHAR(20) NOT NULL CHECK (order_type IN ('MARKET', 'LIMIT', 'STOP_MARKET', 'STOP_LIMIT')),

    -- 가격 및 수량
    price DECIMAL(20,8) NOT NULL,
    quantity DECIMAL(20,8) NOT NULL CHECK (quantity > 0),
    total_usdt DECIMAL(20,2) NOT NULL,  -- price * quantity

    -- 수수료
    fee DECIMAL(20,8) NOT NULL,
    fee_currency VARCHAR(10) NOT NULL DEFAULT 'USDT',

    -- 거래소 주문 ID
    exchange_order_id VARCHAR(100),

    -- 상태
    status VARCHAR(20) DEFAULT 'executed' CHECK (status IN ('pending', 'executed', 'failed', 'cancelled')),

    -- 타임스탬프
    created_at TIMESTAMP DEFAULT NOW()
);

-- 인덱스
CREATE INDEX IF NOT EXISTS idx_trades_user_time ON trades(user_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_trades_position ON trades(position_id);
CREATE INDEX IF NOT EXISTS idx_trades_symbol_time ON trades(symbol, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_trades_exchange_order ON trades(exchange_order_id);

-- 코멘트
COMMENT ON TABLE trades IS '개별 거래 실행 기록 (진입/청산 주문)';
COMMENT ON COLUMN trades.side IS 'BUY: 매수 (LONG 진입 or SHORT 청산), SELL: 매도 (SHORT 진입 or LONG 청산)';
COMMENT ON COLUMN trades.order_type IS 'MARKET: 시장가, LIMIT: 지정가, STOP_MARKET: 스톱 시장가';
COMMENT ON COLUMN trades.exchange_order_id IS '바이낸스 주문 ID (고유)';

-- ============================================================
-- Updated_at Trigger 함수
-- ============================================================
-- 설명: updated_at 자동 업데이트
-- ============================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- users 테이블 트리거
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- positions 테이블 트리거
CREATE TRIGGER update_positions_updated_at
    BEFORE UPDATE ON positions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- 테스트 데이터 삽입 (선택사항)
-- ============================================================
-- 테스트용 사용자 생성
INSERT INTO users (username, email, api_key_encrypted, api_secret_encrypted, risk_profile)
VALUES
    ('test_user', 'test@axis.capital', 'encrypted_key_placeholder', 'encrypted_secret_placeholder', 'balanced')
ON CONFLICT (username) DO NOTHING;

-- ============================================================
-- 마이그레이션 완료
-- ============================================================

