"""
User Service – register / authenticate normal users.
Users are stored in MongoDB (collection: users).
"""

import uuid
from datetime import datetime, timezone
from typing import Optional

from passlib.context import CryptContext

from .database import get_db

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Fields that must never be overwritten via update_user
_IMMUTABLE = {"id", "username", "hashed_password", "created_at"}


def _public(user: dict) -> dict:
    """Strip hashed_password and MongoDB _id from a user dict."""
    return {k: v for k, v in user.items() if k not in ("hashed_password", "_id")}


# ── public API ────────────────────────────────────────────────────────────────

def get_by_username(username: str) -> Optional[dict]:
    doc = get_db().users.find_one({"username": {"$regex": f"^{username}$", "$options": "i"}})
    return doc if doc else None


def get_by_email(email: str) -> Optional[dict]:
    doc = get_db().users.find_one({"email": {"$regex": f"^{email}$", "$options": "i"}})
    return doc if doc else None


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
    get_db().users.insert_one(user)
    return _public(user)


def update_user(username: str, updates: dict) -> Optional[dict]:
    """Update mutable profile fields for an existing user."""
    safe_updates = {k: v for k, v in updates.items() if k not in _IMMUTABLE}
    if not safe_updates:
        doc = get_by_username(username)
        return _public(doc) if doc else None
    result = get_db().users.find_one_and_update(
        {"username": {"$regex": f"^{username}$", "$options": "i"}},
        {"$set": safe_updates},
        return_document=True,
    )
    return _public(result) if result else None


def update_password(username: str, new_password: str) -> bool:
    """Hash and persist a new password for an existing user."""
    result = get_db().users.update_one(
        {"username": {"$regex": f"^{username}$", "$options": "i"}},
        {"$set": {"hashed_password": _pwd_context.hash(new_password)}},
    )
    return result.modified_count > 0


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
