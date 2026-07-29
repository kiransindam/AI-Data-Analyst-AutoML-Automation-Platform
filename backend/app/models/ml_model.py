# backend/app/models/ml_model.py
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class MLModel(Base):
    __tablename__ = "ml_models"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    name = Column(String(255), nullable=False)
    algorithm = Column(String(100), nullable=False)
    version = Column(Integer, default=1)
    problem_type = Column(String(50))  # classification, regression, clustering
    metrics = Column(JSON, nullable=True)  # {accuracy: 0.95, f1: 0.93, ...}
    hyperparameters = Column(JSON, nullable=True)
    feature_importance = Column(JSON, nullable=True)
    artifact_path = Column(String(1000), nullable=True)
    training_data_info = Column(JSON, nullable=True)
    status = Column(String(50), default="trained")
    # trained, deployed, archived, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="models")
    predictions = relationship("Prediction", back_populates="model", lazy="dynamic")
