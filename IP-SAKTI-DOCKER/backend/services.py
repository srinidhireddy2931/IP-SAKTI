from typing import Any

import httpx
from sqlalchemy.orm import Session

from database import AI_ENGINE_URL
from models import Query, Source
from schemas import (
    AbsCheckResponse,
    AskResponse,
    ClassifyResponse,
    RiskAnalyzeResponse,
    SourceRef,
)

ASK_TIMEOUT_SECONDS = 30.0


class AIEngineError(Exception):
    """Raised when the Member 3 RAG service cannot be reached or returns a bad payload."""

    def __init__(self, message: str, status_code: int = 502):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


DISCLAIMER = "Information, not legal advice."

MOCK_SOURCES = [
    {
        "title": "[MOCK] Indian Patents Act, 1970 — demo note",
        "description": "Demo label for Indian patent-law topics. Not a live citation.",
        "category": "patent",
    },
    {
        "title": "[MOCK] Trade Marks Act, 1999 — demo note",
        "description": "Demo label for Indian trade mark topics. Not a live citation.",
        "category": "trademark",
    },
    {
        "title": "[MOCK] Copyright Act, 1957 — demo note",
        "description": "Demo label for Indian copyright topics. Not a live citation.",
        "category": "copyright",
    },
    {
        "title": "[MOCK] Biological Diversity Act — ABS demo note",
        "description": "Demo label for Access and Benefit Sharing topics. Not a live citation.",
        "category": "abs",
    },
    {
        "title": "[MOCK] TKDL / prior-art demo note",
        "description": "Demo label for Traditional Knowledge Digital Library style references. Not a live citation.",
        "category": "tkdl",
    },
    {
        "title": "[MOCK] International IP (WIPO-style) demo note",
        "description": "Demo label for international jurisdiction comparisons. Not a live citation.",
        "category": "international",
    },
]


def seed_mock_sources(db: Session) -> None:
    """Insert demo sources once so GET /api/sources has data."""
    if db.query(Source).first():
        return

    for item in MOCK_SOURCES:
        db.add(Source(**item, is_mock=True))
    db.commit()


def _normalize_jurisdiction(jurisdiction: str) -> str:
    value = jurisdiction.strip().lower()
    if value in {"india", "in", "indian"}:
        return "india"
    if value in {"international", "global", "wipo", "foreign"}:
        return "international"
    return value


def _keyword_hits(text: str, keywords: list[str]) -> bool:
    lowered = text.lower()
    return any(word in lowered for word in keywords)


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _citation_to_source(item: Any) -> SourceRef:
    """Map one RAG source/citation object onto the backend SourceRef contract."""
    if not isinstance(item, dict):
        return SourceRef(title=str(item))

    title = str(item.get("title") or "Untitled source")
    authority = _optional_str(item.get("authority"))
    version = _optional_str(item.get("version"))
    # RAG uses url/reference; keep source_url/section as fallbacks.
    source_url = _optional_str(item.get("url")) or _optional_str(item.get("source_url"))
    reference = _optional_str(item.get("reference"))
    section = reference or _optional_str(item.get("section"))
    if reference:
        note = reference
    else:
        note_parts = [part for part in (authority, section) if part]
        note = " — ".join(note_parts) if note_parts else "Retrieved from the IP knowledge base."

    return SourceRef(
        title=title,
        note=note,
        authority=authority,
        section=section,
        source_url=source_url,
        version=version,
    )


def _map_rag_items(raw: Any) -> list[SourceRef]:
    if not isinstance(raw, list):
        return []
    return [_citation_to_source(item) for item in raw]


def ask_via_engine(
    question: str,
    jurisdiction: str,
    language: str,
    db: Session,
) -> AskResponse:
    """Proxy /api/ask to the Member 3 RAG service and log the query."""
    q = question.strip()
    jurisdiction = _normalize_jurisdiction(jurisdiction)
    language = language.strip() or "English"
    url = f"{AI_ENGINE_URL}/ask"

    try:
        with httpx.Client(timeout=ASK_TIMEOUT_SECONDS) as client:
            response = client.post(
                url,
                json={
                    "question": q,
                    "jurisdiction": jurisdiction,
                    "language": language,
                },
            )
    except httpx.TimeoutException as exc:
        raise AIEngineError(
            "The AI/RAG service timed out. Confirm it is running at AI_ENGINE_URL.",
            status_code=504,
        ) from exc
    except httpx.RequestError as exc:
        raise AIEngineError(
            "Could not reach the AI/RAG service. Confirm it is running at AI_ENGINE_URL "
            f"({AI_ENGINE_URL}).",
            status_code=502,
        ) from exc

    if response.status_code == 422:
        raise AIEngineError(
            "The AI/RAG service rejected the request. Check question length and fields.",
            status_code=400,
        )
    if response.status_code >= 400:
        raise AIEngineError(
            f"The AI/RAG service returned HTTP {response.status_code}.",
            status_code=502,
        )

    try:
        payload = response.json()
    except ValueError as exc:
        raise AIEngineError("The AI/RAG service returned a non-JSON response.") from exc

    if not isinstance(payload, dict) or "answer" not in payload:
        raise AIEngineError("The AI/RAG service returned an unexpected payload.")

    sources = _map_rag_items(payload.get("sources"))
    citations = _map_rag_items(payload.get("citations"))

    abstained = bool(payload.get("abstained", payload.get("safe_abstention", False)))
    escalate = bool(payload.get("escalate_to_human", abstained))
    try:
        confidence = float(payload.get("confidence", 0.0))
    except (TypeError, ValueError):
        confidence = 0.0

    answer = str(payload.get("answer") or "")
    resolved_jurisdiction = str(payload.get("jurisdiction") or jurisdiction)
    resolved_language = str(payload.get("language") or language)
    disclaimer = str(payload.get("disclaimer") or DISCLAIMER)

    record = Query(
        question=q,
        jurisdiction=resolved_jurisdiction,
        answer=answer,
        confidence=confidence,
    )
    db.add(record)
    db.commit()

    return AskResponse(
        answer=answer,
        jurisdiction=resolved_jurisdiction,
        confidence=confidence,
        sources=sources,
        disclaimer=disclaimer,
        language=resolved_language,
        abstained=abstained,
        safe_abstention=abstained,
        escalate_to_human=escalate,
        citations=citations,
    )


