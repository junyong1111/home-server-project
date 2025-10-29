"""
AI Decision Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime
from decimal import Decimal


class AIDecisionCreate(BaseModel):
    """AI 의사결정 생성 요청"""
    agent_name: str = Field(..., description="AI 에이전트 이름 (예: AXIS-CEO)")
    agent_role: str = Field(..., description="에이전트 역할 (Executive/Research/Risk/Operations)")
    decision_type: str = Field(..., description="의사결정 유형 (예: trade_signal)")
    decision: str = Field(..., description="결정 내용 (예: LONG, SHORT, HOLD)")
    confidence: Decimal = Field(..., ge=0, le=1, description="확신도 (0.0 ~ 1.0)")

    input_data: Dict[str, Any] = Field(..., description="AI에게 제공된 입력 데이터")
    output_data: Dict[str, Any] = Field(..., description="AI의 응답 데이터")
    evidence: List[Dict[str, Any]] = Field(..., description="의사결정 근거 배열")
    reasoning: str = Field(..., description="AI의 자연어 설명")

    # LLM Meta (선택)
    llm_model: Optional[str] = Field(None, description="LLM 모델명 (예: gpt-4o)")
    prompt_tokens: Optional[int] = Field(None, description="프롬프트 토큰 수")
    completion_tokens: Optional[int] = Field(None, description="완료 토큰 수")
    llm_cost: Optional[Decimal] = Field(None, description="LLM 비용 (USD)")
    execution_time_ms: Optional[int] = Field(None, description="실행 시간 (밀리초)")


class AIDecisionResponse(BaseModel):
    """AI 의사결정 응답"""
    decision_id: int
    user_id: int
    timestamp: datetime
    agent_name: str
    agent_role: str
    decision_type: str
    decision: str
    confidence: Decimal

    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    evidence: List[Dict[str, Any]]
    reasoning: str

    actual_outcome: Optional[Decimal] = None
    decision_quality: Optional[str] = None
    evidence_accuracy: Optional[Dict[str, Any]] = None

    llm_model: Optional[str] = None
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    llm_cost: Optional[Decimal] = None
    execution_time_ms: Optional[int] = None

    created_at: datetime

    class Config:
        from_attributes = True


class RegimeHistoryCreate(BaseModel):
    """시장 레짐 기록 생성 요청"""
    regime: str = Field(..., description="시장 레짐 (Bull Trend/Bear Trend/Consolidation)")
    confidence: Decimal = Field(..., ge=0, le=1, description="확신도")

    adx: Optional[Decimal] = Field(None, description="ADX 지표")
    rsi: Optional[Decimal] = Field(None, description="RSI 지표")
    price_vs_ma50: Optional[Decimal] = Field(None, description="현재가/MA50 비율")
    trend_strength: Optional[str] = Field(None, description="추세 강도 (weak/moderate/strong)")

    ai_rationale: Optional[str] = Field(None, description="AI의 레짐 판단 근거")


class RegimeHistoryResponse(BaseModel):
    """시장 레짐 응답"""
    regime_id: int
    timestamp: datetime
    regime: str
    confidence: Decimal

    adx: Optional[Decimal] = None
    rsi: Optional[Decimal] = None
    price_vs_ma50: Optional[Decimal] = None
    trend_strength: Optional[str] = None

    ai_rationale: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

