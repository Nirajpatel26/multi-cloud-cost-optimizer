# AWS cost-related endpoints
from fastapi import APIRouter, Query, Depends
from typing import Optional
from datetime import datetime, timedelta
import logging

from app.schemas.aws_schemas import CostResponse, CostSummaryResponse
from app.services.aws_mock_service import AWSMockService
from app.core.dependencies import get_mock_service
from app.core.validators import validate_date_range
from app.core.exceptions import DatabaseConnectionError

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/aws/costs", response_model=CostResponse)
async def get_costs(
    start_date: Optional[str] = Query(None, description="Start date in YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format"),
    region: Optional[str] = Query(None, description="AWS region (e.g., us-east-1)"),
    service_name: Optional[str] = Query(None, description="AWS service name (e.g., EC2, S3)"),
    service: AWSMockService = Depends(get_mock_service)
):
    """
    Get cost data with optional filters
    
    Step 1: Validate date parameters
    Step 2: Fetch cost data from database through mock service
    Step 3: Apply filters (region, service_name)
    Step 4: Calculate total and return response
    """
    
    try:
        # Step 1: Validate and parse dates
        logger.info(f"Fetching costs - start: {start_date}, end: {end_date}, region: {region}, service: {service_name}")
        
        start_dt, end_dt = validate_date_range(start_date, end_date)
        
        # Set defaults if not provided (last 30 days)
        if not start_dt:
            start_dt = datetime.now() - timedelta(days=30)
        if not end_dt:
            end_dt = datetime.now()
        
        # Step 2: Fetch cost data from database
        logger.info("Querying database for cost data")
        cost_data = service.fetch_cost_data(
            start_date=start_dt,
            end_date=end_dt,
            granularity='DAILY'
        )
        
        # Step 3: Apply filters
        # Filter by region if provided
        if region:
            cost_data = [item for item in cost_data if item.get('region') == region]
        
        # Filter by service_name if provided
        if service_name:
            cost_data = [
                item for item in cost_data 
                if item.get('service_name', '').lower() == service_name.lower()
            ]
        
        # Step 4: Aggregate data by service
        service_costs = {}
        for item in cost_data:
            service = item.get('service_name', 'Unknown')
            cost = item.get('cost', 0.0)
            
            if service in service_costs:
                service_costs[service] += cost
            else:
                service_costs[service] = cost
        
        # Convert to list format for response
        breakdown_data = [
            {"service": service, "cost": cost}
            for service, cost in service_costs.items()
        ]
        
        total_cost = sum(item["cost"] for item in breakdown_data)
        
        logger.info(f"Successfully retrieved {len(cost_data)} cost records, total: ${total_cost:.2f}")
        
        # Step 5: Return response
        return {
            "filters": {
                "start_date": start_dt.strftime("%Y-%m-%d") if start_dt else None,
                "end_date": end_dt.strftime("%Y-%m-%d") if end_dt else None,
                "region": region,
                "service_name": service_name
            },
            "total_cost": round(total_cost, 2),
            "currency": "USD",
            "breakdown": breakdown_data
        }
        
    except DatabaseConnectionError:
        # Re-raise database errors (already handled by dependency)
        raise
    except Exception as e:
        # Log unexpected errors
        logger.error(f"Error fetching cost data: {str(e)}")
        raise DatabaseConnectionError(detail=f"Failed to fetch cost data: {str(e)}")


@router.get("/aws/costs/summary", response_model=CostSummaryResponse)
async def get_costs_summary(
    start_date: Optional[str] = Query(None, description="Start date in YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format"),
    service: AWSMockService = Depends(get_mock_service)
):
    """
    Get aggregated cost summary by service and region
    
    Step 1: Validate dates
    Step 2: Fetch cost data from database
    Step 3: Aggregate by service and region
    Step 4: Calculate percentages
    Step 5: Return summary
    """
    
    try:
        # Step 1: Validate dates
        logger.info(f"Fetching cost summary - start: {start_date}, end: {end_date}")
        
        start_dt, end_dt = validate_date_range(start_date, end_date)
        
        # Set defaults (last 30 days)
        if not start_dt:
            start_dt = datetime.now() - timedelta(days=30)
        if not end_dt:
            end_dt = datetime.now()
        
        # Step 2: Fetch cost data
        logger.info("Querying database for cost summary")
        cost_data = service.fetch_cost_data(
            start_date=start_dt,
            end_date=end_dt,
            granularity='DAILY'
        )
        
        # Step 3: Aggregate by service and region
        service_totals = {}
        region_totals = {}
        total_cost = 0.0
        
        for item in cost_data:
            cost = item.get('cost', 0.0)
            service_name = item.get('service_name', 'Unknown')
            region = item.get('region', 'Unknown')
            
            # Aggregate by service
            if service_name in service_totals:
                service_totals[service_name] += cost
            else:
                service_totals[service_name] = cost
            
            # Aggregate by region
            if region in region_totals:
                region_totals[region] += cost
            else:
                region_totals[region] = cost
            
            total_cost += cost
        
        # Step 4: Calculate percentages and format data
        by_service = []
        for service_name, cost in service_totals.items():
            percentage = (cost / total_cost * 100) if total_cost > 0 else 0
            by_service.append({
                "service_name": service_name,
                "total_cost": round(cost, 2),
                "percentage": round(percentage, 2)
            })
        
        by_region = []
        for region, cost in region_totals.items():
            percentage = (cost / total_cost * 100) if total_cost > 0 else 0
            by_region.append({
                "region": region,
                "total_cost": round(cost, 2),
                "percentage": round(percentage, 2)
            })
        
        logger.info(f"Cost summary generated - total: ${total_cost:.2f}, services: {len(by_service)}, regions: {len(by_region)}")
        
        # Step 5: Return summary
        return {
            "total_cost": round(total_cost, 2),
            "period": {
                "start_date": start_dt.strftime("%Y-%m-%d"),
                "end_date": end_dt.strftime("%Y-%m-%d")
            },
            "by_service": by_service,
            "by_region": by_region
        }
        
    except DatabaseConnectionError:
        raise
    except Exception as e:
        logger.error(f"Error generating cost summary: {str(e)}")
        raise DatabaseConnectionError(detail=f"Failed to generate cost summary: {str(e)}")
