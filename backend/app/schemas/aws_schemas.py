# Pydantic schemas for request/response models
from pydantic import BaseModel
from typing import Optional, List, Dict


# Cost Schemas
class ServiceCostBreakdown(BaseModel):
    service: str
    cost: float


class CostResponse(BaseModel):
    filters: dict
    total_cost: float
    currency: str
    breakdown: List[ServiceCostBreakdown]


class ServiceSummary(BaseModel):
    service_name: str
    total_cost: float
    percentage: float


class RegionSummary(BaseModel):
    region: str
    total_cost: float
    percentage: float


class CostSummaryResponse(BaseModel):
    total_cost: float
    period: Dict[str, str]
    by_service: List[ServiceSummary]
    by_region: List[RegionSummary]


# Resource Schemas
class ResourceScanRequest(BaseModel):
    regions: List[str]
    resource_types: Optional[List[str]] = ["ec2", "ebs"]


class ResourceScanResponse(BaseModel):
    scan_id: str
    status: str
    resources_found: Dict[str, int]
    regions_scanned: List[str]
    timestamp: str


class EC2Instance(BaseModel):
    id: int
    instance_id: str
    instance_type: str
    state: str
    region: str
    availability_zone: str
    launch_time: str
    cpu_utilization: float
    is_idle: bool
    tags: List[Dict[str, str]]


class EBSVolume(BaseModel):
    id: int
    volume_id: str
    size: int
    volume_type: str
    state: str
    is_attached: bool
    region: str
    availability_zone: str


class ResourceListResponse(BaseModel):
    total_count: int
    resources: Dict[str, List]


# Recommendation Schemas
class Recommendation(BaseModel):
    id: int
    resource_id: str
    resource_type: str
    recommendation_type: str
    description: str
    potential_savings: float
    severity: str
    region: str
    created_at: str


class RecommendationsResponse(BaseModel):
    total_recommendations: int
    total_potential_savings: float
    recommendations: List[Recommendation]


class IdleInstance(BaseModel):
    instance_id: str
    instance_type: str
    region: str
    cpu_utilization: float
    potential_savings: float
    recommendation: str


class IdleInstancesResponse(BaseModel):
    total_idle_instances: int
    total_potential_savings: float
    idle_instances: List[IdleInstance]


class UnattachedVolume(BaseModel):
    volume_id: str
    size: int
    volume_type: str
    region: str
    availability_zone: str
    monthly_cost: float


class UnattachedVolumesResponse(BaseModel):
    total_unattached_volumes: int
    total_potential_savings: float
    unattached_volumes: List[UnattachedVolume]


# Analytics Schemas
class SavingsBreakdown(BaseModel):
    idle_instances_savings: float
    unattached_volumes_savings: float


class RecommendationsCount(BaseModel):
    total: int
    by_severity: Dict[str, int]


class SavingsResponse(BaseModel):
    total_potential_savings: float
    breakdown: SavingsBreakdown
    recommendations_count: RecommendationsCount
    last_analysis: str


class AnalysisRequest(BaseModel):
    regions: Optional[List[str]] = None
    cpu_threshold: Optional[float] = 5.0
    include_cost_data: Optional[bool] = True
    lookback_days: Optional[int] = 30


class AnalysisSummary(BaseModel):
    total_instances: int
    running_instances: int
    idle_instances: int
    unattached_volumes: int
    cost_records: int


class CostData(BaseModel):
    total_cost_30_days: float
    average_daily_cost: float


class TopRecommendation(BaseModel):
    resource_id: str
    resource_type: str
    potential_savings: float
    severity: str


class AnalysisResponse(BaseModel):
    analysis_id: str
    timestamp: str
    summary: AnalysisSummary
    total_potential_savings: float
    regions_analyzed: List[str]
    cost_data: CostData
    top_recommendations: List[TopRecommendation]
