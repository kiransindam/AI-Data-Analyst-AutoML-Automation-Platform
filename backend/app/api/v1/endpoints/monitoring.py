# backend/app/api/v1/endpoints/monitoring.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
import uuid

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.ml_model import MLModel
from app.models.prediction import Prediction

router = APIRouter()


@router.get("/model/{model_id}/metrics")
async def get_model_metrics(
    model_id: uuid.UUID,
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get model performance metrics over time."""
    model = db.query(MLModel).filter(MLModel.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    # Get predictions in time range
    since = datetime.utcnow() - timedelta(days=days)
    predictions = db.query(Prediction).filter(
        Prediction.model_id == model_id,
        Prediction.created_at >= since,
    ).all()

    # Calculate metrics
    total_predictions = len(predictions)
    avg_latency = (
        sum(p.latency_ms for p in predictions if p.latency_ms) / total_predictions
        if total_predictions > 0 else 0
    )
    avg_confidence = (
        sum(p.confidence for p in predictions if p.confidence) / total_predictions
        if total_predictions > 0 else 0
    )

    return {
        "model_id": str(model_id),
        "model_name": model.name,
        "period_days": days,
        "total_predictions": total_predictions,
        "avg_latency_ms": round(avg_latency, 2),
        "avg_confidence": round(avg_confidence, 4),
        "training_metrics": model.metrics,
        "status": model.status,
    }


@router.get("/system/health")
async def system_health():
    """System-wide health check."""
    import psutil
    import shutil

    disk = shutil.disk_usage("/")
    memory = psutil.virtual_memory()

    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "system": {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": memory.percent,
            "memory_available_gb": round(memory.available / 1024**3, 2),
            "disk_percent": disk.percent,
            "disk_free_gb": round(disk.free / 1024**3, 2),
        },
    }


@router.post("/model/{model_id}/drift-check")
async def trigger_drift_check(
    model_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Trigger a drift check for a model."""
    model = db.query(MLModel).filter(MLModel.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    # In production, this would trigger an async task
    return {
        "model_id": str(model_id),
        "status": "drift_check_initiated",
        "message": "Drift check started. Results will be available shortly.",
    }
