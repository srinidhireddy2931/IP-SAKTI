from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from database import Base, SessionLocal, engine
from models import Query, Source  # noqa: F401 — register tables on Base.metadata
from routes import router
from services import seed_mock_sources


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_mock_sources(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="IP Knowledge Assistant",
    description=(
        "MVP backend for the SIH IP Knowledge Assistant. "
        "POST /api/ask proxies to the Member 3 RAG service at AI_ENGINE_URL. "
        "Classify, risk, and ABS endpoints still return mock/demo data."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",
    ],
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.exception_handler(SQLAlchemyError)
def database_exception_handler(request: Request, exc: SQLAlchemyError):
    return JSONResponse(
        status_code=503,
        content={
            "detail": "Database error. Check that PostgreSQL is running and DATABASE_URL is correct."
        },
    )
