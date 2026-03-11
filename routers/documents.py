"""
routers/documents.py — PDF upload, listing, and deletion endpoints.

Per-user ChromaDB isolation is achieved via a collection name derived from the
user's UUID: user_<id_without_hyphens>_docs.

IMPORTANT: VectorStoreManager is imported lazily (inside route functions) to
prevent the pysqlite3 monkey-patch in vector_store.py from interfering with
the standard sqlite3 used by core.database.
"""

import hashlib
import os
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status

from core.database import (
    delete_document_by_id,
    delete_user_documents,
    document_exists_by_hash,
    get_document_by_id,
    get_user_documents,
    insert_document,
)
from core.security import get_current_user

# config values needed here — standard import, no pysqlite3 involved
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import UPLOAD_DIR

router = APIRouter()


def user_collection(user_id: str) -> str:
    """Derive an isolated ChromaDB collection name from a user UUID."""
    return f"user_{user_id.replace('-', '')}_docs"


@router.post("/documents/upload")
async def upload_documents(
    files: list[UploadFile],
    current_user: Annotated[dict, Depends(get_current_user)],
):
    """
    Upload one or more PDF files.

    For each file:
    - Computes a SHA-256 hash for deduplication (scoped per user).
    - Writes bytes to UPLOAD_DIR.
    - Parses and chunks the PDF via PDFProcessor.
    - Indexes chunks in the user's isolated ChromaDB collection.
    - Records metadata in the documents SQLite table.
    """
    user_id: str = current_user["user_id"]
    results = []

    for file in files:
        contents: bytes = await file.read()
        file_hash = hashlib.sha256(contents).hexdigest()

        # Deduplication check
        if document_exists_by_hash(user_id, file_hash):
            results.append({
                "filename": file.filename,
                "num_chunks": 0,
                "status": "duplicate",
            })
            continue

        # Persist to disk
        # We do NOT use PDFProcessor.save_uploaded_file because it expects a
        # Streamlit UploadedFile object (.name, .getbuffer()), not FastAPI's
        # UploadFile. We write the bytes directly and call load_and_split_pdf.
        file_path = Path(UPLOAD_DIR) / file.filename
        file_path.write_bytes(contents)

        # Parse + chunk (lazy import to avoid circular / patch issues)
        try:
            from processador_pdf import PDFProcessor
            processor = PDFProcessor()
            chunks = processor.load_and_split_pdf(str(file_path))
        except Exception as exc:
            results.append({
                "filename": file.filename,
                "num_chunks": 0,
                "status": f"error: {exc}",
            })
            continue

        # Index in ChromaDB (lazy import — keeps pysqlite3 patch after sqlite3 init)
        from vector_store import VectorStoreManager
        vs = VectorStoreManager(user_collection(user_id))
        vs.add_documents(chunks)

        # Persist metadata
        insert_document(
            user_id=user_id,
            filename=file.filename,
            file_path=str(file_path),
            file_hash=file_hash,
            chunk_count=len(chunks),
        )

        results.append({
            "filename": file.filename,
            "num_chunks": len(chunks),
            "status": "success",
        })

    return results


@router.get("/documents")
def list_documents(
    current_user: Annotated[dict, Depends(get_current_user)],
):
    """Return all documents uploaded by the authenticated user."""
    user_id: str = current_user["user_id"]
    return get_user_documents(user_id)


@router.delete("/documents/{document_id}")
def delete_document(
    document_id: str,
    current_user: Annotated[dict, Depends(get_current_user)],
):
    """
    Delete a document by UUID.

    Removes its vector embeddings from ChromaDB and its metadata from SQLite.
    Returns 404 if the document does not exist or belongs to a different user.
    """
    user_id: str = current_user["user_id"]

    doc = get_document_by_id(document_id)
    if doc is None or doc["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    # Remove embeddings from ChromaDB (lazy import)
    from vector_store import VectorStoreManager
    vs = VectorStoreManager(user_collection(user_id))
    vs.delete_by_source(doc["file_path"])

    delete_document_by_id(document_id)
    return {"success": True}


@router.delete("/collection")
def clear_collection(
    current_user: Annotated[dict, Depends(get_current_user)],
):
    """
    Delete the entire ChromaDB collection and all document records for the
    authenticated user. This operation is irreversible.
    """
    user_id: str = current_user["user_id"]

    # Drop the ChromaDB collection (lazy import)
    from vector_store import VectorStoreManager
    vs = VectorStoreManager(user_collection(user_id))
    vs.delete_collection()

    delete_user_documents(user_id)
    return {"success": True}
