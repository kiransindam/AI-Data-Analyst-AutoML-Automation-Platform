# backend/app/services/analysis_service.py
import pandas as pd
import os
import logging
from typing import Dict, Any, Optional

from ml_engine.data_profiler import DataProfiler
from ml_engine.data_cleaner import DataCleaner
from ml_engine.eda_engine import EDAEngine
from agents.orchestrator import run_full_pipeline
from app.core.database import SessionLocal
from app.models.project import Project

logger = logging.getLogger(__name__)


class AnalysisService:
    """Service layer for data analysis operations."""

    @staticmethod
    def run_full_analysis(
        project_id: str,
        dataset_path: str,
        file_type: str,
        config: Optional[Dict] = None,
    ):
        """Run the complete analysis pipeline (background task)."""
        db = SessionLocal()
        try:
            # Update project status
            project = db.query(Project).filter(Project.id == project_id).first()
            if not project:
                return

            project.status = "analyzing"
            db.commit()

            # Run the agent pipeline
            final_state = run_full_pipeline(
                dataset_path=dataset_path,
                file_type=file_type,
                project_id=project_id,
                config=config or {},
            )

            # Store results
            project.results = {
                "data_quality": final_state.get("data_profile", {}),
                "cleaning": final_state.get("cleaning_report", {}),
                "eda": final_state.get("eda_report", {}),
                "insights": final_state.get("insights", {}),
                "ml_results": final_state.get("ml_results", {}),
                "evaluation": final_state.get("evaluation_report", {}),
                "report": final_state.get("final_report", {}),
            }
            project.status = "completed" if final_state.get("status") == "completed" else "failed"
            db.commit()

            logger.info(f"Analysis complete for project {project_id}")

        except Exception as e:
            logger.error(f"Analysis failed for project {project_id}: {e}")
            if project:
                project.status = "failed"
                project.results = {"error": str(e)}
                db.commit()
        finally:
            db.close()

    @staticmethod
    def load_dataframe(path: str, file_type: str) -> pd.DataFrame:
        """Load dataframe from file."""
        if file_type in ("csv", ".csv"):
            return pd.read_csv(path)
        elif file_type in ("xlsx", "xls", ".xlsx", ".xls"):
            return pd.read_excel(path)
        elif file_type in ("json", ".json"):
            return pd.read_json(path)
        elif file_type in ("parquet", ".parquet"):
            return pd.read_parquet(path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
