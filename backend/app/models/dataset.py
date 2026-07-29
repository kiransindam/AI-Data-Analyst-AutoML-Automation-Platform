# backend/app/models/dataset.py
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    filename = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False)  # csv, excel, json, sql
    file_size = Column(Float, nullable=False)  # in bytes
    storage_path = Column(String(1000), nullable=False)
    row_count = Column(Integer, nullable=True)
    col_count = Column(Integer, nullable=True)
    columns_info = Column(JSON, nullable=True)  # {col_name: dtype}
    metadata = Column(JSON, nullable=True)
    status = Column(String(50), default="uploaded")  # uploaded, processing, ready, error
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="datasets")
    projects = relationship("Project", back_populates="dataset", lazy="dynamic")
