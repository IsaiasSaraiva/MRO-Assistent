"""
api.py — FastAPI entrypoint for MRO Assistant.

Wraps existing domain logic (PDF processing, LLM, vector store) in a REST API
with JWT authentication and per-user ChromaDB isolation.

Run with: uvicorn api:app --reload --port 8000
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# core.database must be imported BEFORE any vector_store import anywhere in the
# process. The vector_store module monkey-patches sqlite3 with pysqlite3 at
# import time; importing core.database first ensures standard sqlite3 is bound
# to our DB_PATH connection before that patch fires.
from core.database import init_db
from routers import auth, documents, chat


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the SQLite user/document database on startup."""
    init_db()
    yield


app = FastAPI(title="MRO Assistant API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(chat.router)


@app.get("/health")
def health():
    """Liveness check — no authentication required."""
    return {"status": "ok"}
