"""
Mock AWS Service for Local Testing
Uses mock data instead of real AWS API calls - ZERO COST testing
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
import json
from .mock_data_generator import AWSMockDataGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database Models (same as aws_service.py)
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


class AWSMockService:
    """
    Mock AWS Service for local testing - NO AWS API CALLS
    Uses mock data generator for zero-cost development
    """
    
    def __init__(
        self,
        database_url: str = 'postgresql://admin:local_dev_password_2024@localhost:5432/cost_optimizer'
    ):
        """
        Initialize Mock AWS service with database connection
        
        Args:
            database_url: PostgreSQL connection string
        """
        # Initialize mock data generator
        self.mock_generator = AWSMockDataGenerator()
        
        # Database setup
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)
        
        logger.info("Mock AWS Service initialized (ZERO AWS API COSTS)")
    
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
        Fetch MOCK cost data (no AWS API calls)
        
        Args:
            start_date: Start date for cost data (defaults to 30 days ago)
            end_date: End date for cost data (defaults to today)
            granularity: DAILY or MONTHLY
            
        Returns:
            List of mock cost data dictionaries
        """
        if not end_date:
            end_date = datetime.now()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        logger.info(f"Generating mock cost data from {start_date.date()} to {end_date.date()}")
        
        # Generate mock cost data
        days_diff = (end_date - start_date).days
        mock_cost_data = self.mock_generator.generate_cost_data(days=days_diff)
        
        db_session = self.get_db_session()
        
        # Store in database
        for cost_record in mock_cost_data:
            db_cost = AWSCostData(
                service_name=cost_record['service_name'],
                cost=cost_record['cost'],
                usage_type='standard',
                start_date=cost_record['start_date'],
                end_date=cost_record['end_date'],
                region=cost_record['region']
            )
            db_session.add(db_cost)
        
        db_session.commit()
        db_session.close()
        
        logger.info(f"✅ Stored {len(mock_cost_data)} mock cost records in database")
        return mock_cost_data
    
    def scan_ec2_instances(self, regions: Optional[List[str]] = None) -> List[Dict]:
        """
        Scan MOCK EC2 instances (no AWS API calls)
        
        Args:
            regions: List of AWS regions (ignored in mock, generates for all)
            
        Returns:
            List of mock EC2 instance data
        """
        logger.info("Generating mock EC2 instances...")
        
        # Generate mock instances
        mock_instances = self.mock_generator.generate_ec2_instances(count=20)
        
        db_session = self.get_db_session()
        
        for instance in mock_instances:
            # Store in database
            db_instance = AWSEC2Instance(
                instance_id=instance['instance_id'],
                instance_type=instance['instance_type'],
                state=instance['state'],
                region=instance['region'],
                availability_zone=instance['availability_zone'],
                launch_time=instance['launch_time'],
                tags=json.dumps(instance['tags'])
            )
            
            # Update if exists, insert if new
            existing = db_session.query(AWSEC2Instance).filter_by(
                instance_id=instance['instance_id']
            ).first()
            
            if existing:
                existing.state = instance['state']
                existing.updated_at = datetime.utcnow()
            else:
                db_session.add(db_instance)
        
        db_session.commit()
        db_session.close()
        
        logger.info(f"✅ Stored {len(mock_instances)} mock EC2 instances in database")
        return mock_instances
    
    def get_cpu_utilization(
        self, 
        instance_id: str, 
        instance_state: str,
        period_hours: int = 24
    ) -> float:
        """
        Get MOCK CPU utilization (no CloudWatch API calls)
        
        Args:
            instance_id: EC2 instance ID
            instance_state: State of the instance
            period_hours: Number of hours to look back
            
        Returns:
            Average CPU utilization percentage (MOCK DATA)
        """
        # Generate mock CPU utilization
        cpu_data = self.mock_generator.generate_cpu_utilization(instance_state, hours=period_hours)
        
        if cpu_data:
            avg_cpu = sum(dp['Average'] for dp in cpu_data) / len(cpu_data)
            return round(avg_cpu, 2)
        
        return 0.0
    
    def identify_idle_resources(
        self, 
        cpu_threshold: float = 5.0,
        regions: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Identify idle EC2 instances using MOCK data
        
        Args:
            cpu_threshold: CPU percentage threshold for idle detection
            regions: List of regions to check (optional)
            
        Returns:
            List of idle instances with recommendations
        """
        logger.info(f"Identifying idle resources (CPU threshold: {cpu_threshold}%)...")
        
        idle_instances = []
        db_session = self.get_db_session()
        
        # Get all running instances
        instances = db_session.query(AWSEC2Instance).filter_by(state='running').all()
        
        for instance in instances:
            # Get mock CPU utilization
            cpu_util = self.get_cpu_utilization(
                instance.instance_id, 
                instance.state,
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
                    'recommendation': 'Consider stopping or downsizing this instance',
                    'potential_savings': self._estimate_instance_cost(instance.instance_type)
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
        
        logger.info(f"✅ Identified {len(idle_instances)} idle instances")
        return idle_instances
    
    def find_unattached_ebs_volumes(
        self, 
        regions: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Find unattached EBS volumes using MOCK data
        
        Args:
            regions: List of AWS regions to check
            
        Returns:
            List of unattached volumes with cost estimates
        """
        logger.info("Finding unattached EBS volumes (MOCK)...")
        
        # Generate mock volumes
        mock_volumes = self.mock_generator.generate_ebs_volumes(count=15)
        
        unattached_volumes = []
        db_session = self.get_db_session()
        
        for volume in mock_volumes:
            # Only process unattached volumes
            if not volume['is_attached']:
                monthly_cost = self._estimate_ebs_cost(volume['size'], volume['volume_type'])
                
                volume_data = {
                    'volume_id': volume['volume_id'],
                    'size': volume['size'],
                    'volume_type': volume['volume_type'],
                    'region': volume['region'],
                    'availability_zone': volume['availability_zone'],
                    'monthly_cost': monthly_cost
                }
                unattached_volumes.append(volume_data)
            
            # Store all volumes (attached and unattached) in database
            db_volume = AWSEBSVolume(
                volume_id=volume['volume_id'],
                size=volume['size'],
                volume_type=volume['volume_type'],
                state=volume['state'],
                is_attached=volume['is_attached'],
                instance_id=volume['instance_id'],
                region=volume['region'],
                availability_zone=volume['availability_zone']
            )
            
            existing = db_session.query(AWSEBSVolume).filter_by(
                volume_id=volume['volume_id']
            ).first()
            
            if existing:
                existing.state = volume['state']
                existing.is_attached = volume['is_attached']
                existing.updated_at = datetime.utcnow()
            else:
                db_session.add(db_volume)
            
            # Create recommendation only for unattached volumes
            if not volume['is_attached']:
                recommendation = AWSOptimizationRecommendation(
                    resource_id=volume['volume_id'],
                    resource_type='EBS',
                    recommendation_type='UNATTACHED_VOLUME',
                    description=f'Unattached {volume["size"]}GB {volume["volume_type"]} volume',
                    potential_savings=monthly_cost,
                    severity='LOW',
                    region=volume['region']
                )
                db_session.add(recommendation)
        
        db_session.commit()
        db_session.close()
        
        logger.info(f"✅ Found {len(unattached_volumes)} unattached volumes")
        return unattached_volumes
    
    def _estimate_instance_cost(self, instance_type: str) -> float:
        """Estimate monthly cost for EC2 instance (simplified)"""
        base_costs = {
            't2.micro': 8.5,
            't2.small': 17.0,
            't2.medium': 34.0,
            't2.large': 68.0,
            't3.micro': 7.5,
            't3.small': 15.0,
            't3.medium': 30.0,
            't3.large': 60.0,
            'm5.large': 70.0,
            'm5.xlarge': 140.0,
            'm5.2xlarge': 280.0,
            'c5.large': 62.0,
            'c5.xlarge': 124.0,
            'r5.large': 91.0
        }
        return base_costs.get(instance_type, 50.0)
    
    def _estimate_ebs_cost(self, size_gb: int, volume_type: str) -> float:
        """Estimate monthly cost for EBS volume"""
        pricing = {
            'gp2': 0.10,
            'gp3': 0.08,
            'io1': 0.125,
            'io2': 0.125,
            'st1': 0.045,
            'sc1': 0.025
        }
        price_per_gb = pricing.get(volume_type, 0.10)
        return round(size_gb * price_per_gb, 2)
    
    def run_full_analysis(self, regions: Optional[List[str]] = None) -> Dict:
        """
        Run complete AWS cost optimization analysis using MOCK data
        
        Args:
            regions: List of regions to analyze
            
        Returns:
            Dictionary with complete analysis results
        """
        logger.info("🚀 Starting full MOCK AWS cost optimization analysis")
        
        results = {
            'timestamp': datetime.utcnow().isoformat(),
            'mode': 'MOCK_DATA',
            'regions': regions or ['us-east-1', 'us-west-2', 'eu-west-1']
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
        results['total_potential_savings'] = round(idle_savings + volume_savings, 2)
        
        # Add summary statistics
        results['summary'] = {
            'total_instances': len(results['ec2_instances']),
            'running_instances': sum(1 for i in results['ec2_instances'] if i['state'] == 'running'),
            'idle_instances': len(results['idle_instances']),
            'total_volumes': 15,  # Generated count
            'unattached_volumes': len(results['unattached_volumes']),
            'cost_records': len(results['cost_data'])
        }
        
        logger.info(f"✅ Analysis complete. Potential monthly savings: ${results['total_potential_savings']:.2f}")
        logger.info(f"📊 Summary: {results['summary']}")
        
        return results


# Example usage
if __name__ == "__main__":
    # Initialize mock service
    mock_service = AWSMockService(
        database_url='postgresql://admin:local_dev_password_2024@localhost:5432/cost_optimizer'
    )
    
    # Run full analysis with ZERO AWS costs
    print("\n" + "="*60)
    print("🎯 MOCK AWS COST OPTIMIZATION ANALYSIS")
    print("="*60 + "\n")
    
    results = mock_service.run_full_analysis(regions=['us-east-1', 'us-west-2'])
    
    print("\n📊 Analysis Results:")
    print(f"├─ EC2 Instances: {results['summary']['total_instances']}")
    print(f"├─ Running Instances: {results['summary']['running_instances']}")
    print(f"├─ Idle Instances: {results['summary']['idle_instances']}")
    print(f"├─ Unattached Volumes: {results['summary']['unattached_volumes']}")
    print(f"└─ Potential Monthly Savings: ${results['total_potential_savings']:.2f}")
    
    print("\n💰 Cost Breakdown:")
    for idle in results['idle_instances'][:3]:  # Show first 3
        print(f"  • {idle['instance_id']} ({idle['instance_type']}): "
              f"{idle['cpu_utilization']}% CPU → Save ${idle['potential_savings']:.2f}/month")
    
    print("\n💾 Volume Savings:")
    for vol in results['unattached_volumes'][:3]:  # Show first 3
        print(f"  • {vol['volume_id']}: {vol['size']}GB {vol['volume_type']} → "
              f"Save ${vol['monthly_cost']:.2f}/month")
    
    print("\n" + "="*60)
    print("✅ Analysis complete - NO AWS API CALLS MADE (ZERO COST)")
    print("="*60)
