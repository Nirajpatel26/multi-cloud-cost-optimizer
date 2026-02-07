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
from app.services.aws_mock_service import (
    AWSOptimizationRecommendation,
    AWSEC2Instance,
    AWSEBSVolume
)
from app.core.dependencies import get_service
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
    service = Depends(get_service)
):
    """
    Get recommendations from database (read-only)
    """
    
    try:
        logger.info(f"Fetching recommendations from database")
        
        db_session = service.get_db_session()
        
        try:
            query = db_session.query(AWSOptimizationRecommendation)
            
            if severity:
                query = query.filter(AWSOptimizationRecommendation.severity == severity)
            if recommendation_type:
                query = query.filter(AWSOptimizationRecommendation.recommendation_type == recommendation_type)
            if region:
                query = query.filter(AWSOptimizationRecommendation.region == region)
            if min_savings:
                query = query.filter(AWSOptimizationRecommendation.potential_savings >= min_savings)
            
            recommendations_data = query.all()
            
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
        
        total_savings = sum(rec["potential_savings"] for rec in recommendations)
        
        logger.info(f"Found {len(recommendations)} recommendations, total savings: ${total_savings:.2f}")
        
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
    service = Depends(get_service)
):
    """
    Get idle instances from database (read-only)
    """
    
    try:
        cpu_threshold = validate_cpu_threshold(cpu_threshold)
        
        logger.info(f"Fetching idle instances from database - threshold: {cpu_threshold}%")
        
        db_session = service.get_db_session()
        
        try:
            # Query EC2 instances marked as idle
            query = db_session.query(AWSEC2Instance).filter(AWSEC2Instance.is_idle == True)
            
            if region:
                query = query.filter(AWSEC2Instance.region == region)
            
            # Filter by CPU threshold
            query = query.filter(AWSEC2Instance.cpu_utilization < cpu_threshold)
            
            instances = query.all()
            
            idle_instances = []
            for inst in instances:
                # Estimate savings based on instance type
                potential_savings = service._estimate_instance_cost(inst.instance_type)
                
                idle_instances.append({
                    "instance_id": inst.instance_id,
                    "instance_type": inst.instance_type,
                    "region": inst.region,
                    "cpu_utilization": inst.cpu_utilization or 0.0,
                    "potential_savings": potential_savings,
                    "recommendation": "Consider stopping or downsizing this instance"
                })
            
        finally:
            db_session.close()
        
        total_savings = sum(inst["potential_savings"] for inst in idle_instances)
        
        logger.info(f"Found {len(idle_instances)} idle instances, savings: ${total_savings:.2f}")
        
        return {
            "total_idle_instances": len(idle_instances),
            "total_potential_savings": round(total_savings, 2),
            "idle_instances": idle_instances
        }
        
    except DatabaseConnectionError:
        raise
    except Exception as e:
        logger.error(f"Error fetching idle instances: {str(e)}")
        raise DatabaseConnectionError(detail=f"Failed to fetch idle instances: {str(e)}")


@router.get("/aws/recommendations/unattached-volumes", response_model=UnattachedVolumesResponse)
async def get_unattached_volumes(
    region: Optional[str] = Query(None, description="Filter by region"),
    min_size: Optional[int] = Query(None, description="Minimum volume size in GB"),
    service = Depends(get_service)
):
    """
    Get unattached volumes from database (read-only)
    """
    
    try:
        logger.info(f"Fetching unattached volumes from database")
        
        db_session = service.get_db_session()
        
        try:
            # Query unattached EBS volumes
            query = db_session.query(AWSEBSVolume).filter(AWSEBSVolume.is_attached == False)
            
            if region:
                query = query.filter(AWSEBSVolume.region == region)
            if min_size:
                query = query.filter(AWSEBSVolume.size >= min_size)
            
            volumes = query.all()
            
            unattached_volumes = []
            for vol in volumes:
                # Calculate monthly cost
                monthly_cost = service._estimate_ebs_cost(vol.size, vol.volume_type)
                
                unattached_volumes.append({
                    "volume_id": vol.volume_id,
                    "size": vol.size,
                    "volume_type": vol.volume_type,
                    "region": vol.region,
                    "availability_zone": vol.availability_zone,
                    "monthly_cost": monthly_cost
                })
            
        finally:
            db_session.close()
        
        total_savings = sum(vol["monthly_cost"] for vol in unattached_volumes)
        
        logger.info(f"Found {len(unattached_volumes)} unattached volumes, savings: ${total_savings:.2f}")
        
        return {
            "total_unattached_volumes": len(unattached_volumes),
            "total_potential_savings": round(total_savings, 2),
            "unattached_volumes": unattached_volumes
        }
        
    except DatabaseConnectionError:
        raise
    except Exception as e:
        logger.error(f"Error fetching unattached volumes: {str(e)}")
        raise DatabaseConnectionError(detail=f"Failed to fetch unattached volumes: {str(e)}")
