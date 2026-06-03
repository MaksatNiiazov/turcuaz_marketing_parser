from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Annotated, Any

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.core.auth import get_identity_claims
from app.core.config import settings
from app.modules.market_parser.permissions import MARKET_PARSER_PERMISSIONS

router = APIRouter()


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/dev-admin-login", response_model=TokenResponse)
def dev_admin_login(payload: LoginRequest) -> TokenResponse:
    if not settings.dev_admin_login_enabled:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    if (
        payload.email.strip().casefold() != settings.dev_admin_email.casefold()
        or payload.password != settings.dev_admin_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    claims = _admin_claims()
    token = jwt.encode(claims, settings.identity_secret_key, algorithm=settings.identity_algorithm)
    return TokenResponse(access_token=token)


@router.get("/me")
def me(claims: Annotated[dict[str, Any], Depends(get_identity_claims)]) -> dict[str, Any]:
    return _current_user_from_claims(claims)


def _admin_claims() -> dict[str, Any]:
    expires_at = datetime.now(timezone.utc) + timedelta(hours=12)
    return {
        "sub": "market-parser-dev-admin",
        "id": 0,
        "email": settings.dev_admin_email,
        "full_name": settings.dev_admin_full_name,
        "roles": ["market_parser_manager"],
        "permissions": MARKET_PARSER_PERMISSIONS,
        "active": True,
        "branch_id": None,
        "active_branch_id": None,
        "branch_code": None,
        "branch_name": None,
        "branch": None,
        "branches": [],
        "branch_permissions": {},
        "branch_permissions_by_id": {},
        "department": None,
        "exp": expires_at,
    }


def _current_user_from_claims(claims: dict[str, Any]) -> dict[str, Any]:
    branch = claims.get("branch") if isinstance(claims.get("branch"), dict) else None
    return {
        "id": _int_claim(claims.get("id")) or 0,
        "active": bool(claims.get("active", True)),
        "email": str(claims.get("email") or claims.get("sub") or "admin@example.com"),
        "full_name": str(claims.get("full_name") or claims.get("email") or "Admin"),
        "branch_id": _int_claim(claims.get("branch_id"))
        or _int_claim(branch.get("id") if branch else None),
        "active_branch_id": _int_claim(claims.get("active_branch_id")),
        "branch_code": _string_claim(
            claims.get("branch_code") or (branch.get("code") if branch else None)
        ),
        "branch_name": _string_claim(
            claims.get("branch_name") or (branch.get("name") if branch else None)
        ),
        "branch": branch,
        "roles": _string_list_claim(claims.get("roles")),
        "permissions": _string_list_claim(claims.get("permissions")),
        "branches": _string_list_claim(claims.get("branches")),
        "branch_permissions": _permissions_map_claim(claims.get("branch_permissions")),
        "branch_permissions_by_id": _permissions_map_claim(claims.get("branch_permissions_by_id")),
        "department": _string_claim(claims.get("department")),
    }


def _int_claim(value: object) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.strip().isdigit():
        return int(value.strip())
    return None


def _string_claim(value: object) -> str | None:
    return value.strip() if isinstance(value, str) and value.strip() else None


def _string_list_claim(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def _permissions_map_claim(value: object) -> dict[str, list[str]]:
    if not isinstance(value, dict):
        return {}
    result: dict[str, list[str]] = {}
    for key, items in value.items():
        if isinstance(key, str):
            result[key] = _string_list_claim(items)
    return result
