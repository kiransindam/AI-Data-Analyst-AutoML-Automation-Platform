# backend/app/api/v1/router.py
from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth, upload, analysis, ml, predict, reports, dashboard, monitoring
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(upload.router, prefix="/upload", tags=["File Upload"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["Data Analysis"])
api_router.include_router(ml.router, prefix="/ml", tags=["Machine Learning"])
api_router.include_router(predict.router, prefix="/predict", tags=["Predictions"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(monitoring.router, prefix="/monitoring", tags=["Monitoring"])
