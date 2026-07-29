# backend/app/services/ml_service.py
import pandas as pd
import os
import uuid
import logging
from typing import Dict, Any, Optional, List

from ml_engine.automl_pipeline import AutoMLPipeline
from app.core.database import SessionLocal
from app.models.project import Project
from app.models.ml_model import MLModel
from app.config import settings

logger = logging.getLogger(__name__)


class MLService:
    """Service for ML model training and management."""

    @staticmethod
    def train_models(
        project_id: str,
        target_column: str,
        problem_type: Optional[str] = None,
        algorithms: Optional[List[str]] = None,
        cv_folds: int = 5,
        tune_hyperparams: bool = True,
    ):
        """Train ML models (background task)."""
        db = SessionLocal()
        try:
            project = db.query(Project).filter(Project.id == project_id).first()
            if not project:
                return

            project.status = "training"
            db.commit()

            # Load cleaned data
            dataset = project.dataset
            df = pd.read_csv(dataset.storage_path)  # Simplified; use proper loader

            # Run AutoML
            pipeline = AutoMLPipeline(
                df=df,
                target_col=target_column,
                problem_type=problem_type or "auto",
                cv_folds=cv_folds,
            )

            results = pipeline.train_all_models()

            # Tune best model
            tuning_results = None
            if tune_hyperparams and pipeline.best_model:
                tuning_results = pipeline.tune_best_model()

            # Save best model
            model_id = str(uuid.uuid4())
            model_path = os.path.join(settings.MODEL_DIR, f"{model_id}.joblib")
            pipeline.save_model(model_path)

            # Store in database
            best = results.get("best_model", {})
            ml_model = MLModel(
                project_id=project.id,
                name=f"Best Model - {pipeline.best_model_name}",
                algorithm=pipeline.best_model_name,
                problem_type=pipeline.problem_type,
                metrics=best.get("metrics", {}),
                hyperparameters=tuning_results.get("best_params") if tuning_results else {},
                feature_importance=pipeline.get_feature_importance(),
                artifact_path=model_path,
                training_data_info={
                    "training_time": best.get("training_time_sec"),
                    "cv_score": best.get("cv_mean"),
                    "n_features": len(df.columns) - 1,
                    "n_samples": len(df),
                },
                status="trained",
            )
            db.add(ml_model)

            # Store all model results
            project.results = project.results or {}
            project.results["ml_training"] = {
                "all_models": [
                    {k: v for k, v in r.items() if k != "pipeline"}
                    for r in results.get("all_results", [])
                ],
                "best_model": pipeline.best_model_name,
                "tuning": tuning_results,
            }
            project.status = "completed"
            db.commit()

            logger.info(f"ML training complete for project {project_id}")

        except Exception as e:
            logger.error(f"ML training failed: {e}")
            if project:
                project.status = "failed"
                db.commit()
        finally:
            db.close()
