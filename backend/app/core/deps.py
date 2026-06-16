from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.roles import Role
from app.core.security import decode_token


security = HTTPBearer(auto_error=False)


@dataclass
class CurrentUser:
    id: str
    email: str
    role: Role


def _role_from_payload(payload: dict[str, Any]) -> Role:
    raw = payload.get("role", Role.USER.value)
    try:
        return Role(raw)
    except ValueError:
        return Role.USER


def get_current_user(creds: HTTPAuthorizationCredentials | None = Depends(security)) -> CurrentUser:
    if not creds:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Authorization header")

    try:
        payload: dict[str, Any] = decode_token(creds.credentials)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject")

    return CurrentUser(
        id=str(user_id),
        email=str(payload.get("email", "")),
        role=_role_from_payload(payload),
    )


def get_current_user_id(user: CurrentUser = Depends(get_current_user)) -> str:
    return user.id


def require_admin(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    if user.role != Role.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return user
