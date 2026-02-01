# Optimization recommendations endpoints
from fastapi import APIRouter, Query, Depends
from typing import Optional
from datetime import datetime
import logging

from app.schemas.aws_schemas import (
    RecommendationsResponse,
    IdleInstancesResponse,
    UnattachedVolumesResponse
)
from app.services.aws_mock_service import AWSMockService
from app.core.dependencies import get_mock_service
from app.core.validators import validate_cpu_threshold
from app.core.exceptions import DatabaseConnectionError

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/aws/recommendations", response_model=RecommendationsResponse)
async def get_recommendations(
    severity: Optional[str] = Query(None, description="Filter by severity"),
    recommendation_type: Optional[str] = Query(None, description="Filter by recommendation type"),
    region: Optional[str] = Query(None, description="Filter by region"),
    min_savings: Optional[float] = Query(None, description="Minimum potential savings threshold"),
    service: AWSMockService = Depends(get_mock_service)
):
    """
    Get all optimization recommendations
    
    Step 1: Query recommendations from database
    Step 2: Apply filters
    Step 3: Calculate total savings
    Step 4: Return results
    """
    
    try:
        logger.info(f"Fetching recommendations - severity: {severity}, type: {recommendation_type}, region: {region}")
        
        # Step 1: Query database
        db_session = service.get_db_session()
        
        try:
            from app.services.aws_mock_service import AWSOptimizationRecommendation
            
            query = db_session.query(AWSOptimizationRecommendation)
            
            # Step 2: Apply filters at database level
            if severity:
                query = query.filter(AWSOptimizationRecommendation.severity == severity)
            
            if recommendation_type:
                query = query.filter(AWSOptimizationRecommendation.recommendation_type == recommendation_type)
            
            if region:
                query = query.filter(AWSOptimizationRecommendation.region == region)
            
            if min_savings:
                query = query.filter(AWSOptimizationRecommendation.potential_savings >= min_savings)
            
            recommendations_data = query.all()
            
            # Convert to dict format
            recommendations = []
            for rec in recommendations_data:
                recommendations.append({
                    "id": rec.id,
                    "resource_id": rec.resource_id,
                    "resource_type": rec.resource_type,
                    "recommendation_type": rec.recommendation_type,
                    "description": rec.description,
                    "potential_savings": rec.potential_savings,
                    "severity": rec.severity,
                    "region": rec.region,
                    "created_at": rec.created_at.isoformat() + "Z" if rec.created_at else None
                })
            
        finally:
            db_session.close()
        
        # Step 3: Calculate total savings
        total_savings = sum(rec["potential_savings"] for rec in recommendations)
        
        logger.info(f"Found {len(recommendations)} recommendations with total savings: ${total_savings:.2f}")
        
        # Step 4: Return results
        return {
            "total_recommendations": len(recommendations),
            "total_potential_savings": round(total_savings, 2),
            "recommendations": recommendations
        }
        
    except DatabaseConnectionError:
        raise
    except Exception as e:
        logger.error(f"Error fetching recommendations: {str(e)}")
        raise DatabaseConnectionError(detail=f"Failed to fetch recommendations: {str(e)}")


@router.get("/aws/recommendations/idle-instances", response_model=IdleInstancesResponse)
async def get_idle_instances(
    cpu_threshold: Optional[float] = Query(5.0, description="CPU utilization threshold percentage"),
    region: Optional[str] = Query(None, description="Filter by region"),
    service: AWSMockService = Depends(get_mock_service)
):
    """
    Get list of idle EC2 instances
    
    Step 1: Validate CPU threshold
    Step 2: Identify idle resources using mock service
    Step 3: Apply region filter
    Step 4: Return idle instances with savings
    """
    
    try:
        # Step 1: Validate CPU threshold
        cpu_threshold = validate_cpu_threshold(cpu_threshold)
        
        logger.info(f"Identifying idle instances - threshold: {cpu_threshold}%, region: {region}")
        
        # Step 2: Call mock service to identify idle resources
        regions = [region] if region else None
        idle_data = service.identify_idle_resources(
            cpu_threshold=cpu_threshold,
            regions=regions
        )
        
        # Step 3: Format response
        idle_instances = []
        for item in idle_data:
            idle_instances.append({
                "instance_id": item.get("instance_id"),
                "instance_type": item.get("instance_type"),
                "region": item.get("region"),
                "cpu_utilization": item.get("cpu_utilization", 0.0),
                "potential_savings": item.get("potential_savings", 0.0),
                "recommendation": item.get("recommendation", "Consider stopping or downsizing this instance")
            })
        
        total_savings = sum(inst["potential_savings"] for inst in idle_instances)
        
        logger.info(f"Found {len(idle_instances)} idle instances with potential savings: ${total_savings:.2f}")
        
        # Step 4: Return results
        return {
            "total_idle_instances": len(idle_instances),
            "total_potential_savings": round(total_savings, 2),
            "idle_instances": idle_instances
        }
        
    except DatabaseConnectionError:
        raise
    except Exception as e:
        logger.error(f"Error identifying idle instances: {str(e)}")
        raise DatabaseConnectionError(detail=f"Failed to identify idle instances: {str(e)}")


@router.get("/aws/recommendations/unattached-volumes", response_model=UnattachedVolumesResponse)
async def get_unattached_volumes(
    region: Optional[str] = Query(None, description="Filter by region"),
    min_size: Optional[int] = Query(None, description="Minimum volume size in GB"),
    service: AWSMockService = Depends(get_mock_service)
):
    """
    Get list of unattached EBS volumes
    
    Step 1: Find unattached volumes using mock service
    Step 2: Apply size filter
    Step 3: Return unattached volumes with costs
    """
    
    try:
        logger.info(f"Finding unattached volumes - region: {region}, min_size: {min_size}")
        
        # Step 1: Call mock service to find unattached volumes
        regions = [region] if region else None
        unattached_data = service.find_unattached_ebs_volumes(regions=regions)
        
        # Step 2: Apply size filter
        if min_size:
            unattached_data = [
                vol for vol in unattached_data 
                if vol.get("size", 0) >= min_size
            ]
        
        # Step 3: Format response
        unattached_volumes = []
        for vol in unattached_data:
            unattached_volumes.append({
                "volume_id": vol.get("volume_id"),
                "size": vol.get("size"),
                "volume_type": vol.get("volume_type"),
                "region": vol.get("region"),
                "availability_zone": vol.get("availability_zone"),
                "monthly_cost": vol.get("monthly_cost", 0.0)
            })
        
        total_savings = sum(vol["monthly_cost"] for vol in unattached_volumes)
        
        logger.info(f"Found {len(unattached_volumes)} unattached volumes with potential savings: ${total_savings:.2f}")
        
        return {
            "total_unattached_volumes": len(unattached_volumes),
            "total_potential_savings": round(total_savings, 2),
            "unattached_volumes": unattached_volumes
        }
        
    except DatabaseConnectionError:
        raise
    except Exception as e:
        logger.error(f"Error finding unattached volumes: {str(e)}")
        raise DatabaseConnectionError(detail=f"Failed to find unattached volumes: {str(e)}")
