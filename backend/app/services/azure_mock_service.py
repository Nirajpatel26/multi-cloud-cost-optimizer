"""
Mock Azure Service for Local Testing
Uses mock data instead of real Azure SDK calls - ZERO COST testing
Same PostgreSQL container as AWS, separate azure_* tables
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
import json
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base

from .azure_mock_data_generator import AzureMockDataGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

AzureBase = declarative_base()


class AzureCostData(AzureBase):
    __tablename__ = 'azure_cost_data'

    id = Column(Integer, primary_key=True, autoincrement=True)
    service_name = Column(String(100))
    cost = Column(Float)
    usage = Column(Float)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    region = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)


class AzureVMInstance(AzureBase):
    __tablename__ = 'azure_vm_instances'

    id = Column(Integer, primary_key=True, autoincrement=True)
    vm_id = Column(String(100), unique=True, index=True)
    vm_size = Column(String(50))
    state = Column(String(30))
    region = Column(String(100))
    resource_group = Column(String(100))
    cpu_utilization = Column(Float)
    is_idle = Column(Boolean, default=False)
    launch_time = Column(DateTime)
    tags = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AzureManagedDisk(AzureBase):
    __tablename__ = 'azure_managed_disks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    disk_id = Column(String(100), unique=True, index=True)
    size = Column(Integer)
    disk_type = Column(String(30))
    state = Column(String(30))
    is_attached = Column(Boolean)
    region = Column(String(100))
    resource_group = Column(String(100))
    monthly_cost = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AzureOptimizationRecommendation(AzureBase):
    __tablename__ = 'azure_optimization_recommendations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    resource_id = Column(String(100), index=True)
    resource_type = Column(String(50))
    recommendation_type = Column(String(100))
    description = Column(Text)
    potential_savings = Column(Float)
    severity = Column(String(20))
    region = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)


class AzureMockService:
    """
    Mock Azure Service for local testing - NO AZURE SDK CALLS
    Uses same PostgreSQL container as AWS, separate azure_* tables
    """

    def __init__(self, database_url: str = 'postgresql://admin:admin@localhost:5432/cost_optimizer_mock'):
        self.mock_generator = AzureMockDataGenerator()
        self.engine = create_engine(database_url)
        AzureBase.metadata.create_all(self.engine)
        logger.info("Azure Mock Service initialized (ZERO AZURE SDK COSTS)")

    def get_db_session(self) -> Session:
        from sqlalchemy.orm import sessionmaker
        SessionLocal = sessionmaker(bind=self.engine)
        return SessionLocal()

    def fetch_cost_data(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Dict]:
        if not end_date:
            end_date = datetime.now()
        if not start_date:
            start_date = end_date - timedelta(days=30)

        days_diff = (end_date - start_date).days
        mock_costs = self.mock_generator.generate_cost_data(days=days_diff)

        db_session = self.get_db_session()
        try:
            for record in mock_costs:
                db_session.add(AzureCostData(
                    service_name=record['service_name'],
                    cost=record['cost'],
                    usage=record['usage'],
                    start_date=record['start_date'],
                    end_date=record['end_date'],
                    region=record['region'],
                ))
            db_session.commit()
        finally:
            db_session.close()

        logger.info(f"Stored {len(mock_costs)} Azure mock cost records")
        return mock_costs

    def scan_vm_instances(self, regions: Optional[List[str]] = None) -> List[Dict]:
        logger.info("Generating mock Azure VM instances...")
        mock_vms = self.mock_generator.generate_vm_instances(count=20)

        db_session = self.get_db_session()
        try:
            for vm in mock_vms:
                existing = db_session.query(AzureVMInstance).filter_by(vm_id=vm['vm_id']).first()
                if existing:
                    existing.state = vm['state']
                    existing.cpu_utilization = vm['cpu_utilization']
                    existing.updated_at = datetime.utcnow()
                else:
                    db_session.add(AzureVMInstance(
                        vm_id=vm['vm_id'],
                        vm_size=vm['vm_size'],
                        state=vm['state'],
                        region=vm['region'],
                        resource_group=vm['resource_group'],
                        cpu_utilization=vm['cpu_utilization'],
                        is_idle=vm['is_idle'],
                        launch_time=datetime.fromisoformat(vm['launch_time']),
                        tags=json.dumps(vm['tags']),
                    ))
            db_session.commit()
        finally:
            db_session.close()

        logger.info(f"Stored {len(mock_vms)} Azure VM instances")
        return mock_vms

    def identify_idle_vms(self, cpu_threshold: float = 5.0) -> List[Dict]:
        logger.info(f"Identifying idle Azure VMs (CPU threshold: {cpu_threshold}%)...")

        db_session = self.get_db_session()
        try:
            vms = db_session.query(AzureVMInstance).filter_by(state='Running').all()
            idle_vms = []

            for vm in vms:
                if vm.cpu_utilization < cpu_threshold:
                    potential_savings = self._estimate_vm_cost(vm.vm_size)
                    idle_vms.append({
                        'vm_id': vm.vm_id,
                        'vm_size': vm.vm_size,
                        'region': vm.region,
                        'resource_group': vm.resource_group,
                        'cpu_utilization': vm.cpu_utilization,
                        'potential_savings': potential_savings,
                        'recommendation': 'Consider deallocating or rightsizing this VM',
                    })
                    vm.is_idle = True
                    db_session.add(AzureOptimizationRecommendation(
                        resource_id=vm.vm_id,
                        resource_type='VirtualMachine',
                        recommendation_type='IDLE_VM',
                        description=f'VM {vm.vm_id} ({vm.vm_size}) has {vm.cpu_utilization}% CPU utilization',
                        potential_savings=potential_savings,
                        severity='MEDIUM' if vm.cpu_utilization > 2.0 else 'HIGH',
                        region=vm.region,
                    ))

            db_session.commit()
        finally:
            db_session.close()

        logger.info(f"Found {len(idle_vms)} idle Azure VMs")
        return idle_vms

    def find_unattached_disks(self) -> List[Dict]:
        logger.info("Finding unattached Azure Managed Disks...")
        mock_disks = self.mock_generator.generate_managed_disks(count=15)
        unattached = []

        db_session = self.get_db_session()
        try:
            for disk in mock_disks:
                existing = db_session.query(AzureManagedDisk).filter_by(disk_id=disk['disk_id']).first()
                if existing:
                    existing.state = disk['state']
                    existing.is_attached = disk['is_attached']
                    existing.updated_at = datetime.utcnow()
                else:
                    db_session.add(AzureManagedDisk(
                        disk_id=disk['disk_id'],
                        size=disk['size'],
                        disk_type=disk['disk_type'],
                        state=disk['state'],
                        is_attached=disk['is_attached'],
                        region=disk['region'],
                        resource_group=disk['resource_group'],
                        monthly_cost=disk['monthly_cost'],
                    ))

                if not disk['is_attached']:
                    unattached.append({
                        'disk_id': disk['disk_id'],
                        'size': disk['size'],
                        'disk_type': disk['disk_type'],
                        'region': disk['region'],
                        'resource_group': disk['resource_group'],
                        'monthly_cost': disk['monthly_cost'],
                    })
                    db_session.add(AzureOptimizationRecommendation(
                        resource_id=disk['disk_id'],
                        resource_type='ManagedDisk',
                        recommendation_type='UNATTACHED_DISK',
                        description=f'Unattached {disk["size"]}GB {disk["disk_type"]} managed disk',
                        potential_savings=disk['monthly_cost'],
                        severity='LOW',
                        region=disk['region'],
                    ))

            db_session.commit()
        finally:
            db_session.close()

        logger.info(f"Found {len(unattached)} unattached Azure Managed Disks")
        return unattached

    def _estimate_vm_cost(self, vm_size: str) -> float:
        costs = {
            'Standard_B1s': 7.4,
            'Standard_B2s': 29.6,
            'Standard_B4ms': 59.1,
            'Standard_D2s_v3': 70.1,
            'Standard_D4s_v3': 140.2,
            'Standard_D8s_v3': 280.3,
            'Standard_E2s_v3': 91.3,
            'Standard_E4s_v3': 182.6,
            'Standard_F2s_v2': 61.3,
            'Standard_F4s_v2': 122.6,
            'Standard_NC6': 657.0,
            'Standard_A2_v2': 40.2,
        }
        return costs.get(vm_size, 60.0)

    def run_full_analysis(self) -> Dict:
        logger.info("Starting full Azure mock cost optimization analysis")

        results = {
            'timestamp': datetime.utcnow().isoformat(),
            'mode': 'AZURE_MOCK_DATA',
            'provider': 'azure',
        }

        results['cost_data'] = self.fetch_cost_data()
        results['vm_instances'] = self.scan_vm_instances()
        results['idle_vms'] = self.identify_idle_vms()
        results['unattached_disks'] = self.find_unattached_disks()

        idle_savings = sum(v.get('potential_savings', 0) for v in results['idle_vms'])
        disk_savings = sum(d.get('monthly_cost', 0) for d in results['unattached_disks'])
        results['total_potential_savings'] = round(idle_savings + disk_savings, 2)

        results['summary'] = {
            'total_vms': len(results['vm_instances']),
            'running_vms': sum(1 for v in results['vm_instances'] if v['state'] == 'Running'),
            'idle_vms': len(results['idle_vms']),
            'unattached_disks': len(results['unattached_disks']),
            'cost_records': len(results['cost_data']),
        }

        logger.info(f"Azure analysis complete. Potential savings: ${results['total_potential_savings']:.2f}")
        return results
