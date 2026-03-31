# Azure recommendation endpoints
from fastapi import APIRouter, Query, Depends
from typing import Optional
import logging

from app.schemas.azure_schemas import (
    AzureRecommendationsResponse, AzureIdleVMsResponse, AzureUnattachedDisksResponse
)
from app.services.azure_mock_service import AzureMockService, AzureOptimizationRecommendation
from app.core.dependencies import get_azure_service
from app.core.exceptions import DatabaseConnectionError

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/azure/recommendations", response_model=AzureRecommendationsResponse)
async def get_azure_recommendations(
    region: Optional[str] = Query(None),
    severity: Optional[str] = Query(None, description="LOW, MEDIUM, HIGH, CRITICAL"),
    resource_type: Optional[str] = Query(None, description="VirtualMachine or ManagedDisk"),
    service: AzureMockService = Depends(get_azure_service),
):
    """Get all Azure optimization recommendations."""
    try:
        db_session = service.get_db_session()
        try:
            query = db_session.query(AzureOptimizationRecommendation)
            if region:
                query = query.filter(AzureOptimizationRecommendation.region == region)
            if severity:
                query = query.filter(AzureOptimizationRecommendation.severity == severity.upper())
            if resource_type:
                query = query.filter(AzureOptimizationRecommendation.resource_type == resource_type)

            recs = query.all()
            total_savings = sum(r.potential_savings for r in recs)

            recommendations = [
                {
                    "id": r.id,
                    "resource_id": r.resource_id,
                    "resource_type": r.resource_type,
                    "recommendation_type": r.recommendation_type,
                    "description": r.description,
                    "potential_savings": r.potential_savings,
                    "severity": r.severity,
                    "region": r.region,
                    "created_at": r.created_at.isoformat(),
                }
                for r in recs
            ]
        finally:
            db_session.close()

        return {
            "total_recommendations": len(recommendations),
            "total_potential_savings": round(total_savings, 2),
            "recommendations": recommendations,
        }

    except Exception as e:
        logger.error(f"Error fetching Azure recommendations: {e}")
        raise DatabaseConnectionError(detail=f"Failed to fetch Azure recommendations: {e}")


@router.get("/azure/recommendations/idle-vms", response_model=AzureIdleVMsResponse)
async def get_idle_azure_vms(
    service: AzureMockService = Depends(get_azure_service),
):
    """Get list of idle Azure VMs with savings potential."""
    try:
        idle_vms = service.identify_idle_vms()
        total_savings = sum(v.get('potential_savings', 0) for v in idle_vms)
        return {
            "total_idle_vms": len(idle_vms),
            "total_potential_savings": round(total_savings, 2),
            "idle_vms": idle_vms,
        }
    except Exception as e:
        logger.error(f"Error fetching idle Azure VMs: {e}")
        raise DatabaseConnectionError(detail=f"Failed to fetch idle VMs: {e}")


@router.get("/azure/recommendations/unattached-disks", response_model=AzureUnattachedDisksResponse)
async def get_unattached_azure_disks(
    service: AzureMockService = Depends(get_azure_service),
):
    """Get list of unattached Azure Managed Disks."""
    try:
        unattached = service.find_unattached_disks()
        total_savings = sum(d.get('monthly_cost', 0) for d in unattached)
        return {
            "total_unattached_disks": len(unattached),
            "total_potential_savings": round(total_savings, 2),
            "unattached_disks": unattached,
        }
    except Exception as e:
        logger.error(f"Error fetching unattached Azure disks: {e}")
        raise DatabaseConnectionError(detail=f"Failed to fetch unattached disks: {e}")
