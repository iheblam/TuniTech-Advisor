"""
Community endpoints – reviews, trending, price history.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional

from ..services import community_service
from ..services.auth_service import get_current_user

router = APIRouter(prefix="/community", tags=["Community"])


# ─── Reviews ─────────────────────────────────────────────────────────────────

class ReviewIn(BaseModel):
    rating: int   # 1–5
    comment: str = ""


@router.get("/reviews/{phone_name:path}")
def get_reviews(phone_name: str):
    reviews = community_service.get_reviews(phone_name)
    stats   = community_service.get_review_stats(phone_name)
    return {"phone_name": phone_name, "stats": stats, "reviews": reviews}


@router.post("/reviews/{phone_name:path}")
def add_review(
    phone_name: str,
    body: ReviewIn,
    current_user: dict = Depends(get_current_user),
):
    if not 1 <= body.rating <= 5:
        raise HTTPException(status_code=422, detail="Rating must be between 1 and 5")
    review = community_service.add_review(
        phone_name, current_user["username"], body.rating, body.comment
    )
    return review


@router.delete("/reviews/{phone_name:path}")
def delete_review(
    phone_name: str,
    review_id: str = Query(..., description="Review ID to delete"),
    current_user: dict = Depends(get_current_user),
):
    ok = community_service.delete_review(phone_name, review_id, current_user["username"])
    if not ok:
        raise HTTPException(status_code=404, detail="Review not found or not yours")
    return {"deleted": True}


# ─── Trending ─────────────────────────────────────────────────────────────────

class TrackIn(BaseModel):
    event_type: str = "view"   # "view" | "search"


@router.post("/track/{phone_name:path}")
def track_event(phone_name: str, body: TrackIn):
    community_service.track_event(phone_name, body.event_type)
    return {"ok": True}


@router.get("/trending")
def get_trending(limit: int = 12):
    return {"trending": community_service.get_trending(limit)}


# ─── Price History ──────────────────────────────────────────────────────────

@router.get("/price-history/{phone_name:path}")
def get_price_history(phone_name: str, store: Optional[str] = None):
    history = community_service.get_price_history(phone_name, store)
    return {"phone_name": phone_name, "store": store or "all", "history": history}
