# ml_engine/automl_pipeline.py
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, classification_report,
    mean_absolute_error, mean_squared_error, r2_score
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
import joblib
import os
import time
import logging

try:
    import xgboost as xgb
    HAS_XGB = True
except ImportError:
    HAS_XGB = False

try:
    import lightgbm as lgb
    HAS_LGB = True
except ImportError:
    HAS_LGB = False

logger = logging.getLogger(__name__)


class AutoMLPipeline:
    """Automated Machine Learning Pipeline."""

    CLASSIFICATION_MODELS = {
        "logistic_regression": LogisticRegression(max_iter=1000, random_state=42),
        "random_forest": RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1),
        "gradient_boosting": GradientBoostingClassifier(random_state=42),
        "decision_tree": DecisionTreeClassifier(random_state=42),
        "knn": KNeighborsClassifier(n_neighbors=5),
    }

    REGRESSION_MODELS = {
        "linear_regression": LinearRegression(),
        "random_forest": RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1),
        "gradient_boosting": GradientBoostingRegressor(random_state=42),
    }

    def __init__(
        self,
        df: pd.DataFrame,
        target_col: str,
        problem_type: str = "auto",
        test_size: float = 0.2,
        cv_folds: int = 5,
        random_state: int = 42,
    ):
        self.df = df
        self.target_col = target_col
        self.problem_type = problem_type
        self.test_size = test_size
        self.cv_folds = cv_folds
        self.random_state = random_state

        self.X = None
        self.y = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.results = {}
        self.best_model = None
        self.best_model_name = None

        # Add XGBoost/LightGBM if available
        if HAS_XGB:
            self.CLASSIFICATION_MODELS["xgboost"] = xgb.XGBClassifier(
                random_state=42, use_label_encoder=False, eval_metric="logloss"
            )
            self.REGRESSION_MODELS["xgboost"] = xgb.XGBRegressor(random_state=42)

        if HAS_LGB:
            self.CLASSIFICATION_MODELS["lightgbm"] = lgb.LGBMClassifier(
                random_state=42, verbose=-1
            )
            self.REGRESSION_MODELS["lightgbm"] = lgb.LGBMRegressor(random_state=42, verbose=-1)

    def prepare_data(self):
        """Split data into train/test sets."""
        self.X = self.df.drop(columns=[self.target_col])
        self.y = self.df[self.target_col]

        # Auto-detect problem type
        if self.problem_type == "auto":
            if self.y.nunique() == 2:
                self.problem_type = "binary_classification"
            elif self.y.nunique() < 20 and not pd.api.types.is_numeric_dtype(self.y):
                self.problem_type = "multiclass_classification"
            else:
                self.problem_type = "regression"

        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X, self.y, test_size=self.test_size, random_state=self.random_state,
            stratify=self.y if "classification" in self.problem_type else None,
        )

        logger.info(f"Data prepared. Problem type: {self.problem_type}")
        logger.info(f"Train: {self.X_train.shape}, Test: {self.X_test.shape}")

    def train_all_models(self) -> Dict[str, Any]:
        """Train all applicable models and compare."""
        self.prepare_data()

        models = (
            self.CLASSIFICATION_MODELS
            if "classification" in self.problem_type
            else self.REGRESSION_MODELS
        )

        results = []
        for name, model in models.items():
            try:
                logger.info(f"Training {name}...")
                start_time = time.time()

                # Create pipeline with scaling
                pipe = Pipeline([
                    ("scaler", StandardScaler()),
                    ("model", model),
                ])

                # Cross-validation
                scoring = self._get_scoring_metric()
                cv_scores = cross_val_score(
                    pipe, self.X_train, self.y_train,
                    cv=self.cv_folds, scoring=scoring, n_jobs=-1
                )

                # Fit on full training set
                pipe.fit(self.X_train, self.y_train)
                training_time = time.time() - start_time

                # Predictions
                y_pred = pipe.predict(self.X_test)
                metrics = self._calculate_metrics(y_pred)

                result = {
                    "model_name": name,
                    "cv_mean": round(float(cv_scores.mean()), 4),
                    "cv_std": round(float(cv_scores.std()), 4),
                    "metrics": metrics,
                    "training_time_sec": round(training_time, 2),
                    "pipeline": pipe,
                }
                results.append(result)
                logger.info(f"  {name}: CV={cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

            except Exception as e:
                logger.warning(f"  {name} failed: {str(e)}")
                results.append({
                    "model_name": name,
                    "error": str(e),
                })

        # Sort by primary metric
        primary_metric = "accuracy" if "classification" in self.problem_type else "r2_score"
        valid_results = [r for r in results if "error" not in r]
        valid_results.sort(key=lambda x: x["metrics"].get(primary_metric, 0), reverse=True)

        self.results = {
            "problem_type": self.problem_type,
            "all_results": valid_results,
            "best_model": valid_results[0] if valid_results else None,
            "n_models_trained": len(valid_results),
            "n_models_failed": len(results) - len(valid_results),
        }

        if valid_results:
            self.best_model = valid_results[0]["pipeline"]
            self.best_model_name = valid_results[0]["model_name"]

        return self.results

    def tune_best_model(self, param_grid: Optional[Dict] = None) -> Dict[str, Any]:
        """Hyperparameter tuning for the best model."""
        if not self.best_model_name:
            return {"error": "No model trained yet"}

        if param_grid is None:
            param_grid = self._get_default_param_grid(self.best_model_name)

        if not param_grid:
            return {"message": "No tuning parameters available for this model"}

        logger.info(f"Tuning {self.best_model_name}...")
        start_time = time.time()

        grid_search = GridSearchCV(
            self.best_model,
            param_grid,
            cv=self.cv_folds,
            scoring=self._get_scoring_metric(),
            n_jobs=-1,
            verbose=1,
        )
        grid_search.fit(self.X_train, self.y_train)

        tuning_time = time.time() - start_time
        self.best_model = grid_search.best_estimator_

        # Re-evaluate
        y_pred = self.best_model.predict(self.X_test)
        metrics = self._calculate_metrics(y_pred)

        return {
            "best_params": grid_search.best_params_,
            "best_cv_score": round(float(grid_search.best_score_), 4),
            "test_metrics": metrics,
            "tuning_time_sec": round(tuning_time, 2),
            "n_candidates": len(grid_search.cv_results_["params"]),
        }

    def save_model(self, path: str) -> str:
        """Save the best model."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        model_data = {
            "pipeline": self.best_model,
            "feature_names": self.X.columns.tolist(),
            "target_col": self.target_col,
            "problem_type": self.problem_type,
            "metrics": self.results.get("best_model", {}).get("metrics", {}),
        }
        joblib.dump(model_data, path)
        logger.info(f"Model saved to {path}")
        return path

    def _get_scoring_metric(self) -> str:
        if self.problem_type == "binary_classification":
            return "roc_auc"
        elif self.problem_type == "multiclass_classification":
            return "f1_weighted"
        else:
            return "r2"

    def _calculate_metrics(self, y_pred) -> Dict[str, float]:
        if "classification" in self.problem_type:
            metrics = {
                "accuracy": round(float(accuracy_score(self.y_test, y_pred)), 4),
                "precision": round(float(precision_score(
                    self.y_test, y_pred, average="weighted", zero_division=0
                )), 4),
                "recall": round(float(recall_score(
                    self.y_test, y_pred, average="weighted", zero_division=0
                )), 4),
                "f1_score": round(float(f1_score(
                    self.y_test, y_pred, average="weighted", zero_division=0
                )), 4),
            }
            if self.problem_type == "binary_classification":
                try:
                    y_proba = self.best_model.predict_proba(self.X_test)[:, 1]
                    metrics["roc_auc"] = round(float(roc_auc_score(self.y_test, y_proba)), 4)
                except Exception:
                    pass
        else:
            metrics = {
                "mae": round(float(mean_absolute_error(self.y_test, y_pred)), 4),
                "mse": round(float(mean_squared_error(self.y_test, y_pred)), 4),
                "rmse": round(float(np.sqrt(mean_squared_error(self.y_test, y_pred))), 4),
                "r2_score": round(float(r2_score(self.y_test, y_pred)), 4),
            }
        return metrics

    def _get_default_param_grid(self, model_name: str) -> Dict:
        grids = {
            "random_forest": {
                "model__n_estimators": [50, 100, 200],
                "model__max_depth": [None, 10, 20, 30],
                "model__min_samples_split": [2, 5, 10],
            },
            "xgboost": {
                "model__n_estimators": [50, 100, 200],
                "model__max_depth": [3, 5, 7],
                "model__learning_rate": [0.01, 0.1, 0.2],
            },
            "lightgbm": {
                "model__n_estimators": [50, 100, 200],
                "model__max_depth": [-1, 5, 10],
                "model__learning_rate": [0.01, 0.1, 0.2],
            },
            "logistic_regression": {
                "model__C": [0.01, 0.1, 1, 10],
                "model__penalty": ["l2"],
            },
        }
        return grids.get(model_name, {})

    def get_feature_importance(self, top_n: int = 20) -> Dict[str, float]:
        """Get feature importance from best model."""
        if not self.best_model:
            return {}

        model = self.best_model.named_steps.get("model", self.best_model)
        importance = {}

        if hasattr(model, "feature_importances_"):
            imp = model.feature_importances_
            for name, val in zip(self.X.columns, imp):
                importance[name] = round(float(val), 4)
        elif hasattr(model, "coef_"):
            coef = model.coef_
            if len(coef.shape) > 1:
                coef = coef[0]
            for name, val in zip(self.X.columns, coef):
                importance[name] = round(float(abs(val)), 4)

        # Sort and return top N
        sorted_imp = dict(sorted(importance.items(), key=lambda x: x[1], reverse=True)[:top_n])
        return sorted_imp
