"""
AI Decisions Router
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from core.database import get_db
from models.user import User
from routers.users import get_current_user
from models.ai_decision import AIDecision, RegimeHistory
from schemas.ai_decision import (
    AIDecisionCreate,
    AIDecisionResponse,
    RegimeHistoryCreate,
    RegimeHistoryResponse
)

router = APIRouter(prefix="/api/v1/ai", tags=["AI Decisions"])


@router.post("/decisions", response_model=AIDecisionResponse, status_code=status.HTTP_201_CREATED)
def create_ai_decision(
    decision: AIDecisionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    AI 의사결정 기록 생성

    - **agent_name**: AI 에이전트 이름 (예: AXIS-CEO, AXIS-BTC-Analyst)
    - **decision**: 결정 내용 (LONG, SHORT, HOLD 등)
    - **evidence**: 의사결정 근거 배열 (JSON)
    - **reasoning**: AI의 자연어 설명
    """
    db_decision = AIDecision(
        user_id=current_user.user_id,
        agent_name=decision.agent_name,
        agent_role=decision.agent_role,
        decision_type=decision.decision_type,
        decision=decision.decision,
        confidence=decision.confidence,
        input_data=decision.input_data,
        output_data=decision.output_data,
        evidence=decision.evidence,
        reasoning=decision.reasoning,
        llm_model=decision.llm_model,
        prompt_tokens=decision.prompt_tokens,
        completion_tokens=decision.completion_tokens,
        llm_cost=decision.llm_cost,
        execution_time_ms=decision.execution_time_ms
    )

    db.add(db_decision)
    db.commit()
    db.refresh(db_decision)

    return db_decision


@router.get("/decisions", response_model=List[AIDecisionResponse])
def get_my_decisions(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    내 AI 의사결정 기록 조회

    - **limit**: 조회 개수 (기본 10개)
    """
    decisions = db.query(AIDecision).filter(
        AIDecision.user_id == current_user.user_id
    ).order_by(AIDecision.created_at.desc()).limit(limit).all()

    return decisions


@router.get("/decisions/{decision_id}", response_model=AIDecisionResponse)
def get_decision(
    decision_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    특정 AI 의사결정 상세 조회
    """
    decision = db.query(AIDecision).filter(
        AIDecision.decision_id == decision_id,
        AIDecision.user_id == current_user.user_id
    ).first()

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )

    return decision


@router.post("/regime", response_model=RegimeHistoryResponse, status_code=status.HTTP_201_CREATED)
def create_regime(
    regime: RegimeHistoryCreate,
    db: Session = Depends(get_db)
):
    """
    시장 레짐 기록 생성

    - **regime**: Bull Trend, Bear Trend, Consolidation
    - **confidence**: 확신도 (0.0 ~ 1.0)
    - **adx, rsi**: 기술적 지표
    """
    db_regime = RegimeHistory(
        regime=regime.regime,
        confidence=regime.confidence,
        adx=regime.adx,
        rsi=regime.rsi,
        price_vs_ma50=regime.price_vs_ma50,
        trend_strength=regime.trend_strength,
        ai_rationale=regime.ai_rationale
    )

    db.add(db_regime)
    db.commit()
    db.refresh(db_regime)

    return db_regime


@router.get("/regime/latest", response_model=RegimeHistoryResponse)
def get_latest_regime(db: Session = Depends(get_db)):
    """
    최신 시장 레짐 조회
    """
    regime = db.query(RegimeHistory).order_by(
        RegimeHistory.created_at.desc()
    ).first()

    if not regime:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No regime history found"
        )

    return regime


@router.get("/regime", response_model=List[RegimeHistoryResponse])
def get_regime_history(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    시장 레짐 변경 이력 조회

    - **limit**: 조회 개수 (기본 10개)
    """
    regimes = db.query(RegimeHistory).order_by(
        RegimeHistory.created_at.desc()
    ).limit(limit).all()

    return regimes

