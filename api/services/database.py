"""
MongoDB connection manager.

If MONGODB_URI is set (production / Atlas), it connects there.
Otherwise it falls back to a local MongoDB instance so local development
with `docker compose up` still works without any extra config.
"""

from __future__ import annotations

import logging
from typing import Optional

from pymongo import MongoClient
from pymongo.database import Database
from pymongo.errors import ConnectionFailure

from ..config import settings

logger = logging.getLogger("database")

_client: Optional[MongoClient] = None
_db: Optional[Database] = None

DB_NAME = "tunitech"


def get_db() -> Database:
    """Return the shared MongoDB database, initialising the client on first call."""
    global _client, _db
    if _db is not None:
        return _db

    uri = settings.mongodb_uri or "mongodb://localhost:27017"
    try:
        _client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        # Ping to verify the connection is alive
        _client.admin.command("ping")
        _db = _client[DB_NAME]
        logger.info("[OK] MongoDB connected → %s", DB_NAME)
        _ensure_indexes(_db)
    except ConnectionFailure as exc:
        logger.error("MongoDB connection FAILED: %s", exc)
        raise RuntimeError(
            "Cannot reach MongoDB. Set MONGODB_URI in your environment or "
            "start a local MongoDB instance."
        ) from exc

    return _db


def _ensure_indexes(db: Database) -> None:
    """Create indexes once on startup – safe to call multiple times (idempotent)."""
    # users
    db.users.create_index("username", unique=True)
    db.users.create_index("email", unique=True)

    # reviews: one review per user per phone
    db.reviews.create_index([("phone_name", 1), ("username", 1)], unique=True)
    db.reviews.create_index("phone_name")

    # trending
    db.trending.create_index("phone_name", unique=True)

    # price_history
    db.price_history.create_index([("phone_name", 1), ("store", 1)], unique=True)

    logger.info("[OK] MongoDB indexes ensured")
