-- =============================================
-- 002_create_ai_tables.sql
-- AI 의사결정 및 분석 테이블 생성
-- =============================================
-- 생성일: 2025-10-28
-- 설명: AI 에이전트의 의사결정, 사후 분석, 시장 레짐 변경 이력
-- =============================================

-- =============================================
-- 1. ai_decisions
-- =============================================
-- AI 에이전트의 의사결정 기록
-- - 모든 AI 판단과 근거를 저장
-- - 백테스팅을 위한 실제 결과 저장
-- - LLM 비용 및 성능 추적
CREATE TABLE ai_decisions (
    decision_id SERIAL PRIMARY KEY,

    -- 기본 정보
    user_id INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),

    -- AI Agent 정보
    agent_name VARCHAR(50) NOT NULL,  -- AXIS-CEO, AXIS-BTC-Analyst, AXIS-Risk-Chief 등
    agent_role VARCHAR(50) NOT NULL,  -- Executive, Research, Risk, Operations

    -- 결정 내용
    decision_type VARCHAR(50) NOT NULL,  -- trade_signal, risk_assessment, regime_change 등
    decision VARCHAR(20) NOT NULL,       -- LONG, SHORT, HOLD, CLOSE, REDUCE 등
    confidence DECIMAL(5,4) NOT NULL CHECK (confidence >= 0 AND confidence <= 1),

    -- Input/Output
    input_data JSONB NOT NULL,   -- AI에게 제공된 데이터
    output_data JSONB NOT NULL,  -- AI의 응답 (JSON 구조화)

    -- Evidence (증거 기반 의사결정) 🔥 핵심!
    evidence JSONB NOT NULL,     -- 근거 데이터 (배열)
    reasoning TEXT NOT NULL,     -- AI의 논리적 설명 (자연어)

    -- Validation (백테스팅용) 🧪
    actual_outcome DECIMAL(10,4),        -- 실제 결과 (24h 후 업데이트)
    decision_quality VARCHAR(20),        -- correct, incorrect, neutral
    evidence_accuracy JSONB,             -- 각 evidence의 정확도 분석

    -- LLM Meta (비용 추적)
    llm_model VARCHAR(50),               -- gpt-4o, gpt-o1, gpt-4o-mini
    prompt_tokens INT,
    completion_tokens INT,
    llm_cost DECIMAL(10,6),              -- USD 단위
    execution_time_ms INT,               -- 실행 시간 (밀리초)

    created_at TIMESTAMP DEFAULT NOW()
);

-- 인덱스 생성
CREATE INDEX idx_decisions_user_time ON ai_decisions(user_id, timestamp DESC);
CREATE INDEX idx_decisions_agent ON ai_decisions(agent_name, timestamp DESC);
CREATE INDEX idx_decisions_quality ON ai_decisions(decision_quality, timestamp DESC);
CREATE INDEX idx_decisions_type ON ai_decisions(decision_type, timestamp DESC);

-- 코멘트
COMMENT ON TABLE ai_decisions IS 'AI 에이전트의 모든 의사결정 기록 (증거 기반)';
COMMENT ON COLUMN ai_decisions.evidence IS '의사결정 근거 (JSON 배열): [{"type": "technical", "data": {...}, "weight": 0.3}, ...]';
COMMENT ON COLUMN ai_decisions.reasoning IS 'AI의 자연어 설명 (왜 이 결정을 내렸는지)';
COMMENT ON COLUMN ai_decisions.actual_outcome IS '24시간 후 실제 결과 (백테스팅용)';
COMMENT ON COLUMN ai_decisions.evidence_accuracy IS '각 evidence가 실제로 맞았는지 검증';

