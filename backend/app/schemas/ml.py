# backend/app/schemas/ml.py
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uuid


class TrainRequest(BaseModel):
    project_id: uuid.UUID
    target_column: str
    problem_type: Optional[str] = None  # auto-detect if None
    algorithms: Optional[List[str]] = None
    cv_folds: Optional[int] = 5
    tune_hyperparams: bool = True


class TrainResponse(BaseModel):
    project_id: str
    status: str
    message: str


class ModelResponse(BaseModel):
    id: uuid.UUID
    name: str
    algorithm: str
    version: int
    problem_type: str
    metrics: Dict[str, float]
    status: str
    created_at: Any

    class Config:
        from_attributes = True


class ModelComparison(BaseModel):
    project_id: str
    models: List[Dict[str, Any]]
    best_model: Optional[Dict[str, Any]]
    primary_metric: str
