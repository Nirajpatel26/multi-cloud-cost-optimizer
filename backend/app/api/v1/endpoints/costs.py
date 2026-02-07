# AWS cost-related endpoints
from fastapi import APIRouter, Query, Depends
from typing import Optional
from datetime import datetime, timedelta
import logging

from app.schemas.aws_schemas import CostResponse, CostSummaryResponse
from app.services.aws_mock_service import AWSCostData
from app.core.dependencies import get_service
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
    service = Depends(get_service)
):
    """
    Get cost data from database (read-only, no regeneration)
    """
    
    try:
        logger.info(f"Fetching costs from database - filters: region={region}, service={service_name}")
        
        # Validate dates
        start_dt, end_dt = validate_date_range(start_date, end_date)
        
        # Query database directly
        db_session = service.get_db_session()
        
        try:
            query = db_session.query(AWSCostData)
            
            # Apply filters
            if start_dt:
                query = query.filter(AWSCostData.start_date >= start_dt)
            if end_dt:
                query = query.filter(AWSCostData.end_date <= end_dt)
            if region:
                query = query.filter(AWSCostData.region == region)
            if service_name:
                query = query.filter(AWSCostData.service_name == service_name)
            
            cost_records = query.all()
            
            # Aggregate by service
            service_costs = {}
            for record in cost_records:
                service = record.service_name
                cost = record.cost
                
                if service in service_costs:
                    service_costs[service] += cost
                else:
                    service_costs[service] = cost
            
            breakdown_data = [
                {"service": service, "cost": cost}
                for service, cost in service_costs.items()
            ]
            
            total_cost = sum(item["cost"] for item in breakdown_data)
            
        finally:
            db_session.close()
        
        logger.info(f"Retrieved {len(cost_records)} cost records, total: ${total_cost:.2f}")
        
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
        raise
    except Exception as e:
        logger.error(f"Error fetching cost data: {str(e)}")
        raise DatabaseConnectionError(detail=f"Failed to fetch cost data: {str(e)}")


@router.get("/aws/costs/summary", response_model=CostSummaryResponse)
async def get_costs_summary(
    start_date: Optional[str] = Query(None, description="Start date in YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format"),
    service = Depends(get_service)
):
    """
    Get cost summary from database (read-only, no regeneration)
    """
    
    try:
        logger.info("Fetching cost summary from database")
        
        # Validate dates
        start_dt, end_dt = validate_date_range(start_date, end_date)
        
        # Query database directly
        db_session = service.get_db_session()
        
        try:
            query = db_session.query(AWSCostData)
            
            if start_dt:
                query = query.filter(AWSCostData.start_date >= start_dt)
            if end_dt:
                query = query.filter(AWSCostData.end_date <= end_dt)
            
            cost_records = query.all()
            
            # Aggregate
            service_totals = {}
            region_totals = {}
            total_cost = 0.0
            
            for record in cost_records:
                cost = record.cost
                service_name = record.service_name
                region = record.region
                
                if service_name in service_totals:
                    service_totals[service_name] += cost
                else:
                    service_totals[service_name] = cost
                
                if region in region_totals:
                    region_totals[region] += cost
                else:
                    region_totals[region] = cost
                
                total_cost += cost
            
            # Format response
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
            
        finally:
            db_session.close()
        
        logger.info(f"Cost summary: total=${total_cost:.2f}, services={len(by_service)}, regions={len(by_region)}")
        
        return {
            "total_cost": round(total_cost, 2),
            "period": {
                "start_date": start_dt.strftime("%Y-%m-%d") if start_dt else "N/A",
                "end_date": end_dt.strftime("%Y-%m-%d") if end_dt else "N/A"
            },
            "by_service": by_service,
            "by_region": by_region
        }
        
    except DatabaseConnectionError:
        raise
    except Exception as e:
        logger.error(f"Error generating cost summary: {str(e)}")
        raise DatabaseConnectionError(detail=f"Failed to generate cost summary: {str(e)}")
