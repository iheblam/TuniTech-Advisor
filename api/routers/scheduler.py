"""
Scheduler Router
────────────────
Public:
  GET  /api/v1/scheduler/status   — current state (last run, next run, logs …)

Admin-only:
  POST /api/v1/scheduler/run-now           — trigger a scrape now
  POST /api/v1/scheduler/set-interval      — change the recurrence interval
  POST /api/v1/scheduler/set-include-mytek — toggle Mytek Selenium scraper
"""

from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from api.services.scheduler_service import scheduler_service
from api.services.auth_service import get_current_admin

router = APIRouter(prefix="/scheduler", tags=["Scheduler"])


# ── Request schemas ────────────────────────────────────────────────────────────

class IntervalRequest(BaseModel):
    hours: int  # 1 – 8760 (1 h – 1 year)

class MytekRequest(BaseModel):
    enabled: bool


# ── Public endpoints ───────────────────────────────────────────────────────────

@router.get("/status", response_model=Dict[str, Any])
def get_status():
    """
    Returns the current scheduler state:
    - running         : bool
    - last_run        : ISO datetime or null
    - next_run        : ISO datetime or null
    - interval_hours  : int
    - include_mytek   : bool
    - last_results    : {store: {status, count, error?}}
    - logs            : [recent log lines]
    """
    return scheduler_service.get_status()


# ── Admin-only endpoints ───────────────────────────────────────────────────────

@router.post("/run-now", dependencies=[Depends(get_current_admin)])
def trigger_now():
    """Trigger a full scrape + fill + reload pipeline immediately."""
    result = scheduler_service.trigger_now()
    if result.get("status") == "already_running":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Pipeline is already running",
        )
    return {"message": "Pipeline started in background", **result}


@router.post("/set-interval", dependencies=[Depends(get_current_admin)])
def set_interval(req: IntervalRequest):
    """Update how often the scheduler fires (in hours)."""
    if not 1 <= req.hours <= 8760:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="hours must be between 1 and 8760",
        )
    scheduler_service.set_interval(req.hours)
    return {"message": f"Interval updated to {req.hours} h"}


@router.post("/set-include-mytek", dependencies=[Depends(get_current_admin)])
def set_include_mytek(req: MytekRequest):
    """Toggle whether the Mytek Selenium scraper is included in the run."""
    scheduler_service.set_include_mytek(req.enabled)
    return {"message": f"include_mytek set to {req.enabled}"}
