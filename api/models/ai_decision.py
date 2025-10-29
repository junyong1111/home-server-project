"""
AI Decision Models
"""
from sqlalchemy import Column, Integer, String, DECIMAL, Text, TIMESTAMP, ForeignKey, JSON
from sqlalchemy.sql import func
from core.database import Base


class AIDecision(Base):
    """AI 의사결정 기록"""
    __tablename__ = "ai_decisions"

    decision_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(TIMESTAMP, nullable=False, server_default=func.now())

    # AI Agent 정보
    agent_name = Column(String(50), nullable=False)
    agent_role = Column(String(50), nullable=False)

    # 결정 내용
    decision_type = Column(String(50), nullable=False)
    decision = Column(String(20), nullable=False)
    confidence = Column(DECIMAL(5, 4), nullable=False)

    # Input/Output
    input_data = Column(JSON, nullable=False)
    output_data = Column(JSON, nullable=False)

    # Evidence (핵심!)
    evidence = Column(JSON, nullable=False)
    reasoning = Column(Text, nullable=False)

    # Validation (백테스팅용)
    actual_outcome = Column(DECIMAL(10, 4), nullable=True)
    decision_quality = Column(String(20), nullable=True)
    evidence_accuracy = Column(JSON, nullable=True)

    # LLM Meta
    llm_model = Column(String(50), nullable=True)
    prompt_tokens = Column(Integer, nullable=True)
    completion_tokens = Column(Integer, nullable=True)
    llm_cost = Column(DECIMAL(10, 6), nullable=True)
    execution_time_ms = Column(Integer, nullable=True)

    created_at = Column(TIMESTAMP, server_default=func.now())


class RegimeHistory(Base):
    """시장 레짐 변경 이력"""
    __tablename__ = "regime_history"

    regime_id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(TIMESTAMP, nullable=False, server_default=func.now())
    regime = Column(String(20), nullable=False)
    confidence = Column(DECIMAL(5, 4), nullable=False)

    # Evidence
    adx = Column(DECIMAL(10, 4), nullable=True)
    rsi = Column(DECIMAL(10, 4), nullable=True)
    price_vs_ma50 = Column(DECIMAL(10, 4), nullable=True)
    trend_strength = Column(String(20), nullable=True)

    ai_rationale = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

