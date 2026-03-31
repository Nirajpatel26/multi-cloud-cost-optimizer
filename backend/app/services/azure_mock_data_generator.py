"""
Mock Data Generator for Azure Resources
Generates realistic synthetic Azure data for local testing
"""
import random
from datetime import datetime, timedelta
from typing import List, Dict


class AzureMockDataGenerator:
    """Generate realistic mock Azure resource data for testing"""

    VM_SIZES = [
        'Standard_B1s', 'Standard_B2s', 'Standard_B4ms',
        'Standard_D2s_v3', 'Standard_D4s_v3', 'Standard_D8s_v3',
        'Standard_E2s_v3', 'Standard_E4s_v3',
        'Standard_F2s_v2', 'Standard_F4s_v2',
        'Standard_NC6', 'Standard_A2_v2',
    ]

    REGIONS = [
        'East US', 'East US 2', 'West US', 'West US 2',
        'North Europe', 'West Europe',
        'Southeast Asia', 'East Asia',
        'UK South', 'Australia East',
    ]

    SERVICES = [
        'Azure Virtual Machines',
        'Azure Blob Storage',
        'Azure SQL Database',
        'Azure Kubernetes Service',
        'Azure Functions',
        'Azure CDN',
        'Azure Load Balancer',
    ]

    DISK_TYPES = ['Premium_LRS', 'Standard_LRS', 'StandardSSD_LRS', 'UltraSSD_LRS']

    VM_STATES = ['Running', 'Deallocated', 'Stopped', 'Starting']

    ENVIRONMENTS = ['production', 'staging', 'development', 'testing']
    PROJECTS = ['web-app', 'data-pipeline', 'api-service', 'ml-training', 'analytics']

    @staticmethod
    def generate_vm_id() -> str:
        return f"vm-{random.randbytes(6).hex()}"

    @staticmethod
    def generate_disk_id() -> str:
        return f"disk-{random.randbytes(6).hex()}"

    @staticmethod
    def generate_resource_group() -> str:
        groups = ['rg-prod', 'rg-staging', 'rg-dev', 'rg-infra', 'rg-data']
        return random.choice(groups)

    @staticmethod
    def generate_tags(env: str = None, project: str = None) -> List[Dict]:
        return [
            {'Key': 'Environment', 'Value': env or random.choice(AzureMockDataGenerator.ENVIRONMENTS)},
            {'Key': 'Project', 'Value': project or random.choice(AzureMockDataGenerator.PROJECTS)},
            {'Key': 'ManagedBy', 'Value': 'Terraform'},
            {'Key': 'Owner', 'Value': random.choice(['team-backend', 'team-data', 'team-infra'])},
        ]

    @staticmethod
    def generate_cost_data(days: int = 30) -> List[Dict]:
        cost_data = []
        end_date = datetime.now()

        for day in range(days):
            current_date = end_date - timedelta(days=day)
            for service in AzureMockDataGenerator.SERVICES:
                for region in random.sample(AzureMockDataGenerator.REGIONS, k=random.randint(2, 4)):
                    base_cost = random.uniform(5.0, 450.0)
                    variation = base_cost * random.uniform(-0.2, 0.2)
                    daily_cost = base_cost + variation
                    cost_data.append({
                        'service_name': service,
                        'cost': round(daily_cost, 2),
                        'usage': round(random.uniform(10.0, 1000.0), 2),
                        'start_date': current_date.replace(hour=0, minute=0, second=0),
                        'end_date': current_date.replace(hour=23, minute=59, second=59),
                        'region': region,
                    })

        return cost_data

    @staticmethod
    def generate_vm_instances(count: int = 20) -> List[Dict]:
        instances = []
        for _ in range(count):
            cpu = random.uniform(0.5, 95.0)
            region = random.choice(AzureMockDataGenerator.REGIONS)
            vm_size = random.choice(AzureMockDataGenerator.VM_SIZES)
            state = random.choice(AzureMockDataGenerator.VM_STATES)
            is_idle = cpu < 5.0 and state == 'Running'

            instances.append({
                'vm_id': AzureMockDataGenerator.generate_vm_id(),
                'vm_size': vm_size,
                'state': state,
                'region': region,
                'resource_group': AzureMockDataGenerator.generate_resource_group(),
                'cpu_utilization': round(cpu, 2),
                'is_idle': is_idle,
                'launch_time': (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat(),
                'tags': AzureMockDataGenerator.generate_tags(),
            })

        return instances

    @staticmethod
    def generate_managed_disks(count: int = 15) -> List[Dict]:
        disks = []
        for _ in range(count):
            is_attached = random.choice([True, True, True, False])
            size = random.choice([32, 64, 128, 256, 512, 1024])
            disk_type = random.choice(AzureMockDataGenerator.DISK_TYPES)

            # Approximate monthly cost per GB
            cost_per_gb = {'Premium_LRS': 0.17, 'Standard_LRS': 0.05,
                           'StandardSSD_LRS': 0.10, 'UltraSSD_LRS': 0.29}
            monthly_cost = size * cost_per_gb.get(disk_type, 0.10)

            disks.append({
                'disk_id': AzureMockDataGenerator.generate_disk_id(),
                'size': size,
                'disk_type': disk_type,
                'state': 'Attached' if is_attached else 'Unattached',
                'is_attached': is_attached,
                'region': random.choice(AzureMockDataGenerator.REGIONS),
                'resource_group': AzureMockDataGenerator.generate_resource_group(),
                'monthly_cost': round(monthly_cost, 2),
            })

        return disks

    @staticmethod
    def generate_full_dataset() -> Dict:
        vms = AzureMockDataGenerator.generate_vm_instances(20)
        disks = AzureMockDataGenerator.generate_managed_disks(15)
        costs = AzureMockDataGenerator.generate_cost_data(30)

        idle_vms = [v for v in vms if v['is_idle']]
        unattached_disks = [d for d in disks if not d['is_attached']]

        # Estimate savings
        vm_savings = sum(random.uniform(20, 200) for _ in idle_vms)
        disk_savings = sum(d['monthly_cost'] for d in unattached_disks)

        return {
            'vms': vms,
            'disks': disks,
            'cost_data': costs,
            'metadata': {
                'total_vms': len(vms),
                'running_vms': sum(1 for v in vms if v['state'] == 'Running'),
                'idle_vms': len(idle_vms),
                'unattached_disks': len(unattached_disks),
                'estimated_monthly_savings': round(vm_savings + disk_savings, 2),
            },
        }
