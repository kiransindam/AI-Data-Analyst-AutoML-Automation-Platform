# backend/app/api/v1/endpoints/upload.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional
import uuid
import os
import aiofiles

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.dataset import Dataset
from app.schemas.dataset import DatasetResponse, DatasetPreview
from app.config import settings
from app.utils.file_utils import validate_file, get_file_metadata
from app.utils.validators import validate_file_type, validate_file_size

router = APIRouter()

ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls", ".json", ".parquet", ".sql"}
MAX_SIZE = settings.MAX_UPLOAD_SIZE


@router.post("/", response_model=DatasetResponse, status_code=201)
async def upload_file(
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upload a dataset file."""
    # Validate file
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{file_ext}' not supported. Allowed: {ALLOWED_EXTENSIONS}"
        )

    # Read and validate size
    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(status_code=413, detail="File too large (max 500MB)")

    # Save file
    file_id = str(uuid.uuid4())
    storage_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}{file_ext}")
    os.makedirs(os.path.dirname(storage_path), exist_ok=True)

    async with aiofiles.open(storage_path, "wb") as f:
        await f.write(content)

    # Extract metadata
    metadata = get_file_metadata(storage_path, file_ext)

    # Create database record
    dataset = Dataset(
        user_id=current_user.id,
        filename=file.filename,
        file_type=file_ext.lstrip("."),
        file_size=len(content),
        storage_path=storage_path,
        row_count=metadata.get("row_count"),
        col_count=metadata.get("col_count"),
        columns_info=metadata.get("columns"),
        metadata={"description": description, "original_filename": file.filename},
        status="uploaded",
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)

    return dataset


@router.get("/{dataset_id}/preview", response_model=DatasetPreview)
async def preview_dataset(
    dataset_id: uuid.UUID,
    rows: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Preview dataset content."""
    dataset = db.query(Dataset).filter(
        Dataset.id == dataset_id, Dataset.user_id == current_user.id
    ).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    import pandas as pd
    try:
        if dataset.file_type == "csv":
            df = pd.read_csv(dataset.storage_path, nrows=rows)
        elif dataset.file_type in ("xlsx", "xls"):
            df = pd.read_excel(dataset.storage_path, nrows=rows)
        elif dataset.file_type == "json":
            df = pd.read_json(dataset.storage_path, nrows=rows)
        elif dataset.file_type == "parquet":
            df = pd.read_parquet(dataset.storage_path).head(rows)
        else:
            raise HTTPException(status_code=400, detail="Unsupported format for preview")

        return DatasetPreview(
            columns=df.columns.tolist(),
            dtypes={col: str(dtype) for col, dtype in df.dtypes.items()},
            data=df.fillna("").to_dict(orient="records"),
            total_rows=dataset.row_count or len(df),
            total_cols=len(df.columns),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")


@router.get("/", response_model=list[DatasetResponse])
async def list_datasets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all user datasets."""
    return db.query(Dataset).filter(Dataset.user_id == current_user.id).all()


@router.delete("/{dataset_id}")
async def delete_dataset(
    dataset_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a dataset."""
    dataset = db.query(Dataset).filter(
        Dataset.id == dataset_id, Dataset.user_id == current_user.id
    ).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    # Remove file
    if os.path.exists(dataset.storage_path):
        os.remove(dataset.storage_path)

    db.delete(dataset)
    db.commit()
    return {"message": "Dataset deleted successfully"}
