# AWS cost-related endpoints
from fastapi import APIRouter, Query
from typing import Optional

from app.schemas.aws_schemas import CostResponse, CostSummaryResponse

router = APIRouter()


@router.get("/aws/costs", response_model=CostResponse)
async def get_costs(
    start_date: Optional[str] = Query(
        None, description="Start date in YYYY-MM-DD format"
    ),
    end_date: Optional[str] = Query(
        None, description="End date in YYYY-MM-DD format"
    ),
    region: Optional[str] = Query(
        None, description="AWS region (e.g., us-east-1)"
    ),
    service_name: Optional[str] = Query(
        None, description="AWS service name (e.g., EC2, S3)"
    )
):
    """Get cost data with optional filters"""
    
    # TODO: Replace with actual database query
    breakdown_data = [
        {"service": "EC2", "cost": 180.50},
        {"service": "S3", "cost": 70.25},
        {"service": "RDS", "cost": 95.30}
    ]

    if service_name:
        breakdown_data = [
            item for item in breakdown_data
            if item["service"].lower() == service_name.lower()
        ]

    total_cost = sum(item["cost"] for item in breakdown_data)

    return {
        "filters": {
            "start_date": start_date,
            "end_date": end_date,
            "region": region,
            "service_name": service_name
        },
        "total_cost": total_cost,
        "currency": "USD",
        "breakdown": breakdown_data
    }


@router.get("/aws/costs/summary", response_model=CostSummaryResponse)
async def get_costs_summary(
    start_date: Optional[str] = Query(
        None, description="Start date in YYYY-MM-DD format"
    ),
    end_date: Optional[str] = Query(
        None, description="End date in YYYY-MM-DD format"
    )
):
    """Get aggregated cost summary by service and region"""
    
    # TODO: Replace with actual database query and aggregation
    total_cost = 1250.75
    
    by_service = [
        {"service_name": "EC2", "total_cost": 850.25, "percentage": 68.0},
        {"service_name": "S3", "total_cost": 200.50, "percentage": 16.0},
        {"service_name": "RDS", "total_cost": 200.00, "percentage": 16.0}
    ]
    
    by_region = [
        {"region": "us-east-1", "total_cost": 900.00, "percentage": 72.0},
        {"region": "us-west-2", "total_cost": 350.75, "percentage": 28.0}
    ]
    
    return {
        "total_cost": total_cost,
        "period": {
            "start_date": start_date or "2026-01-01",
            "end_date": end_date or "2026-01-31"
        },
        "by_service": by_service,
        "by_region": by_region
    }
