"""
core/security.py — JWT creation, decoding, and FastAPI dependency for auth.

SECRET_KEY can be overridden via the JWT_SECRET environment variable.
Tokens expire after ACCESS_TOKEN_EXPIRE_HOURS hours.
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Annotated

from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

SECRET_KEY: str = os.environ.get("JWT_SECRET", "mro-assistant-dev-secret-2025")
ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS: int = 8

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def create_access_token(data: dict) -> str:
    """Encode a JWT containing *data* with an expiry timestamp."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    """Decode and validate a JWT. Raises HTTP 401 on failure."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> dict:
    """FastAPI dependency — extracts and returns the authenticated user payload."""
    return decode_token(token)
