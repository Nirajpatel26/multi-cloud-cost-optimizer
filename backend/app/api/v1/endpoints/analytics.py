# Analytics and reporting endpoints
from fastapi import APIRouter, Body, Depends
from typing import Optional, List
from datetime import datetime
import logging

from app.schemas.aws_schemas import SavingsResponse, AnalysisRequest, AnalysisResponse
from app.services.aws_mock_service import (
    AWSOptimizationRecommendation,
    AWSEC2Instance,
    AWSEBSVolume,
    AWSCostData
)
from app.core.dependencies import get_service
from app.core.validators import validate_cpu_threshold
from app.core.exceptions import DatabaseConnectionError

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/aws/savings", response_model=SavingsResponse)
async def get_savings(service = Depends(get_service)):
    """
    Get savings summary from database (read-only)
    """
    
    try:
        logger.info("Calculating savings from database")
        
        db_session = service.get_db_session()
        
        try:
            recommendations = db_session.query(AWSOptimizationRecommendation).all()
            
            # Calculate savings by type
            idle_savings = sum(
                rec.potential_savings 
                for rec in recommendations 
                if rec.recommendation_type == "IDLE_INSTANCE"
            )
            
            volume_savings = sum(
                rec.potential_savings 
                for rec in recommendations 
                if rec.recommendation_type == "UNATTACHED_VOLUME"
            )
            
            # Count by severity
            severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
            
            for rec in recommendations:
                if rec.severity in severity_counts:
                    severity_counts[rec.severity] += 1
            
            total_savings = idle_savings + volume_savings
            
            last_analysis = None
            if recommendations:
                last_analysis = max(rec.created_at for rec in recommendations).isoformat() + "Z"
            else:
                last_analysis = datetime.utcnow().isoformat() + "Z"
            
        finally:
            db_session.close()
        
        logger.info(f"Total savings: ${total_savings:.2f}")
        
        return {
            "total_potential_savings": round(total_savings, 2),
            "breakdown": {
                "idle_instances_savings": round(idle_savings, 2),
                "unattached_volumes_savings": round(volume_savings, 2)
            },
            "recommendations_count": {
                "total": len(recommendations),
                "by_severity": severity_counts
            },
            "last_analysis": last_analysis
        }
        
    except DatabaseConnectionError:
        raise
    except Exception as e:
        logger.error(f"Error calculating savings: {str(e)}")
        raise DatabaseConnectionError(detail=f"Failed to calculate savings: {str(e)}")


@router.post("/aws/analyze", response_model=AnalysisResponse)
async def run_analysis(
    request: AnalysisRequest = Body(...),
    service = Depends(get_service)
):
    """
    Run analysis - this WILL regenerate data and recommendations
    Use this endpoint sparingly to refresh data
    """
    
    try:
        cpu_threshold = validate_cpu_threshold(request.cpu_threshold)
        
        logger.info(f"Running full analysis - regions: {request.regions}")
        
        # This will regenerate data
        analysis_results = service.run_full_analysis(regions=request.regions)
        
        analysis_id = f"analysis_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        # Get summary from database
        db_session = service.get_db_session()
        
        try:
            total_instances = db_session.query(AWSEC2Instance).count()
            running_instances = db_session.query(AWSEC2Instance).filter(AWSEC2Instance.state == "running").count()
            idle_instances = db_session.query(AWSEC2Instance).filter(AWSEC2Instance.is_idle == True).count()
            unattached_volumes = db_session.query(AWSEBSVolume).filter(AWSEBSVolume.is_attached == False).count()
            cost_records = db_session.query(AWSCostData).count()
            
            # Get top recommendations
            top_recs = db_session.query(AWSOptimizationRecommendation)\
                .order_by(AWSOptimizationRecommendation.potential_savings.desc())\
                .limit(5)\
                .all()
            
            top_recommendations = []
            for rec in top_recs:
                top_recommendations.append({
                    "resource_id": rec.resource_id,
                    "resource_type": rec.resource_type,
                    "potential_savings": rec.potential_savings,
                    "severity": rec.severity
                })
            
        finally:
            db_session.close()
        
        summary = {
            "total_instances": total_instances,
            "running_instances": running_instances,
            "idle_instances": idle_instances,
            "unattached_volumes": unattached_volumes,
            "cost_records": cost_records
        }
        
        total_savings = analysis_results.get("total_potential_savings", 0.0)
        
        cost_data_summary = {
            "total_cost_30_days": 0.0,
            "average_daily_cost": 0.0
        }
        
        logger.info(f"Analysis complete - savings: ${total_savings:.2f}")
        
        return {
            "analysis_id": analysis_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "summary": summary,
            "total_potential_savings": round(total_savings, 2),
            "regions_analyzed": request.regions or ["us-east-1"],
            "cost_data": cost_data_summary,
            "top_recommendations": top_recommendations
        }
        
    except DatabaseConnectionError:
        raise
    except Exception as e:
        logger.error(f"Error running analysis: {str(e)}")
        raise DatabaseConnectionError(detail=f"Analysis failed: {str(e)}")
