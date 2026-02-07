"""
AWS Cost Optimization DAG - REAL AWS ENVIRONMENT
=================================================
Daily workflow for production AWS environment (Uses real AWS API calls)

Backend: http://mcco-backend-aws:8000 (Port 8001 externally)
Database: cost_optimizer_aws
Schedule: Daily at 7:00 AM (1 hour after mock for comparison)

WARNING: This DAG makes real AWS API calls and may incur costs!
Monitor your AWS Free Tier usage carefully.
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
import logging

logger = logging.getLogger(__name__)

default_args = {
    'owner': 'niraj',
    'depends_on_past': False,
    'email': ['niraj2632000@gmail.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=10),
    'start_date': datetime(2024, 2, 1),
    'execution_timeout': timedelta(minutes=30),
}

BACKEND_URL = 'http://mcco-backend-aws:8000'
API_TIMEOUT = 600

def make_api_call(endpoint, method='GET', data=None, timeout=API_TIMEOUT):
    url = f"{BACKEND_URL}{endpoint}"
    
    try:
        if method == 'GET':
            response = requests.get(url, timeout=timeout)
        elif method == 'POST':
            response = requests.post(url, json=data, timeout=timeout)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.Timeout:
        logger.error(f"[TIMEOUT] API call to {endpoint} timed out after {timeout}s")
        raise Exception(f"API timeout: {endpoint}")
    
    except requests.exceptions.ConnectionError:
        logger.error(f"[CONNECTION ERROR] Could not connect to AWS backend at {BACKEND_URL}")
        raise Exception(f"Backend connection failed: {endpoint}")
    
    except requests.exceptions.HTTPError as e:
        logger.error(f"[FAILED] API call failed: {e.response.status_code} - {e.response.text}")
        raise Exception(f"API error: {endpoint} - {e.response.status_code}")
    
    except Exception as e:
        logger.error(f"[ERROR] Unexpected error calling {endpoint}: {str(e)}")
        raise


def check_backend_health(**context):
    logger.info("=" * 60)
    logger.info("HEALTH CHECK - REAL AWS Environment")
    logger.info("[WARNING] This will connect to real AWS services")
    logger.info("=" * 60)
    
    try:
        data = make_api_call('/api/v1/health', timeout=10)
        
        logger.info(f"[SUCCESS] AWS backend is healthy")
        logger.info(f"   Status: {data.get('status')}")
        logger.info(f"   Database: {data.get('database')}")
        logger.info(f"   Timestamp: {data.get('timestamp')}")
        
        context['ti'].xcom_push(key='health_status', value=data)
        return data
    
    except Exception as e:
        logger.error(f"[FAILED] Health check failed: {str(e)}")
        logger.error("[HINT] Make sure AWS credentials are configured correctly")
        raise


def scan_cost_data(**context):
    logger.info("=" * 60)
    logger.info("COST SCAN - Real AWS Cost Explorer API")
    logger.info("[WARNING] This makes real AWS API calls")
    logger.info("=" * 60)
    
    try:
        request_body = {
            "regions": ["us-east-1", "us-west-2", "eu-west-1"],
            "cpu_threshold": 5.0
        }
        data = make_api_call('/api/v1/aws/analyze', method='POST', data=request_body)
        
        logger.info(f"[SUCCESS] Analysis completed successfully (Real AWS data)")
        logger.info(f"   Analysis ID: {data.get('analysis_id')}")
        logger.info(f"   Timestamp: {data.get('timestamp')}")
        logger.info(f"   Potential Savings: ${data.get('total_potential_savings', 0):.2f}")
        
        summary = data.get('summary', {})
        logger.info(f"   Total Instances: {summary.get('total_instances', 0)}")
        logger.info(f"   Running Instances: {summary.get('running_instances', 0)}")
        logger.info(f"   Idle Instances: {summary.get('idle_instances', 0)}")
        logger.info(f"   Cost Records: {summary.get('cost_records', 0)}")
        logger.info(f"   Regions: {', '.join(data.get('regions_analyzed', []))}")
        
        context['ti'].xcom_push(key='cost_summary', value=data)
        return data
    
    except Exception as e:
        logger.error(f"[FAILED] Cost scan failed: {str(e)}")
        logger.error("[HINT] Check AWS Cost Explorer permissions")
        raise


def scan_ec2_resources(**context):
    logger.info("=" * 60)
    logger.info("RESOURCE SCAN - Real AWS EC2/EBS API")
    logger.info("[WARNING] This makes real AWS API calls")
    logger.info("=" * 60)
    
    try:
        request_body = {
            "regions": ["us-east-1", "us-west-2", "eu-west-1"],
            "resource_types": ["ec2", "ebs"]
        }
        
        data = make_api_call('/api/v1/aws/resources/scan', method='POST', data=request_body)
        
        logger.info(f"[SUCCESS] Resource scan completed (Real AWS data)")
        logger.info(f"   Scan ID: {data.get('scan_id')}")
        logger.info(f"   Status: {data.get('status')}")
        
        resources_found = data.get('resources_found', {})
        logger.info(f"   EC2 Instances Found: {resources_found.get('ec2_instances', 0)}")
        logger.info(f"   EBS Volumes Found: {resources_found.get('ebs_volumes', 0)}")
        logger.info(f"   Regions Scanned: {', '.join(data.get('regions_scanned', []))}")
        
        summary = {
            'total_instances': resources_found.get('ec2_instances', 0),
            'unattached_volumes': resources_found.get('ebs_volumes', 0),
            'scan_id': data.get('scan_id'),
            'regions': data.get('regions_scanned', [])
        }
        
        context['ti'].xcom_push(key='resource_summary', value=data)
        return data
    
    except Exception as e:
        logger.error(f"[FAILED] Resource scan failed: {str(e)}")
        logger.error("[HINT] Check AWS EC2 ReadOnly permissions")
        raise


def generate_optimization_recommendations(**context):
    logger.info("=" * 60)
    logger.info("RECOMMENDATIONS - Real AWS Data Analysis")
    logger.info("=" * 60)
    
    try:
        data = make_api_call('/api/v1/aws/recommendations', method='GET')
        
        logger.info(f"[SUCCESS] Recommendations retrieved successfully (Real AWS data)")
        logger.info(f"   Total Recommendations: {data.get('total_recommendations', 0)}")
        logger.info(f"   REAL POTENTIAL SAVINGS: ${data.get('total_potential_savings', 0):.2f}/month")
        
        recommendations = data.get('recommendations', [])
        if recommendations:
            logger.info(f"   Top 3 Recommendations:")
            for i, rec in enumerate(recommendations[:3], 1):
                logger.info(f"      {i}. {rec.get('resource_type')} - {rec.get('recommendation_type')} - ${rec.get('potential_savings', 0):.2f}")
        
        if data.get('total_potential_savings', 0) > 100:
            logger.warning(f"[HIGH SAVINGS] HIGH SAVINGS POTENTIAL: ${data.get('total_potential_savings', 0):.2f}/month")
            logger.warning("   Review recommendations urgently!")
        
        context['ti'].xcom_push(key='recommendations', value=data)
        return data
    
    except Exception as e:
        logger.error(f"[FAILED] Recommendation generation failed: {str(e)}")
        raise


def send_daily_summary(**context):
    logger.info("=" * 60)
    logger.info("SUMMARY - Real AWS Pipeline Complete")
    logger.info("=" * 60)
    
    ti = context['ti']
    
    cost_summary = ti.xcom_pull(key='cost_summary', task_ids='scan_cost_data')
    resource_summary = ti.xcom_pull(key='resource_summary', task_ids='scan_ec2_resources')
    recommendations = ti.xcom_pull(key='recommendations', task_ids='generate_recommendations')
    
    total_savings = recommendations.get('total_potential_savings', 0)
    
    logger.info(f"[SUCCESS] Real AWS analysis complete")
    logger.info(f"   Potential Savings: ${cost_summary.get('total_potential_savings', 0):.2f}")
    logger.info(f"   Resources Scanned: {resource_summary.get('resources_found', {})}")
    logger.info(f"   Total Recommendations: {recommendations.get('total_recommendations', 0)}")
    logger.info(f"   REAL potential monthly savings: ${total_savings:.2f}")
    
    logger.info("=" * 60)
    logger.info("ACTION ITEMS:")
    logger.info("   1. Review recommendations at http://localhost:3000")
    logger.info("   2. Check AWS Console for verification")
    logger.info("   3. Address critical/high severity items")
    logger.info("=" * 60)
    
    return {
        'status': 'pipeline_complete',
        'environment': 'aws',
        'total_savings': total_savings
    }


dag = DAG(
    dag_id='aws_cost_optimization_production',
    default_args=default_args,
    description='Daily AWS cost optimization - PRODUCTION with real AWS API (WARNING: Incurs costs)',
    schedule_interval='0 7 * * *',
    catchup=False,
    max_active_runs=1,
    tags=['aws', 'cost-optimization', 'production', 'real-aws', 'warning'],
)

task_health_check = PythonOperator(
    task_id='check_backend_health',
    python_callable=check_backend_health,
    dag=dag,
)

task_scan_costs = PythonOperator(
    task_id='scan_cost_data',
    python_callable=scan_cost_data,
    dag=dag,
)

task_scan_resources = PythonOperator(
    task_id='scan_ec2_resources',
    python_callable=scan_ec2_resources,
    dag=dag,
)

task_generate_recommendations = PythonOperator(
    task_id='generate_recommendations',
    python_callable=generate_optimization_recommendations,
    dag=dag,
)

task_send_notification = PythonOperator(
    task_id='send_daily_summary',
    python_callable=send_daily_summary,
    dag=dag,
)

task_health_check >> [task_scan_costs, task_scan_resources]
[task_scan_costs, task_scan_resources] >> task_generate_recommendations
task_generate_recommendations >> task_send_notification
