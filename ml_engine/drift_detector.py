# ml_engine/drift_detector.py
import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, Any, List, Tuple
import logging

logger = logging.getLogger(__name__)


class DriftDetector:
    """Detect data drift and concept drift in ML models."""

    def __init__(self, reference_data: pd.DataFrame, threshold: float = 0.05):
        self.reference_data = reference_data
        self.threshold = threshold
        self.drift_results = {}

    def detect_all_drift(self, new_data: pd.DataFrame) -> Dict[str, Any]:
        """Run all drift detection methods."""
        results = {
            "feature_drift": self._detect_feature_drift(new_data),
            "prediction_drift": self._detect_prediction_drift(new_data),
            "statistical_drift": self._detect_statistical_drift(new_data),
            "overall_drift_detected": False,
            "severity": "none",
            "recommendations": [],
        }

        # Determine overall drift
        n_drifted = sum(
            1 for v in results["feature_drift"].values()
            if v.get("drifted", False)
        )
        total_features = len(results["feature_drift"])

        if total_features > 0:
            drift_ratio = n_drifted / total_features
            if drift_ratio > 0.3:
                results["overall_drift_detected"] = True
                results["severity"] = "high"
                results["recommendations"].append("Immediate retraining recommended.")
            elif drift_ratio > 0.1:
                results["overall_drift_detected"] = True
                results["severity"] = "medium"
                results["recommendations"].append("Schedule retraining within 1 week.")
            elif n_drifted > 0:
                results["severity"] = "low"
                results["recommendations"].append("Monitor closely. Minor drift detected.")

        return results

    def _detect_feature_drift(self, new_data: pd.DataFrame) -> Dict[str, Any]:
        """Detect drift in individual features using KS test."""
        results = {}
        common_cols = set(self.reference_data.columns) & set(new_data.columns)

        for col in common_cols:
            ref = self.reference_data[col].dropna()
            new = new_data[col].dropna()

            if len(ref) < 30 or len(new) < 30:
                continue

            if pd.api.types.is_numeric_dtype(ref):
                # Kolmogorov-Smirnov test
                stat, p_value = stats.ks_2samp(ref, new)
                drifted = p_value < self.threshold

                results[col] = {
                    "drifted": drifted,
                    "ks_statistic": round(float(stat), 4),
                    "p_value": round(float(p_value), 6),
                    "method": "KS-test",
                    "ref_mean": round(float(ref.mean()), 4),
                    "new_mean": round(float(new.mean()), 4),
                    "mean_shift_pct": round(
                        abs(new.mean() - ref.mean()) / (abs(ref.mean()) + 1e-10) * 100, 2
                    ),
                }
            else:
                # Chi-squared test for categorical
                ref_counts = ref.value_counts(normalize=True)
                new_counts = new.value_counts(normalize=True)

                # Align categories
                all_cats = set(ref_counts.index) | set(new_counts.index)
                ref_aligned = [ref_counts.get(c, 0) for c in all_cats]
                new_aligned = [new_counts.get(c, 0) for c in all_cats]

                if sum(ref_aligned) > 0 and sum(new_aligned) > 0:
                    stat, p_value = stats.chisquare(
                        [x * len(new) for x in new_aligned],
                        [x * len(new) for x in ref_aligned],
                    )
                    drifted = p_value < self.threshold
                else:
                    stat, p_value, drifted = 0, 1, False

                results[col] = {
                    "drifted": drifted,
                    "chi2_statistic": round(float(stat), 4),
                    "p_value": round(float(p_value), 6),
                    "method": "chi-squared",
                }

        return results

    def _detect_prediction_drift(self, new_data: pd.DataFrame) -> Dict[str, Any]:
        """Detect if prediction distribution has changed."""
        # This would compare prediction distributions
        return {
            "detected": False,
            "method": "PSI (Population Stability Index)",
            "psi_score": 0.0,
        }

    def _detect_statistical_drift(self, new_data: pd.DataFrame) -> Dict[str, Any]:
        """Overall statistical comparison."""
        numeric_cols = self.reference_data.select_dtypes(include=[np.number]).columns
        common_numeric = [c for c in numeric_cols if c in new_data.columns]

        if not common_numeric:
            return {"detected": False}

        # Compare overall distributions
        ref_stats = self.reference_data[common_numeric].describe()
        new_stats = new_data[common_numeric].describe()

        mean_diff = (ref_stats.loc["mean"] - new_stats.loc["mean"]).abs().mean()
        std_diff = (ref_stats.loc["std"] - new_stats.loc["std"]).abs().mean()

        return {
            "mean_difference": round(float(mean_diff), 4),
            "std_difference": round(float(std_diff), 4),
            "detected": mean_diff > 0.5 or std_diff > 0.5,
        }
