from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple

import bcrypt
import jwt
from fastapi import Request

JWT_SECRET = os.getenv("JWT_SECRET", "fallback-secret-key")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

logger = logging.getLogger(__name__)


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def generate_token(
    user_id: int,
    username: str,
    role: str = "user",
    organization_id: Optional[int] = None,
    expires_in_seconds: int = 7 * 24 * 60 * 60,
) -> str:
    now = datetime.utcnow()
    payload = {
        "userId": user_id,
        "username": username,
        "role": role,
        "organizationId": organization_id,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=expires_in_seconds)).timestamp()),
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token if isinstance(token, str) else token.decode("utf-8")


def authenticate_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        decoded = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return {
            "userId": decoded.get("userId"),
            "username": decoded.get("username"),
            "role": decoded.get("role", "user"),
            "organizationId": decoded.get("organizationId"),
        }
    except jwt.PyJWTError as exc:  # pragma: no cover - logging only
        logger.debug("Token verification failed: %s", exc)
        return None


def extract_token_from_header(header: Optional[str]) -> Optional[str]:
    if not header or not header.startswith("Bearer "):
        return None
    return header[7:]


async def get_session(request: Request) -> Dict[str, Optional[Dict[str, Any]]]:
    try:
        token = request.cookies.get("authToken")
    except Exception as exc:  # pragma: no cover - FastAPI always provides cookies
        logger.debug("Auth Debug - failed to read cookies: %s", exc)
        token = None

    if not token:
        auth_header = request.headers.get("Authorization")
        token = extract_token_from_header(auth_header)

    if not token:
        logger.debug("Auth Debug - authToken missing on request")
        return {"user": None}

    decoded = authenticate_token(token)
    if not decoded:
        return {"user": None}

    logger.debug("Auth Debug - token decoded for user: %s", decoded.get("userId"))
    return {
        "user": {
            "userId": decoded.get("userId"),
            "username": decoded.get("username"),
            "role": decoded.get("role", "user"),
            "organizationId": decoded.get("organizationId"),
        }
    }


async def verify_admin(request: Request) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    token = extract_token_from_header(request.headers.get("Authorization"))
    if not token:
        return None, "توکن احراز هویت ارسال نشده است"

    decoded = authenticate_token(token)
    if not decoded or decoded.get("role") != "admin":
        return None, "دسترسی غیرمجاز. شما ادمین نیستید."

    return decoded, None
