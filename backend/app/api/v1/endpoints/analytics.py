# Analytics and reporting endpoints
from fastapi import APIRouter, Body, Depends
from typing import Optional, List
from datetime import datetime
import logging

from app.schemas.aws_schemas import SavingsResponse, AnalysisRequest, AnalysisResponse
from app.services.aws_mock_service import AWSMockService
from app.core.dependencies import get_mock_service
from app.core.validators import validate_cpu_threshold
from app.core.exceptions import DatabaseConnectionError

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/aws/savings", response_model=SavingsResponse)
async def get_savings(service: AWSMockService = Depends(get_mock_service)):
    """
    Get potential savings summary
    
    Step 1: Query all recommendations from database
    Step 2: Calculate total savings by type
    Step 3: Count recommendations by severity
    Step 4: Return summary
    """
    
    try:
        logger.info("Calculating potential savings")
        
        # Step 1: Query recommendations
        db_session = service.get_db_session()
        
        try:
            from app.services.aws_mock_service import AWSOptimizationRecommendation
            
            recommendations = db_session.query(AWSOptimizationRecommendation).all()
            
            # Step 2: Calculate savings by type
            idle_savings = 0.0
            volume_savings = 0.0
            
            # Step 3: Count by severity
            severity_counts = {
                "CRITICAL": 0,
                "HIGH": 0,
                "MEDIUM": 0,
                "LOW": 0
            }
            
            for rec in recommendations:
                # Add to savings by type
                if rec.recommendation_type == "IDLE_INSTANCE":
                    idle_savings += rec.potential_savings
                elif rec.recommendation_type == "UNATTACHED_VOLUME":
                    volume_savings += rec.potential_savings
                
                # Count by severity
                if rec.severity in severity_counts:
                    severity_counts[rec.severity] += 1
            
            total_savings = idle_savings + volume_savings
            total_count = len(recommendations)
            
            # Get timestamp of most recent recommendation
            last_analysis = None
            if recommendations:
                last_analysis = max(rec.created_at for rec in recommendations)
                last_analysis = last_analysis.isoformat() + "Z"
            else:
                last_analysis = datetime.utcnow().isoformat() + "Z"
            
        finally:
            db_session.close()
        
        logger.info(f"Total potential savings: ${total_savings:.2f} from {total_count} recommendations")
        
        # Step 4: Return summary
        return {
            "total_potential_savings": round(total_savings, 2),
            "breakdown": {
                "idle_instances_savings": round(idle_savings, 2),
                "unattached_volumes_savings": round(volume_savings, 2)
            },
            "recommendations_count": {
                "total": total_count,
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
    service: AWSMockService = Depends(get_mock_service)
):
    """
    Run full cost optimization analysis
    
    Step 1: Validate request parameters
    Step 2: Run full analysis using mock service
    Step 3: Get cost data summary
    Step 4: Get top recommendations
    Step 5: Return comprehensive analysis results
    """
    
    try:
        # Step 1: Validate CPU threshold
        cpu_threshold = validate_cpu_threshold(request.cpu_threshold)
        
        logger.info(f"Starting full analysis - regions: {request.regions}, threshold: {cpu_threshold}%")
        
        # Step 2: Run full analysis
        analysis_results = service.run_full_analysis(regions=request.regions)
        
        # Generate analysis ID
        analysis_id = f"analysis_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        # Step 3: Extract summary from results
        summary = {
            "total_instances": len(analysis_results.get("ec2_instances", [])),
            "running_instances": len([
                i for i in analysis_results.get("ec2_instances", []) 
                if i.get("state") == "running"
            ]),
            "idle_instances": len(analysis_results.get("idle_instances", [])),
            "unattached_volumes": len(analysis_results.get("unattached_volumes", [])),
            "cost_records": len(analysis_results.get("cost_data", []))
        }
        
        # Step 4: Get top recommendations from database
        db_session = service.get_db_session()
        top_recommendations = []
        
        try:
            from app.services.aws_mock_service import AWSOptimizationRecommendation
            
            # Get top 5 recommendations by savings
            top_recs = db_session.query(AWSOptimizationRecommendation)\
                .order_by(AWSOptimizationRecommendation.potential_savings.desc())\
                .limit(5)\
                .all()
            
            for rec in top_recs:
                top_recommendations.append({
                    "resource_id": rec.resource_id,
                    "resource_type": rec.resource_type,
                    "potential_savings": rec.potential_savings,
                    "severity": rec.severity
                })
        
        finally:
            db_session.close()
        
        # Calculate cost data summary if included
        cost_data_summary = {
            "total_cost_30_days": 0.0,
            "average_daily_cost": 0.0
        }
        
        if request.include_cost_data:
            cost_records = analysis_results.get("cost_data", [])
            if cost_records:
                total_cost = sum(record.get("cost", 0) for record in cost_records)
                cost_data_summary["total_cost_30_days"] = round(total_cost, 2)
                
                # Calculate average (assuming records span lookback_days)
                if request.lookback_days > 0:
                    cost_data_summary["average_daily_cost"] = round(
                        total_cost / request.lookback_days, 2
                    )
        
        total_savings = analysis_results.get("total_potential_savings", 0.0)
        
        logger.info(f"Analysis complete - total savings: ${total_savings:.2f}")
        
        # Step 5: Return comprehensive results
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
