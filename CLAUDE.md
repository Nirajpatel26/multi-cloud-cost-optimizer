# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Multi-Cloud Cost Optimization Platform — analyzes and optimizes cloud costs across AWS, Azure, and OCI. Surfaces idle/underutilized resources and cost savings recommendations through a React dashboard backed by a FastAPI API.

## Service Ports

| Service       | URL                      |
|---------------|--------------------------|
| Backend API   | http://localhost:8000    |
| Airflow UI    | http://localhost:8080 (admin/admin) |
| Jenkins       | http://localhost:8081    |
| Frontend      | http://localhost:3000    |
| PostgreSQL    | localhost:5433           |

## Commands

### Full Stack (Docker)

```bash
docker-compose up -d           # Start all services
docker-compose up -d --build   # Rebuild and start
docker-compose down            # Stop services
docker-compose down -v         # Stop and delete volumes
docker-compose logs -f backend # Tail backend logs
```

### Backend (local dev)

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload   # Runs on :8000
```

**Linting / formatting:**
```bash
black app/
flake8 app/
mypy app/
```

**Tests:**
```bash
pytest app/tests/ -v            # All backend tests
pytest app/tests/test_health.py -v   # Single test file
pytest app/tests/ -v --tb=short      # Short traceback (used in CI)
```

### Frontend (local dev)

```bash
cd frontend
npm install
npm start       # Dev server on :3000
npm test        # Jest tests
npm run build   # Production build
```

## Architecture

### Mock vs. Real AWS

The backend has two service implementations:

- `app/services/aws_mock_service.py` — uses `mock_data_generator.py`; zero-cost, no AWS credentials required.
- `app/services/aws_service.py` — calls real AWS APIs (Cost Explorer, EC2, CloudWatch).

`app/core/dependencies.py::get_service()` selects between them at runtime via env vars:
- `USE_REAL_AWS=true` or `SERVICE_MODE=aws` → real AWS
- Default → mock service

The `docker-compose.yml` runs the mock environment by default (`USE_REAL_AWS=false`, `SERVICE_MODE=mock`).

### Backend Structure

```
backend/app/
├── main.py              # FastAPI app, CORS config, router registration
├── api/v1/endpoints/    # Route handlers: costs, resources, recommendations, analytics, health
├── services/            # Business logic: aws_service, aws_mock_service, mock_data_generator
├── schemas/             # Pydantic request/response models (aws_schemas.py)
├── core/
│   ├── config.py        # Settings via pydantic-settings (loads .env)
│   ├── dependencies.py  # FastAPI dependency injection (get_service, get_db_session)
│   ├── exceptions.py    # Custom exception classes
│   └── validators.py    # Input validation helpers
└── tests/               # pytest tests
```

All API routes are prefixed `/api/v1`. The SQLAlchemy models for `aws_cost_data`, `aws_ec2_instances`, `aws_ebs_volumes`, and `aws_optimization_recommendations` tables are defined directly inside `aws_service.py` and `aws_mock_service.py` (not in `models/`).

### Frontend Structure

React 18 SPA using React Router v6, Recharts/Chart.js for visualization, Axios for API calls. Single page: `Dashboard.jsx` in `src/components/` with supporting pages in `src/pages/` and API client in `src/services/`.

### Airflow DAGs

Three DAGs in `airflow/dags/`:
- `aws_cost_optimization_mock.py` — mock pipeline for development
- `aws_cost_optimization_dag.py` — base DAG
- `aws_cost_optimization_production.py` — production pipeline

### CI/CD

Jenkins pipeline at `jenkins/pipelines/Jenkinsfile`:
1. Checkout → Install dependencies → Run `pytest app/tests/` → Build Docker images → `docker-compose up -d`

## Environment Configuration

Copy `.env.example` to `.env`. Key variables:

```
DB_HOST / DB_PORT / DB_NAME / DB_USER / DB_PASSWORD
USE_REAL_AWS=false          # Set true to use real AWS APIs
SERVICE_MODE=mock           # Set to "aws" for real AWS
AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY / AWS_REGION
AIRFLOW_FERNET_KEY          # Generate: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

The mock PostgreSQL runs on port **5433** (not 5432) to avoid conflicts with a local Postgres instance.
