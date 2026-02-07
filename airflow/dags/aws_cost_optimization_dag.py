from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
from datetime import datetime, timedelta
import requests
import logging
import json

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

BACKEND_URL = 'http://host.docker.internal:8000'
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
        logger.error(f" API call to {endpoint} timed out after {timeout}s")
        raise Exception(f"API timeout: {endpoint}")
    
    except requests.exceptions.ConnectionError:
        logger.error(f" Could not connect to backend at {BACKEND_URL}")
        raise Exception(f"Backend connection failed: {endpoint}")
    
    except requests.exceptions.HTTPError as e:
        logger.error(f" API call failed: {e.response.status_code} - {e.response.text}")
        raise Exception(f"API error: {endpoint} - {e.response.status_code}")
    
    except Exception as e:
        logger.error(f" Unexpected error calling {endpoint}: {str(e)}")
        raise

def check_backend_health(**context):

    logger.info("HEALTH CHECK - Verifying backend status")
    try:
        data = make_api_call('/api/v1/health', timeout=10)
        
        logger.info(f" Backend is healthy")
        logger.info(f"   Status: {data.get('status')}")
        logger.info(f"   Database: {data.get('database')}")
        logger.info(f"   Timestamp: {data.get('timestamp')}")
        
        context['ti'].xcom_push(key='health_status', value=data)
        
        return data
    
    except Exception as e:
        logger.error(f" Health check failed: {str(e)}")
        raise


def scan_cost_data(**context):
    logger.info(" COST SCAN - Fetching AWS cost data")
    try:
        data = make_api_call('/api/v1/analytics/generate', method='POST')
        
        logger.info(f" Cost scan completed successfully")
        logger.info(f"   Message: {data.get('message')}")
        logger.info(f"   Total Records: {data.get('total_records')}")
        logger.info(f"   Total Cost: ${data.get('total_cost', 0):.2f}")
        
        summary = data.get('summary', {})
        logger.info(f"   By Service: {len(summary.get('by_service', []))} services")
        logger.info(f"   By Region: {len(summary.get('by_region', []))} regions")
        
        context['ti'].xcom_push(key='cost_summary', value=data)
        
        return data
    
    except Exception as e:
        logger.error(f" Cost scan failed: {str(e)}")
        raise


def scan_ec2_resources(**context):

    logger.info(" RESOURCE SCAN - Analyzing EC2 instances")
    try:
        data = make_api_call('/api/v1/resources/scan', method='POST')
        
        logger.info(f" Resource scan completed successfully")
        logger.info(f"   Message: {data.get('message')}")
        
        summary = data.get('summary', {})
        logger.info(f"   Total Instances: {summary.get('total_instances')}")
        logger.info(f"   Running: {summary.get('running_instances')}")
        logger.info(f"   Stopped: {summary.get('stopped_instances')}")
        logger.info(f"   Idle Instances: {summary.get('idle_instances')}")
        logger.info(f"   Unattached Volumes: {summary.get('unattached_volumes')}")
        
        context['ti'].xcom_push(key='resource_summary', value=data)
        
        return data
    
    except Exception as e:
        logger.error(f" Resource scan failed: {str(e)}")
        raise


def generate_optimization_recommendations(**context):

    logger.info(" RECOMMENDATIONS - Generating optimization suggestions")

    try:
        data = make_api_call('/api/v1/recommendations/generate', method='POST')
        
        logger.info(f" Recommendations generated successfully")
        logger.info(f"   Message: {data.get('message')}")
        
        summary = data.get('summary', {})
        logger.info(f"   Total Recommendations: {summary.get('total_recommendations')}")
        logger.info(f"   Potential Savings: ${summary.get('total_potential_savings', 0):.2f}/month")
        
        by_severity = summary.get('by_severity', {})
        logger.info(f"   Critical: {by_severity.get('CRITICAL', 0)}")
        logger.info(f"   High: {by_severity.get('HIGH', 0)}")
        logger.info(f"   Medium: {by_severity.get('MEDIUM', 0)}")
        logger.info(f"   Low: {by_severity.get('LOW', 0)}")
        
        context['ti'].xcom_push(key='recommendations', value=data)
        
        return data
    
    except Exception as e:
        logger.error(f" Recommendation generation failed: {str(e)}")
        raise


def send_daily_summary(**context):

    logger.info(" Pipeline completed successfully")

    ti = context['ti']
    
    cost_summary = ti.xcom_pull(key='cost_summary', task_ids='scan_cost_data')
    resource_summary = ti.xcom_pull(key='resource_summary', task_ids='scan_ec2_resources')
    recommendations = ti.xcom_pull(key='recommendations', task_ids='generate_recommendations')
    
    logger.info(f" Cost scan: {cost_summary.get('total_records', 0)} records")
    logger.info(f" Resource scan: {resource_summary.get('summary', {}).get('total_instances', 0)} instances")
    logger.info(f" Recommendations: {recommendations.get('summary', {}).get('total_recommendations', 0)} generated")
    
    return {'status': 'pipeline_complete'}

def cleanup_old_data(**context):

    logger.info(" CLEANUP - Removing old optimization data")
    
    # TODO: Implement cleanup logic
    # - Remove recommendations older than 30 days
    # - Archive old cost data
    # - Clean up temporary files
    
    logger.info(" Cleanup completed")
    
    return {'status': 'cleanup_complete'}

# Create the DAG
dag = DAG(
    dag_id='aws_cost_optimization_daily',
    default_args=default_args,
    description='Daily AWS cost optimization analysis with mock data',
    schedule_interval='0 6 * * *',
    catchup=False,
    max_active_runs=1,
    tags=['aws', 'cost-optimization', 'daily', 'mock-data'],
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
