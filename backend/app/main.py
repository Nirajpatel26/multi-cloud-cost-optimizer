# Main FastAPI application
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import health, costs, resources, recommendations, analytics
from app.api.v1.endpoints import azure_costs, azure_resources, azure_recommendations, azure_analytics

app = FastAPI(
    title="Multi Cloud Cost Optimizer API",
    version="1.0.0"
)

# Configure CORS to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# AWS Routers
app.include_router(health.router, prefix="/api/v1")
app.include_router(costs.router, prefix="/api/v1")
app.include_router(resources.router, prefix="/api/v1")
app.include_router(recommendations.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")

# Azure Routers
app.include_router(azure_costs.router, prefix="/api/v1")
app.include_router(azure_resources.router, prefix="/api/v1")
app.include_router(azure_recommendations.router, prefix="/api/v1")
app.include_router(azure_analytics.router, prefix="/api/v1")
