import uuid
import bcrypt

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr

from core.database import get_user_by_email, _get_connection
from core.security import create_access_token

router = APIRouter()


# -----------------------------
# Helpers
# -----------------------------
def _verify_password(plain: str, hashed: str) -> bool:
    """Verifica uma senha hashada com bcrypt."""
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def _hash_password(plain: str) -> str:
    """Gera hash bcrypt de uma senha em texto plano."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(plain.encode("utf-8"), salt).decode("utf-8")


# -----------------------------
# Request models
# -----------------------------
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    new_password: str


# -----------------------------
# Routes
# -----------------------------
@router.post("/auth/login")
def login(request: LoginRequest):
    """Autentica o usuário e retorna um JWT."""
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


@router.post("/auth/register")
def register(request: RegisterRequest):
    """Registra um novo usuário no banco de dados."""
    existing_user = get_user_by_email(request.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists.",
        )

    user_id = str(uuid.uuid4())
    hashed_password = _hash_password(request.password)

    conn = _get_connection()
    try:
        conn.execute(
            "INSERT INTO users (id, name, email, hashed_password) VALUES (?, ?, ?, ?)",
            (user_id, request.name, request.email, hashed_password),
        )
        conn.commit()
    finally:
        conn.close()

    return {"message": "User created successfully", "user_id": user_id}


@router.post("/auth/reset-password")
def reset_password(request: ResetPasswordRequest):
    """Altera a senha de um usuário baseado no email."""
    user = get_user_by_email(request.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    hashed_password = _hash_password(request.new_password)

    conn = _get_connection()
    try:
        conn.execute(
            "UPDATE users SET hashed_password = ? WHERE email = ?",
            (hashed_password, request.email),
        )
        conn.commit()
    finally:
        conn.close()

    return {"message": "Password updated successfully"}