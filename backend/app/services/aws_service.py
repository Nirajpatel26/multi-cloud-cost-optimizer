import boto3
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database Models
Base = declarative_base()

class AWSCostData(Base):
    __tablename__ = 'aws_cost_data'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    service_name = Column(String(100))
    cost = Column(Float)
    usage_type = Column(String(100))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    region = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

class AWSEC2Instance(Base):
    __tablename__ = 'aws_ec2_instances'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    instance_id = Column(String(100), unique=True, index=True)
    instance_type = Column(String(50))
    state = Column(String(20))
    region = Column(String(50))
    availability_zone = Column(String(50))
    launch_time = Column(DateTime)
    cpu_utilization = Column(Float)
    is_idle = Column(Boolean, default=False)
    tags = Column(Text)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AWSEBSVolume(Base):
    __tablename__ = 'aws_ebs_volumes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    volume_id = Column(String(100), unique=True, index=True)
    size = Column(Integer)  # GB
    volume_type = Column(String(20))
    state = Column(String(20))
    is_attached = Column(Boolean)
    instance_id = Column(String(100), nullable=True)
    region = Column(String(50))
    availability_zone = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AWSOptimizationRecommendation(Base):
    __tablename__ = 'aws_optimization_recommendations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    resource_id = Column(String(100), index=True)
    resource_type = Column(String(50))  # EC2, EBS, etc.
    recommendation_type = Column(String(100))
    description = Column(Text)
    potential_savings = Column(Float)
    severity = Column(String(20))  # LOW, MEDIUM, HIGH, CRITICAL
    region = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)


