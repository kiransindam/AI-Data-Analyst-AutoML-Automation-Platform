# backend/app/schemas/prediction.py
from pydantic import BaseModel
from typing import List, Dict, Any
import uuid


class PredictRequest(BaseModel):
    model_id: uuid.UUID
    input_data: Dict[str, Any]


class BatchPredictRequest(BaseModel):
    model_id: uuid.UUID
    input_data_list: List[Dict[str, Any]]


class PredictResponse(BaseModel):
    prediction_id: str
    model_id: str
    result: Dict[str, Any]
    latency_ms: float
