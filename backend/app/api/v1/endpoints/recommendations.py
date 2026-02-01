# Optimization recommendations endpoints
from fastapi import APIRouter, Query
from typing import Optional
from datetime import datetime

from app.schemas.aws_schemas import (
    RecommendationsResponse,
    IdleInstancesResponse,
    UnattachedVolumesResponse
)

router = APIRouter()


@router.get("/aws/recommendations", response_model=RecommendationsResponse)
async def get_recommendations(
    severity: Optional[str] = Query(None, description="Filter by severity"),
    recommendation_type: Optional[str] = Query(None, description="Filter by recommendation type"),
    region: Optional[str] = Query(None, description="Filter by region"),
    min_savings: Optional[float] = Query(None, description="Minimum potential savings threshold")
):
    """Get all optimization recommendations"""
    
    # TODO: Replace with actual database query
    recommendations = [
        {
            "id": 1,
            "resource_id": "i-1234567890abcdef0",
            "resource_type": "EC2",
            "recommendation_type": "IDLE_INSTANCE",
            "description": "Instance has 2.5% CPU utilization over 7 days",
            "potential_savings": 70.00,
            "severity": "HIGH",
            "region": "us-east-1",
            "created_at": datetime.utcnow().isoformat() + "Z"
        },
        {
            "id": 2,
            "resource_id": "vol-0123456789abcdef0",
            "resource_type": "EBS",
            "recommendation_type": "UNATTACHED_VOLUME",
            "description": "Unattached 100GB gp3 volume",
            "potential_savings": 8.00,
            "severity": "LOW",
            "region": "us-east-1",
            "created_at": datetime.utcnow().isoformat() + "Z"
        }
    ]
    
    # Apply filters
    if severity:
        recommendations = [r for r in recommendations if r["severity"] == severity]
    
    if recommendation_type:
        recommendations = [r for r in recommendations if r["recommendation_type"] == recommendation_type]
    
    if region:
        recommendations = [r for r in recommendations if r["region"] == region]
    
    if min_savings:
        recommendations = [r for r in recommendations if r["potential_savings"] >= min_savings]
    
    total_savings = sum(r["potential_savings"] for r in recommendations)
    
    return {
        "total_recommendations": len(recommendations),
        "total_potential_savings": total_savings,
        "recommendations": recommendations
    }


@router.get("/aws/recommendations/idle-instances", response_model=IdleInstancesResponse)
async def get_idle_instances(
    cpu_threshold: Optional[float] = Query(5.0, description="CPU utilization threshold percentage"),
    region: Optional[str] = Query(None, description="Filter by region")
):
    """Get list of idle EC2 instances"""
    
    # TODO: Replace with actual database query
    idle_instances = [
        {
            "instance_id": "i-1234567890abcdef0",
            "instance_type": "t3.medium",
            "region": "us-east-1",
            "cpu_utilization": 2.5,
            "potential_savings": 70.00,
            "recommendation": "Consider stopping or downsizing this instance"
        },
        {
            "instance_id": "i-0987654321fedcba0",
            "instance_type": "t3.small",
            "region": "us-west-2",
            "cpu_utilization": 3.2,
            "potential_savings": 35.00,
            "recommendation": "Consider stopping or downsizing this instance"
        }
    ]
    
    # Apply filters
    idle_instances = [i for i in idle_instances if i["cpu_utilization"] < cpu_threshold]
    
    if region:
        idle_instances = [i for i in idle_instances if i["region"] == region]
    
    total_savings = sum(i["potential_savings"] for i in idle_instances)
    
    return {
        "total_idle_instances": len(idle_instances),
        "total_potential_savings": total_savings,
        "idle_instances": idle_instances
    }


@router.get("/aws/recommendations/unattached-volumes", response_model=UnattachedVolumesResponse)
async def get_unattached_volumes(
    region: Optional[str] = Query(None, description="Filter by region"),
    min_size: Optional[int] = Query(None, description="Minimum volume size in GB")
):
    """Get list of unattached EBS volumes"""
    
    # TODO: Replace with actual database query
    unattached_volumes = [
        {
            "volume_id": "vol-0123456789abcdef0",
            "size": 100,
            "volume_type": "gp3",
            "region": "us-east-1",
            "availability_zone": "us-east-1a",
            "monthly_cost": 8.00
        },
        {
            "volume_id": "vol-fedcba0987654321",
            "size": 50,
            "volume_type": "gp2",
            "region": "us-west-2",
            "availability_zone": "us-west-2b",
            "monthly_cost": 5.00
        }
    ]
    
    # Apply filters
    if region:
        unattached_volumes = [v for v in unattached_volumes if v["region"] == region]
    
    if min_size:
        unattached_volumes = [v for v in unattached_volumes if v["size"] >= min_size]
    
    total_savings = sum(v["monthly_cost"] for v in unattached_volumes)
    
    return {
        "total_unattached_volumes": len(unattached_volumes),
        "total_potential_savings": total_savings,
        "unattached_volumes": unattached_volumes
    }
