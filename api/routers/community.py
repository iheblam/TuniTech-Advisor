"""
Community endpoints – reviews, trending, price history.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional

from ..services import community_service
from ..services.auth_service import get_current_user
from ..config import settings

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


# ─── Phone Identification (Groq proxy) ───────────────────────────────────────

class IdentifyPhoneIn(BaseModel):
    query: str


@router.post("/identify-phone")
def identify_phone(
    body: IdentifyPhoneIn,
    current_user: dict = Depends(get_current_user),
):
    """Use Groq to identify a phone from a partial / messy name."""
    if len(body.query.strip()) < 3:
        raise HTTPException(status_code=422, detail="Query too short")
    if not settings.groq_api_key:
        raise HTTPException(status_code=503, detail="Groq API key not configured")

    try:
        from groq import Groq
        client = Groq(api_key=settings.groq_api_key)
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            temperature=0.1,
            max_tokens=60,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a smartphone identifier. Given a partial or messy phone name, "
                        "output ONLY a JSON object with keys \"model\" (full official model name), "
                        "\"brand\" (manufacturer), \"confidence\" (high/medium/low). "
                        "No commentary, only valid JSON."
                    ),
                },
                {"role": "user", "content": f'Identify this phone: "{body.query}"'},
            ],
        )
        text = completion.choices[0].message.content or ""
        import re, json
        match = re.search(r"\{[\s\S]*\}", text)
        if not match:
            raise HTTPException(status_code=422, detail="Could not parse Groq response")
        result = json.loads(match.group())
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Groq error: {str(e)}")


# ─── Detailed user phone review ───────────────────────────────────────────────

class DetailedReviewIn(BaseModel):
    phone_name: str
    years_owned: Optional[str] = None
    performance: int    # 1–5
    battery: int        # 1–5
    camera: int         # 1–5
    durability: int     # 1–5
    review: Optional[str] = ""


@router.post("/user-phone-review")
def submit_user_phone_review(
    body: DetailedReviewIn,
    current_user: dict = Depends(get_current_user),
):
    """Submit a detailed personal phone review."""
    for field in ("performance", "battery", "camera", "durability"):
        val = getattr(body, field)
        if not 1 <= val <= 5:
            raise HTTPException(status_code=422, detail=f"{field} must be 1–5")

    avg_rating = round((body.performance + body.battery + body.camera + body.durability) / 4)
    comment_parts = []
    if body.years_owned:
        comment_parts.append(f"Owned: {body.years_owned}")
    comment_parts += [
        f"Performance: {body.performance}/5",
        f"Battery: {body.battery}/5",
        f"Camera: {body.camera}/5",
        f"Durability: {body.durability}/5",
    ]
    if body.review:
        comment_parts.append(body.review.strip())

    review = community_service.add_review(
        body.phone_name,
        current_user["username"],
        avg_rating,
        " | ".join(comment_parts),
    )
    return review
