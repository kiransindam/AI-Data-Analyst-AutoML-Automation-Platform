# ml_engine/eda_engine.py
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
from plotly.subplots import make_subplots
from typing import Dict, Any, List
import base64
from io import BytesIO
import logging

logger = logging.getLogger(__name__)


class EDAEngine:
    """Automated Exploratory Data Analysis engine."""

    def __init__(self, df: pd.DataFrame, target_col: str = None):
        self.df = df
        self.target_col = target_col
        self.charts = []

    def generate_full_eda(self) -> Dict[str, Any]:
        """Generate complete EDA report."""
        report = {
            "statistical_summary": self._statistical_summary(),
            "correlation_analysis": self._correlation_analysis(),
            "distribution_analysis": self._distribution_analysis(),
            "categorical_analysis": self._categorical_analysis(),
            "target_analysis": self._target_analysis() if self.target_col else None,
            "charts": self._generate_charts(),
            "summary": self._generate_summary(),
        }
        return report

    def _statistical_summary(self) -> Dict[str, Any]:
        """Generate statistical summary."""
        numeric_df = self.df.select_dtypes(include=[np.number])
        summary = {
            "count": numeric_df.count().to_dict(),
            "mean": numeric_df.mean().round(4).to_dict(),
            "std": numeric_df.std().round(4).to_dict(),
            "min": numeric_df.min().to_dict(),
            "25%": numeric_df.quantile(0.25).to_dict(),
            "50%": numeric_df.median().to_dict(),
            "75%": numeric_df.quantile(0.75).to_dict(),
            "max": numeric_df.max().to_dict(),
            "skewness": numeric_df.skew().round(4).to_dict(),
            "kurtosis": numeric_df.kurtosis().round(4).to_dict(),
        }
        return summary

    def _correlation_analysis(self) -> Dict[str, Any]:
        """Compute correlation matrix."""
        numeric_df = self.df.select_dtypes(include=[np.number])
        if numeric_df.shape[1] < 2:
            return {"matrix": {}, "high_correlations": []}

        corr_matrix = numeric_df.corr()

        # Find highly correlated pairs
        high_corr = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                corr_val = corr_matrix.iloc[i, j]
                if abs(corr_val) > 0.7:
                    high_corr.append({
                        "feature_1": corr_matrix.columns[i],
                        "feature_2": corr_matrix.columns[j],
                        "correlation": round(float(corr_val), 4),
                    })

        high_corr.sort(key=lambda x: abs(x["correlation"]), reverse=True)

        return {
            "matrix": corr_matrix.round(4).to_dict(),
            "high_correlations": high_corr[:20],
            "target_correlations": (
                corr_matrix[self.target_col].drop(self.target_col).sort_values(
                    key=abs, ascending=False
                ).head(10).to_dict()
                if self.target_col and self.target_col in corr_matrix.columns
                else {}
            ),
        }

    def _distribution_analysis(self) -> Dict[str, Any]:
        """Analyze distributions of numeric columns."""
        from scipy import stats as scipy_stats

        distributions = {}
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns[:20]

        for col in numeric_cols:
            series = self.df[col].dropna()
            if len(series) < 10:
                continue

            # Normality test
            if len(series) > 5000:
                sample = series.sample(5000)
            else:
                sample = series

            stat, p_value = scipy_stats.shapiro(sample) if len(sample) <= 5000 else (0, 0)

            distributions[col] = {
                "is_normal": p_value > 0.05,
                "shapiro_p_value": round(float(p_value), 6),
                "skewness": round(float(series.skew()), 4),
                "kurtosis": round(float(series.kurtosis()), 4),
                "suggested_transform": (
                    "log" if series.skew() > 2 else
                    "sqrt" if series.skew() > 1 else
                    "none"
                ),
            }

        return distributions

    def _categorical_analysis(self) -> Dict[str, Any]:
        """Analyze categorical columns."""
        cat_cols = self.df.select_dtypes(include=["object", "category"]).columns[:15]
        analysis = {}

        for col in cat_cols:
            value_counts = self.df[col].value_counts()
            analysis[col] = {
                "n_unique": int(self.df[col].nunique()),
                "top_values": value_counts.head(10).to_dict(),
                "top_value_pct": round(float(value_counts.iloc[0] / len(self.df) * 100), 2) if len(value_counts) > 0 else 0,
                "entropy": round(float(-sum(
                    (value_counts / len(self.df)) * np.log2(value_counts / len(self.df) + 1e-10)
                )), 4),
            }

        return analysis

    def _target_analysis(self) -> Dict[str, Any]:
        """Analyze target variable."""
        if self.target_col not in self.df.columns:
            return {}

        target = self.df[self.target_col]
        analysis = {
            "distribution": target.value_counts().to_dict() if target.nunique() < 50 else None,
            "class_balance": (
                (target.value_counts(normalize=True) * 100).round(2).to_dict()
                if target.nunique() < 50 else None
            ),
            "is_imbalanced": (
                target.value_counts(normalize=True).min() < 0.2
                if target.nunique() < 50 else False
            ),
        }
        return analysis

    def _generate_charts(self) -> List[Dict[str, Any]]:
        """Generate Plotly charts."""
        charts = []
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns[:10]

        # 1. Correlation Heatmap
        if len(numeric_cols) >= 2:
            corr = self.df[numeric_cols].corr()
            fig = px.imshow(
                corr, text_auto=".2f", aspect="auto",
                title="Feature Correlation Heatmap",
                color_continuous_scale="RdBu_r",
            )
            fig.update_layout(width=800, height=600)
            charts.append({
                "type": "heatmap",
                "title": "Correlation Heatmap",
                "figure": fig.to_json(),
            })

        # 2. Distribution plots for top numeric columns
        for col in numeric_cols[:6]:
            fig = px.histogram(
                self.df, x=col, nbins=50,
                title=f"Distribution of {col}",
                marginal="box",
            )
            charts.append({
                "type": "histogram",
                "title": f"Distribution: {col}",
                "figure": fig.to_json(),
            })

        # 3. Box plots
        if len(numeric_cols) >= 2:
            fig = go.Figure()
            for col in numeric_cols[:8]:
                fig.add_trace(go.Box(y=self.df[col], name=col))
            fig.update_layout(title="Box Plots - Numeric Features", width=900, height=500)
            charts.append({
                "type": "boxplot",
                "title": "Box Plots",
                "figure": fig.to_json(),
            })

        # 4. Scatter plot (top 2 correlated features)
        if len(numeric_cols) >= 2:
            corr = self.df[numeric_cols].corr()
            # Find most correlated pair
            max_corr = 0
            pair = (numeric_cols[0], numeric_cols[1])
            for i in range(len(numeric_cols)):
                for j in range(i+1, len(numeric_cols)):
                    if abs(corr.iloc[i, j]) > abs(max_corr):
                        max_corr = corr.iloc[i, j]
                        pair = (numeric_cols[i], numeric_cols[j])

            fig = px.scatter(
                self.df, x=pair[0], y=pair[1],
                title=f"Scatter: {pair[0]} vs {pair[1]} (r={max_corr:.3f})",
                trendline="ols",
                opacity=0.6,
            )
            charts.append({
                "type": "scatter",
                "title": f"{pair[0]} vs {pair[1]}",
                "figure": fig.to_json(),
            })

        # 5. Target distribution
        if self.target_col and self.target_col in self.df.columns:
            target = self.df[self.target_col]
            if target.nunique() < 20:
                fig = px.bar(
                    target.value_counts().reset_index(),
                    x="index", y="count",
                    title=f"Target Variable Distribution: {self.target_col}",
                    color="count",
                )
            else:
                fig = px.histogram(
                    self.df, x=self.target_col, nbins=50,
                    title=f"Target Distribution: {self.target_col}",
                )
            charts.append({
                "type": "target_distribution",
                "title": "Target Distribution",
                "figure": fig.to_json(),
            })

        return charts

    def _generate_summary(self) -> str:
        """Generate text summary of EDA findings."""
        n_rows, n_cols = self.df.shape
        n_numeric = len(self.df.select_dtypes(include=[np.number]).columns)
        n_categorical = len(self.df.select_dtypes(include=["object", "category"]).columns)
        missing_pct = self.df.isnull().mean().mean() * 100

        summary = f"""
## EDA Summary

**Dataset Overview:**
- {n_rows:,} rows × {n_cols} columns
- {n_numeric} numeric features, {n_categorical} categorical features
- {missing_pct:.1f}% overall missing data

**Key Findings:**
"""
        # Add correlation findings
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) >= 2:
            corr = self.df[numeric_cols].corr()
            high_corr_pairs = []
            for i in range(len(corr)):
                for j in range(i+1, len(corr)):
                    if abs(corr.iloc[i, j]) > 0.7:
                        high_corr_pairs.append(f"{corr.columns[i]} & {corr.columns[j]}")
            if high_corr_pairs:
                summary += f"- Highly correlated features: {', '.join(high_corr_pairs[:5])}\n"

        # Target balance
        if self.target_col and self.target_col in self.df.columns:
            target = self.df[self.target_col]
            if target.nunique() < 20:
                balance = target.value_counts(normalize=True)
                if balance.min() < 0.2:
                    summary += f"- ⚠️ Target variable is imbalanced (minority class: {balance.min()*100:.1f}%)\n"

        return summary
