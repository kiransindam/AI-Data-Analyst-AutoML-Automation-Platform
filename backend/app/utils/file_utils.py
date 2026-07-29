# backend/app/utils/file_utils.py
import pandas as pd
import os
from typing import Dict, Any


def validate_file(filename: str, content_length: int) -> bool:
    """Validate uploaded file."""
    allowed_ext = {".csv", ".xlsx", ".xls", ".json", ".parquet"}
    ext = os.path.splitext(filename)[1].lower()
    if ext not in allowed_ext:
        return False
    if content_length > 500 * 1024 * 1024:  # 500MB
        return False
    return True


def get_file_metadata(file_path: str, file_type: str) -> Dict[str, Any]:
    """Extract metadata from uploaded file."""
    try:
        if file_type == ".csv":
            df = pd.read_csv(file_path, nrows=1000)
            total_rows = sum(1 for _ in open(file_path)) - 1
        elif file_type in (".xlsx", ".xls"):
            df = pd.read_excel(file_path)
            total_rows = len(df)
        elif file_type == ".json":
            df = pd.read_json(file_path)
            total_rows = len(df)
        elif file_type == ".parquet":
            df = pd.read_parquet(file_path)
            total_rows = len(df)
        else:
            return {}

        columns_info = {}
        for col in df.columns:
            columns_info[col] = {
                "dtype": str(df[col].dtype),
                "null_count": int(df[col].isnull().sum()),
                "unique_count": int(df[col].nunique()),
                "sample_values": df[col].dropna().head(5).tolist(),
            }

        return {
            "row_count": total_rows,
            "col_count": len(df.columns),
            "columns": columns_info,
            "memory_usage_mb": round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2),
        }
    except Exception as e:
        return {"error": str(e)}
