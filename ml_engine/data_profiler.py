# ml_engine/data_profiler.py
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple
from scipy import stats
import logging

logger = logging.getLogger(__name__)


class DataProfiler:
    """Automated data profiling and understanding engine."""

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.profile = {}

    def generate_full_profile(self) -> Dict[str, Any]:
        """Generate comprehensive data profile."""
        self.profile = {
            "basic_info": self._basic_info(),
            "column_profiles": self._column_profiles(),
            "missing_analysis": self._missing_analysis(),
            "duplicate_analysis": self._duplicate_analysis(),
            "data_types": self._detect_data_types(),
            "target_detection": self._detect_target_variable(),
            "problem_type": self._detect_problem_type(),
            "business_domain": self._detect_business_domain(),
            "quality_score": self._calculate_quality_score(),
        }
        return self.profile

    def _basic_info(self) -> Dict[str, Any]:
        return {
            "rows": len(self.df),
            "columns": len(self.df.columns),
            "memory_usage_mb": round(self.df.memory_usage(deep=True).sum() / 1024 / 1024, 2),
            "column_names": self.df.columns.tolist(),
        }

    def _column_profiles(self) -> Dict[str, Any]:
        profiles = {}
        for col in self.df.columns:
            series = self.df[col]
            profile = {
                "dtype": str(series.dtype),
                "null_count": int(series.isnull().sum()),
                "null_percentage": round(series.isnull().mean() * 100, 2),
                "unique_count": int(series.nunique()),
                "is_numeric": pd.api.types.is_numeric_dtype(series),
                "is_categorical": pd.api.types.is_categorical_dtype(series) or series.nunique() < 20,
                "is_datetime": pd.api.types.is_datetime64_any_dtype(series),
            }

            if pd.api.types.is_numeric_dtype(series):
                profile.update({
                    "mean": round(float(series.mean()), 4) if not series.isnull().all() else None,
                    "median": round(float(series.median()), 4) if not series.isnull().all() else None,
                    "std": round(float(series.std()), 4) if not series.isnull().all() else None,
                    "min": float(series.min()) if not series.isnull().all() else None,
                    "max": float(series.max()) if not series.isnull().all() else None,
                    "q25": float(series.quantile(0.25)) if not series.isnull().all() else None,
                    "q75": float(series.quantile(0.75)) if not series.isnull().all() else None,
                    "skewness": round(float(series.skew()), 4),
                    "kurtosis": round(float(series.kurtosis()), 4),
                })
            else:
                value_counts = series.value_counts()
                profile.update({
                    "top_values": value_counts.head(10).to_dict(),
                    "most_frequent": str(value_counts.index[0]) if len(value_counts) > 0 else None,
                    "most_frequent_pct": round(float(value_counts.iloc[0] / len(series) * 100), 2) if len(value_counts) > 0 else None,
                })

            profiles[col] = profile
        return profiles

    def _missing_analysis(self) -> Dict[str, Any]:
        missing = self.df.isnull().sum()
        missing_pct = (missing / len(self.df) * 100).round(2)
        return {
            "total_missing_cells": int(missing.sum()),
            "columns_with_missing": int((missing > 0).sum()),
            "missing_by_column": {
                col: {"count": int(missing[col]), "percentage": float(missing_pct[col])}
                for col in self.df.columns if missing[col] > 0
            },
            "complete_rows": int(self.df.dropna().shape[0]),
            "complete_rows_pct": round(self.df.dropna().shape[0] / len(self.df) * 100, 2),
        }

    def _duplicate_analysis(self) -> Dict[str, Any]:
        dup_count = self.df.duplicated().sum()
        return {
            "duplicate_rows": int(dup_count),
            "duplicate_percentage": round(dup_count / len(self.df) * 100, 2),
            "duplicate_columns": self._find_duplicate_columns(),
        }

    def _find_duplicate_columns(self) -> List[Tuple[str, str]]:
        """Find columns with identical values."""
        duplicates = []
        cols = self.df.columns.tolist()
        for i in range(len(cols)):
            for j in range(i + 1, len(cols)):
                if self.df[cols[i]].equals(self.df[cols[j]]):
                    duplicates.append((cols[i], cols[j]))
        return duplicates

    def _detect_data_types(self) -> Dict[str, str]:
        """Enhanced data type detection."""
        types = {}
        for col in self.df.columns:
            series = self.df[col].dropna()
            if len(series) == 0:
                types[col] = "unknown"
            elif pd.api.types.is_datetime64_any_dtype(series):
                types[col] = "datetime"
            elif pd.api.types.is_numeric_dtype(series):
                if series.nunique() == 2 and set(series.unique()).issubset({0, 1}):
                    types[col] = "binary"
                elif series.nunique() < 20:
                    types[col] = "ordinal"
                else:
                    types[col] = "continuous"
            elif series.apply(lambda x: isinstance(x, str) and "@" in str(x)).mean() > 0.8:
                types[col] = "email"
            elif series.apply(lambda x: str(x).replace(".", "").replace("-", "").isdigit()).mean() > 0.8:
                types[col] = "phone/id"
            else:
                types[col] = "categorical" if series.nunique() < 50 else "text"
        return types

    def _detect_target_variable(self) -> Dict[str, Any]:
        """Heuristic target variable detection."""
        candidates = []
        target_keywords = ["target", "label", "class", "result", "outcome",
                          "y", "output", "prediction", "price", "amount", "revenue"]

        for col in self.df.columns:
            score = 0
            col_lower = col.lower()

            # Keyword matching
            for keyword in target_keywords:
                if keyword in col_lower:
                    score += 10

            # Binary classification target
            if self.df[col].nunique() == 2:
                score += 5

            # Low cardinality categorical (classification)
            if self.df[col].nunique() < 10 and not pd.api.types.is_numeric_dtype(self.df[col]):
                score += 3

            # Last column heuristic
            if col == self.df.columns[-1]:
                score += 2

            if score > 0:
                candidates.append({"column": col, "score": score})

        candidates.sort(key=lambda x: x["score"], reverse=True)
        return {
            "suggested_target": candidates[0]["column"] if candidates else None,
            "candidates": candidates[:5],
            "confidence": "high" if candidates and candidates[0]["score"] >= 10 else "medium",
        }

    def _detect_problem_type(self) -> Dict[str, Any]:
        """Detect ML problem type."""
        target_info = self._detect_target_variable()
        target_col = target_info.get("suggested_target")

        if not target_col:
            return {"type": "clustering", "confidence": "low", "reason": "No clear target variable"}

        series = self.df[target_col].dropna()
        n_unique = series.nunique()

        if n_unique == 2:
            return {"type": "binary_classification", "confidence": "high",
                    "reason": f"Target '{target_col}' has 2 unique values"}
        elif n_unique < 20 and not pd.api.types.is_numeric_dtype(series):
            return {"type": "multiclass_classification", "confidence": "high",
                    "reason": f"Target '{target_col}' has {n_unique} categories"}
        elif pd.api.types.is_numeric_dtype(series) and n_unique > 20:
            # Check if time series
            datetime_cols = [c for c in self.df.columns
                           if pd.api.types.is_datetime64_any_dtype(self.df[c])]
            if datetime_cols:
                return {"type": "time_series", "confidence": "medium",
                        "reason": "Numeric target with datetime column present"}
            return {"type": "regression", "confidence": "high",
                    "reason": f"Target '{target_col}' is continuous numeric"}
        else:
            return {"type": "regression", "confidence": "medium",
                    "reason": "Defaulting to regression"}

    def _detect_business_domain(self) -> Dict[str, str]:
        """Detect business domain from column names."""
        all_cols = " ".join(self.df.columns.str.lower().tolist())

        domains = {
            "sales": ["sales", "revenue", "order", "transaction", "purchase", "customer"],
            "finance": ["stock", "price", "interest", "loan", "credit", "balance", "profit"],
            "healthcare": ["patient", "diagnosis", "treatment", "disease", "medical", "health"],
            "marketing": ["campaign", "click", "conversion", "impression", "ad", "engagement"],
            "hr": ["employee", "salary", "department", "performance", "attrition", "hire"],
            "ecommerce": ["product", "cart", "review", "rating", "category", "inventory"],
            "manufacturing": ["machine", "sensor", "defect", "production", "quality", "maintenance"],
        }

        scores = {}
        for domain, keywords in domains.items():
            score = sum(1 for kw in keywords if kw in all_cols)
            if score > 0:
                scores[domain] = score

        if scores:
            best_domain = max(scores, key=scores.get)
            return {"domain": best_domain, "confidence": "high" if scores[best_domain] >= 3 else "medium"}
        return {"domain": "general", "confidence": "low"}

    def _calculate_quality_score(self) -> float:
        """Calculate overall data quality score (0-100)."""
        score = 100.0

        # Penalize missing values
        missing_pct = self.df.isnull().mean().mean() * 100
        score -= missing_pct * 0.5

        # Penalize duplicates
        dup_pct = self.df.duplicated().mean() * 100
        score -= dup_pct * 0.3

        # Penalize high cardinality categorical columns
        for col in self.df.select_dtypes(include=["object"]).columns:
            if self.df[col].nunique() / len(self.df) > 0.9:
                score -= 2

        # Penalize constant columns
        constant_cols = sum(1 for col in self.df.columns if self.df[col].nunique() <= 1)
        score -= constant_cols * 3

        return max(0, min(100, round(score, 2)))
