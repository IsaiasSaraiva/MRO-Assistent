"""
core/database.py — SQLite persistence for users and document metadata.

Uses standard sqlite3 (NOT pysqlite3). This module must be imported before
any module that imports vector_store, because vector_store.py monkey-patches
sys.modules['sqlite3'] with pysqlite3 at import time. Importing this module
first ensures that our sqlite3 connections are established with the real
standard library module.

DB_PATH is derived from config.BASE_DIR so that users.db lives alongside the
rest of the persistent data in drive/.
"""

import sqlite3
import uuid
from pathlib import Path
import sys
import os

# Insert drive/ root on path so config.py is importable from within core/
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import BASE_DIR  # BASE_DIR is a plain str from os.path.abspath

DB_PATH: Path = Path(BASE_DIR) / "users.db"


def _get_connection() -> sqlite3.Connection:
    """Return a sqlite3 connection with row_factory set to dict-like rows."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create the users and documents tables if they do not already exist."""
    conn = _get_connection()
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id              TEXT PRIMARY KEY,
                name            TEXT NOT NULL,
                email           TEXT UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL,
                created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS documents (
                id          TEXT PRIMARY KEY,
                user_id     TEXT NOT NULL,
                filename    TEXT NOT NULL,
                file_path   TEXT NOT NULL,
                file_hash   TEXT NOT NULL,
                chunk_count INTEGER NOT NULL,
                uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
        """)
        conn.commit()
    finally:
        conn.close()


def get_user_by_email(email: str) -> dict | None:
    """Return a user row as a dict, or None if not found."""
    conn = _get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def insert_document(
    user_id: str,
    filename: str,
    file_path: str,
    file_hash: str,
    chunk_count: int,
) -> str:
    """Insert a document record and return the new UUID."""
    doc_id = str(uuid.uuid4())
    conn = _get_connection()
    try:
        conn.execute(
            """
            INSERT INTO documents (id, user_id, filename, file_path, file_hash, chunk_count)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (doc_id, user_id, filename, file_path, file_hash, chunk_count),
        )
        conn.commit()
    finally:
        conn.close()
    return doc_id


def get_user_documents(user_id: str) -> list[dict]:
    """Return all document records for a given user."""
    conn = _get_connection()
    try:
        rows = conn.execute(
            """
            SELECT id, filename, chunk_count, uploaded_at
            FROM documents
            WHERE user_id = ?
            ORDER BY uploaded_at DESC
            """,
            (user_id,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_document_by_id(document_id: str) -> dict | None:
    """Return a single document record by UUID, or None if not found."""
    conn = _get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM documents WHERE id = ?", (document_id,)
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def delete_document_by_id(document_id: str) -> None:
    """Delete a document record by UUID."""
    conn = _get_connection()
    try:
        conn.execute("DELETE FROM documents WHERE id = ?", (document_id,))
        conn.commit()
    finally:
        conn.close()


def document_exists_by_hash(user_id: str, file_hash: str) -> bool:
    """Return True if this user already has a document with the given SHA-256 hash."""
    conn = _get_connection()
    try:
        row = conn.execute(
            "SELECT id FROM documents WHERE user_id = ? AND file_hash = ?",
            (user_id, file_hash),
        ).fetchone()
        return row is not None
    finally:
        conn.close()


def delete_user_documents(user_id: str) -> None:
    """Delete all document records belonging to a user."""
    conn = _get_connection()
    try:
        conn.execute("DELETE FROM documents WHERE user_id = ?", (user_id,))
        conn.commit()
    finally:
        conn.close()
