"""
Test script for AWS Mock Service - Zero Cost Testing
Run this to validate the mock data and database integration
"""
import sys
sys.path.append('.')

from app.services.aws_mock_service import AWSMockService
import time

def test_mock_service():
    """Test the mock AWS service without any real AWS API calls"""
    
    print("\n" + "="*70)
    print("TESTING MOCK AWS SERVICE (ZERO COST)")
    print("="*70 + "\n")
    
    try:
        # Initialize mock service
        print("1. Initializing mock service...")
        mock_service = AWSMockService(
            database_url='postgresql://admin:admin@127.0.0.1:5433/cost_optimizer'
        )
        print("   [OK] Mock service initialized successfully\n")
        time.sleep(1)
        
        # Test cost data generation
        print("2. Testing cost data generation...")
        cost_data = mock_service.fetch_cost_data()
        print(f"   [OK] Generated {len(cost_data)} cost records\n")
        time.sleep(1)
        
        # Test EC2 instance scanning
        print("3. Testing EC2 instance scanning...")
        instances = mock_service.scan_ec2_instances()
        print(f"   [OK] Scanned {len(instances)} EC2 instances\n")
        time.sleep(1)
        
        # Test idle resource identification
        print("4. Testing idle resource identification...")
        idle_instances = mock_service.identify_idle_resources()
        print(f"   [OK] Found {len(idle_instances)} idle instances\n")
        time.sleep(1)
        
        # Test unattached volume discovery
        print("5. Testing unattached volume discovery...")
        unattached_volumes = mock_service.find_unattached_ebs_volumes()
        print(f"   [OK] Found {len(unattached_volumes)} unattached volumes\n")
        time.sleep(1)
        
        # Run full analysis
        print("6. Running full analysis...")
        results = mock_service.run_full_analysis()
        
        print("\n" + "="*70)
        print("ANALYSIS RESULTS")
        print("="*70)
        print(f"\nSummary:")
        print(f"   - Total Instances: {results['summary']['total_instances']}")
        print(f"   - Running Instances: {results['summary']['running_instances']}")
        print(f"   - Idle Instances: {results['summary']['idle_instances']}")
        print(f"   - Unattached Volumes: {results['summary']['unattached_volumes']}")
        print(f"   - Cost Records: {results['summary']['cost_records']}")
        
        print(f"\nPotential Monthly Savings: ${results['total_potential_savings']:.2f}")
        
        # Show sample idle instances
        if results['idle_instances']:
            print(f"\nTop Idle Instances:")
            for idx, inst in enumerate(results['idle_instances'][:3], 1):
                print(f"   {idx}. {inst['instance_id']} ({inst['instance_type']})")
                print(f"      CPU: {inst['cpu_utilization']}%")
                print(f"      Savings: ${inst['potential_savings']:.2f}/month")
        
        # Show sample unattached volumes
        if results['unattached_volumes']:
            print(f"\nSample Unattached Volumes:")
            for idx, vol in enumerate(results['unattached_volumes'][:3], 1):
                print(f"   {idx}. {vol['volume_id']}")
                print(f"      Size: {vol['size']}GB {vol['volume_type']}")
                print(f"      Savings: ${vol['monthly_cost']:.2f}/month")
        
        print("\n" + "="*70)
        print("[SUCCESS] ALL TESTS PASSED - NO AWS COSTS INCURRED")
        print("="*70 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_mock_service()
    sys.exit(0 if success else 1)
