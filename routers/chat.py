"""
routers/chat.py — RAG chat endpoint.

POST /chat accepts a question and returns an LLM-generated answer grounded in
the authenticated user's uploaded documents. Chat history is intentionally NOT
passed to the LLM (stateless per request — by design).

VectorStoreManager and LLMHandler are imported lazily to prevent the
pysqlite3 monkey-patch in vector_store.py from conflicting with the standard
sqlite3 used by core.database.
"""

import os
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from core.security import get_current_user

router = APIRouter()


class ChatRequest(BaseModel):
    question: str


def user_collection(user_id: str) -> str:
    """Derive an isolated ChromaDB collection name from a user UUID."""
    return f"user_{user_id.replace('-', '')}_docs"


@router.post("/chat")
def chat(
    request: ChatRequest,
    current_user: Annotated[dict, Depends(get_current_user)],
):
    """
    Perform a RAG query against the authenticated user's document collection.

    Retrieves up to 3 relevant chunks from ChromaDB, then passes them as
    context to the Groq/LLaMA LLM via LLMHandler.generate_rag_response.
    """
    user_id: str = current_user["user_id"]
    collection_name = user_collection(user_id)

    # Lazy imports — must come after core.database has been imported at startup
    from vector_store import VectorStoreManager
    from gerenciador_llm import LLMHandler

    vs = VectorStoreManager(collection_name)
    docs = vs.similarity_search(request.question, k=3)

    if not docs:
        return {
            "answer": "Nenhum documento encontrado. Faça o upload dos manuais em PDF primeiro.",
            "sources": [],
        }

    llm = LLMHandler()
    # chat_history is intentionally omitted — stateless design
    answer = llm.generate_rag_response(request.question, docs)

    sources = []
    for doc in docs:
        sources.append({
            "filename": os.path.basename(doc.metadata.get("source", "Desconhecido")),
            "page": doc.metadata.get("page", None),
            "excerpt": doc.page_content[:200],
        })

    return {"answer": answer, "sources": sources}
