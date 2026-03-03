"""
Admin endpoints – MLflow experiments, runs, model management.
All routes require a valid admin JWT.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Any, Dict, List, Optional
import subprocess, sys, os

from ..services.auth_service import get_current_admin
from ..services.ml_service import ml_service
from ..config import settings

router = APIRouter(prefix="/admin", tags=["Admin"])


def _get_mlflow_client():
    try:
        import mlflow
        mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
        return mlflow.tracking.MlflowClient()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"MLflow unavailable: {e}")


# ── Experiments ─────────────────────────────────────────────────────────────

@router.get("/experiments")
async def list_experiments(_: dict = Depends(get_current_admin)) -> List[Dict[str, Any]]:
    """List all MLflow experiments."""
    client = _get_mlflow_client()
    exps = client.search_experiments()
    return [
        {
            "experiment_id": e.experiment_id,
            "name": e.name,
            "lifecycle_stage": e.lifecycle_stage,
            "artifact_location": e.artifact_location,
        }
        for e in exps
    ]


# ── Runs ─────────────────────────────────────────────────────────────────────

@router.get("/runs")
async def list_runs(
    experiment_id: Optional[str] = None,
    limit: int = 50,
    _: dict = Depends(get_current_admin),
) -> Dict[str, Any]:
    """List MLflow runs, newest first."""
    client = _get_mlflow_client()
    import mlflow
    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)

    if experiment_id:
        exp_ids = [experiment_id]
    else:
        exps = client.search_experiments()
        exp_ids = [e.experiment_id for e in exps]

    runs = client.search_runs(
        experiment_ids=exp_ids,
        order_by=["start_time DESC"],
        max_results=limit,
    )

    result = []
    for r in runs:
        result.append(
            {
                "run_id": r.info.run_id,
                "run_name": r.info.run_name or r.info.run_id[:8],
                "experiment_id": r.info.experiment_id,
                "status": r.info.status,
                "start_time": r.info.start_time,
                "end_time": r.info.end_time,
                "metrics": dict(r.data.metrics),
                "params": dict(r.data.params),
                "tags": {k: v for k, v in r.data.tags.items() if not k.startswith("mlflow.")},
            }
        )

    return {"total": len(result), "runs": result}


@router.get("/runs/{run_id}")
async def get_run(run_id: str, _: dict = Depends(get_current_admin)) -> Dict[str, Any]:
    """Get details of a single MLflow run."""
    client = _get_mlflow_client()
    try:
        r = client.get_run(run_id)
    except Exception:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")
    return {
        "run_id": r.info.run_id,
        "run_name": r.info.run_name or r.info.run_id[:8],
        "experiment_id": r.info.experiment_id,
        "status": r.info.status,
        "start_time": r.info.start_time,
        "end_time": r.info.end_time,
        "metrics": dict(r.data.metrics),
        "params": dict(r.data.params),
        "tags": dict(r.data.tags),
        "artifact_uri": r.info.artifact_uri,
    }


# ── Active model info ────────────────────────────────────────────────────────

@router.get("/model/active")
async def get_active_model(_: dict = Depends(get_current_admin)) -> Dict[str, Any]:
    """Return info about the currently loaded in-memory model."""
    info = ml_service.get_model_info()
    brand_means = {}
    if hasattr(ml_service, "_brand_mean"):
        brand_means = {
            k: round(v, 2)
            for k, v in sorted(
                ml_service._brand_mean.items(), key=lambda x: -x[1]
            )
        }
    return {
        **info,
        "brand_price_tiers": brand_means,
    }


# ── Log current model to MLflow ──────────────────────────────────────────────

@router.post("/model/log")
async def log_model_to_mlflow(_: dict = Depends(get_current_admin)) -> Dict[str, Any]:
    """
    Log the currently running KNN model as a new MLflow run.
    Creates / reuses the experiment defined in settings.
    """
    if not ml_service.is_model_loaded():
        raise HTTPException(status_code=503, detail="No model loaded")

    try:
        import mlflow
        mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
        mlflow.set_experiment(settings.mlflow_experiment_name)

        info = ml_service.get_model_info()
        with mlflow.start_run(run_name="KNN-brand-aware") as run:
            # Log params
            mlflow.log_param("algorithm",   info.get("algorithm", "KNN"))
            mlflow.log_param("k",            info.get("k", 15))
            mlflow.log_param("features",     info.get("features", ""))
            mlflow.log_param("dataset",      info.get("dataset", ""))
            mlflow.log_param("samples",      info.get("samples", 0))
            mlflow.log_param("brands",       info.get("brands", 0))
            # Log metrics
            if "approx_mae" in info:
                mlflow.log_metric("approx_mae", info["approx_mae"])
            mlflow.log_metric("price_min",  info.get("price_min", 0))
            mlflow.log_metric("price_max",  info.get("price_max", 0))
            mlflow.log_metric("price_mean", info.get("price_mean", 0))
            # Tag as active
            mlflow.set_tag("status",  "active")
            mlflow.set_tag("version", "2.0")

        return {
            "message": "Model logged to MLflow",
            "run_id": run.info.run_id,
            "experiment": settings.mlflow_experiment_name,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MLflow logging failed: {e}")


# ── MLflow UI proxy info ─────────────────────────────────────────────────────

def _is_port_open(host: str = "127.0.0.1", port: int = 5000, timeout: float = 0.5) -> bool:
    """Server-side TCP probe – avoids browser CORS/console-error noise."""
    import socket
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


@router.get("/mlflow-ui/status")
async def mlflow_ui_status(_: dict = Depends(get_current_admin)) -> Dict[str, Any]:
    """Check whether the MLflow UI process is reachable on port 5000."""
    alive = _is_port_open()
    return {
        "running": alive,
        "url": "http://localhost:5000" if alive else None,
    }


@router.post("/mlflow-ui/start")
async def start_mlflow_ui(_: dict = Depends(get_current_admin)) -> Dict[str, str]:
    """Launch mlflow ui as a background process."""
    if _is_port_open():
        return {"message": "MLflow UI already running at http://localhost:5000"}
    try:
        subprocess.Popen(
            [
                sys.executable, "-m", "mlflow", "ui",
                "--backend-store-uri", settings.mlflow_tracking_uri,
                "--host", "0.0.0.0",
                "--port", "5000",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd=os.getcwd(),
        )
        return {"message": "MLflow UI started at http://localhost:5000"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── System stats ─────────────────────────────────────────────────────────────

@router.get("/system")
async def system_stats(_: dict = Depends(get_current_admin)) -> Dict[str, Any]:
    """Basic system info for the admin dashboard."""
    from ..services.data_service import data_service
    return {
        "model_loaded": ml_service.is_model_loaded(),
        "data_loaded": data_service.is_data_loaded(),
        "data_rows": int(len(data_service.data)) if data_service.is_data_loaded() else 0,
        "mlflow_uri": settings.mlflow_tracking_uri,
        "mlflow_experiment": settings.mlflow_experiment_name,
    }
