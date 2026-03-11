"""
routers/auth.py — Authentication endpoint.

POST /auth/login accepts email + password, validates against the users table,
and returns a signed JWT access token.

Note: We use the bcrypt library directly rather than passlib.CryptContext
because passlib 1.7.4 is incompatible with bcrypt >= 4.0 (missing __about__
attribute). bcrypt >= 4.0 is already present in the venv (pulled in by
chromadb), so we call it directly to avoid downgrading.
"""

import bcrypt

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from core.database import get_user_by_email
from core.security import create_access_token

router = APIRouter()


def _verify_password(plain: str, hashed: str) -> bool:
    """Verify a bcrypt-hashed password."""
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/auth/login")
def login(request: LoginRequest):
    """Authenticate a user and return a JWT access token."""
    user = get_user_by_email(request.email)
    if not user or not _verify_password(request.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    token = create_access_token({
        "user_id": user["id"],
        "email": user["email"],
        "name": user["name"],
    })
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_name": user["name"],
    }
