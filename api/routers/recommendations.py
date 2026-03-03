"""
Smartphone recommendation endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import pandas as pd
import asyncio
from concurrent.futures import ThreadPoolExecutor
import requests as http_requests
from bs4 import BeautifulSoup

from ..models.schemas import (
    RecommendationRequest,
    RecommendationResponse,
    SmartphoneDetail
)
from ..services.data_service import data_service
from ..config import settings

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.post("/", response_model=RecommendationResponse)
async def get_recommendations(request: RecommendationRequest):
    """
    Get smartphone recommendations based on user criteria
    
    This endpoint filters and returns smartphones that match
    the user's budget and specification requirements.
    """
    if not data_service.is_data_loaded():
        raise HTTPException(
            status_code=503,
            detail="Smartphone data is not loaded."
        )
    
    try:
        # Get recommendations
        recommendations = data_service.get_recommendations(
            budget_min=request.budget_min,
            budget_max=request.budget_max,
            min_ram=request.min_ram,
            min_storage=request.min_storage,
            min_battery=request.min_battery,
            min_camera=request.min_camera,
            brand=request.brand,
            requires_5g=request.requires_5g,
            limit=request.limit
        )
        
        # Convert to SmartphoneDetail objects
        smartphone_details = []
        for rec in recommendations:
            # Map data fields to SmartphoneDetail schema
            detail = SmartphoneDetail(
                name=rec.get('name', 'Unknown'),
                brand=rec.get('brand', 'Unknown'),
                price=rec.get('price', 0),
                store=rec.get('store', 'Unknown'),
                url=rec.get('url'),
                ram=rec.get('ram'),
                storage=rec.get('storage'),
                battery=rec.get('battery'),
                screen_size=rec.get('screen_size'),
                main_camera=rec.get('main_camera'),
                front_camera=rec.get('front_camera'),
                processor=rec.get('processor'),
                is_5g=rec.get('is_5g'),
                has_nfc=rec.get('has_nfc'),
                availability=rec.get('availability', 'In Stock'),
                match_score=rec.get('match_score')
            )
            smartphone_details.append(detail)
        
        # Prepare filters applied
        filters_applied = {
            "budget_min": request.budget_min,
            "budget_max": request.budget_max
        }
        if request.min_ram:
            filters_applied["min_ram"] = request.min_ram
        if request.min_storage:
            filters_applied["min_storage"] = request.min_storage
        if request.min_battery:
            filters_applied["min_battery"] = request.min_battery
        if request.min_camera:
            filters_applied["min_camera"] = request.min_camera
        if request.brand:
            filters_applied["brand"] = request.brand
        if request.requires_5g is not None:
            filters_applied["requires_5g"] = request.requires_5g
        
        return RecommendationResponse(
            total_found=len(smartphone_details),
            recommendations=smartphone_details,
            filters_applied=filters_applied
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting recommendations: {str(e)}"
        )


@router.get("/search")
async def search_smartphones(
    query: str = Query(..., description="Search query (name or brand)"),
    min_price: Optional[float] = Query(None, description="Minimum price"),
    max_price: Optional[float] = Query(None, description="Maximum price"),
    limit: int = Query(50, ge=1, le=200, description="Maximum results"),
    store: Optional[str] = Query(None, description="Filter by store name")
):
    """
    Search for smartphones by name or brand
    
    Simple text search across smartphone names and brands
    """
    if not data_service.is_data_loaded():
        raise HTTPException(
            status_code=503,
            detail="Smartphone data is not loaded."
        )
    
    try:
        # Get all data
        data = data_service.data.copy()
        
        # Search in name and brand columns
        if 'name' in data.columns:
            mask = data['name'].str.contains(query, case=False, na=False)
        else:
            mask = pd.Series([False] * len(data))
        
        if 'brand' in data.columns:
            mask |= data['brand'].str.contains(query, case=False, na=False)
        
        filtered_data = data[mask]
        
        # Apply price filters if provided
        if min_price is not None and 'price' in filtered_data.columns:
            filtered_data = filtered_data[filtered_data['price'] >= min_price]
        
        if max_price is not None and 'price' in filtered_data.columns:
            filtered_data = filtered_data[filtered_data['price'] <= max_price]

        # Filter by store if provided
        if store and 'store' in filtered_data.columns:
            filtered_data = filtered_data[
                filtered_data['store'].str.lower() == store.lower()
            ]

        # Interleave results across stores so all shops are represented
        if 'store' in filtered_data.columns and filtered_data['store'].nunique() > 1:
            filtered_data = (
                filtered_data
                .assign(_rank=filtered_data.groupby('store').cumcount())
                .sort_values(['_rank', 'store'])
                .drop(columns=['_rank'])
                .reset_index(drop=True)
            )

        # Limit results
        filtered_data = filtered_data.head(limit)
        
        # Convert to list of dicts
        results = filtered_data.to_dict('records')
        
        return {
            "query": query,
            "total_found": len(results),
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error during search: {str(e)}"
        )


@router.get("/compare")
async def compare_smartphones(
    ids: str = Query(..., description="Comma-separated smartphone IDs")
):
    """
    Compare multiple smartphones side by side
    
    Provide comma-separated IDs like: ?ids=1,2,3
    """
    if not data_service.is_data_loaded():
        raise HTTPException(
            status_code=503,
            detail="Smartphone data is not loaded."
        )
    
    try:
        # Parse IDs
        smartphone_ids = [int(id.strip()) for id in ids.split(',')]
        
        if len(smartphone_ids) > 10:
            raise HTTPException(
                status_code=400,
                detail="Maximum 10 smartphones can be compared at once"
            )
        
        # Get smartphones
        smartphones = []
        for sid in smartphone_ids:
            phone = data_service.get_smartphone_by_id(sid)
            if phone:
                smartphones.append(phone)
        
        if not smartphones:
            raise HTTPException(
                status_code=404,
                detail="No smartphones found with the provided IDs"
            )
        
        return {
            "total": len(smartphones),
            "smartphones": smartphones
        }
        
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid ID format. Please provide comma-separated integers."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error during comparison: {str(e)}"
        )


# ─── Phone Image ──────────────────────────────────────────────────────────────

# In-memory cache: "Brand|Name" -> list of image URLs
_image_cache: dict = {}

_EXECUTOR = ThreadPoolExecutor(max_workers=8)

_SCRAPE_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )
}


def _og_image_sync(url: str) -> Optional[str]:
    """Blocking: extract og:image from a product page."""
    try:
        resp = http_requests.get(url, timeout=4, headers=_SCRAPE_HEADERS)
        soup = BeautifulSoup(resp.text, "html.parser")
        tag = soup.find("meta", property="og:image") or soup.find("meta", attrs={"name": "og:image"})
        if tag:
            img = tag.get("content") or tag.get("value")
            # Reject generic logos/site images — only keep product-looking URLs
            if img and not any(k in img.lower() for k in ("logo", "logo-share", "favicon", "sprite")):
                return img
    except Exception:
        pass
    return None


_GSMARENA_SYSTEM = (
    "Given a phone brand and exact model name, return ONLY the GSMArena bigpic image filename. "
    "Format: brand-model.jpg (all lowercase, words separated by hyphens, no spaces, no quotes, no explanation). "
    "Examples: vivo-y21d.jpg, apple-iphone-14-pro.jpg, xiaomi-redmi-note-13-pro.jpg, "
    "samsung-galaxy-s23.jpg, tecno-spark-20-pro.jpg. "
    "Return ONLY the filename, nothing else."
)


def _groq_gsmarena_sync(brand: str, name: str) -> Optional[str]:
    """Ask Groq for the GSMArena bigpic filename, try with optional -4g/-5g suffixes,
    and return the first URL that responds with HTTP 200."""
    if not settings.groq_api_key:
        return None
    try:
        from groq import Groq
        client = Groq(api_key=settings.groq_api_key)
        resp = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": _GSMARENA_SYSTEM},
                {"role": "user", "content": f"{brand} {name}"},
            ],
            max_tokens=25,
            temperature=0.0,
        )
        raw = resp.choices[0].message.content.strip().strip('"').split()[0]
        if not raw.endswith(".jpg"):
            raw = raw.rstrip(".") + ".jpg"
        # Build candidate slugs: Groq's guess + 4G/5G added/stripped variants
        stem = raw[:-4]  # strip .jpg
        # Strip any trailing -4g / -5g for a "base" slug
        base = stem
        for suffix in ("-5g", "-4g"):
            if base.endswith(suffix):
                base = base[: -len(suffix)]
                break
        candidates = [raw, f"{base}.jpg", f"{base}-5g.jpg", f"{base}-4g.jpg"]
        # Deduplicate while preserving order
        seen_c: set = set()
        candidates = [c for c in candidates if not (c in seen_c or seen_c.add(c))]  # type: ignore
        for filename in candidates:
            url = f"https://fdn2.gsmarena.com/vv/bigpic/{filename}"
            try:
                r = http_requests.head(url, timeout=4, headers=_SCRAPE_HEADERS)
                if r.status_code == 200:
                    return url
            except Exception:
                continue
    except Exception:
        pass
    return None


@router.get("/phone-image")
async def get_phone_image(
    name: str = Query(..., description="Phone model name"),
    brand: str = Query(..., description="Phone brand"),
    url: Optional[str] = Query(None, description="Product page URL (optional)"),
):
    """
    Return a product image URL.
    1. Try og:image from the store product page (fast, works for Tunisianet/Mytek).
    2. Fallback: ask Groq for the GSMArena bigpic filename and validate with HEAD.
    Result is cached in memory after first fetch.
    """
    cache_key = f"{brand}|{name}"
    if cache_key in _image_cache:
        return {"image_urls": _image_cache[cache_key], "source": "cache"}

    loop = asyncio.get_event_loop()
    image_urls: list = []
    source = "none"

    # Step 1 — og:image from store page
    if url:
        try:
            og = await asyncio.wait_for(
                loop.run_in_executor(_EXECUTOR, _og_image_sync, url),
                timeout=5.0,
            )
            if og:
                image_urls = [og]
                source = "store"
        except Exception:
            pass

    # Step 2 — Groq → GSMArena bigpic (fallback when store page gave nothing)
    if not image_urls:
        try:
            gsm = await asyncio.wait_for(
                loop.run_in_executor(_EXECUTOR, _groq_gsmarena_sync, brand, name),
                timeout=8.0,
            )
            if gsm:
                image_urls = [gsm]
                source = "gsmarena"
        except Exception:
            pass

    _image_cache[cache_key] = image_urls
    return {"image_urls": image_urls, "source": source}
