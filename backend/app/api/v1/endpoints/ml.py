# backend/app/api/v1/endpoints/ml.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional
import uuid

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.project import Project
from app.models.ml_model import MLModel
from app.schemas.ml import (
    TrainRequest, TrainResponse, ModelResponse,
    ModelComparison, HyperparameterTuneRequest
)
from app.services.ml_service import MLService

router = APIRouter()


@router.post("/train", response_model=TrainResponse)
async def train_model(
    request: TrainRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Train ML model(s) on dataset."""
    project = db.query(Project).filter(
        Project.id == request.project_id,
        Project.user_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    background_tasks.add_task(
        MLService.train_models,
        project_id=str(project.id),
        target_column=request.target_column,
        problem_type=request.problem_type,
        algorithms=request.algorithms,
        cv_folds=request.cv_folds or 5,
        tune_hyperparams=request.tune_hyperparams,
    )

    return TrainResponse(
        project_id=str(project.id),
        status="training",
        message="Model training started.",
    )


@router.get("/{project_id}/models", response_model=list[ModelResponse])
async def list_models(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all trained models for a project."""
    models = db.query(MLModel).filter(
        MLModel.project_id == project_id
    ).order_by(MLModel.created_at.desc()).all()
    return models


@router.get("/{project_id}/comparison", response_model=ModelComparison)
async def compare_models(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Compare all models for a project."""
    models = db.query(MLModel).filter(
        MLModel.project_id == project_id,
        MLModel.status == "trained"
    ).all()

    if not models:
        raise HTTPException(status_code=404, detail="No trained models found")

    comparison = []
    for model in models:
        comparison.append({
            "model_id": str(model.id),
            "name": model.name,
            "algorithm": model.algorithm,
            "metrics": model.metrics,
            "training_time": model.training_data_info.get("training_time"),
        })

    # Sort by primary metric
    primary_metric = "accuracy" if models[0].problem_type == "classification" else "r2_score"
    comparison.sort(key=lambda x: x["metrics"].get(primary_metric, 0), reverse=True)

    return ModelComparison(
        project_id=str(project_id),
        models=comparison,
        best_model=comparison[0] if comparison else None,
        primary_metric=primary_metric,
    )


@router.post("/{model_id}/deploy")
async def deploy_model(
    model_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Deploy a model for predictions."""
    model = db.query(MLModel).filter(MLModel.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    model.status = "deployed"
    db.commit()

    return {"message": f"Model '{model.name}' deployed successfully", "model_id": str(model.id)}
