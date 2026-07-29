# tests/unit/test_cleaning.py
import pytest
import pandas as pd
import numpy as np
from ml_engine.data_cleaner import DataCleaner


class TestDataCleaner:
    @pytest.fixture
    def dirty_df(self):
        """Create a dirty dataframe for testing."""
        np.random.seed(42)
        return pd.DataFrame({
            "numeric_col": [1, 2, np.nan, 4, 5, 100, 7, 8, np.nan, 10],
            "cat_col": ["A", "B", "A", None, "C", "A", "B", "A", "C", "A"],
            "dup_col": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            "target": [0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
        })

    def test_remove_duplicates(self, dirty_df):
        cleaner = DataCleaner(dirty_df)
        cleaner._remove_duplicates()
        # dup_col is constant but rows aren't exact duplicates
        assert len(cleaner.df) == 10

    def test_handle_missing_numeric(self, dirty_df):
        cleaner = DataCleaner(dirty_df)
        cleaner._handle_missing_values()
        assert cleaner.df["numeric_col"].isnull().sum() == 0

    def test_handle_missing_categorical(self, dirty_df):
        cleaner = DataCleaner(dirty_df)
        cleaner._handle_missing_values()
        assert cleaner.df["cat_col"].isnull().sum() == 0

    def test_outlier_detection(self, dirty_df):
        cleaner = DataCleaner(dirty_df)
        cleaner._handle_outliers()
        # Value 100 should be clipped
        assert cleaner.df["numeric_col"].max() < 100

    def test_full_pipeline(self, dirty_df):
        cleaner = DataCleaner(dirty_df)
        cleaned_df, report = cleaner.run_full_pipeline()
        assert cleaned_df.isnull().sum().sum() == 0
        assert "dup_col" not in cleaned_df.columns  # Removed as low variance
        assert len(report["cleaning_steps"]) > 0
