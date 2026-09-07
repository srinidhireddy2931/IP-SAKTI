import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
AI_ENGINE_URL = os.getenv("AI_ENGINE_URL", "").rstrip("/")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not set. Copy .env.example to .env and add your PostgreSQL URL."
    )

if not AI_ENGINE_URL:
    raise RuntimeError(
        "AI_ENGINE_URL is not set. Copy .env.example to .env and add the RAG service URL."
    )

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Provide a database session for each request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
