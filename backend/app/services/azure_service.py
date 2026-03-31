"""
Real Azure Service — uses Azure SDK for actual API calls
Requires environment variables:
    AZURE_SUBSCRIPTION_ID
    AZURE_TENANT_ID
    AZURE_CLIENT_ID
    AZURE_CLIENT_SECRET

Same PostgreSQL container as AWS/mock — uses azure_* tables.
"""
import os
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from azure.identity import ClientSecretCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.monitor import MonitorManagementClient
from azure.mgmt.costmanagement import CostManagementClient
from azure.mgmt.costmanagement.models import (
    QueryDefinition, QueryTimePeriod, QueryDataset,
    QueryAggregation, QueryGrouping, QueryColumnType,
    TimeframeType,
)

# Reuse the ORM models defined in azure_mock_service
from .azure_mock_service import (
    AzureBase,
    AzureCostData,
    AzureVMInstance,
    AzureManagedDisk,
    AzureOptimizationRecommendation,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AzureService:
    """
    Real Azure Service — makes live Azure SDK calls.
    Uses the same PostgreSQL container and azure_* tables as the mock service.
    """

    def __init__(self, database_url: str):
        self.subscription_id = os.getenv('AZURE_SUBSCRIPTION_ID')
        tenant_id = os.getenv('AZURE_TENANT_ID')
        client_id = os.getenv('AZURE_CLIENT_ID')
        client_secret = os.getenv('AZURE_CLIENT_SECRET')

        if not all([self.subscription_id, tenant_id, client_id, client_secret]):
            raise ValueError(
                "Missing Azure credentials. Set AZURE_SUBSCRIPTION_ID, "
                "AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET."
            )

        self.credential = ClientSecretCredential(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret,
        )

        self.compute_client = ComputeManagementClient(self.credential, self.subscription_id)
        self.monitor_client = MonitorManagementClient(self.credential, self.subscription_id)
        self.cost_client = CostManagementClient(self.credential)

        self.engine = create_engine(database_url)
        AzureBase.metadata.create_all(self.engine)

        logger.info(f"Azure Service initialized (subscription: {self.subscription_id})")

    def get_db_session(self) -> Session:
        from sqlalchemy.orm import sessionmaker
        return sessionmaker(bind=self.engine)()

    # ── Cost Data ──────────────────────────────────────────────────────────

    def fetch_cost_data(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Dict]:
        """Fetch real cost data from Azure Cost Management API."""
        if not end_date:
            end_date = datetime.now()
        if not start_date:
            start_date = end_date - timedelta(days=30)

        logger.info(f"Fetching Azure cost data {start_date.date()} -> {end_date.date()}")

        scope = f"/subscriptions/{self.subscription_id}"
        query = QueryDefinition(
            type="Usage",
            timeframe=TimeframeType.CUSTOM,
            time_period=QueryTimePeriod(
                from_property=start_date,
                to=end_date,
            ),
            dataset=QueryDataset(
                granularity="Daily",
                aggregation={
                    "totalCost": QueryAggregation(name="Cost", function="Sum"),
                },
                grouping=[
                    QueryGrouping(type=QueryColumnType.DIMENSION, name="ServiceName"),
                    QueryGrouping(type=QueryColumnType.DIMENSION, name="ResourceLocation"),
                ],
            ),
        )

        result = self.cost_client.query.usage(scope=scope, parameters=query)

        cost_records = []
        db_session = self.get_db_session()
        try:
            for row in result.rows:
                cost = float(row[0])
                service_name = str(row[1]) if len(row) > 1 else "Unknown"
                region = str(row[2]) if len(row) > 2 else "Unknown"
                record_date = datetime.strptime(str(row[3])[:10], "%Y-%m-%d") if len(row) > 3 else start_date

                record = {
                    "service_name": service_name,
                    "cost": round(cost, 2),
                    "usage": 0.0,
                    "start_date": record_date,
                    "end_date": record_date,
                    "region": region,
                }
                cost_records.append(record)

                db_session.add(AzureCostData(
                    service_name=service_name,
                    cost=cost,
                    usage=0.0,
                    start_date=record_date,
                    end_date=record_date,
                    region=region,
                ))
            db_session.commit()
        finally:
            db_session.close()

        logger.info(f"Fetched and stored {len(cost_records)} real Azure cost records")
        return cost_records

    # ── VM Instances ───────────────────────────────────────────────────────

    def scan_vm_instances(self, resource_groups: Optional[List[str]] = None) -> List[Dict]:
        """Scan all VMs across the subscription (or specific resource groups)."""
        logger.info("Scanning real Azure VMs...")

        vms_raw = list(self.compute_client.virtual_machines.list_all())
        vm_list = []
        db_session = self.get_db_session()

        try:
            for vm in vms_raw:
                rg = vm.id.split("/")[4]
                if resource_groups and rg not in resource_groups:
                    continue

                # Get instance view for power state
                instance_view = self.compute_client.virtual_machines.instance_view(rg, vm.name)
                state = "Unknown"
                for status in (instance_view.statuses or []):
                    if status.code and status.code.startswith("PowerState/"):
                        state = status.code.replace("PowerState/", "").capitalize()
                        break

                cpu = self._get_vm_cpu(vm.id) if state == "Running" else 0.0
                is_idle = cpu < 5.0 and state == "Running"

                record = {
                    "vm_id": vm.name,
                    "vm_size": vm.hardware_profile.vm_size if vm.hardware_profile else "Unknown",
                    "state": state,
                    "region": vm.location,
                    "resource_group": rg,
                    "cpu_utilization": cpu,
                    "is_idle": is_idle,
                    "launch_time": datetime.utcnow().isoformat(),
                    "tags": [{"Key": k, "Value": v} for k, v in (vm.tags or {}).items()],
                }
                vm_list.append(record)

                existing = db_session.query(AzureVMInstance).filter_by(vm_id=vm.name).first()
                if existing:
                    existing.state = state
                    existing.cpu_utilization = cpu
                    existing.is_idle = is_idle
                    existing.updated_at = datetime.utcnow()
                else:
                    db_session.add(AzureVMInstance(
                        vm_id=vm.name,
                        vm_size=record["vm_size"],
                        state=state,
                        region=vm.location,
                        resource_group=rg,
                        cpu_utilization=cpu,
                        is_idle=is_idle,
                        launch_time=datetime.utcnow(),
                        tags=json.dumps(record["tags"]),
                    ))

            db_session.commit()
        finally:
            db_session.close()

        logger.info(f"Scanned {len(vm_list)} real Azure VMs")
        return vm_list

    def _get_vm_cpu(self, vm_resource_id: str, hours: int = 168) -> float:
        """Get average CPU utilization from Azure Monitor for the past N hours."""
        try:
            end = datetime.utcnow()
            start = end - timedelta(hours=hours)
            timespan = f"{start.isoformat()}Z/{end.isoformat()}Z"

            metrics = self.monitor_client.metrics.list(
                resource_uri=vm_resource_id,
                timespan=timespan,
                interval="PT1H",
                metricnames="Percentage CPU",
                aggregation="Average",
            )

            values = []
            for metric in metrics.value:
                for ts in metric.timeseries:
                    for dp in ts.data:
                        if dp.average is not None:
                            values.append(dp.average)

            return round(sum(values) / len(values), 2) if values else 0.0

        except Exception as e:
            logger.warning(f"Could not fetch CPU for {vm_resource_id}: {e}")
            return 0.0

    # ── Managed Disks ──────────────────────────────────────────────────────

    def find_unattached_disks(self) -> List[Dict]:
        """Find all unattached Managed Disks across the subscription."""
        logger.info("Scanning real Azure Managed Disks...")

        all_disks = list(self.compute_client.disks.list())
        unattached = []
        db_session = self.get_db_session()

        cost_per_gb = {
            "Premium_LRS": 0.17, "Standard_LRS": 0.05,
            "StandardSSD_LRS": 0.10, "UltraSSD_LRS": 0.29,
        }

        try:
            for disk in all_disks:
                rg = disk.id.split("/")[4]
                is_attached = disk.disk_state != "Unattached"
                size = disk.disk_size_gb or 0
                disk_type = disk.sku.name if disk.sku else "Standard_LRS"
                monthly_cost = round(size * cost_per_gb.get(disk_type, 0.10), 2)

                existing = db_session.query(AzureManagedDisk).filter_by(disk_id=disk.name).first()
                state = "Attached" if is_attached else "Unattached"

                if existing:
                    existing.state = state
                    existing.is_attached = is_attached
                    existing.updated_at = datetime.utcnow()
                else:
                    db_session.add(AzureManagedDisk(
                        disk_id=disk.name,
                        size=size,
                        disk_type=disk_type,
                        state=state,
                        is_attached=is_attached,
                        region=disk.location,
                        resource_group=rg,
                        monthly_cost=monthly_cost,
                    ))

                if not is_attached:
                    unattached.append({
                        "disk_id": disk.name,
                        "size": size,
                        "disk_type": disk_type,
                        "region": disk.location,
                        "resource_group": rg,
                        "monthly_cost": monthly_cost,
                    })
                    db_session.add(AzureOptimizationRecommendation(
                        resource_id=disk.name,
                        resource_type="ManagedDisk",
                        recommendation_type="UNATTACHED_DISK",
                        description=f"Unattached {size}GB {disk_type} disk in {rg}",
                        potential_savings=monthly_cost,
                        severity="LOW",
                        region=disk.location,
                    ))

            db_session.commit()
        finally:
            db_session.close()

        logger.info(f"Found {len(unattached)} real unattached Azure Managed Disks")
        return unattached

    # ── Idle VMs ───────────────────────────────────────────────────────────

    def identify_idle_vms(self, cpu_threshold: float = 5.0) -> List[Dict]:
        """Identify idle VMs from the DB (after scan_vm_instances has run)."""
        db_session = self.get_db_session()
        idle = []
        try:
            vms = db_session.query(AzureVMInstance).filter_by(state="Running").all()
            for vm in vms:
                if vm.cpu_utilization < cpu_threshold:
                    savings = self._estimate_vm_cost(vm.vm_size)
                    idle.append({
                        "vm_id": vm.vm_id,
                        "vm_size": vm.vm_size,
                        "region": vm.region,
                        "resource_group": vm.resource_group,
                        "cpu_utilization": vm.cpu_utilization,
                        "potential_savings": savings,
                        "recommendation": "Consider deallocating or rightsizing this VM",
                    })
                    vm.is_idle = True
                    db_session.add(AzureOptimizationRecommendation(
                        resource_id=vm.vm_id,
                        resource_type="VirtualMachine",
                        recommendation_type="IDLE_VM",
                        description=f"VM {vm.vm_id} ({vm.vm_size}) has {vm.cpu_utilization}% avg CPU",
                        potential_savings=savings,
                        severity="MEDIUM" if vm.cpu_utilization > 2.0 else "HIGH",
                        region=vm.region,
                    ))
            db_session.commit()
        finally:
            db_session.close()

        logger.info(f"Identified {len(idle)} idle real Azure VMs")
        return idle

    def _estimate_vm_cost(self, vm_size: str) -> float:
        costs = {
            "Standard_B1s": 7.4, "Standard_B2s": 29.6, "Standard_B4ms": 59.1,
            "Standard_D2s_v3": 70.1, "Standard_D4s_v3": 140.2, "Standard_D8s_v3": 280.3,
            "Standard_E2s_v3": 91.3, "Standard_E4s_v3": 182.6,
            "Standard_F2s_v2": 61.3, "Standard_F4s_v2": 122.6,
            "Standard_NC6": 657.0, "Standard_A2_v2": 40.2,
        }
        return costs.get(vm_size, 60.0)

    # ── Full Analysis ──────────────────────────────────────────────────────

    def run_full_analysis(self) -> Dict:
        logger.info("Starting real Azure cost optimization analysis")

        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "mode": "REAL_AZURE",
            "provider": "azure",
        }

        results["cost_data"] = self.fetch_cost_data()
        results["vm_instances"] = self.scan_vm_instances()
        results["idle_vms"] = self.identify_idle_vms()
        results["unattached_disks"] = self.find_unattached_disks()

        idle_savings = sum(v.get("potential_savings", 0) for v in results["idle_vms"])
        disk_savings = sum(d.get("monthly_cost", 0) for d in results["unattached_disks"])
        results["total_potential_savings"] = round(idle_savings + disk_savings, 2)

        results["summary"] = {
            "total_vms": len(results["vm_instances"]),
            "running_vms": sum(1 for v in results["vm_instances"] if v["state"] == "Running"),
            "idle_vms": len(results["idle_vms"]),
            "unattached_disks": len(results["unattached_disks"]),
            "cost_records": len(results["cost_data"]),
        }

        logger.info(f"Real Azure analysis complete. Potential savings: ${results['total_potential_savings']:.2f}")
        return results
