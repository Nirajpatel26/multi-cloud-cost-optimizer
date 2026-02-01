# Main FastAPI application
# TODO: Setup FastAPI app and include routers

from fastapi import FastAPI
from app.api.v1.endpoints import health, costs, resources, recommendations, analytics

app = FastAPI(
    title="AWS Cost Optimizer API",
    version="1.0.0"
)

# Register Routers
app.include_router(health.router, prefix="/api/v1")
app.include_router(costs.router, prefix="/api/v1")
app.include_router(resources.router, prefix="/api/v1")
app.include_router(recommendations.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")