def mock_classify(description: str) -> ClassifyResponse:
    """Dummy IP classification. Replace later with a real classifier."""
    text = description.strip()

    if _keyword_hits(text, ["biological", "genetic", "plant variety", "traditional knowledge"]):
        return ClassifyResponse(
            ip_type="mixed / abs-sensitive (mock)",
            confidence=0.61,
            explanation=(
                "[MOCK] The description mentions biological resources or traditional knowledge. "
                "Possible IP types include patent, plant variety, and related ABS issues. "
                "This is demo classification only."
            ),
        )
    if _keyword_hits(text, ["logo", "brand", "trademark", "trade mark"]):
        return ClassifyResponse(
            ip_type="trademark (mock)",
            confidence=0.66,
            explanation="[MOCK] Branding language suggests a trade mark filing path. Demo only.",
        )
    if _keyword_hits(text, ["song", "book", "software ui", "artistic", "copyright", "literary"]):
        return ClassifyResponse(
            ip_type="copyright (mock)",
            confidence=0.64,
            explanation="[MOCK] Creative-work language suggests copyright. Demo only.",
        )
    if _keyword_hits(text, ["design", "ornamental", "shape", "appearance"]):
        return ClassifyResponse(
            ip_type="industrial design (mock)",
            confidence=0.6,
            explanation="[MOCK] Appearance-focused language suggests industrial design. Demo only.",
        )
    if _keyword_hits(text, ["invention", "device", "process", "technical", "patent"]):
        return ClassifyResponse(
            ip_type="patent (mock)",
            confidence=0.63,
            explanation="[MOCK] Technical invention language suggests a patent path. Demo only.",
        )

    return ClassifyResponse(
        ip_type="unclear (mock)",
        confidence=0.35,
        explanation=(
            "[MOCK] Not enough distinctive signals to pick one IP type. "
            "A human IP facilitator should review this. Demo only."
        ),
    )


def mock_risk_analyze(title: str, description: str) -> RiskAnalyzeResponse:
    """Dummy innovation risk analysis. Replace later with a real risk model."""
    text = f"{title} {description}".lower()
    risks = []
    recommendations = []
    risk_level = "low"
    confidence = 0.45

    if _keyword_hits(text, ["traditional knowledge", "biological", "genetic", "ayurveda"]):
        risk_level = "high"
        confidence = 0.58
        risks.append("[MOCK] Possible ABS / traditional-knowledge compliance issues.")
        recommendations.append(
            "[MOCK] Check biological-resource and traditional-knowledge disclosure rules."
        )

    if _keyword_hits(text, ["software", "algorithm", "business method", "ai model"]):
        risk_level = "medium" if risk_level != "high" else "high"
        confidence = max(confidence, 0.52)
        risks.append("[MOCK] Software / business-method subject-matter may be excluded or limited.")
        recommendations.append(
            "[MOCK] Focus claims on a technical effect if a patent path is considered."
        )

    if _keyword_hits(text, ["public", "published", "disclosed", "youtube", "conference"]):
        risk_level = "medium" if risk_level == "low" else risk_level
        confidence = max(confidence, 0.5)
        risks.append("[MOCK] Prior public disclosure can harm novelty.")
        recommendations.append("[MOCK] Confirm disclosure dates before any patent filing.")

    if not risks:
        risks.append("[MOCK] No high-signal risk keywords found in this demo check.")
        recommendations.append(
            "[MOCK] Still run a prior-art search and consider facilitator review before filing."
        )

    recommendations.append("[MOCK] Escalate to a human IP facilitator for a real opinion.")

    return RiskAnalyzeResponse(
        risk_level=risk_level,
        risks=risks,
        recommendations=recommendations,
        confidence=confidence,
    )


def mock_abs_check(description: str) -> AbsCheckResponse:
    """Dummy Access and Benefit Sharing check. Replace later with real ABS logic."""
    text = description.strip()
    applicable = _keyword_hits(
        text,
        [
            "biological",
            "genetic",
            "plant",
            "microbe",
            "traditional knowledge",
            "tkdl",
            "ayurveda",
            "biodiversity",
        ],
    )

    if applicable:
        return AbsCheckResponse(
            applicable=True,
            risk_level="high",
            explanation=(
                "[MOCK] The description appears to involve biological resources and/or "
                "traditional knowledge. Indian ABS-style rules may apply. This is demo output, "
                "not a compliance determination."
            ),
            recommendations=[
                "[MOCK] Identify the biological resource and any associated traditional knowledge.",
                "[MOCK] Review whether prior informed consent and benefit-sharing may be required.",
                "[MOCK] Escalate to a human IP / ABS facilitator before filing or commercial use.",
            ],
        )

    return AbsCheckResponse(
        applicable=False,
        risk_level="low",
        explanation=(
            "[MOCK] No clear biological-resource or traditional-knowledge signals were found. "
            "This dummy check can miss relevant facts. Demo only."
        ),
        recommendations=[
            "[MOCK] Re-run this check if the innovation uses plants, microbes, genetic material, or TK.",
            "[MOCK] Keep a human facilitator in the loop for uncertain cases.",
        ],
    )
