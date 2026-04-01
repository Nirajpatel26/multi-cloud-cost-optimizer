"""
Azure Cost Optimization DAG - MOCK ENVIRONMENT
===============================================
Daily workflow for Azure mock environment (zero Azure SDK calls)

Backend: http://host.docker.internal:8000
Schedule: Daily at 6:30 AM (30 min after AWS mock)
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
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2024, 2, 1),
    'execution_timeout': timedelta(minutes=20),
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
            raise ValueError(f"Unsupported method: {method}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        logger.error(f"[TIMEOUT] {endpoint} timed out after {timeout}s")
        raise Exception(f"API timeout: {endpoint}")
    except requests.exceptions.ConnectionError:
        logger.error(f"[CONNECTION ERROR] Could not reach backend at {BACKEND_URL}")
        raise Exception(f"Backend connection failed: {endpoint}")
    except requests.exceptions.HTTPError as e:
        logger.error(f"[FAILED] {endpoint} returned {e.response.status_code}")
        raise Exception(f"API error {e.response.status_code}: {endpoint}")


def check_backend_health(**context):
    logger.info("=" * 60)
    logger.info("AZURE MOCK - Health Check")
    logger.info("=" * 60)
    data = make_api_call('/api/v1/health', timeout=10)
    logger.info(f"Backend healthy: status={data.get('status')}, db={data.get('database')}")
    context['ti'].xcom_push(key='health_status', value=data)
    return data


def scan_azure_cost_data(**context):
    logger.info("=" * 60)
    logger.info("AZURE MOCK - Generating mock cost data")
    logger.info("=" * 60)
    request_body = {
        "regions": ["East US", "West Europe", "Southeast Asia"],
        "cpu_threshold": 5.0,
        "include_cost_data": True,
        "lookback_days": 30,
    }
    data = make_api_call('/api/v1/azure/analyze', method='POST', data=request_body)
    logger.info(f"Analysis ID: {data.get('analysis_id')}")
    logger.info(f"Potential savings: ${data.get('total_potential_savings', 0):.2f}")
    summary = data.get('summary', {})
    logger.info(f"Total VMs: {summary.get('total_vms', 0)}")
    logger.info(f"Idle VMs: {summary.get('idle_vms', 0)}")
    logger.info(f"Unattached Disks: {summary.get('unattached_disks', 0)}")
    context['ti'].xcom_push(key='cost_summary', value=data)
    return data


def scan_azure_resources(**context):
    logger.info("=" * 60)
    logger.info("AZURE MOCK - Scanning VMs and Managed Disks")
    logger.info("=" * 60)
    request_body = {
        "regions": ["East US", "West Europe", "Southeast Asia"],
        "resource_types": ["vm", "disk"],
    }
    data = make_api_call('/api/v1/azure/resources/scan', method='POST', data=request_body)
    logger.info(f"Scan ID: {data.get('scan_id')}")
    logger.info(f"Status: {data.get('status')}")
    resources = data.get('resources_found', {})
    logger.info(f"VMs found: {resources.get('virtual_machines', 0)}")
    logger.info(f"Disks found: {resources.get('managed_disks', 0)}")
    context['ti'].xcom_push(key='resource_summary', value=data)
    return data


def generate_azure_recommendations(**context):
    logger.info("=" * 60)
    logger.info("AZURE MOCK - Generating recommendations")
    logger.info("=" * 60)
    data = make_api_call('/api/v1/azure/recommendations')
    logger.info(f"Total recommendations: {data.get('total_recommendations', 0)}")
    logger.info(f"Potential savings: ${data.get('total_potential_savings', 0):.2f}/month")
    recs = data.get('recommendations', [])
    for rec in recs[:3]:
        logger.info(f"  - {rec.get('resource_type')} | {rec.get('recommendation_type')} | ${rec.get('potential_savings', 0):.2f}")
    context['ti'].xcom_push(key='recommendations', value=data)
    return data


def send_daily_summary(**context):
    logger.info("=" * 60)
    logger.info("AZURE MOCK - Daily Summary")
    logger.info("=" * 60)
    ti = context['ti']
    cost_summary = ti.xcom_pull(key='cost_summary', task_ids='scan_azure_cost_data')
    recommendations = ti.xcom_pull(key='recommendations', task_ids='generate_azure_recommendations')

    total_savings = recommendations.get('total_potential_savings', 0) if recommendations else 0
    logger.info(f"Mock Azure pipeline complete")
    logger.info(f"Potential monthly savings: ${total_savings:.2f}")
    logger.info(f"Total recommendations: {recommendations.get('total_recommendations', 0) if recommendations else 0}")
    logger.info("Review at http://localhost:3000")
    return {'status': 'pipeline_complete', 'environment': 'azure_mock', 'total_savings': total_savings}


dag = DAG(
    dag_id='azure_cost_optimization_mock',
    default_args=default_args,
    description='Daily Azure cost optimization - MOCK environment (zero Azure SDK costs)',
    schedule_interval='30 6 * * *',
    catchup=False,
    max_active_runs=1,
    tags=['azure', 'cost-optimization', 'mock'],
)

task_health_check = PythonOperator(
    task_id='check_backend_health',
    python_callable=check_backend_health,
    dag=dag,
)

task_scan_costs = PythonOperator(
    task_id='scan_azure_cost_data',
    python_callable=scan_azure_cost_data,
    dag=dag,
)

task_scan_resources = PythonOperator(
    task_id='scan_azure_resources',
    python_callable=scan_azure_resources,
    dag=dag,
)

task_recommendations = PythonOperator(
    task_id='generate_azure_recommendations',
    python_callable=generate_azure_recommendations,
    dag=dag,
)

task_summary = PythonOperator(
    task_id='send_daily_summary',
    python_callable=send_daily_summary,
    dag=dag,
)

task_health_check >> [task_scan_costs, task_scan_resources]
[task_scan_costs, task_scan_resources] >> task_recommendations
task_recommendations >> task_summary