-- =============================================
-- 2. decision_analysis
-- =============================================
-- AI 의사결정에 대한 사후 분석
-- - 거래 후 24시간 뒤 자동 분석
-- - 예측과 실제 결과 비교
-- - 개선 제안 생성
CREATE TABLE decision_analysis (
    analysis_id SERIAL PRIMARY KEY,
    decision_id INT NOT NULL REFERENCES ai_decisions(decision_id) ON DELETE CASCADE,

    -- 분석 시점 (거래 후 24시간)
    analysis_timestamp TIMESTAMP NOT NULL DEFAULT NOW(),

    -- 예측 vs 실제
    predicted_direction VARCHAR(10),     -- LONG, SHORT, HOLD
    actual_direction VARCHAR(10),        -- 실제 시장 방향
    was_correct BOOLEAN NOT NULL,        -- 예측이 맞았는지

    -- 성과 비교
    predicted_return DECIMAL(10,4),      -- 예측한 수익률 (%)
    actual_return DECIMAL(10,4),         -- 실제 수익률 (%)
    error_pct DECIMAL(10,4),             -- 오차 (%)

    -- 근거 검증
    evidence_breakdown JSONB,            -- 각 evidence가 맞았는지 세부 분석

    -- 개선 제안
    improvement_suggestions TEXT,        -- AI가 제안하는 개선 방안

    created_at TIMESTAMP DEFAULT NOW()
);

-- 인덱스 생성
CREATE INDEX idx_analysis_decision ON decision_analysis(decision_id);
CREATE INDEX idx_analysis_time ON decision_analysis(analysis_timestamp DESC);
CREATE INDEX idx_analysis_correct ON decision_analysis(was_correct, analysis_timestamp DESC);

-- 코멘트
COMMENT ON TABLE decision_analysis IS 'AI 의사결정 사후 분석 (24h 후 자동 실행)';
COMMENT ON COLUMN decision_analysis.was_correct IS '예측이 맞았는지 (TRUE/FALSE)';
COMMENT ON COLUMN decision_analysis.evidence_breakdown IS 'evidence 별 정확도 분석';
COMMENT ON COLUMN decision_analysis.improvement_suggestions IS 'AI가 제안하는 개선점';

-- =============================================
-- 3. regime_history
-- =============================================
-- 시장 레짐 변경 이력
-- - Bull Trend, Bear Trend, Consolidation
-- - 레짐 변경 시점 추적
-- - 전략 변경 근거
CREATE TABLE regime_history (
    regime_id SERIAL PRIMARY KEY,

    -- 시간 및 레짐
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    regime VARCHAR(20) NOT NULL CHECK (regime IN ('Bull Trend', 'Bear Trend', 'Consolidation')),
    confidence DECIMAL(5,4) NOT NULL CHECK (confidence >= 0 AND confidence <= 1),

    -- Evidence (기술적 지표)
    adx DECIMAL(10,4),                   -- Average Directional Index
    rsi DECIMAL(10,4),                   -- Relative Strength Index
    price_vs_ma50 DECIMAL(10,4),         -- 현재가 / MA50 비율
    trend_strength VARCHAR(20),          -- weak, moderate, strong

    -- AI 판단 근거
    ai_rationale TEXT,                   -- AI가 이 레짐으로 판단한 이유

    created_at TIMESTAMP DEFAULT NOW()
);

-- 인덱스 생성
CREATE INDEX idx_regime_time ON regime_history(timestamp DESC);
CREATE INDEX idx_regime_type ON regime_history(regime, timestamp DESC);

-- 코멘트
COMMENT ON TABLE regime_history IS '시장 레짐 변경 이력 (Bull/Bear/Consolidation)';
COMMENT ON COLUMN regime_history.regime IS '시장 상태: Bull Trend, Bear Trend, Consolidation';
COMMENT ON COLUMN regime_history.confidence IS '레짐 판단의 확신도 (0.0 ~ 1.0)';
COMMENT ON COLUMN regime_history.ai_rationale IS 'AI의 레짐 판단 근거';

-- =============================================
-- 트리거: updated_at 자동 업데이트 (불필요, created_at만 사용)
-- =============================================

-- =============================================
-- 완료 메시지
-- =============================================
DO $$
BEGIN
    RAISE NOTICE '✅ AI Tables 생성 완료:';
    RAISE NOTICE '  - ai_decisions: AI 의사결정 기록';
    RAISE NOTICE '  - decision_analysis: 사후 분석';
    RAISE NOTICE '  - regime_history: 시장 레짐 변경';
    RAISE NOTICE '  - 총 인덱스: 9개';
END $$;

