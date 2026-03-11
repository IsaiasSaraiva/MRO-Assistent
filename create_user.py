#!/usr/bin/env python3
"""
create_user.py — Provisions the 5 MRO Assistant users.

Run from drive/:
    python create_user.py

Uses bcrypt directly (passlib 1.7.4 is incompatible with bcrypt >= 4.0 which
is already present in the venv as a chromadb dependency).
"""

import sqlite3
import uuid
from pathlib import Path
import bcrypt
import sys

sys.path.insert(0, str(Path(__file__).parent))
from core.database import init_db, DB_PATH

USERS = [
    {"name": "Andre",  "email": "andre.silva@mroassist.dev",     "password": "Mro@Andre2025"},
    {"name": "Fabio",  "email": "fabio.costa@mroassist.dev",     "password": "Mro@Fabio2025"},
    {"name": "Rafael", "email": "rafael.mendes@mroassist.dev",   "password": "Mro@Rafael2025"},
    {"name": "Marcos", "email": "marcos.lima@mroassist.dev",     "password": "Mro@Marcos2025"},
    {"name": "Isaias", "email": "isaias.ferreira@mroassist.dev", "password": "Mro@Isaias2025"},
]


def _hash_password(plain: str) -> str:
    """Hash a plaintext password with bcrypt and return the hash as a string."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(plain.encode("utf-8"), salt).decode("utf-8")


def main() -> None:
    init_db()
    conn = sqlite3.connect(str(DB_PATH))
    print("Creating users...")
    for u in USERS:
        uid = str(uuid.uuid4())
        hashed = _hash_password(u["password"])
        try:
            conn.execute(
                "INSERT INTO users (id, name, email, hashed_password) VALUES (?, ?, ?, ?)",
                (uid, u["name"], u["email"], hashed),
            )
            conn.commit()
            print(f"  Created: {u['email']}")
        except sqlite3.IntegrityError:
            print(f"  Skipped (exists): {u['email']}")
    conn.close()
    print("Done.")


if __name__ == "__main__":
    main()
