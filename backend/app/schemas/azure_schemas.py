# Pydantic schemas for Azure request/response models
from pydantic import BaseModel
from typing import Optional, List, Dict


# Cost Schemas
class AzureServiceCostBreakdown(BaseModel):
    service: str
    cost: float


class AzureCostResponse(BaseModel):
    filters: dict
    total_cost: float
    currency: str
    breakdown: List[AzureServiceCostBreakdown]


class AzureServiceSummary(BaseModel):
    service_name: str
    total_cost: float
    percentage: float


class AzureRegionSummary(BaseModel):
    region: str
    total_cost: float
    percentage: float


class AzureCostSummaryResponse(BaseModel):
    total_cost: float
    period: Dict[str, str]
    by_service: List[AzureServiceSummary]
    by_region: List[AzureRegionSummary]


# Resource Schemas
class AzureResourceScanRequest(BaseModel):
    regions: Optional[List[str]] = None
    resource_types: Optional[List[str]] = ["vm", "disk"]


class AzureResourceScanResponse(BaseModel):
    scan_id: str
    status: str
    resources_found: Dict[str, int]
    regions_scanned: List[str]
    timestamp: str


class AzureVMInstance(BaseModel):
    id: int
    vm_id: str
    vm_size: str
    state: str
    region: str
    resource_group: str
    cpu_utilization: float
    is_idle: bool
    tags: List[Dict[str, str]]


class AzureManagedDisk(BaseModel):
    id: int
    disk_id: str
    size: int
    disk_type: str
    state: str
    is_attached: bool
    region: str
    resource_group: str
    monthly_cost: float


class AzureResourceListResponse(BaseModel):
    total_count: int
    resources: Dict[str, List]


# Recommendation Schemas
class AzureRecommendation(BaseModel):
    id: int
    resource_id: str
    resource_type: str
    recommendation_type: str
    description: str
    potential_savings: float
    severity: str
    region: str
    created_at: str


class AzureRecommendationsResponse(BaseModel):
    total_recommendations: int
    total_potential_savings: float
    recommendations: List[AzureRecommendation]


class AzureIdleVM(BaseModel):
    vm_id: str
    vm_size: str
    region: str
    resource_group: str
    cpu_utilization: float
    potential_savings: float
    recommendation: str


class AzureIdleVMsResponse(BaseModel):
    total_idle_vms: int
    total_potential_savings: float
    idle_vms: List[AzureIdleVM]


class AzureUnattachedDisk(BaseModel):
    disk_id: str
    size: int
    disk_type: str
    region: str
    resource_group: str
    monthly_cost: float


class AzureUnattachedDisksResponse(BaseModel):
    total_unattached_disks: int
    total_potential_savings: float
    unattached_disks: List[AzureUnattachedDisk]


# Analytics Schemas
class AzureSavingsBreakdown(BaseModel):
    idle_vms_savings: float
    unattached_disks_savings: float


class AzureRecommendationsCount(BaseModel):
    total: int
    by_severity: Dict[str, int]


class AzureSavingsResponse(BaseModel):
    total_potential_savings: float
    breakdown: AzureSavingsBreakdown
    recommendations_count: AzureRecommendationsCount
    last_analysis: str


class AzureAnalysisRequest(BaseModel):
    regions: Optional[List[str]] = None
    cpu_threshold: Optional[float] = 5.0
    include_cost_data: Optional[bool] = True
    lookback_days: Optional[int] = 30


class AzureAnalysisSummary(BaseModel):
    total_vms: int
    running_vms: int
    idle_vms: int
    unattached_disks: int
    cost_records: int


class AzureCostData(BaseModel):
    total_cost_30_days: float
    average_daily_cost: float


class AzureTopRecommendation(BaseModel):
    resource_id: str
    resource_type: str
    potential_savings: float
    severity: str


class AzureAnalysisResponse(BaseModel):
    analysis_id: str
    timestamp: str
    summary: AzureAnalysisSummary
    total_potential_savings: float
    regions_analyzed: List[str]
    cost_data: AzureCostData
    top_recommendations: List[AzureTopRecommendation]
