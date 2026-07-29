# backend/app/api/v1/endpoints/predict.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import uuid
import time

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.ml_model import MLModel
from app.models.prediction import Prediction
from app.schemas.prediction import PredictRequest, PredictResponse, BatchPredictRequest
from app.services.prediction_service import PredictionService

router = APIRouter()


@router.post("/", response_model=PredictResponse)
async def predict(
    request: PredictRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Make a single prediction."""
    model = db.query(MLModel).filter(
        MLModel.id == request.model_id,
        MLModel.status == "deployed"
    ).first()
    if not model:
        raise HTTPException(status_code=404, detail="Deployed model not found")

    start_time = time.time()
    result = PredictionService.predict(
        model_path=model.artifact_path,
        input_data=request.input_data,
    )
    latency = (time.time() - start_time) * 1000

    # Store prediction
    prediction = Prediction(
        model_id=model.id,
        input_data=request.input_data,
        output=result,
        confidence=result.get("confidence"),
        latency_ms=latency,
    )
    db.add(prediction)
    db.commit()

    return PredictResponse(
        prediction_id=str(prediction.id),
        model_id=str(model.id),
        result=result,
        latency_ms=latency,
    )


@router.post("/batch", response_model=List[PredictResponse])
async def batch_predict(
    request: BatchPredictRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Make batch predictions."""
    model = db.query(MLModel).filter(
        MLModel.id == request.model_id,
        MLModel.status == "deployed"
    ).first()
    if not model:
        raise HTTPException(status_code=404, detail="Deployed model not found")

    results = []
    for input_data in request.input_data_list:
        start_time = time.time()
        result = PredictionService.predict(
            model_path=model.artifact_path,
            input_data=input_data,
        )
        latency = (time.time() - start_time) * 1000

        prediction = Prediction(
            model_id=model.id,
            input_data=input_data,
            output=result,
            confidence=result.get("confidence"),
            latency_ms=latency,
        )
        db.add(prediction)
        results.append(PredictResponse(
            prediction_id=str(uuid.uuid4()),
            model_id=str(model.id),
            result=result,
            latency_ms=latency,
        ))

    db.commit()
    return results
