# backend/app/api/v1/endpoints/analysis.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional
import uuid

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.dataset import Dataset
from app.models.project import Project
from app.schemas.analysis import (
    AnalysisRequest, AnalysisResponse,
    EDAReport, DataQualityReport, InsightReport
)
from app.services.analysis_service import AnalysisService

router = APIRouter()


@router.post("/start", response_model=AnalysisResponse)
async def start_analysis(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Start full data analysis pipeline."""
    dataset = db.query(Dataset).filter(
        Dataset.id == request.dataset_id,
        Dataset.user_id == current_user.id
    ).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    # Create project
    project = Project(
        user_id=current_user.id,
        dataset_id=dataset.id,
        name=request.project_name or f"Analysis - {dataset.filename}",
        status="analyzing",
        config=request.config,
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    # Run analysis in background
    background_tasks.add_task(
        AnalysisService.run_full_analysis,
        project_id=str(project.id),
        dataset_path=dataset.storage_path,
        file_type=dataset.file_type,
        config=request.config,
    )

    return AnalysisResponse(
        project_id=str(project.id),
        status="analyzing",
        message="Analysis started. Check status endpoint for progress.",
    )


@router.get("/{project_id}/status")
async def get_analysis_status(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get analysis progress."""
    project = db.query(Project).filter(
        Project.id == project_id, Project.user_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return {
        "project_id": str(project.id),
        "status": project.status,
        "results": project.results,
    }


@router.get("/{project_id}/data-quality", response_model=DataQualityReport)
async def get_data_quality(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get data quality report."""
    project = db.query(Project).filter(
        Project.id == project_id, Project.user_id == current_user.id
    ).first()
    if not project or not project.results:
        raise HTTPException(status_code=404, detail="Analysis not available")

    return project.results.get("data_quality", {})


@router.get("/{project_id}/eda", response_model=EDAReport)
async def get_eda_report(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get EDA report with charts."""
    project = db.query(Project).filter(
        Project.id == project_id, Project.user_id == current_user.id
    ).first()
    if not project or not project.results:
        raise HTTPException(status_code=404, detail="Analysis not available")

    return project.results.get("eda", {})


@router.get("/{project_id}/insights", response_model=InsightReport)
async def get_insights(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get AI-generated business insights."""
    project = db.query(Project).filter(
        Project.id == project_id, Project.user_id == current_user.id
    ).first()
    if not project or not project.results:
        raise HTTPException(status_code=404, detail="Analysis not available")

    return project.results.get("insights", {})
