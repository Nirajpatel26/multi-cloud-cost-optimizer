# Multi-Cloud Cost Optimization Platform

## Overview
Automated platform for analyzing and optimizing cloud costs across AWS, Azure, and OCI.

## Tech Stack
- **Backend:** Python, FastAPI, PostgreSQL
- **Orchestration:** Apache Airflow
- **CI/CD:** Jenkins
- **Container:** Docker, Kubernetes
- **IaC:** Terraform
- **Frontend:** React

## Project Structure
```
multi-cloud-cost-optimizer/
├── backend/           # FastAPI application
├── airflow/          # Airflow DAGs
├── terraform/        # Infrastructure as Code
├── frontend/         # React dashboard
├── k8s/             # Kubernetes manifests
├── jenkins/         # CI/CD pipelines
└── docs/            # Documentation
```

## Setup Instructions

### Prerequisites
- Docker & Docker Compose
- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- Jenkins 2.4+

### Quick Start
```bash
# Clone repository
git clone https://github.com/Nirajpatel26/multi-cloud-cost-optimizer.git
cd multi-cloud-cost-optimizer

# Start services
docker-compose up -d

# Access services
- Backend API: http://localhost:8000
- Airflow UI: http://localhost:8080
- Jenkins: http://localhost:8081
- Frontend: http://localhost:3000
```

## Development

### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Development
```bash
cd frontend
npm install
npm start
```

## License
MIT