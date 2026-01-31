"""
Mock Data Generator for AWS Resources
Generates realistic synthetic data for local testing without AWS API costs
"""
import random
from datetime import datetime, timedelta
from typing import List, Dict
import json


class AWSMockDataGenerator:
    """Generate realistic mock AWS data for testing"""
    
    INSTANCE_TYPES = [
        't2.micro', 't2.small', 't2.medium', 't2.large',
        't3.micro', 't3.small', 't3.medium', 't3.large',
        'm5.large', 'm5.xlarge', 'm5.2xlarge',
        'c5.large', 'c5.xlarge', 'r5.large'
    ]
    
    REGIONS = [
        'us-east-1', 'us-east-2', 'us-west-1', 'us-west-2',
        'eu-west-1', 'eu-central-1', 'ap-southeast-1', 'ap-northeast-1'
    ]
    
    SERVICES = [
        'Amazon Elastic Compute Cloud - Compute',
        'Amazon Simple Storage Service',
        'Amazon Relational Database Service',
        'Amazon CloudFront',
        'Amazon DynamoDB',
        'AWS Lambda',
        'Amazon EC2 Container Service'
    ]
    
    VOLUME_TYPES = ['gp2', 'gp3', 'io1', 'io2', 'st1', 'sc1']
    
    INSTANCE_STATES = ['running', 'stopped', 'pending', 'terminated']
    
    ENVIRONMENTS = ['production', 'staging', 'development', 'testing']
    PROJECTS = ['web-app', 'data-pipeline', 'api-service', 'ml-training', 'analytics']
    
    @staticmethod
    def generate_instance_id() -> str:
        """Generate realistic EC2 instance ID"""
        return f"i-{random.randbytes(8).hex()}"
    
    @staticmethod
    def generate_volume_id() -> str:
        """Generate realistic EBS volume ID"""
        return f"vol-{random.randbytes(8).hex()}"
    
    @staticmethod
    def generate_tags(env: str = None, project: str = None) -> List[Dict]:
        """Generate realistic resource tags"""
        tags = [
            {'Key': 'Environment', 'Value': env or random.choice(AWSMockDataGenerator.ENVIRONMENTS)},
            {'Key': 'Project', 'Value': project or random.choice(AWSMockDataGenerator.PROJECTS)},
            {'Key': 'ManagedBy', 'Value': 'Terraform'},
            {'Key': 'Owner', 'Value': random.choice(['team-backend', 'team-data', 'team-infra'])}
        ]
        return tags
    
    @staticmethod
    def generate_cost_data(days: int = 30) -> List[Dict]:
        """
        Generate mock cost data for specified number of days
        
        Args:
            days: Number of days of historical data
            
        Returns:
            List of cost records
        """
        cost_data = []
        end_date = datetime.now()
        
        for day in range(days):
            current_date = end_date - timedelta(days=day)
            
            for service in AWSMockDataGenerator.SERVICES:
                for region in random.sample(AWSMockDataGenerator.REGIONS, k=random.randint(2, 4)):
                    # Generate realistic cost variations
                    base_cost = random.uniform(5.0, 500.0)
                    
                    # Add some variation (±20%)
                    variation = base_cost * random.uniform(-0.2, 0.2)
                    daily_cost = base_cost + variation
                    
                    cost_record = {
                        'service_name': service,
                        'cost': round(daily_cost, 2),
                        'usage': round(random.uniform(10.0, 1000.0), 2),
                        'start_date': current_date.replace(hour=0, minute=0, second=0),
                        'end_date': current_date.replace(hour=23, minute=59, second=59),
                        'region': region
                    }
                    cost_data.append(cost_record)
        
        return cost_data
    
    @staticmethod
    def generate_ec2_instances(count: int = 20) -> List[Dict]:
        """
        Generate mock EC2 instance data
        
        Args:
            count: Number of instances to generate
            
        Returns:
            List of EC2 instance records
        """
        instances = []
        
        for i in range(count):
            region = random.choice(AWSMockDataGenerator.REGIONS)
            instance_type = random.choice(AWSMockDataGenerator.INSTANCE_TYPES)
            state = random.choice(AWSMockDataGenerator.INSTANCE_STATES)
            
            # 70% running, 20% stopped, 10% other states
            state_weights = [0.7, 0.2, 0.05, 0.05]
            state = random.choices(AWSMockDataGenerator.INSTANCE_STATES, weights=state_weights)[0]
            
            # Launch time between 1 day and 6 months ago
            launch_days_ago = random.randint(1, 180)
            launch_time = datetime.now() - timedelta(days=launch_days_ago)
            
            instance = {
                'instance_id': AWSMockDataGenerator.generate_instance_id(),
                'instance_type': instance_type,
                'state': state,
                'region': region,
                'availability_zone': f"{region}{random.choice(['a', 'b', 'c'])}",
                'launch_time': launch_time,
                'tags': AWSMockDataGenerator.generate_tags()
            }
            instances.append(instance)
        
        return instances
    
    @staticmethod
    def generate_cpu_utilization(
        instance_state: str,
        hours: int = 24
    ) -> List[Dict]:
        """
        Generate mock CPU utilization data for an instance
        
        Args:
            instance_state: State of the instance (running, stopped, etc.)
            hours: Number of hours of metrics to generate
            
        Returns:
            List of CPU utilization datapoints
        """
        if instance_state != 'running':
            return []
        
        datapoints = []
        end_time = datetime.now()
        
        # Determine if this is an "idle" instance (30% chance)
        is_idle = random.random() < 0.3
        
        for hour in range(hours):
            timestamp = end_time - timedelta(hours=hour)
            
            if is_idle:
                # Idle instance: 0-10% CPU
                cpu_value = random.uniform(0.5, 10.0)
            else:
                # Active instance: realistic workload patterns
                # Higher during business hours (9 AM - 5 PM)
                hour_of_day = timestamp.hour
                
                if 9 <= hour_of_day <= 17:
                    cpu_value = random.uniform(30.0, 85.0)
                else:
                    cpu_value = random.uniform(10.0, 40.0)
            
            datapoint = {
                'Timestamp': timestamp,
                'Average': round(cpu_value, 2),
                'Unit': 'Percent'
            }
            datapoints.append(datapoint)
        
        return datapoints
    
    @staticmethod
    def generate_ebs_volumes(count: int = 15) -> List[Dict]:
        """
        Generate mock EBS volume data
        
        Args:
            count: Number of volumes to generate
            
        Returns:
            List of EBS volume records
        """
        volumes = []
        
        for i in range(count):
            region = random.choice(AWSMockDataGenerator.REGIONS)
            volume_type = random.choice(AWSMockDataGenerator.VOLUME_TYPES)
            size = random.choice([8, 16, 32, 50, 100, 200, 500, 1000])
            
            # 30% unattached, 70% attached
            is_attached = random.random() > 0.3
            
            volume = {
                'volume_id': AWSMockDataGenerator.generate_volume_id(),
                'size': size,
                'volume_type': volume_type,
                'state': 'in-use' if is_attached else 'available',
                'is_attached': is_attached,
                'instance_id': AWSMockDataGenerator.generate_instance_id() if is_attached else None,
                'region': region,
                'availability_zone': f"{region}{random.choice(['a', 'b', 'c'])}",
                'created_time': datetime.now() - timedelta(days=random.randint(10, 365))
            }
            volumes.append(volume)
        
        return volumes
    
    @staticmethod
    def generate_full_mock_dataset() -> Dict:
        """
        Generate a complete mock dataset for testing
        
        Returns:
            Dictionary with all mock data
        """
        print("Generating mock AWS dataset...")
        
        dataset = {
            'cost_data': AWSMockDataGenerator.generate_cost_data(days=30),
            'ec2_instances': AWSMockDataGenerator.generate_ec2_instances(count=20),
            'ebs_volumes': AWSMockDataGenerator.generate_ebs_volumes(count=15),
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'total_instances': 20,
                'total_volumes': 15,
                'total_cost_records': 0,  # Will be calculated
                'regions_covered': AWSMockDataGenerator.REGIONS
            }
        }
        
        # Add CPU utilization for each running instance
        for instance in dataset['ec2_instances']:
            instance['cpu_utilization_data'] = AWSMockDataGenerator.generate_cpu_utilization(
                instance['state'],
                hours=168  # 7 days
            )
        
        dataset['metadata']['total_cost_records'] = len(dataset['cost_data'])
        
        print(f"✅ Generated {len(dataset['ec2_instances'])} EC2 instances")
        print(f"✅ Generated {len(dataset['ebs_volumes'])} EBS volumes")
        print(f"✅ Generated {len(dataset['cost_data'])} cost records")
        
        return dataset


