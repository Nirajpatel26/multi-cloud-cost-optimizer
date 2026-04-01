# Azure cost-related endpoints
from fastapi import APIRouter, Query, Depends
from typing import Optional
import logging

from app.schemas.azure_schemas import AzureCostResponse, AzureCostSummaryResponse
from app.services.azure_mock_service import AzureMockService, AzureCostData
from app.core.dependencies import get_azure_service
from app.core.validators import validate_date_range
from app.core.exceptions import DatabaseConnectionError

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/azure/costs", response_model=AzureCostResponse)
async def get_azure_costs(
    start_date: Optional[str] = Query(None, description="Start date YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="End date YYYY-MM-DD"),
    region: Optional[str] = Query(None, description="Azure region e.g. East US"),
    service_name: Optional[str] = Query(None, description="Azure service name"),
    service: AzureMockService = Depends(get_azure_service),
):
    """Get Azure cost data with optional filters."""
    try:
        start_dt, end_dt = validate_date_range(start_date, end_date)
        db_session = service.get_db_session()

        try:
            query = db_session.query(AzureCostData)
            if start_dt:
                query = query.filter(AzureCostData.start_date >= start_dt)
            if end_dt:
                query = query.filter(AzureCostData.end_date <= end_dt)
            if region:
                query = query.filter(AzureCostData.region == region)
            if service_name:
                query = query.filter(AzureCostData.service_name == service_name)

            records = query.all()

            service_costs = {}
            for r in records:
                service_costs[r.service_name] = service_costs.get(r.service_name, 0) + r.cost

            breakdown = [{"service": k, "cost": v} for k, v in service_costs.items()]
            total_cost = sum(item["cost"] for item in breakdown)
        finally:
            db_session.close()

        logger.info(f"Azure costs fetched: {len(records)} records, total ${total_cost:.2f}")
        return {
            "filters": {
                "start_date": start_dt.strftime("%Y-%m-%d") if start_dt else None,
                "end_date": end_dt.strftime("%Y-%m-%d") if end_dt else None,
                "region": region,
                "service_name": service_name,
            },
            "total_cost": round(total_cost, 2),
            "currency": "USD",
            "breakdown": breakdown,
        }

    except DatabaseConnectionError:
        raise
    except Exception as e:
        logger.error(f"Error fetching Azure costs: {e}")
        raise DatabaseConnectionError(detail=f"Failed to fetch Azure cost data: {e}")


@router.get("/azure/costs/summary", response_model=AzureCostSummaryResponse)
async def get_azure_costs_summary(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    service: AzureMockService = Depends(get_azure_service),
):
    """Get Azure cost summary broken down by service and region."""
    try:
        start_dt, end_dt = validate_date_range(start_date, end_date)
        db_session = service.get_db_session()

        try:
            query = db_session.query(AzureCostData)
            if start_dt:
                query = query.filter(AzureCostData.start_date >= start_dt)
            if end_dt:
                query = query.filter(AzureCostData.end_date <= end_dt)

            records = query.all()
            service_totals, region_totals, total_cost = {}, {}, 0.0

            for r in records:
                service_totals[r.service_name] = service_totals.get(r.service_name, 0) + r.cost
                region_totals[r.region] = region_totals.get(r.region, 0) + r.cost
                total_cost += r.cost

            by_service = [
                {"service_name": k, "total_cost": round(v, 2),
                 "percentage": round(v / total_cost * 100, 2) if total_cost else 0}
                for k, v in service_totals.items()
            ]
            by_region = [
                {"region": k, "total_cost": round(v, 2),
                 "percentage": round(v / total_cost * 100, 2) if total_cost else 0}
                for k, v in region_totals.items()
            ]
        finally:
            db_session.close()

        return {
            "total_cost": round(total_cost, 2),
            "period": {
                "start_date": start_dt.strftime("%Y-%m-%d") if start_dt else "N/A",
                "end_date": end_dt.strftime("%Y-%m-%d") if end_dt else "N/A",
            },
            "by_service": by_service,
            "by_region": by_region,
        }

    except DatabaseConnectionError:
        raise
    except Exception as e:
        logger.error(f"Error fetching Azure cost summary: {e}")
        raise DatabaseConnectionError(detail=f"Failed to fetch Azure cost summary: {e}")
