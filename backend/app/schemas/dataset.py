# backend/app/schemas/dataset.py
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid


class DatasetResponse(BaseModel):
    id: uuid.UUID
    filename: str
    file_type: str
    file_size: float
    row_count: Optional[int]
    col_count: Optional[int]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class DatasetPreview(BaseModel):
    columns: List[str]
    dtypes: Dict[str, str]
    data: List[Dict[str, Any]]
    total_rows: int
    total_cols: int