# Example usage and testing
if __name__ == "__main__":
    generator = AWSMockDataGenerator()
    
    # Generate full dataset
    mock_data = generator.generate_full_mock_dataset()
    
    # Display summary
    print("\n📊 Mock Data Summary:")
    print(f"Total EC2 Instances: {len(mock_data['ec2_instances'])}")
    print(f"Running Instances: {sum(1 for i in mock_data['ec2_instances'] if i['state'] == 'running')}")
    print(f"Total EBS Volumes: {len(mock_data['ebs_volumes'])}")
    print(f"Unattached Volumes: {sum(1 for v in mock_data['ebs_volumes'] if not v['is_attached'])}")
    print(f"Cost Records (30 days): {len(mock_data['cost_data'])}")
    
    # Calculate idle instances
    idle_count = 0
    for instance in mock_data['ec2_instances']:
        if instance['state'] == 'running' and instance['cpu_utilization_data']:
            avg_cpu = sum(dp['Average'] for dp in instance['cpu_utilization_data']) / len(instance['cpu_utilization_data'])
            if avg_cpu < 5.0:
                idle_count += 1
    
    print(f"Potential Idle Instances (CPU < 5%): {idle_count}")
    
    # Save to file for inspection
    output_file = "mock_aws_data.json"
    with open(output_file, 'w') as f:
        # Convert datetime objects to strings for JSON serialization
        def datetime_converter(o):
            if isinstance(o, datetime):
                return o.isoformat()
        
        json.dump(mock_data, f, default=datetime_converter, indent=2)
    
    print(f"\n💾 Mock data saved to: {output_file}")
