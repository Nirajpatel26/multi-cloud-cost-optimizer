# Azure resource management endpoints
from fastapi import APIRouter, Query, Depends
from typing import Optional
import uuid
import logging
from datetime import datetime

from app.schemas.azure_schemas import (
    AzureResourceScanRequest, AzureResourceScanResponse, AzureResourceListResponse
)
from app.services.azure_mock_service import AzureMockService, AzureVMInstance, AzureManagedDisk
from app.core.dependencies import get_azure_service
from app.core.exceptions import DatabaseConnectionError

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/azure/resources/scan", response_model=AzureResourceScanResponse)
async def scan_azure_resources(
    request: AzureResourceScanRequest,
    service: AzureMockService = Depends(get_azure_service),
):
    """Trigger a scan of Azure VMs and Managed Disks."""
    try:
        logger.info(f"Starting Azure resource scan for types: {request.resource_types}")
        resources_found = {}

        if "vm" in (request.resource_types or []):
            vms = service.scan_vm_instances(regions=request.regions)
            resources_found["virtual_machines"] = len(vms)

        if "disk" in (request.resource_types or []):
            disks = service.find_unattached_disks()
            resources_found["managed_disks"] = len(disks)

        regions_scanned = request.regions or ["East US", "West Europe", "Southeast Asia"]

        return {
            "scan_id": str(uuid.uuid4()),
            "status": "completed",
            "resources_found": resources_found,
            "regions_scanned": regions_scanned,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Azure resource scan failed: {e}")
        raise DatabaseConnectionError(detail=f"Azure scan failed: {e}")


@router.get("/azure/resources", response_model=AzureResourceListResponse)
async def list_azure_resources(
    resource_type: Optional[str] = Query(None, description="vm or disk"),
    region: Optional[str] = Query(None, description="Azure region e.g. East US"),
    state: Optional[str] = Query(None, description="Running, Deallocated, Stopped"),
    idle_only: Optional[bool] = Query(None, description="Filter idle VMs only"),
    unattached_only: Optional[bool] = Query(None, description="Filter unattached disks only"),
    service: AzureMockService = Depends(get_azure_service),
):
    """List Azure VMs and Managed Disks with optional filters."""
    try:
        db_session = service.get_db_session()
        resources = {"virtual_machines": [], "managed_disks": []}

        try:
            if not resource_type or resource_type == "vm":
                query = db_session.query(AzureVMInstance)
                if region:
                    query = query.filter(AzureVMInstance.region == region)
                if state:
                    query = query.filter(AzureVMInstance.state == state)
                if idle_only:
                    query = query.filter(AzureVMInstance.is_idle == True)
                vms = query.all()
                resources["virtual_machines"] = [
                    {
                        "id": v.id, "vm_id": v.vm_id, "vm_size": v.vm_size,
                        "state": v.state, "region": v.region,
                        "resource_group": v.resource_group,
                        "cpu_utilization": v.cpu_utilization,
                        "is_idle": v.is_idle, "tags": [],
                    }
                    for v in vms
                ]

            if not resource_type or resource_type == "disk":
                query = db_session.query(AzureManagedDisk)
                if region:
                    query = query.filter(AzureManagedDisk.region == region)
                if unattached_only:
                    query = query.filter(AzureManagedDisk.is_attached == False)
                disks = query.all()
                resources["managed_disks"] = [
                    {
                        "id": d.id, "disk_id": d.disk_id, "size": d.size,
                        "disk_type": d.disk_type, "state": d.state,
                        "is_attached": d.is_attached, "region": d.region,
                        "resource_group": d.resource_group,
                        "monthly_cost": d.monthly_cost,
                    }
                    for d in disks
                ]
        finally:
            db_session.close()

        total = sum(len(v) for v in resources.values())
        return {"total_count": total, "resources": resources}

    except Exception as e:
        logger.error(f"Error listing Azure resources: {e}")
        raise DatabaseConnectionError(detail=f"Failed to list Azure resources: {e}")
