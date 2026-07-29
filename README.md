<div align="center">

# 🤖 AI Data Analyst & AutoML Automation Platform

### Production-Level AI-Powered End-to-End Data Analytics and AutoML Platform

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)
[![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF.svg)](.github/workflows)
[![Code Style](https://img.shields.io/badge/Code%20Style-Ruff-000000.svg)](https://github.com/astral-sh/ruff)

[![Stars](https://img.shields.io/github/stars/yourusername/ai-automl-platform?style=social)](https://github.com/yourusername/ai-automl-platform/stargazers)
[![Forks](https://img.shields.io/github/forks/yourusername/ai-automl-platform?style=social)](https://github.com/yourusername/ai-automl-platform/network/members)

**Upload any dataset → AI automatically analyzes, cleans, builds ML models, generates reports, deploys APIs, and monitors performance.**

[Demo](#) | [Documentation](docs/) | [API Reference](#-api-reference) | [Report Bug](issues) | [Request Feature](issues)

</div>

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Technology Stack](#-technology-stack)
- [Project Structure](#-project-structure)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Usage Guide](#-usage-guide)
- [API Reference](#-api-reference)
- [AI Agent Pipeline](#-ai-agent-pipeline)
- [ML Automation](#-ml-automation)
- [Dashboard](#-dashboard)
- [Database Design](#-database-design)
- [Security](#-security)
- [Docker Deployment](#-docker-deployment)
- [Cloud Deployment](#-cloud-deployment)
- [CI/CD Pipeline](#-cicd-pipeline)
- [Monitoring & Observability](#-monitoring--observability)
- [Automatic Retraining](#-automatic-retraining)
- [Testing](#-testing)
- [Configuration](#-configuration)
- [Contributing](#-contributing)
- [Roadmap](#-roadmap)
- [Resume & Interview Guide](#-resume--interview-guide)
- [Future Improvements](#-future-improvements)
- [License](#-license)
- [Acknowledgments](#-acknowledgments)
- [Contact](#-contact)

---

## 🎯 Overview

The **AI Data Analyst & AutoML Automation Platform** is an intelligent, autonomous system that acts as a virtual Data Analyst. Users simply upload a dataset (CSV, Excel, JSON, Parquet, or SQL), and the platform automatically performs the entire data science lifecycle:

This eliminates the need for manual data science workflows, reducing what typically takes **weeks of analyst work** to **minutes of automated processing**.

### 🎬 What It Does

| Step | Action | Output |
|------|--------|--------|
| 1 | **Data Understanding** | Schema detection, type inference, domain identification |
| 2 | **Data Cleaning** | Missing values, outliers, encoding, scaling |
| 3 | **EDA** | Statistical analysis, correlation, distributions, charts |
| 4 | **Business Insights** | LLM-generated recommendations & executive summary |
| 5 | **ML Model Building** | Auto algorithm selection, training, hyperparameter tuning |
| 6 | **Model Evaluation** | Cross-validation, metrics comparison, feature importance |
| 7 | **Report Generation** | PDF, PowerPoint, Excel reports |
| 8 | **Dashboard** | Interactive Streamlit/Plotly dashboard |
| 9 | **API Generation** | RESTful prediction endpoints |
| 10 | **Deployment** | Docker, cloud-ready infrastructure |
| 11 | **Monitoring** | Drift detection, performance tracking |
| 12 | **Retraining** | Automatic model refresh on data drift |

---

## ✨ Key Features

### 🧠 AI-Powered Analysis
- **Autonomous AI Agents** (LangGraph) orchestrate the entire pipeline
- **LLM Integration** (OpenAI GPT-4 / Gemini) for business insight generation
- **Automatic Problem Detection** — classification, regression, clustering, time series
- **Smart Target Variable Detection** using heuristics and statistical analysis

### 📊 Data Processing
- **Multi-format Support** — CSV, Excel, JSON, Parquet, SQL databases
- **Automated Data Profiling** — 50+ statistical metrics per column
- **Intelligent Cleaning** — context-aware imputation, outlier handling
- **Feature Engineering** — automatic encoding, scaling, transformation

### 🤖 AutoML Engine
- **Multi-algorithm Training** — XGBoost, LightGBM, Random Forest, SVM, Logistic Regression
- **Hyperparameter Tuning** — GridSearchCV with intelligent parameter grids
- **Model Comparison** — side-by-side metrics across all trained models
- **Cross-Validation** — configurable K-fold with stratification
- **Model Versioning** — MLflow integration for experiment tracking

### 📈 Visualization & Reporting
- **Interactive EDA Charts** — Plotly heatmaps, distributions, scatter plots
- **Auto-generated Reports** — PDF, PPTX, XLSX with executive summaries
- **Real-time Dashboard** — Streamlit + Plotly with KPIs and drill-down
- **Business Recommendations** — AI-generated actionable insights

### 🚀 Production Ready
- **RESTful API** — FastAPI with auto-generated OpenAPI docs
- **Authentication** — JWT + Role-Based Access Control
- **Containerized** — Docker + Docker Compose (12 services)
- **CI/CD** — GitHub Actions with automated testing and deployment
- **Monitoring** — Prometheus + Grafana + custom ML metrics
- **Scalable** — Horizontal scaling, Redis caching, connection pooling

### 🔄 MLOps
- **Data Drift Detection** — KS-test, Chi-squared, PSI metrics
- **Automatic Retraining** — triggered on drift or performance degradation
- **Model Registry** — versioned model artifacts with metadata
- **Prediction Logging** — full audit trail of all predictions

---

## 🏗️ System Architecture
┌─────────────────────────────────────────────────────────────────────────┐
│ CLIENT LAYER │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│ │ Next.js │ │ Streamlit │ │ API Client │ │
│ │ Frontend │ │ Dashboard │ │ (cURL/SDK) │ │
│ └──────┬──────┘ └──────┬──────┘ └──────┬──────┘ │
└──────────┼───────────────────┼───────────────────┼──────────────────────┘
│ │ │
▼ ▼ ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ NGINX REVERSE PROXY / API GATEWAY │
│ SSL Termination │ Rate Limiting │ Load Balancing │
└──────────────────────────────┬──────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────────────┐
│ BACKEND SERVICE (FastAPI) │
│ │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ API Layer: /auth │ /upload │ /analysis │ /ml │ /predict │ ... │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│ │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ Service Layer: Upload │ Analysis │ ML │ Prediction │ Report │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│ │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ AI AGENT ORCHESTRATION (LangGraph State Machine) │ │
│ │ │ │
│ │ [Data Understanding] → [Cleaning] → [EDA] → [Insights] → │ │
│ │ [ML Decision] → [Training] → [Evaluation] → [Report] │ │
│ └─────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────┬──────────────────────────────────────────┘
│
┌───────────────────┼───────────────────┐
▼ ▼ ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ PostgreSQL │ │ MongoDB │ │ Redis │
│ (Metadata) │ │ (Documents) │ │ (Cache) │
└─────────────────┘ └─────────────────┘ └─────────────────┘
│ │ │
▼ ▼ ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ AWS S3 │ │ MLflow │ │ Prometheus + │
│ (File Store) │ │ (ML Tracking) │ │ Grafana │
└─────────────────┘ └─────────────────┘ └─────────────────┘

---

## 🛠️ Technology Stack

| Layer | Technologies |
|-------|-------------|
| **Backend** | Python 3.11, FastAPI, Uvicorn, Pydantic v2 |
| **Frontend** | Next.js 14, React 18, TypeScript, Tailwind CSS, Zustand |
| **Dashboard** | Streamlit, Plotly, Recharts |
| **Data Processing** | Pandas, NumPy, Polars, PyArrow |
| **Machine Learning** | Scikit-learn, XGBoost, LightGBM |
| **AutoML** | PyCaret, AutoGluon (optional) |
| **AI / LLM** | LangChain, LangGraph, LlamaIndex, OpenAI API, Gemini API |
| **Database** | PostgreSQL 16, MongoDB 7, Redis 7 |
| **ML Ops** | MLflow, Joblib, Prometheus, Grafana |
| **Visualization** | Plotly, Matplotlib, Seaborn |
| **Reports** | ReportLab (PDF), python-pptx, XlsxWriter |
| **Cloud** | AWS (EC2, S3, RDS), Docker, Nginx |
| **DevOps** | Docker, Docker Compose, GitHub Actions, Terraform |
| **Security** | JWT, bcrypt, RBAC, CORS, Rate Limiting |
| **Testing** | Pytest, pytest-cov, httpx |

---

## 📁 Project Structure
AI-AutoML-Platform/
│
├── backend/ # FastAPI Backend Service
│ ├── app/
│ │ ├── main.py # Application entry point
│ │ ├── config.py # Settings & environment config
│ │ ├── api/v1/endpoints/ # API route handlers
│ │ │ ├── auth.py # Authentication (register, login, JWT)
│ │ │ ├── upload.py # File upload & dataset management
│ │ │ ├── analysis.py # Data analysis pipeline triggers
│ │ │ ├── ml.py # Model training & management
│ │ │ ├── predict.py # Prediction endpoints
│ │ │ ├── reports.py # Report generation & download
│ │ │ ├── dashboard.py # Dashboard data endpoints
│ │ │ └── monitoring.py # Model monitoring & health
│ │ ├── core/ # Core infrastructure
│ │ │ ├── security.py # JWT, password hashing, RBAC
│ │ │ ├── database.py # SQLAlchemy engine & sessions
│ │ │ ├── redis_client.py # Redis connection
│ │ │ └── exceptions.py # Custom exception handlers
│ │ ├── models/ # SQLAlchemy ORM models
│ │ ├── schemas/ # Pydantic request/response schemas
│ │ ├── services/ # Business logic layer
│ │ └── utils/ # Helper utilities
│ ├── requirements.txt
│ ├── Dockerfile
│ └── .env.example
│
├── ml_engine/ # Machine Learning Engine
│ ├── data_profiler.py # Automated data profiling
│ ├── data_cleaner.py # Data cleaning pipeline
│ ├── eda_engine.py # Exploratory Data Analysis
│ ├── feature_engineer.py # Feature engineering
│ ├── automl_pipeline.py # AutoML training & evaluation
│ ├── prediction_engine.py # Inference engine
│ ├── drift_detector.py # Data/concept drift detection
│ └── retraining_pipeline.py # Automatic retraining
│
├── agents/ # AI Agent System (LangGraph)
│ ├── orchestrator.py # Pipeline state machine
│ ├── data_understanding_agent.py
│ ├── data_cleaning_agent.py
│ ├── eda_agent.py
│ ├── insight_agent.py # LLM-powered insights
│ ├── ml_decision_agent.py
│ ├── model_training_agent.py
│ ├── evaluation_agent.py
│ ├── report_agent.py
│ └── monitoring_agent.py
│
├── frontend/ # Next.js Frontend
│ ├── src/
│ │ ├── app/ # App router pages
│ │ │ ├── login/page.tsx
│ │ │ ├── dashboard/page.tsx
│ │ │ ├── upload/page.tsx
│ │ │ ├── analysis/page.tsx
│ │ │ ├── models/page.tsx
│ │ │ └── reports/page.tsx
│ │ ├── components/ # Reusable UI components
│ │ ├── services/api.ts # API client (Axios)
│ │ ├── store/useStore.ts # Zustand state management
│ │ └── types/ # TypeScript interfaces
│ ├── package.json
│ ├── tailwind.config.js
│ └── Dockerfile
│
├── dashboard/ # Streamlit Dashboard
│ ├── app.py # Main dashboard application
│ ├── requirements.txt
│ └── Dockerfile
│
├── data_pipeline/ # Data Ingestion & Transformation
│ ├── ingestion.py
│ ├── transformation.py
│ └── validation.py
│
├── deployment/ # Infrastructure & Deployment
│ ├── docker/
│ │ ├── docker-compose.yml # Development (12 services)
│ │ ├── docker-compose.prod.yml
│ │ └── nginx/nginx.conf
│ ├── kubernetes/ # K8s manifests
│ ├── terraform/ # AWS infrastructure as code
│ └── scripts/ # Deployment scripts
│
├── monitoring/ # Observability
│ ├── prometheus/prometheus.yml
│ ├── grafana/dashboards/
│ └── alerting/alert_rules.yml
│
├── tests/ # Test Suite
│ ├── unit/ # Unit tests
│ ├── integration/ # Integration tests
│ └── conftest.py # Pytest fixtures
│
├── docs/ # Documentation
│ ├── API.md
│ ├── ARCHITECTURE.md
│ ├── DEPLOYMENT.md
│ └── USER_GUIDE.md
│
├── .github/workflows/ # CI/CD Pipelines
│ ├── ci.yml # Lint → Test → Build
│ ├── cd.yml # Deploy to production
│ └── ml-pipeline.yml # ML-specific workflows
│
├── .env.example # Environment template
├── .gitignore
├── Makefile # Common commands
├── pyproject.toml # Python project config
└── README.md # This file


---

## 🚀 Quick Start

### Prerequisites

- **Docker** ≥ 24.0 & **Docker Compose** ≥ 2.20
- **Python** ≥ 3.11 (for local development)
- **Node.js** ≥ 20 (for frontend development)
- **Git** ≥ 2.40

### One-Command Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/ai-automl-platform.git
cd ai-automl-platform

# Copy environment file
cp .env.example .env
# Edit .env with your API keys (OPENAI_API_KEY, AWS keys, etc.)

# Start all services with Docker
docker compose -f deployment/docker/docker-compose.yml up -d --build

# Access the platform
# Frontend:    http://localhost:3000
# API Docs:    http://localhost:8000/docs
# Dashboard:   http://localhost:8501
# MLflow:      http://localhost:5000
# Grafana:     http://localhost:3001
# Prometheus:  http://localhost:9090

┌────────────────────┐
│  Data Understanding │ ← Profiles data, detects types, identifies target
│       Agent         │
└─────────┬──────────┘
          ▼
┌────────────────────┐
│   Data Cleaning     │ ← Handles missing values, outliers, encoding
│       Agent         │
└─────────┬──────────┘
          ▼
┌────────────────────┐
│      EDA Agent      │ ← Statistics, correlations, distributions, charts
└─────────┬──────────┘
          ▼
┌────────────────────┐
│   Insight Agent     │ ← LLM generates business recommendations
│   (LLM-Powered)    │
└─────────┬──────────┘
          ▼
┌────────────────────┐
│  ML Decision Agent  │ ← Selects algorithms, problem type
└─────────┬──────────┘
          ▼
┌────────────────────┐
│  Training Agent     │ ← Trains models, tunes hyperparameters
└─────────┬──────────┘
          ▼
┌────────────────────┐
│ Evaluation Agent    │ ← Metrics, comparison, feature importance
└─────────┬──────────┘
          ▼
┌────────────────────┐
│   Report Agent      │ ← Generates PDF/PPTX/XLSX reports
└────────────────────┘

                    ┌─────────────┐
                    │  Route 53   │
                    │  (DNS)      │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │ CloudFront  │
                    │   (CDN)     │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
       ┌──────▼──────┐    │    ┌──────▼──────┐
       │  Vercel /   │    │    │   AWS ALB   │
       │  S3+CF      │    │    │ (Load       │
       │ (Frontend)  │    │    │  Balancer)  │
       └─────────────┘    │    └──────┬──────┘
                           │           │
                           │    ┌──────▼──────┐
                           │    │  EC2 / ECS  │
                           │    │  (Backend)  │
                           │    └──────┬──────┘
                           │           │
                    ┌──────┼───────────┼──────────┐
                    │      │           │          │
             ┌──────▼──┐ ┌─▼────┐ ┌───▼───┐ ┌───▼───┐
             │  RDS    │ │ S3   │ │ElastiCache│ │ MLflow│
             │(Postgres)│ │(Files)│ │ (Redis) │ │(EC2) │
             └─────────┘ └──────┘ └─────────┘ └───────┘
New Data Arrives
       │
       ▼
┌─────────────────┐
│ Drift Detection │ ← KS-test, Chi-squared, PSI
└────────┬────────┘
         │ (drift detected)
         ▼
┌─────────────────┐
│ Data Validation │ ← Schema check, quality gates
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Model Training │ ← Full AutoML pipeline on combined data
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Comparison     │ ← New vs. Old model metrics
└────────┬────────┘
         │ (improvement > 1%)
         ▼
┌─────────────────┐
│  Deploy New     │ ← Swap model artifact, update registry
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Notify         │ ← Slack/email alert with results
└─────────────────┘

tests/
├── unit/                    # Isolated component tests
│   ├── test_upload.py       # File upload validation
│   ├── test_cleaning.py     # Data cleaning logic
│   ├── test_eda.py          # EDA computations
│   ├── test_ml.py           # AutoML pipeline
│   └── test_api.py          # Endpoint behavior
├── integration/             # Multi-component tests
│   ├── test_pipeline.py     # Full analysis pipeline
│   └── test_agents.py       # Agent orchestration
└── conftest.py              # Shared fixtures



---

This README is a **single, self-contained file** that covers:

| Section | Content |
|---------|---------|
| Overview | What the platform does, visual workflow |
| Features | All 14 capabilities with details |
| Architecture | Full system diagram |
| Tech Stack | Every technology with purpose |
| Project Structure | Complete folder tree with descriptions |
| Quick Start | One-command Docker setup |
| Installation | 3 options (Docker, local, Makefile) |
| Usage Guide | Step-by-step curl examples |
| API Reference | All 25+ endpoints in a table |
| AI Agents | LangGraph pipeline explanation |
| ML Automation | Algorithms, metrics, pipeline steps |
| Database | ER relationships, table descriptions |
| Security | JWT, RBAC, encryption, headers |
| Docker | All 12 services, commands |
| Cloud | AWS architecture, Terraform |
| CI/CD | Pipeline stages, workflows |
| Monitoring | Metrics, alerts, Grafana |
| Retraining | Trigger conditions, pipeline flow |
| Testing | Structure, commands, coverage |
| Configuration | All environment variables |
| Contributing | Workflow, code style, commits |
| Roadmap | 6 phases with checkboxes |
| Resume/Interview | Ready-to-use descriptions + Q&A |
| Future Work | Prioritized enhancement table |
| License | MIT full text |

Copy this directly into your repository's `README.md` file. Replace `Kiransindam`, email, and links with your actual information.


MIT License

Copyright (c) 2026 AI AutoML Platform Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
