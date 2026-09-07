from typing import List, Optional

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1)
    jurisdiction: str = Field(default="india", min_length=1)
    language: str = Field(default="English", min_length=1)


class SourceRef(BaseModel):
    title: str
    note: str = "Retrieved from the IP knowledge base."
    authority: Optional[str] = None
    section: Optional[str] = None
    source_url: Optional[str] = None
    version: Optional[str] = None


class AskResponse(BaseModel):
    answer: str
    jurisdiction: str
    confidence: float
    sources: List[SourceRef]
    disclaimer: str
    language: Optional[str] = None
    abstained: bool = False
    safe_abstention: bool = False
    escalate_to_human: bool = False
    citations: List[SourceRef] = Field(default_factory=list)


class ClassifyRequest(BaseModel):
    description: str = Field(..., min_length=1)


class ClassifyResponse(BaseModel):
    ip_type: str
    confidence: float
    explanation: str


class RiskAnalyzeRequest(BaseModel):
    title: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)


class RiskAnalyzeResponse(BaseModel):
    risk_level: str
    risks: List[str]
    recommendations: List[str]
    confidence: float


class AbsCheckRequest(BaseModel):
    description: str = Field(..., min_length=1)


class AbsCheckResponse(BaseModel):
    applicable: bool
    risk_level: str
    explanation: str
    recommendations: List[str]


class SourceItem(BaseModel):
    id: int
    title: str
    description: str
    category: str
    is_mock: bool

    class Config:
        from_attributes = True


class SourceListResponse(BaseModel):
    note: str = "These entries are mock/demo data for the MVP, not live legal citations."
    sources: List[SourceItem]


class HealthResponse(BaseModel):
    status: str


class ErrorResponse(BaseModel):
    detail: str
    error: Optional[str] = None
