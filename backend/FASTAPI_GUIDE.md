# FastAPI Development Guide

## Project Structure
```
backend/app/
├── main.py                          # FastAPI application entry point
├── api/
│   └── v1/
│       └── endpoints/
│           ├── health.py           # GET /health
│           ├── costs.py            # GET /aws/costs, GET /aws/costs/summary
│           ├── resources.py        # POST /aws/resources/scan, GET /aws/resources
│           ├── recommendations.py  # GET /aws/recommendations, GET /aws/recommendations/idle-instances
│           └── analytics.py        # GET /aws/savings, POST /aws/analyze
└── schemas/
    └── aws_schemas.py              # Pydantic models for request/response
```

## API Endpoints to Implement

### 1. Health Check (health.py)
- GET /health - Check API and database status

### 2. Cost Management (costs.py)
- GET /aws/costs - Get cost data with optional filters
- GET /aws/costs/summary - Get aggregated cost summary

### 3. Resource Management (resources.py)
- POST /aws/resources/scan - Trigger resource scanning
- GET /aws/resources - List all resources with filters

### 4. Recommendations (recommendations.py)
- GET /aws/recommendations - Get all optimization recommendations
- GET /aws/recommendations/idle-instances - Get idle instances
- GET /aws/recommendations/unattached-volumes - Get unattached volumes

### 5. Analytics (analytics.py)
- GET /aws/savings - Get potential savings summary
- POST /aws/analyze - Run full cost analysis

## Getting Started

1. Install FastAPI dependencies:
   ```bash
   pip install fastapi uvicorn
   ```

2. Start coding in main.py:
   - Create FastAPI app instance
   - Include routers from endpoints
   - Configure CORS

3. Implement each endpoint file:
   - Import FastAPI router
   - Define route functions
   - Use mock service from app/services/aws_mock_service.py

4. Run the application:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

5. Test endpoints at: http://localhost:8000/docs

## Database Connection
Use the existing mock service:
```python
from app.services.aws_mock_service import AWSMockService

mock_service = AWSMockService(
    database_url='postgresql://admin:admin@127.0.0.1:5433/cost_optimizer'
)
```
