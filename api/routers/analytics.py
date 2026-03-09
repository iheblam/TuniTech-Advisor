"""
Analytics endpoints – brand stats, market overview, AI insight.
"""

import asyncio
from functools import lru_cache
from typing import Any, Dict, List

import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException

from ..config import settings
from ..services.data_service import data_service

router = APIRouter(prefix="/analytics", tags=["Analytics"])


# ── helpers ──────────────────────────────────────────────────────────────────

def _df() -> pd.DataFrame:
    """Return a normalised copy of the loaded dataset."""
    if not data_service.is_data_loaded():
        raise HTTPException(status_code=503, detail="Dataset not loaded.")
    df = data_service.data.copy()
    # Normalise brand casing  Samsung/SAMSUNG → Samsung
    df["brand"] = df["brand"].str.strip().str.title().fillna("Unknown")
    # Ensure price is numeric
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df = df.dropna(subset=["price"])
    return df


def _safe(val: Any) -> Any:
    """Convert numpy scalars to plain Python types for JSON serialisation."""
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        return float(val)
    return val


# ── /brands ──────────────────────────────────────────────────────────────────

@router.get("/brands")
async def brand_analytics() -> Dict[str, Any]:
    """
    Per-brand statistics: count, share %, avg/min/max price and
    the single best-value phone (highest specs-per-TND score).
    """
    df = _df()
    total = len(df)

    results: List[Dict[str, Any]] = []

    # Keep only the top 12 brands by listing count to keep the UI readable
    top_brands = df["brand"].value_counts().head(12).index.tolist()

    for brand in top_brands:
        bdf = df[df["brand"] == brand]

        avg_p = _safe(round(bdf["price"].mean(), 1))
        min_p = _safe(bdf["price"].min())
        max_p = _safe(bdf["price"].max())
        share = round(len(bdf) / total * 100, 1)

        # Best-value phone: score = (ram + storage/8 + battery/1000) / price
        score_cols = ["ram", "storage", "battery", "price"]
        # Accept column aliases from data_service rename
        alias = {"ram": "ram", "storage": "storage", "battery": "battery"}
        available = {k: v for k, v in alias.items() if v in bdf.columns}

        best_row = None
        if len(available) == len(alias) and "price" in bdf.columns:
            scored = bdf.copy()
            scored["_score"] = (
                scored.get("ram", 0).fillna(0) +
                scored.get("storage", 0).fillna(0) / 8 +
                scored.get("battery", 0).fillna(0) / 1000
            ) / scored["price"].replace(0, np.nan)
            best_idx = scored["_score"].idxmax()
            r = scored.loc[best_idx]
            best_row = {
                "name": r.get("name", ""),
                "price": _safe(r.get("price", 0)),
                "ram": _safe(r.get("ram", 0)) if "ram" in r else None,
                "storage": _safe(r.get("storage", 0)) if "storage" in r else None,
                "store": r.get("store", r.get("source", "")),
                "url": r.get("url", ""),
            }

        results.append({
            "brand": brand,
            "count": len(bdf),
            "share_pct": share,
            "avg_price": avg_p,
            "min_price": _safe(min_p),
            "max_price": _safe(max_p),
            "best_value_phone": best_row,
        })

    # Sort by count desc
    results.sort(key=lambda x: x["count"], reverse=True)

    return {"total_phones": total, "brands": results}


# ── /market ───────────────────────────────────────────────────────────────────

