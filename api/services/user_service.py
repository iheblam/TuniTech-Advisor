"""
User Service – register / authenticate normal users.
Users are stored in a JSON file (./users.json) for simplicity.
"""

import json
import os
import uuid
from datetime import datetime, timezone
from typing import Optional

from passlib.context import CryptContext

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

_USERS_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "users.json")

# Fields that must never be overwritten via update_user
_IMMUTABLE = {"id", "username", "hashed_password", "created_at"}


# ── helpers ──────────────────────────────────────────────────────────────────

def _load() -> list[dict]:
    if not os.path.exists(_USERS_FILE):
        return []
    with open(_USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f).get("users", [])


def _save(users: list[dict]) -> None:
    with open(_USERS_FILE, "w", encoding="utf-8") as f:
        json.dump({"users": users}, f, indent=2, default=str)


def _public(user: dict) -> dict:
    """Strip hashed_password from a user dict."""
    return {k: v for k, v in user.items() if k != "hashed_password"}


# ── public API ────────────────────────────────────────────────────────────────

def get_by_username(username: str) -> Optional[dict]:
    return next((u for u in _load() if u["username"].lower() == username.lower()), None)


def get_by_email(email: str) -> Optional[dict]:
    return next((u for u in _load() if u["email"].lower() == email.lower()), None)


def create_user(
    username: str,
    email: str,
    password: str,
    age: Optional[int] = None,
    occupation: Optional[str] = None,
    avatar: Optional[str] = None,
    favourite_brand: Optional[str] = None,
    current_phone: Optional[str] = None,
    join_reason: Optional[str] = None,
) -> dict:
    """Create and persist a new user. Returns the public user dict (no hash)."""
    users = _load()
    user = {
        "id": str(uuid.uuid4()),
        "username": username,
        "email": email,
        "hashed_password": _pwd_context.hash(password),
        "age": age,
        "occupation": occupation,
        "avatar": avatar,
        "favourite_brand": favourite_brand,
        "current_phone": current_phone,
        "join_reason": join_reason,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    users.append(user)
    _save(users)
    return _public(user)


def update_user(username: str, updates: dict) -> Optional[dict]:
    """Update mutable profile fields for an existing user."""
    users = _load()
    for i, u in enumerate(users):
        if u["username"].lower() == username.lower():
            for key, value in updates.items():
                if key not in _IMMUTABLE:
                    users[i][key] = value
            _save(users)
            return _public(users[i])
    return None


def update_password(username: str, new_password: str) -> bool:
    """Hash and persist a new password for an existing user."""
    users = _load()
    for i, u in enumerate(users):
        if u["username"].lower() == username.lower():
            users[i]["hashed_password"] = _pwd_context.hash(new_password)
            _save(users)
            return True
    return False


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plain password against its bcrypt hash."""
    return _pwd_context.verify(plain, hashed)


def authenticate_user(username: str, password: str) -> Optional[dict]:
    """Return public user dict on success, None on failure."""
    user = get_by_username(username)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return _public(user)
