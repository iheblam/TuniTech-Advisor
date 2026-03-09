"""
MongoDB Seed Script
───────────────────
Run this ONCE after creating your Atlas cluster to migrate existing
JSON data into MongoDB.

Usage:
    # From the project root (with venv active):
    python scripts/seed_mongodb.py

    # Or with a specific URI:
    MONGODB_URI="mongodb+srv://..." python scripts/seed_mongodb.py

What it does:
    - Loads data/users.json        → users collection
    - Loads data/reviews.json      → reviews collection
    - Loads data/trending.json     → trending collection
    - Loads data/price_history.json → price_history collection

Records that already exist (same username / phone_name) are skipped
(upsert with no overwrite), so it is safe to run multiple times.
"""

import json
import os
import sys
from pathlib import Path

# ── Allow running from project root without installing the package ─────────────
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# Set a default URI so the script works even without a .env file
# Override by setting MONGODB_URI in the environment before running.
if not os.getenv("MONGODB_URI"):
    print("[INFO] MONGODB_URI not set – connecting to localhost:27017")

from api.config import settings  # noqa: E402 (needs sys.path first)
from api.services.database import get_db  # noqa: E402

DATA_DIR = ROOT / "data"


def seed_users(db) -> None:
    path = DATA_DIR / "users.json"
    if not path.exists():
        print("[SKIP] data/users.json not found")
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    users = data.get("users", [])
    inserted = 0
    for user in users:
        result = db.users.update_one(
            {"username": user["username"]},
            {"$setOnInsert": user},
            upsert=True,
        )
        if result.upserted_id:
            inserted += 1
    print(f"[OK] users: {inserted} inserted, {len(users) - inserted} already existed")


def seed_reviews(db) -> None:
    path = DATA_DIR / "reviews.json"
    if not path.exists():
        print("[SKIP] data/reviews.json not found")
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    # Format: { "phone_name": [ {review}, ... ], ... }
    inserted = 0
    for phone_name, reviews in data.items():
        for review in reviews:
            doc = {"phone_name": phone_name, **review}
            result = db.reviews.update_one(
                {"phone_name": phone_name, "username": review["username"]},
                {"$setOnInsert": doc},
                upsert=True,
            )
            if result.upserted_id:
                inserted += 1
    print(f"[OK] reviews: {inserted} inserted")


def seed_trending(db) -> None:
    path = DATA_DIR / "trending.json"
    if not path.exists():
        print("[SKIP] data/trending.json not found")
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    # Format: { "phone_name": { views, searches, score, last_seen }, ... }
    inserted = 0
    for phone_name, stats in data.items():
        doc = {"phone_name": phone_name, **stats}
        result = db.trending.update_one(
            {"phone_name": phone_name},
            {"$setOnInsert": doc},
            upsert=True,
        )
        if result.upserted_id:
            inserted += 1
    print(f"[OK] trending: {inserted} inserted")


def seed_price_history(db) -> None:
    path = DATA_DIR / "price_history.json"
    if not path.exists():
        print("[SKIP] data/price_history.json not found")
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    # Format: { "phone_name||store": [ {date, price}, ... ], ... }
    inserted = 0
    for key, history in data.items():
        if "||" not in key:
            continue
        phone_name, store = key.split("||", 1)
        result = db.price_history.update_one(
            {"phone_name": phone_name, "store": store},
            {"$setOnInsert": {"phone_name": phone_name, "store": store, "history": history}},
            upsert=True,
        )
        if result.upserted_id:
            inserted += 1
    print(f"[OK] price_history: {inserted} inserted")


if __name__ == "__main__":
    print("=" * 50)
    print("TuniTech Advisor – MongoDB Seed Script")
    print("=" * 50)

    db = get_db()
    print(f"[OK] Connected to MongoDB → database: tunitech\n")

    seed_users(db)
    seed_reviews(db)
    seed_trending(db)
    seed_price_history(db)

    print("\n[DONE] Seeding complete.")
    print("You can now deploy your app and all existing data will be available.")
