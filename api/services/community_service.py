"""
Community Service – reviews, trending, price history.
All data stored in MongoDB (collections: reviews, trending, price_history).
"""

import uuid
from datetime import datetime, timezone
from typing import Optional

from pymongo import ReturnDocument

from .database import get_db


# ── Reviews ───────────────────────────────────────────────────────────────────

def get_reviews(phone_name: str) -> list[dict]:
    docs = get_db().reviews.find(
        {"phone_name": phone_name},
        {"_id": 0, "phone_name": 0},
    )
    return list(docs)


def get_review_stats(phone_name: str) -> dict:
    reviews = get_reviews(phone_name)
    if not reviews:
        return {"count": 0, "avg_rating": None}
    ratings = [r["rating"] for r in reviews]
    return {"count": len(ratings), "avg_rating": round(sum(ratings) / len(ratings), 1)}


def add_review(phone_name: str, username: str, rating: int, comment: str) -> dict:
    if not 1 <= rating <= 5:
        raise ValueError("Rating must be 1–5")
    review = {
        "phone_name": phone_name,
        "id": str(uuid.uuid4()),
        "username": username,
        "rating": rating,
        "comment": comment.strip(),
        "date": datetime.now(timezone.utc).isoformat(),
    }
    # Upsert: one review per user per phone
    get_db().reviews.find_one_and_replace(
        {"phone_name": phone_name, "username": username},
        review,
        upsert=True,
    )
    return {k: v for k, v in review.items() if k != "phone_name"}


def delete_review(phone_name: str, review_id: str, username: str) -> bool:
    result = get_db().reviews.delete_one(
        {"phone_name": phone_name, "id": review_id, "username": username}
    )
    return result.deleted_count > 0


# ── Trending ──────────────────────────────────────────────────────────────────

def track_event(phone_name: str, event_type: str = "view") -> None:
    """event_type: 'view' | 'search'"""
    inc = {"searches": 1} if event_type == "search" else {"views": 1}
    # We'll recalculate score after the update
    get_db().trending.update_one(
        {"phone_name": phone_name},
        {
            "$inc": inc,
            "$set": {"last_seen": datetime.now(timezone.utc).isoformat()},
            "$setOnInsert": {"views": 0, "searches": 0},
        },
        upsert=True,
    )
    # Recalculate score: views + searches * 3
    doc = get_db().trending.find_one({"phone_name": phone_name})
    if doc:
        score = doc.get("views", 0) + doc.get("searches", 0) * 3
        get_db().trending.update_one(
            {"phone_name": phone_name},
            {"$set": {"score": score}},
        )


def get_trending(limit: int = 10) -> list[dict]:
    docs = get_db().trending.find(
        {},
        {"_id": 0},
        sort=[("score", -1)],
        limit=limit,
    )
    return list(docs)


# ── Price History ─────────────────────────────────────────────────────────────

def snapshot_prices(phones: list[dict]) -> int:
    """
    Called by the scheduler after each scrape.
    phones: list of dicts with 'name', 'price', 'source' keys.
    """
    today = datetime.now(timezone.utc).date().isoformat()
    db = get_db()
    count = 0
    for p in phones:
        name  = str(p.get("name", "")).strip()
        store = str(p.get("source", p.get("store", ""))).strip()
        price = p.get("price")
        if not name or price is None:
            continue

        doc = db.price_history.find_one({"phone_name": name, "store": store}) or {}
        history = doc.get("history", [])

        if history and history[-1].get("date") == today:
            history[-1]["price"] = price
        else:
            history.append({"date": today, "price": price})

        history = history[-90:]  # keep 90-day window

        db.price_history.update_one(
            {"phone_name": name, "store": store},
            {"$set": {"history": history}},
            upsert=True,
        )
        count += 1
    return count


def get_price_history(phone_name: str, store: Optional[str] = None) -> list[dict]:
    db = get_db()
    if store:
        doc = db.price_history.find_one({"phone_name": phone_name, "store": store})
        return doc.get("history", []) if doc else []

    # All stores
    docs = db.price_history.find({"phone_name": phone_name}, {"_id": 0})
    results = []
    for doc in docs:
        s = doc.get("store", "")
        for pt in doc.get("history", []):
            results.append({"date": pt["date"], "price": pt["price"], "store": s})
    results.sort(key=lambda x: x["date"])
    return results
