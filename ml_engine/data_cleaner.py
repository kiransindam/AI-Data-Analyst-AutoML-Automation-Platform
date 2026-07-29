# ml_engine/data_cleaner.py
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from scipy import stats
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler, MinMaxScaler
import logging

logger = logging.getLogger(__name__)


class DataCleaner:
    """Automated data cleaning pipeline."""

    def __init__(self, df: pd.DataFrame, config: Optional[Dict] = None):
        self.df = df.copy()
        self.config = config or {}
        self.cleaning_log = []
        self.encoders = {}
        self.scalers = {}
        self.imputers = {}

    def run_full_pipeline(self) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Execute complete cleaning pipeline."""
        logger.info("Starting data cleaning pipeline...")

        # Step 1: Remove duplicates
        self._remove_duplicates()

        # Step 2: Handle missing values
        self._handle_missing_values()

        # Step 3: Handle outliers
        self._handle_outliers()

        # Step 4: Fix data types
        self._fix_data_types()

        # Step 5: Encode categorical variables
        self._encode_categoricals()

        # Step 6: Scale numerical features
        self._scale_features()

        # Step 7: Remove constant/low-variance columns
        self._remove_low_variance()

        report = {
            "original_shape": list(self.df.shape),
            "cleaning_steps": self.cleaning_log,
            "final_shape": list(self.df.shape),
            "remaining_missing": int(self.df.isnull().sum().sum()),
        }

        logger.info(f"Cleaning complete. Shape: {self.df.shape}")
        return self.df, report

    def _remove_duplicates(self):
        """Remove duplicate rows."""
        before = len(self.df)
        self.df = self.df.drop_duplicates().reset_index(drop=True)
        removed = before - len(self.df)
        if removed > 0:
            self.cleaning_log.append({
                "step": "remove_duplicates",
                "rows_removed": removed,
                "method": "exact_match",
            })
            logger.info(f"Removed {removed} duplicate rows")

    def _handle_missing_values(self):
        """Handle missing values using appropriate strategies."""
        strategy = self.config.get("missing_strategy", "auto")

        for col in self.df.columns:
            null_count = self.df[col].isnull().sum()
            if null_count == 0:
                continue

            null_pct = null_count / len(self.df)

            # If more than 70% missing, drop column
            if null_pct > 0.7:
                self.df.drop(col, axis=1, inplace=True)
                self.cleaning_log.append({
                    "step": "drop_column",
                    "column": col,
                    "reason": f"{null_pct*100:.1f}% missing",
                })
                continue

            # Determine imputation strategy
            if pd.api.types.is_numeric_dtype(self.df[col]):
                if strategy == "auto":
                    # Use median for skewed data, mean for normal
                    skewness = self.df[col].skew()
                    method = "median" if abs(skewness) > 1 else "mean"
                else:
                    method = strategy

                fill_value = self.df[col].median() if method == "median" else self.df[col].mean()
                self.df[col].fillna(fill_value, inplace=True)
                self.imputers[col] = {"method": method, "value": float(fill_value)}

            else:
                # Categorical: use mode
                mode_val = self.df[col].mode()
                if len(mode_val) > 0:
                    self.df[col].fillna(mode_val[0], inplace=True)
                    self.imputers[col] = {"method": "mode", "value": str(mode_val[0])}

            self.cleaning_log.append({
                "step": "impute_missing",
                "column": col,
                "null_count": int(null_count),
                "method": self.imputers[col]["method"],
            })

    def _handle_outliers(self):
        """Detect and handle outliers using IQR method."""
        method = self.config.get("outlier_method", "iqr")
        threshold = self.config.get("outlier_threshold", 1.5)

        numeric_cols = self.df.select_dtypes(include=[np.number]).columns

        for col in numeric_cols:
            if method == "iqr":
                Q1 = self.df[col].quantile(0.25)
                Q3 = self.df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower = Q1 - threshold * IQR
                upper = Q3 + threshold * IQR

                outliers = ((self.df[col] < lower) | (self.df[col] > upper)).sum()
                if outliers > 0 and outliers / len(self.df) < 0.1:  # Only if < 10%
                    self.df[col] = self.df[col].clip(lower=lower, upper=upper)
                    self.cleaning_log.append({
                        "step": "clip_outliers",
                        "column": col,
                        "outliers_clipped": int(outliers),
                        "method": "IQR",
                        "bounds": [float(lower), float(upper)],
                    })

            elif method == "zscore":
                z_scores = np.abs(stats.zscore(self.df[col].dropna()))
                outlier_mask = z_scores > threshold
                outliers = outlier_mask.sum()
                if outliers > 0:
                    median_val = self.df[col].median()
                    self.df.loc[self.df[col].notna() & outlier_mask, col] = median_val
                    self.cleaning_log.append({
                        "step": "replace_outliers",
                        "column": col,
                        "outliers_replaced": int(outliers),
                        "method": "zscore",
                    })

    def _fix_data_types(self):
        """Fix incorrect data types."""
        for col in self.df.columns:
            # Try to convert object columns that look numeric
            if self.df[col].dtype == "object":
                try:
                    converted = pd.to_numeric(self.df[col], errors="coerce")
                    if converted.notna().mean() > 0.8:
                        self.df[col] = converted
                        self.cleaning_log.append({
                            "step": "type_conversion",
                            "column": col,
                            "from": "object",
                            "to": "numeric",
                        })
                except (ValueError, TypeError):
                    pass

            # Try to detect datetime
            if self.df[col].dtype == "object":
                try:
                    converted = pd.to_datetime(self.df[col], errors="coerce", infer_datetime_format=True)
                    if converted.notna().mean() > 0.8:
                        self.df[col] = converted
                        self.cleaning_log.append({
                            "step": "type_conversion",
                            "column": col,
                            "from": "object",
                            "to": "datetime",
                        })
                except (ValueError, TypeError):
                    pass

    def _encode_categoricals(self):
        """Encode categorical variables."""
        encoding_method = self.config.get("encoding", "auto")
        cat_cols = self.df.select_dtypes(include=["object", "category"]).columns

        for col in cat_cols:
            n_unique = self.df[col].nunique()

            if encoding_method == "auto":
                method = "label" if n_unique <= 5 else "onehot"
            else:
                method = encoding_method

            if method == "label" or n_unique <= 5:
                le = LabelEncoder()
                self.df[col] = le.fit_transform(self.df[col].astype(str))
                self.encoders[col] = {"type": "label", "encoder": le}
            else:
                # One-hot encoding (limit to top 20 categories)
                if n_unique > 20:
                    top_cats = self.df[col].value_counts().head(20).index
                    self.df[col] = self.df[col].where(self.df[col].isin(top_cats), "other")

                dummies = pd.get_dummies(self.df[col], prefix=col, drop_first=True)
                self.df = pd.concat([self.df.drop(col, axis=1), dummies], axis=1)
                self.encoders[col] = {"type": "onehot", "categories": dummies.columns.tolist()}

            self.cleaning_log.append({
                "step": "encode",
                "column": col,
                "method": method,
                "n_categories": n_unique,
            })

    def _scale_features(self):
        """Scale numerical features."""
        scaling_method = self.config.get("scaling", "standard")
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns

        if len(numeric_cols) == 0:
            return

        if scaling_method == "standard":
            scaler = StandardScaler()
        elif scaling_method == "minmax":
            scaler = MinMaxScaler()
        else:
            scaler = StandardScaler()

        self.df[numeric_cols] = scaler.fit_transform(self.df[numeric_cols])
        self.scalers = {"columns": numeric_cols.tolist(), "scaler": scaler}

        self.cleaning_log.append({
            "step": "scale",
            "method": scaling_method,
            "columns_scaled": len(numeric_cols),
        })

    def _remove_low_variance(self):
        """Remove constant or near-constant columns."""
        cols_to_drop = []
        for col in self.df.columns:
            if self.df[col].nunique() <= 1:
                cols_to_drop.append(col)

        if cols_to_drop:
            self.df.drop(cols_to_drop, axis=1, inplace=True)
            self.cleaning_log.append({
                "step": "remove_low_variance",
                "columns_removed": cols_to_drop,
            })

    def get_cleaning_report(self) -> Dict[str, Any]:
        return {
            "steps_performed": len(self.cleaning_log),
            "log": self.cleaning_log,
            "encoders": {k: v["type"] for k, v in self.encoders.items()},
            "final_shape": list(self.df.shape),
        }
