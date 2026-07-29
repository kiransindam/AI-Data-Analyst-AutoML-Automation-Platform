# tests/unit/test_ml.py
import pytest
import pandas as pd
import numpy as np
from ml_engine.automl_pipeline import AutoMLPipeline


class TestAutoMLPipeline:
    @pytest.fixture
    def classification_data(self):
        np.random.seed(42)
        n = 200
        return pd.DataFrame({
            "f1": np.random.normal(0, 1, n),
            "f2": np.random.normal(0, 1, n),
            "f3": np.random.normal(0, 1, n),
            "target": np.random.choice([0, 1], n),
        })

    @pytest.fixture
    def regression_data(self):
        np.random.seed(42)
        n = 200
        x = np.random.normal(0, 1, n)
        return pd.DataFrame({
            "f1": x,
            "f2": np.random.normal(0, 1, n),
            "target": 3 * x + np.random.normal(0, 0.5, n),
        })

    def test_classification_training(self, classification_data):
        pipeline = AutoMLPipeline(
            df=classification_data,
            target_col="target",
            problem_type="binary_classification",
        )
        results = pipeline.train_all_models()

        assert results["problem_type"] == "binary_classification"
        assert results["n_models_trained"] > 0
        assert results["best_model"] is not