class AWSService:
    """
    AWS Service class for cost analysis and resource optimization
    """
    
    def __init__(
        self, 
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        region_name: str = 'us-east-1',
        database_url: str = 'postgresql://user:password@localhost/cost_optimization'
    ):
        """
        Initialize AWS service with credentials and database connection
        
        Args:
            aws_access_key_id: AWS access key (uses default credentials if None)
            aws_secret_access_key: AWS secret key
            region_name: Default AWS region
            database_url: PostgreSQL connection string
        """
        self.region_name = region_name
        
        # Initialize boto3 clients
        session_kwargs = {'region_name': region_name}
        if aws_access_key_id and aws_secret_access_key:
            session_kwargs.update({
                'aws_access_key_id': aws_access_key_id,
                'aws_secret_access_key': aws_secret_access_key
            })
        
        self.session = boto3.Session(**session_kwargs)
        self.ce_client = self.session.client('ce')  # Cost Explorer
        self.ec2_client = self.session.client('ec2')
        self.cloudwatch_client = self.session.client('cloudwatch')
        
        # Database setup
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)
        
        logger.info(f"AWS Service initialized for region: {region_name}")
    
    def get_db_session(self) -> Session:
        """Create a new database session"""
        from sqlalchemy.orm import sessionmaker
        SessionLocal = sessionmaker(bind=self.engine)
        return SessionLocal()
    
    def fetch_cost_data(
        self, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        granularity: str = 'DAILY'
    ) -> List[Dict]:
        """
        Fetch cost data from AWS Cost Explorer
        
        Args:
            start_date: Start date for cost data (defaults to 30 days ago)
            end_date: End date for cost data (defaults to today)
            granularity: DAILY or MONTHLY
            
        Returns:
            List of cost data dictionaries
        """
        if not end_date:
            end_date = datetime.now()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        try:
            response = self.ce_client.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date.strftime('%Y-%m-%d'),
                    'End': end_date.strftime('%Y-%m-%d')
                },
                Granularity=granularity,
                Metrics=['UnblendedCost', 'UsageQuantity'],
                GroupBy=[
                    {'Type': 'DIMENSION', 'Key': 'SERVICE'},
                    {'Type': 'DIMENSION', 'Key': 'REGION'}
                ]
            )
            
            cost_data = []
            db_session = self.get_db_session()
            
            for result in response['ResultsByTime']:
                period_start = datetime.strptime(result['TimePeriod']['Start'], '%Y-%m-%d')
                period_end = datetime.strptime(result['TimePeriod']['End'], '%Y-%m-%d')
                
                for group in result['Groups']:
                    service_name = group['Keys'][0]
                    region = group['Keys'][1]
                    cost = float(group['Metrics']['UnblendedCost']['Amount'])
                    usage = float(group['Metrics']['UsageQuantity']['Amount'])
                    
                    cost_record = {
                        'service_name': service_name,
                        'cost': cost,
                        'usage': usage,
                        'start_date': period_start,
                        'end_date': period_end,
                        'region': region
                    }
                    cost_data.append(cost_record)
                    
                    # Store in database
                    db_cost = AWSCostData(
                        service_name=service_name,
                        cost=cost,
                        usage_type='standard',
                        start_date=period_start,
                        end_date=period_end,
                        region=region
                    )
                    db_session.add(db_cost)
            
            db_session.commit()
            db_session.close()
            
            logger.info(f"Fetched {len(cost_data)} cost records from AWS Cost Explorer")
            return cost_data
            
        except Exception as e:
            logger.error(f"Error fetching AWS cost data: {str(e)}")
            raise
    
    def scan_ec2_instances(self, regions: Optional[List[str]] = None) -> List[Dict]:
        """
        Scan all EC2 instances across specified regions
        
        Args:
            regions: List of AWS regions (defaults to current region)
            
        Returns:
            List of EC2 instance data
        """
        if not regions:
            regions = [self.region_name]
        
        all_instances = []
        db_session = self.get_db_session()
        
        for region in regions:
            try:
                ec2_client = self.session.client('ec2', region_name=region)
                response = ec2_client.describe_instances()
                
                for reservation in response['Reservations']:
                    for instance in reservation['Instances']:
                        instance_data = {
                            'instance_id': instance['InstanceId'],
                            'instance_type': instance['InstanceType'],
                            'state': instance['State']['Name'],
                            'region': region,
                            'availability_zone': instance['Placement']['AvailabilityZone'],
                            'launch_time': instance['LaunchTime'],
                            'tags': instance.get('Tags', [])
                        }
                        all_instances.append(instance_data)
                        
                        # Store in database
                        db_instance = AWSEC2Instance(
                            instance_id=instance['InstanceId'],
                            instance_type=instance['InstanceType'],
                            state=instance['State']['Name'],
                            region=region,
                            availability_zone=instance['Placement']['AvailabilityZone'],
                            launch_time=instance['LaunchTime'],
                            tags=json.dumps(instance.get('Tags', []))
                        )
                        
                        # Update if exists, insert if new
                        existing = db_session.query(AWSEC2Instance).filter_by(
                            instance_id=instance['InstanceId']
                        ).first()
                        
                        if existing:
                            existing.state = instance['State']['Name']
                            existing.updated_at = datetime.utcnow()
                        else:
                            db_session.add(db_instance)
                
                logger.info(f"Scanned EC2 instances in region {region}")
                
            except Exception as e:
                logger.error(f"Error scanning EC2 instances in {region}: {str(e)}")
        
        db_session.commit()
        db_session.close()
        
        logger.info(f"Total EC2 instances scanned: {len(all_instances)}")
        return all_instances
    
    def get_cpu_utilization(
        self, 
        instance_id: str, 
        region: str,
        period_hours: int = 24
    ) -> float:
        """
        Get CPU utilization for an EC2 instance from CloudWatch
        
        Args:
            instance_id: EC2 instance ID
            region: AWS region
            period_hours: Number of hours to look back
            
        Returns:
            Average CPU utilization percentage
        """
        try:
            cloudwatch_client = self.session.client('cloudwatch', region_name=region)
            
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=period_hours)
            
            response = cloudwatch_client.get_metric_statistics(
                Namespace='AWS/EC2',
                MetricName='CPUUtilization',
                Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,  # 1 hour intervals
                Statistics=['Average']
            )
            
            if response['Datapoints']:
                avg_cpu = sum(dp['Average'] for dp in response['Datapoints']) / len(response['Datapoints'])
                return round(avg_cpu, 2)
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Error getting CPU utilization for {instance_id}: {str(e)}")
            return 0.0
    
    def identify_idle_resources(
        self, 
        cpu_threshold: float = 5.0,
        regions: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Identify idle EC2 instances (CPU < threshold)
        
        Args:
            cpu_threshold: CPU percentage threshold for idle detection
            regions: List of regions to check
            
        Returns:
            List of idle instances with recommendations
        """
        if not regions:
            regions = [self.region_name]
        
        idle_instances = []
        db_session = self.get_db_session()
        
        # Get all running instances
        instances = db_session.query(AWSEC2Instance).filter_by(state='running').all()
        
        for instance in instances:
            if instance.region in regions:
                cpu_util = self.get_cpu_utilization(
                    instance.instance_id, 
                    instance.region,
                    period_hours=168  # 7 days
                )
                
                # Update instance CPU utilization
                instance.cpu_utilization = cpu_util
                instance.is_idle = cpu_util < cpu_threshold
                
                if cpu_util < cpu_threshold:
                    idle_data = {
                        'instance_id': instance.instance_id,
                        'instance_type': instance.instance_type,
                        'region': instance.region,
                        'cpu_utilization': cpu_util,
                        'recommendation': 'Consider stopping or downsizing this instance'
                    }
                    idle_instances.append(idle_data)
                    
                    # Create optimization recommendation
                    recommendation = AWSOptimizationRecommendation(
                        resource_id=instance.instance_id,
                        resource_type='EC2',
                        recommendation_type='IDLE_INSTANCE',
                        description=f'Instance {instance.instance_id} has {cpu_util}% CPU utilization over 7 days',
                        potential_savings=self._estimate_instance_cost(instance.instance_type),
                        severity='MEDIUM' if cpu_util > 2.0 else 'HIGH',
                        region=instance.region
                    )
                    db_session.add(recommendation)
        
        db_session.commit()
        db_session.close()
        
        logger.info(f"Identified {len(idle_instances)} idle instances")
        return idle_instances
    
    def find_unattached_ebs_volumes(
        self, 
        regions: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Find unattached EBS volumes across regions
        
        Args:
            regions: List of AWS regions to check
            
        Returns:
            List of unattached volumes with cost estimates
        """
        if not regions:
            regions = [self.region_name]
        
        unattached_volumes = []
        db_session = self.get_db_session()
        
        for region in regions:
            try:
                ec2_client = self.session.client('ec2', region_name=region)
                response = ec2_client.describe_volumes(
                    Filters=[{'Name': 'status', 'Values': ['available']}]
                )
                
                for volume in response['Volumes']:
                    volume_data = {
                        'volume_id': volume['VolumeId'],
                        'size': volume['Size'],
                        'volume_type': volume['VolumeType'],
                        'region': region,
                        'availability_zone': volume['AvailabilityZone'],
                        'monthly_cost': self._estimate_ebs_cost(volume['Size'], volume['VolumeType'])
                    }
                    unattached_volumes.append(volume_data)
                    
                    # Store in database
                    db_volume = AWSEBSVolume(
                        volume_id=volume['VolumeId'],
                        size=volume['Size'],
                        volume_type=volume['VolumeType'],
                        state='available',
                        is_attached=False,
                        region=region,
                        availability_zone=volume['AvailabilityZone']
                    )
                    
                    existing = db_session.query(AWSEBSVolume).filter_by(
                        volume_id=volume['VolumeId']
                    ).first()
                    
                    if existing:
                        existing.state = 'available'
                        existing.is_attached = False
                        existing.updated_at = datetime.utcnow()
                    else:
                        db_session.add(db_volume)
                    
                    # Create recommendation
                    recommendation = AWSOptimizationRecommendation(
                        resource_id=volume['VolumeId'],
                        resource_type='EBS',
                        recommendation_type='UNATTACHED_VOLUME',
                        description=f'Unattached {volume["Size"]}GB {volume["VolumeType"]} volume',
                        potential_savings=volume_data['monthly_cost'],
                        severity='LOW',
                        region=region
                    )
                    db_session.add(recommendation)
                
                logger.info(f"Found {len(response['Volumes'])} unattached volumes in {region}")
                
            except Exception as e:
                logger.error(f"Error finding unattached volumes in {region}: {str(e)}")
        
        db_session.commit()
        db_session.close()
        
        logger.info(f"Total unattached volumes found: {len(unattached_volumes)}")
        return unattached_volumes
    
    def _estimate_instance_cost(self, instance_type: str) -> float:
        """Estimate monthly cost for EC2 instance (simplified)"""
        # Simplified pricing - should be replaced with actual pricing API
        base_costs = {
            't2.micro': 8.5,
            't2.small': 17.0,
            't2.medium': 34.0,
            't3.micro': 7.5,
            't3.small': 15.0,
            't3.medium': 30.0,
            'm5.large': 70.0,
            'm5.xlarge': 140.0
        }
        return base_costs.get(instance_type, 50.0)
    
    def _estimate_ebs_cost(self, size_gb: int, volume_type: str) -> float:
        """Estimate monthly cost for EBS volume"""
        # Simplified pricing per GB per month
        pricing = {
            'gp2': 0.10,
            'gp3': 0.08,
            'io1': 0.125,
            'io2': 0.125,
            'st1': 0.045,
            'sc1': 0.025
        }
        price_per_gb = pricing.get(volume_type, 0.10)
        return size_gb * price_per_gb
    
    def run_full_analysis(self, regions: Optional[List[str]] = None) -> Dict:
        """
        Run complete AWS cost optimization analysis
        
        Args:
            regions: List of regions to analyze
            
        Returns:
            Dictionary with complete analysis results
        """
        logger.info("Starting full AWS cost optimization analysis")
        
        results = {
            'timestamp': datetime.utcnow().isoformat(),
            'regions': regions or [self.region_name]
        }
        
        # Fetch cost data
        results['cost_data'] = self.fetch_cost_data()
        
        # Scan EC2 instances
        results['ec2_instances'] = self.scan_ec2_instances(regions)
        
        # Identify idle resources
        results['idle_instances'] = self.identify_idle_resources(regions=regions)
        
        # Find unattached volumes
        results['unattached_volumes'] = self.find_unattached_ebs_volumes(regions)
        
        # Calculate total potential savings
        idle_savings = sum(inst.get('potential_savings', 0) for inst in results['idle_instances'])
        volume_savings = sum(vol.get('monthly_cost', 0) for vol in results['unattached_volumes'])
        results['total_potential_savings'] = idle_savings + volume_savings
        
        logger.info(f"Analysis complete. Potential monthly savings: ${results['total_potential_savings']:.2f}")
        
        return results


# Example usage
if __name__ == "__main__":
    # Initialize service
    aws_service = AWSService(
        region_name='us-east-1',
        database_url='postgresql://user:password@localhost:5432/cost_optimization'
    )
    
    # Run full analysis
    results = aws_service.run_full_analysis(regions=['us-east-1', 'us-west-2'])
    
    print(f"Analysis Results:")
    print(f"EC2 Instances: {len(results['ec2_instances'])}")
    print(f"Idle Instances: {len(results['idle_instances'])}")
    print(f"Unattached Volumes: {len(results['unattached_volumes'])}")
    print(f"Potential Monthly Savings: ${results['total_potential_savings']:.2f}")