@router.get("/market")
async def market_overview() -> Dict[str, Any]:
    """
    Market-wide stats: price segments, OS distribution,
    network adoption, store comparison, spec averages.
    """
    df = _df()
    total = len(df)

    # Price segments
    bins = [0, 500, 1000, 1500, 3000, float("inf")]
    labels = ["<500 TND", "500–1000", "1000–1500", "1500–3000", ">3000 TND"]
    df["_seg"] = pd.cut(df["price"], bins=bins, labels=labels, right=False)
    seg_counts = df["_seg"].value_counts().reindex(labels, fill_value=0)
    price_segments = [
        {"label": lbl, "count": int(cnt)}
        for lbl, cnt in seg_counts.items()
    ]

    # OS distribution (top 6)
    os_col = "os" if "os" in df.columns else None
    os_dist: List[Dict] = []
    if os_col:
        for os, cnt in df[os_col].value_counts().head(6).items():
            os_dist.append({"os": str(os), "count": int(cnt)})

    # Network stats
    net_col = "network" if "network" in df.columns else None
    net_stats: List[Dict] = []
    if net_col:
        df["_net_norm"] = df[net_col].str.upper().apply(
            lambda x: "5G" if "5G" in str(x) else ("4G" if "4G" in str(x) else "3G/Other")
        )
        for net, cnt in df["_net_norm"].value_counts().items():
            net_stats.append({"type": str(net), "count": int(cnt)})

    # Store stats
    store_col = "store" if "store" in df.columns else "source" if "source" in df.columns else None
    store_stats: List[Dict] = []
    if store_col:
        for store, grp in df.groupby(store_col):
            store_stats.append({
                "store": str(store),
                "count": int(len(grp)),
                "avg_price": round(float(grp["price"].mean()), 1),
            })
        store_stats.sort(key=lambda x: x["count"], reverse=True)

    # Spec averages (across phones that have the field)
    spec_avgs: Dict[str, Any] = {}
    for col, label in [("ram", "Avg RAM (GB)"), ("storage", "Avg Storage (GB)"),
                       ("battery", "Avg Battery (mAh)"), ("screen_size", "Avg Screen (in)")]:
        if col in df.columns:
            spec_avgs[label] = round(float(df[col].dropna().mean()), 1)

    # 5G penetration
    five_g_pct = 0.0
    if net_col:
        five_g_pct = round(df["_net_norm"].eq("5G").sum() / total * 100, 1)

    # Price summary
    price_summary = {
        "min": _safe(df["price"].min()),
        "max": _safe(df["price"].max()),
        "mean": round(float(df["price"].mean()), 1),
        "median": round(float(df["price"].median()), 1),
    }

    return {
        "total_phones": total,
        "price_summary": price_summary,
        "five_g_pct": five_g_pct,
        "price_segments": price_segments,
        "os_distribution": os_dist,
        "network_stats": net_stats,
        "store_stats": store_stats,
        "spec_averages": spec_avgs,
    }


# ── /ai-insight ──────────────────────────────────────────────────────────────

@lru_cache(maxsize=1)
def _cached_insight() -> str:
    """Generate (and cache) a Groq-powered market insight. Called once per process."""
    if not settings.groq_api_key:
        return "AI insight unavailable – no GROQ_API_KEY configured."

    # Build a concise stats digest to feed to the model
    try:
        df = _df()
        total = len(df)
        top_brands = df["brand"].value_counts().head(5).to_dict()
        five_g_count = int(df["network"].str.upper().str.contains("5G", na=False).sum()) if "network" in df.columns else 0
        avg_price = round(float(df["price"].mean()), 0)
        ios_count = int(df["os"].str.contains("iOS", na=False).sum()) if "os" in df.columns else 0
        android_count = total - ios_count

        prompt = (
            f"You are a market analyst for Tunisian consumer electronics.\n"
            f"Here are current stats for the Tunisian smartphone retail market:\n"
            f"- {total} phones listed across Tunisianet, Mytek, SpaceNet, BestBuyTunisie, BestPhone\n"
            f"- Top brands (by listings): {top_brands}\n"
            f"- 5G phones: {five_g_count} ({round(five_g_count/total*100,1)}%)\n"
            f"- Average price: {avg_price} TND\n"
            f"- Android phones: {android_count}, iOS phones: {ios_count}\n\n"
            f"Write a concise 2-3 sentence market insight paragraph for Tunisian shoppers. "
            f"Mention value leaders, 5G adoption trend, and one actionable buying tip. "
            f"Keep it factual, friendly, and under 80 words."
        )

        from groq import Groq  # local import to avoid startup cost
        client = Groq(api_key=settings.groq_api_key)
        resp = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=120,
            temperature=0.4,
        )
        return resp.choices[0].message.content.strip()

    except Exception as exc:
        return f"AI insight temporarily unavailable. ({exc})"


@router.get("/ai-insight")
async def ai_insight() -> Dict[str, str]:
    """Return a Groq-generated market insight (cached for the process lifetime)."""
    loop = asyncio.get_event_loop()
    insight = await loop.run_in_executor(None, _cached_insight)
    return {"insight": insight}
