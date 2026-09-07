from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text

from database import Base


class Query(Base):
    """Stores user questions and the (currently mock) answers returned by /api/ask."""

    __tablename__ = "queries"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    jurisdiction = Column(String(50), nullable=False)
    answer = Column(Text, nullable=False)
    confidence = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Source(Base):
    """Stores IP/legal source labels used as demo references."""

    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(100), nullable=False, default="general")
    is_mock = Column(Boolean, nullable=False, default=True)
