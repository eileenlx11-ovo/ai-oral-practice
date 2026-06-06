"""
Lightweight JWT authentication for AI Oral Practice.
Simplified from talent-agent auth — email/password with PBKDF2 + HS256 JWT.
No email verification or password reset (MVP for contest demo).
"""
import hashlib
import hmac
import json
import os
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, Request

JWT_ALG = "HS256"
JWT_TTL_DAYS = 30
JWT_SECRET = os.getenv("JWT_SECRET", "oral-practice-dev-secret-change-in-prod")

# File-based user storage (MVP — no DB dependency)
USERS_DIR = Path(__file__).parent / "data" / "users"
USERS_DIR.mkdir(parents=True, exist_ok=True)


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 200_000)
    return salt.hex() + ":" + dk.hex()


def verify_password(password: str, stored: str) -> bool:
    try:
        salt_hex, dk_hex = stored.split(":", 1)
        salt = bytes.fromhex(salt_hex)
        dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 200_000)
        return hmac.compare_digest(dk.hex(), dk_hex)
    except (ValueError, TypeError):
        return False


def issue_jwt(user_id: str) -> str:
    payload = {
        "sub": user_id,
        "exp": datetime.now(UTC) + timedelta(days=JWT_TTL_DAYS),
        "iat": datetime.now(UTC),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)


def decode_jwt(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])


# --- User CRUD (file-based) ---

def _user_path(email: str) -> Path:
    """Safe filename from email."""
    safe = email.lower().replace("@", "_at_").replace(".", "_")
    return USERS_DIR / f"{safe}.json"


def get_user_by_email(email: str) -> Optional[dict]:
    path = _user_path(email)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def create_user(email: str, password: str, nickname: str = "") -> dict:
    """Create a new user. Raises ValueError if email already taken."""
    if get_user_by_email(email):
        raise ValueError("email_taken")
    user = {
        "id": email.lower(),
        "email": email.lower(),
        "nickname": nickname or email.split("@")[0],
        "password_hash": hash_password(password),
        "created_at": datetime.now(UTC).isoformat(),
    }
    _user_path(email).write_text(
        json.dumps(user, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return user


# --- FastAPI dependencies ---

def _extract_token(request: Request) -> Optional[str]:
    """Extract Bearer token from Authorization header."""
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return auth[7:]
    return None


async def get_current_user(request: Request) -> dict:
    """Dependency: require authenticated user."""
    token = _extract_token(request)
    if not token:
        raise HTTPException(401, "Not authenticated")
    try:
        payload = decode_jwt(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Invalid token")

    user = get_user_by_email(payload["sub"])
    if not user:
        raise HTTPException(401, "User not found")
    return user


async def get_optional_user(request: Request) -> Optional[dict]:
    """Dependency: return user if authenticated, None otherwise."""
    token = _extract_token(request)
    if not token:
        return None
    try:
        payload = decode_jwt(token)
        return get_user_by_email(payload["sub"])
    except (jwt.InvalidTokenError, KeyError):
        return None
