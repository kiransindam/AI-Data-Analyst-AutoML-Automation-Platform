# backend/app/schemas/analysis.py
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uuid


class AnalysisRequest(BaseModel):
    dataset_id: uuid.UUID
    project_name: Optional[str] = None
    config: Optional[Dict[str, Any]] = None


class AnalysisResponse(BaseModel):
    project_id: str
    status: str
    message: str


class DataQualityReport(BaseModel):
    total_rows: int
    total_columns: int
    missing_values: Dict[str, int]
    duplicate_rows: int
    data_types: Dict[str, str]
    outliers: Dict[str, Any]
    quality_score: float
    recommendations: List[str]


class EDAReport(BaseModel):
    statistics: Dict[str, Any]
    correlations: Dict[str, Any]
    distributions: Dict[str, Any]
    charts: List[Dict[str, Any]]
    summary: str


class InsightReport(BaseModel):
    business_domain: str
    key_findings: List[str]
    recommendations: List[str]
    trends: List[str]
    anomalies: List[str]
    executive_summary: str
