# backend/app/config.py
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "AI AutoML Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/automl_platform"
    MONGODB_URL: str = "mongodb://localhost:27017/automl_documents"
    REDIS_URL: str = "redis://localhost:6379/0"

    # Storage
    UPLOAD_DIR: str = "./uploads"
    MODEL_DIR: str = "./models"
    REPORT_DIR: str = "./reports"
    MAX_UPLOAD_SIZE: int = 500 * 1024 * 1024  # 500MB

    # AWS
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_S3_BUCKET: str = "automl-platform-storage"
    AWS_REGION: str = "us-east-1"

    # LLM
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    LLM_PROVIDER: str = "openai"  # openai, gemini, local
    LLM_MODEL: str = "gpt-4"

    # MLflow
    MLFLOW_TRACKING_URI: str = "http://localhost:5000"

    # Security
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:8501"]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
