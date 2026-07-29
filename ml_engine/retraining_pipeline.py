# ml_engine/retraining_pipeline.py
import pandas as pd
import joblib
import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from ml_engine.automl_pipeline import AutoMLPipeline
from ml_engine.drift_detector import DriftDetector

logger = logging.getLogger(__name__)


class RetrainingPipeline:
    """Automatic model retraining pipeline."""

    def __init__(
        self,
        model_path: str,
        reference_data_path: str,
        drift_threshold: float = 0.05,
        performance_drop_threshold: float = 0.1,
    ):
        self.model_path = model_path
        self.reference_data_path = reference_data_path
        self.drift_threshold = drift_threshold
        self.performance_drop_threshold = performance_drop_threshold

    def check_and_retrain(self, new_data: pd.DataFrame) -> Dict[str, Any]:
        """Check for drift and retrain if necessary."""
        logger.info("Checking if retraining is needed...")

        # Load reference data
        reference_data = pd.read_csv(self.reference_data_path)

        # Detect drift
        detector = DriftDetector(reference_data, threshold=self.drift_threshold)
        drift_results = detector.detect_all_drift(new_data)

        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "drift_detected": drift_results["overall_drift_detected"],
            "drift_severity": drift_results["severity"],
            "retraining_triggered": False,
            "new_model_path": None,
            "performance_comparison": None,
        }

        if not drift_results["overall_drift_detected"]:
            logger.info("No significant drift detected. Skipping retraining.")
            result["message"] = "No retraining needed."
            return result

        logger.info(f"Drift detected (severity: {drift_results['severity']}). Starting retraining...")

        # Retrain
        retrain_result = self._retrain(new_data)
        result["retraining_triggered"] = True
        result.update(retrain_result)

        return result

    def _retrain(self, new_data: pd.DataFrame) -> Dict[str, Any]:
        """Retrain model with new data."""
        # Load existing model info
        model_data = joblib.load(self.model_path)
        target_col = model_data["target_col"]
        problem_type = model_data["problem_type"]

        # Combine reference + new data
        reference_data = pd.read_csv(self.reference_data_path)
        combined_data = pd.concat([reference_data, new_data], ignore_index=True)

        # Train new model
        pipeline = AutoMLPipeline(
            df=combined_data,
            target_col=target_col,
            problem_type=problem_type,
        )

        results = pipeline.train_all_models()
        tuning_results = pipeline.tune_best_model()

        # Compare with old model
        old_metrics = model_data.get("metrics", {})
        new_metrics = results.get("best_model", {}).get("metrics", {})

        primary_metric = "accuracy" if "classification" in problem_type else "r2_score"
        old_score = old_metrics.get(primary_metric, 0)
        new_score = new_metrics.get(primary_metric, 0)

        improvement = new_score - old_score

        # Only deploy if improvement is significant
        if improvement > 0.01:  # At least 1% improvement
            # Save new model
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            new_model_path = self.model_path.replace(".joblib", f"_v2_{timestamp}.joblib")
            pipeline.save_model(new_model_path)

            logger.info(f"New model saved: {new_model_path} (improvement: {improvement:.4f})")

            return {
                "new_model_path": new_model_path,
                "performance_comparison": {
                    "old_score": old_score,
                    "new_score": new_score,
                    "improvement": round(improvement, 4),
                    "deployed": True,
                },
                "message": "New model trained and saved. Performance improved.",
            }
        else:
            logger.info(f"New model not better (improvement: {improvement:.4f}). Keeping old model.")
            return {
                "performance_comparison": {
                    "old_score": old_score,
                    "new_score": new_score,
                    "improvement": round(improvement, 4),
                    "deployed": False,
                },
                "message": "Retraining completed but new model not significantly better.",
            }

    def schedule_periodic_check(self, interval_hours: int = 24):
        """Schedule periodic drift checks (for use with Celery/cron)."""
        # This would be integrated with Celery Beat or a cron job
        logger.info(f"Periodic drift check scheduled every {interval_hours} hours")
        pass
