from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from database import get_db
from models import Source
from schemas import (
    AbsCheckRequest,
    AbsCheckResponse,
    AskRequest,
    AskResponse,
    ClassifyRequest,
    ClassifyResponse,
    HealthResponse,
    RiskAnalyzeRequest,
    RiskAnalyzeResponse,
    SourceItem,
    SourceListResponse,
)
from services import (
    AIEngineError,
    ask_via_engine,
    mock_abs_check,
    mock_classify,
    mock_risk_analyze,
)

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health():
    return {"status": "healthy"}


@router.post("/api/ask", response_model=AskResponse)
def ask_question(payload: AskRequest, db: Session = Depends(get_db)):
    question = payload.question.strip()
    jurisdiction = payload.jurisdiction.strip()
    language = payload.language.strip() or "English"

    if not question:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question cannot be empty.",
        )
    if not jurisdiction:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Jurisdiction cannot be empty.",
        )

    try:
        return ask_via_engine(question, jurisdiction, language, db)
    except AIEngineError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not save the query to the database. Check PostgreSQL and DATABASE_URL.",
        )


@router.post("/api/classify", response_model=ClassifyResponse)
def classify_ip(payload: ClassifyRequest):
    description = payload.description.strip()
    if not description:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Description cannot be empty.",
        )
    return mock_classify(description)


@router.post("/api/risk/analyze", response_model=RiskAnalyzeResponse)
def analyze_risk(payload: RiskAnalyzeRequest):
    title = payload.title.strip()
    description = payload.description.strip()
    if not title or not description:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title and description cannot be empty.",
        )
    return mock_risk_analyze(title, description)


@router.post("/api/abs/check", response_model=AbsCheckResponse)
def check_abs(payload: AbsCheckRequest):
    description = payload.description.strip()
    if not description:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Description cannot be empty.",
        )
    return mock_abs_check(description)


@router.get("/api/sources", response_model=SourceListResponse)
def list_sources(db: Session = Depends(get_db)):
    try:
        rows = db.query(Source).order_by(Source.id).all()
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not read sources from the database. Check PostgreSQL and DATABASE_URL.",
        )

    return SourceListResponse(
        sources=[SourceItem.model_validate(row) for row in rows]
    )
