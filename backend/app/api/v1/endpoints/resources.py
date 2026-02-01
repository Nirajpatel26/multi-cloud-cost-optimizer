# AWS resource scanning and management endpoints
from fastapi import APIRouter, Query, Body, Depends
from typing import Optional, List
from datetime import datetime
import logging

from app.schemas.aws_schemas import (
    ResourceScanRequest,
    ResourceScanResponse,
    ResourceListResponse
)
from app.services.aws_mock_service import AWSMockService
from app.core.dependencies import get_mock_service
from app.core.exceptions import DatabaseConnectionError, InvalidParameterError

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/aws/resources/scan", response_model=ResourceScanResponse)
async def scan_resources(
    request: ResourceScanRequest = Body(...),
    service: AWSMockService = Depends(get_mock_service)
):
    """
    Trigger resource scanning across specified regions
    
    Step 1: Validate request parameters
    Step 2: Scan EC2 instances if requested
    Step 3: Scan EBS volumes if requested
    Step 4: Return scan results
    """
    
    try:
        logger.info(f"Starting resource scan - regions: {request.regions}, types: {request.resource_types}")
        
        # Step 1: Validate regions list
        if not request.regions or len(request.regions) == 0:
            raise InvalidParameterError("regions", "At least one region must be specified")
        
        # Step 2 & 3: Scan resources based on type
        ec2_count = 0
        ebs_count = 0
        
        if "ec2" in request.resource_types:
            logger.info("Scanning EC2 instances")
            ec2_instances = service.scan_ec2_instances(regions=request.regions)
            ec2_count = len(ec2_instances)
        
        if "ebs" in request.resource_types:
            logger.info("Scanning EBS volumes")
            ebs_volumes = service.find_unattached_ebs_volumes(regions=request.regions)
            ebs_count = len(ebs_volumes)
        
        # Step 4: Generate scan ID and return results
        scan_id = f"scan_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        logger.info(f"Scan completed - EC2: {ec2_count}, EBS: {ebs_count}")
        
        return {
            "scan_id": scan_id,
            "status": "completed",
            "resources_found": {
                "ec2_instances": ec2_count,
                "ebs_volumes": ebs_count
            },
            "regions_scanned": request.regions,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    except InvalidParameterError:
        raise
    except DatabaseConnectionError:
        raise
    except Exception as e:
        logger.error(f"Error during resource scan: {str(e)}")
        raise DatabaseConnectionError(detail=f"Resource scan failed: {str(e)}")


@router.get("/aws/resources", response_model=ResourceListResponse)
async def get_resources(
    type: Optional[str] = Query(None, description="Resource type (ec2 or ebs)"),
    region: Optional[str] = Query(None, description="AWS region filter"),
    state: Optional[str] = Query(None, description="Resource state"),
    is_idle: Optional[bool] = Query(None, description="Filter idle resources (EC2 only)"),
    is_attached: Optional[bool] = Query(None, description="Filter by attachment status (EBS only)"),
    service: AWSMockService = Depends(get_mock_service)
):
    """
    List all resources with optional filters
    
    Step 1: Validate resource type
    Step 2: Query database for EC2 instances
    Step 3: Query database for EBS volumes
    Step 4: Apply filters
    Step 5: Return filtered results
    """
    
    try:
        logger.info(f"Fetching resources - type: {type}, region: {region}, state: {state}")
        
        # Step 1: Validate resource type if provided
        if type and type not in ["ec2", "ebs"]:
            raise InvalidParameterError("type", "Resource type must be 'ec2' or 'ebs'")
        
        # Step 2: Get database session and query EC2 instances
        db_session = service.get_db_session()
        ec2_instances = []
        ebs_volumes = []
        
        try:
            # Import models
            from app.services.aws_mock_service import AWSEC2Instance, AWSEBSVolume
            
            # Query EC2 instances if type is None or "ec2"
            if type is None or type == "ec2":
                logger.info("Querying EC2 instances")
                query = db_session.query(AWSEC2Instance)
                
                # Apply filters
                if region:
                    query = query.filter(AWSEC2Instance.region == region)
                if state:
                    query = query.filter(AWSEC2Instance.state == state)
                if is_idle is not None:
                    query = query.filter(AWSEC2Instance.is_idle == is_idle)
                
                instances = query.all()
                
                # Convert to dict format
                for inst in instances:
                    ec2_instances.append({
                        "id": inst.id,
                        "instance_id": inst.instance_id,
                        "instance_type": inst.instance_type,
                        "state": inst.state,
                        "region": inst.region,
                        "availability_zone": inst.availability_zone,
                        "launch_time": inst.launch_time.isoformat() + "Z" if inst.launch_time else None,
                        "cpu_utilization": inst.cpu_utilization or 0.0,
                        "is_idle": inst.is_idle,
                        "tags": eval(inst.tags) if inst.tags else []
                    })
            
            # Step 3: Query EBS volumes if type is None or "ebs"
            if type is None or type == "ebs":
                logger.info("Querying EBS volumes")
                query = db_session.query(AWSEBSVolume)
                
                # Apply filters
                if region:
                    query = query.filter(AWSEBSVolume.region == region)
                if state:
                    query = query.filter(AWSEBSVolume.state == state)
                if is_attached is not None:
                    query = query.filter(AWSEBSVolume.is_attached == is_attached)
                
                volumes = query.all()
                
                # Convert to dict format
                for vol in volumes:
                    ebs_volumes.append({
                        "id": vol.id,
                        "volume_id": vol.volume_id,
                        "size": vol.size,
                        "volume_type": vol.volume_type,
                        "state": vol.state,
                        "is_attached": vol.is_attached,
                        "region": vol.region,
                        "availability_zone": vol.availability_zone
                    })
            
        finally:
            db_session.close()
        
        total_count = len(ec2_instances) + len(ebs_volumes)
        logger.info(f"Found {len(ec2_instances)} EC2 instances and {len(ebs_volumes)} EBS volumes")
        
        # Step 5: Return results
        return {
            "total_count": total_count,
            "resources": {
                "ec2_instances": ec2_instances,
                "ebs_volumes": ebs_volumes
            }
        }
        
    except InvalidParameterError:
        raise
    except DatabaseConnectionError:
        raise
    except Exception as e:
        logger.error(f"Error fetching resources: {str(e)}")
        raise DatabaseConnectionError(detail=f"Failed to fetch resources: {str(e)}")
