# # backend/app/main.py
# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.middleware.gzip import GZipMiddleware
# from contextlib import asynccontextmanager
# import logging

# from app.config import settings
# from app.core.database import init_db
# from app.api.v1.router import api_router
# from app.core.exceptions import register_exception_handlers


# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     """Application lifespan events."""
#     logger.info("🚀 Starting AI AutoML Platform...")
#     init_db()
#     # Create directories
#     import os
#     for dir_path in [settings.UPLOAD_DIR, settings.MODEL_DIR, settings.REPORT_DIR]:
#         os.makedirs(dir_path, exist_ok=True)
#     logger.info("✅ Application started successfully")
#     yield
#     logger.info("👋 Shutting down...")


# app = FastAPI(
#     title=settings.APP_NAME,
#     version=settings.APP_VERSION,
#     description="Production-level AI-powered End-to-End Data Analytics and AutoML Platform",
#     lifespan=lifespan,
#     docs_url="/docs",
#     redoc_url="/redoc",
# )

# # Middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=settings.CORS_ORIGINS,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
# app.add_middleware(GZipMiddleware, minimum_size=1000)

# # Exception handlers
# register_exception_handlers(app)

# # Include routers
# app.include_router(api_router, prefix=settings.API_V1_PREFIX)


# @app.get("/health")
# async def health_check():
#     return {
#         "status": "healthy",
#         "version": settings.APP_VERSION,
#         "service": settings.APP_NAME,
#     }


# @app.get("/")
# async def root():
#     return {
#         "message": "AI Data Analyst & AutoML Automation Platform",
#         "docs": "/docs",
#         "api": settings.API_V1_PREFIX,
#     }

# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="AI AutoML Platform",
    version="1.0.0",
    description="AI-powered End-to-End Data Analytics and AutoML Platform",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "AI AutoML Platform",
    }


@app.get("/")
async def root():
    return {
        "message": "AI Data Analyst & AutoML Automation Platform",
        "docs": "/docs",
        "api": "/api/v1",
    }
