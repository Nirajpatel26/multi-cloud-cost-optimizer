# Azure analytics endpoints
from fastapi import APIRouter, Depends
import uuid
import logging
from datetime import datetime

from app.schemas.azure_schemas import AzureSavingsResponse, AzureAnalysisRequest, AzureAnalysisResponse
from app.services.azure_mock_service import AzureMockService, AzureOptimizationRecommendation
from app.core.dependencies import get_azure_service
from app.core.exceptions import DatabaseConnectionError

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/azure/savings", response_model=AzureSavingsResponse)
async def get_azure_savings(
    service: AzureMockService = Depends(get_azure_service),
):
    """Get Azure savings summary from existing recommendations."""
    try:
        db_session = service.get_db_session()
        try:
            recs = db_session.query(AzureOptimizationRecommendation).all()

            vm_savings = sum(
                r.potential_savings for r in recs if r.resource_type == 'VirtualMachine'
            )
            disk_savings = sum(
                r.potential_savings for r in recs if r.resource_type == 'ManagedDisk'
            )
            total_savings = vm_savings + disk_savings

            severity_counts = {}
            for r in recs:
                severity_counts[r.severity] = severity_counts.get(r.severity, 0) + 1

            last_rec = max((r.created_at for r in recs), default=datetime.utcnow())
        finally:
            db_session.close()

        return {
            "total_potential_savings": round(total_savings, 2),
            "breakdown": {
                "idle_vms_savings": round(vm_savings, 2),
                "unattached_disks_savings": round(disk_savings, 2),
            },
            "recommendations_count": {
                "total": len(recs),
                "by_severity": severity_counts,
            },
            "last_analysis": last_rec.isoformat(),
        }

    except Exception as e:
        logger.error(f"Error fetching Azure savings: {e}")
        raise DatabaseConnectionError(detail=f"Failed to fetch Azure savings: {e}")


@router.post("/azure/analyze", response_model=AzureAnalysisResponse)
async def run_azure_analysis(
    request: AzureAnalysisRequest,
    service: AzureMockService = Depends(get_azure_service),
):
    """Run a full Azure cost optimization analysis (regenerates mock data)."""
    try:
        logger.info("Running full Azure mock analysis")
        results = service.run_full_analysis()

        cost_records = results.get('cost_data', [])
        total_cost = sum(r.get('cost', 0) for r in cost_records)
        avg_daily = total_cost / 30 if total_cost else 0

        db_session = service.get_db_session()
        try:
            top_recs_query = (
                db_session.query(AzureOptimizationRecommendation)
                .order_by(AzureOptimizationRecommendation.potential_savings.desc())
                .limit(5)
                .all()
            )
            top_recommendations = [
                {
                    "resource_id": r.resource_id,
                    "resource_type": r.resource_type,
                    "potential_savings": r.potential_savings,
                    "severity": r.severity,
                }
                for r in top_recs_query
            ]
        finally:
            db_session.close()

        regions_analyzed = request.regions or ["East US", "West Europe", "Southeast Asia"]

        return {
            "analysis_id": str(uuid.uuid4()),
            "timestamp": results['timestamp'],
            "summary": results['summary'],
            "total_potential_savings": results['total_potential_savings'],
            "regions_analyzed": regions_analyzed,
            "cost_data": {
                "total_cost_30_days": round(total_cost, 2),
                "average_daily_cost": round(avg_daily, 2),
            },
            "top_recommendations": top_recommendations,
        }

    except Exception as e:
        logger.error(f"Error running Azure analysis: {e}")
        raise DatabaseConnectionError(detail=f"Failed to run Azure analysis: {e}")
