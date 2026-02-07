"""
AWS Cost Optimization DAG - MOCK ENVIRONMENT
=============================================
Daily workflow for mock/development environment (Zero AWS costs)

Backend: http://mcco-backend-mock:8000 (Port 8000)
Database: cost_optimizer_mock
Schedule: Daily at 6:00 AM
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
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2024, 2, 1),
    'execution_timeout': timedelta(minutes=30),
}

# MOCK BACKEND URL
BACKEND_URL = 'http://mcco-backend-mock:8000'
API_TIMEOUT = 300

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
        logger.error(f"API call to {endpoint} timed out after {timeout}s")
        raise Exception(f"API timeout: {endpoint}")
    
    except requests.exceptions.ConnectionError:
        logger.error(f"Could not connect to backend at {BACKEND_URL}")
        raise Exception(f"Backend connection failed: {endpoint}")
    
    except requests.exceptions.HTTPError as e:
        logger.error(f"API call failed: {e.response.status_code} - {e.response.text}")
        raise Exception(f"API error: {endpoint} - {e.response.status_code}")
    
    except Exception as e:
        logger.error(f"Unexpected error calling {endpoint}: {str(e)}")
        raise


def check_backend_health(**context):
    logger.info("=" * 60)
    logger.info("HEALTH CHECK - MOCK Environment")
    logger.info("=" * 60)
    
    try:
        data = make_api_call('/api/v1/health', timeout=10)
        
        logger.info(f"[SUCCESS] Mock backend is healthy")
        logger.info(f"   Status: {data.get('status')}")
        logger.info(f"   Database: {data.get('database')}")
        logger.info(f"   Timestamp: {data.get('timestamp')}")
        
        context['ti'].xcom_push(key='health_status', value=data)
        return data
    
    except Exception as e:
        logger.error(f"[FAILED] Health check failed: {str(e)}")
        raise


def scan_cost_data(**context):
    logger.info("=" * 60)
    logger.info("COST SCAN - Mock Data Generation")
    logger.info("=" * 60)
    
    try:
        request_body = {
            "regions": ["us-east-1", "us-west-2", "eu-west-1"],
            "cpu_threshold": 5.0
        }
        data = make_api_call('/api/v1/aws/analyze', method='POST', data=request_body)
        
        logger.info(f"[SUCCESS] Analysis completed successfully")
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
        raise


def scan_ec2_resources(**context):
    logger.info("=" * 60)
    logger.info("RESOURCE SCAN - Mock EC2/EBS")
    logger.info("=" * 60)
    
    try:
        request_body = {
            "regions": ["us-east-1", "us-west-2", "eu-west-1"],
            "resource_types": ["ec2", "ebs"]
        }
        
        data = make_api_call('/api/v1/aws/resources/scan', method='POST', data=request_body)
        
        logger.info(f"[SUCCESS] Resource scan completed")
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
        raise


def generate_optimization_recommendations(**context):
    logger.info("=" * 60)
    logger.info("RECOMMENDATIONS - Mock Optimization")
    logger.info("=" * 60)
    
    try:
        data = make_api_call('/api/v1/aws/recommendations', method='GET')
        
        logger.info(f"[SUCCESS] Recommendations retrieved successfully")
        logger.info(f"   Total Recommendations: {data.get('total_recommendations', 0)}")
        logger.info(f"   Potential Savings: ${data.get('total_potential_savings', 0):.2f}/month")
        
        recommendations = data.get('recommendations', [])
        if recommendations:
            logger.info(f"   Top 3 Recommendations:")
            for i, rec in enumerate(recommendations[:3], 1):
                logger.info(f"      {i}. {rec.get('resource_type')} - {rec.get('recommendation_type')} - ${rec.get('potential_savings', 0):.2f}")
        
        context['ti'].xcom_push(key='recommendations', value=data)
        return data
    
    except Exception as e:
        logger.error(f"[FAILED] Recommendation generation failed: {str(e)}")
        raise


def send_daily_summary(**context):
    logger.info("=" * 60)
    logger.info("SUMMARY - Mock Pipeline Complete")
    logger.info("=" * 60)
    
    ti = context['ti']
    
    cost_summary = ti.xcom_pull(key='cost_summary', task_ids='scan_cost_data')
    resource_summary = ti.xcom_pull(key='resource_summary', task_ids='scan_ec2_resources')
    recommendations = ti.xcom_pull(key='recommendations', task_ids='generate_recommendations')
    
    logger.info(f"[SUCCESS] Analysis ID: {cost_summary.get('analysis_id', 'N/A')}")
    logger.info(f"[SUCCESS] Total Instances: {cost_summary.get('summary', {}).get('total_instances', 0)}")
    logger.info(f"[SUCCESS] Resources Scanned: EC2={resource_summary.get('resources_found', {}).get('ec2_instances', 0)}, EBS={resource_summary.get('resources_found', {}).get('ebs_volumes', 0)}")
    logger.info(f"[SUCCESS] Total Recommendations: {recommendations.get('total_recommendations', 0)}")
    logger.info(f"Potential Monthly Savings: ${recommendations.get('total_potential_savings', 0):.2f}")
    logger.info(f"Environment: MOCK (Zero AWS costs)")
    
    return {
        'status': 'pipeline_complete',
        'environment': 'mock',
        'total_savings': recommendations.get('total_potential_savings', 0)
    }


# Create the DAG
dag = DAG(
    dag_id='aws_cost_optimization_mock',
    default_args=default_args,
    description='Daily AWS cost optimization - MOCK environment (Zero cost)',
    schedule_interval='0 6 * * *',
    catchup=False,
    max_active_runs=1,
    tags=['aws', 'cost-optimization', 'mock', 'development'],
)

# Define tasks
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

# Define dependencies
task_health_check >> [task_scan_costs, task_scan_resources]
[task_scan_costs, task_scan_resources] >> task_generate_recommendations
task_generate_recommendations >> task_send_notification
