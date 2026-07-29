# backend/app/services/prediction_service.py
import joblib
import pandas as pd
import numpy as np
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class PredictionService:
    """Service for making predictions with trained models."""

    _model_cache = {}

    @classmethod
    def predict(cls, model_path: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a prediction using a saved model."""
        # Load model (with caching)
        if model_path not in cls._model_cache:
            cls._model_cache[model_path] = joblib.load(model_path)

        model_data = cls._model_cache[model_path]
        pipeline = model_data["pipeline"]
        feature_names = model_data["feature_names"]
        problem_type = model_data["problem_type"]

        # Prepare input
        input_df = pd.DataFrame([input_data])

        # Ensure correct column order
        for col in feature_names:
            if col not in input_df.columns:
                input_df[col] = 0
        input_df = input_df[feature_names]

        # Make prediction
        prediction = pipeline.predict(input_df)[0]

        result = {
            "prediction": (
                int(prediction) if isinstance(prediction, (np.integer,)) else
                float(prediction) if isinstance(prediction, (np.floating,)) else
                str(prediction)
            ),
            "problem_type": problem_type,
        }

        # Add confidence for classification
        if "classification" in problem_type and hasattr(pipeline, "predict_proba"):
            try:
                proba = pipeline.predict_proba(input_df)[0]
                result["confidence"] = float(max(proba))
                result["probabilities"] = {
                    str(cls): float(p) for cls, p in zip(pipeline.classes_, proba)
                }
            except Exception:
                pass

        return result

    @classmethod
    def clear_cache(cls):
        cls._model_cache.clear()
