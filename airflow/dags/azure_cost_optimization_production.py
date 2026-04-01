"""
Azure Cost Optimization DAG - REAL AZURE ENVIRONMENT
=====================================================
Daily workflow for production Azure environment (uses real Azure SDK calls)

Backend: http://mcco-backend-azure:8000
Schedule: Daily at 7:30 AM (after mock runs at 6:30 AM)

WARNING: This DAG makes real Azure API calls.
Requires: AZURE_SUBSCRIPTION_ID, AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET
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

BACKEND_URL = 'http://mcco-backend-azure:8000'
API_TIMEOUT = 600


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
        logger.error(f"[CONNECTION ERROR] Could not reach Azure backend at {BACKEND_URL}")
        raise Exception(f"Backend connection failed: {endpoint}")
    except requests.exceptions.HTTPError as e:
        logger.error(f"[FAILED] {endpoint} returned {e.response.status_code}")
        raise Exception(f"API error {e.response.status_code}: {endpoint}")


def check_backend_health(**context):
    logger.info("=" * 60)
    logger.info("HEALTH CHECK - REAL Azure Environment")
    logger.info("[WARNING] This connects to real Azure services")
    logger.info("=" * 60)
    data = make_api_call('/api/v1/health', timeout=10)
    logger.info(f"Azure backend healthy: status={data.get('status')}")
    context['ti'].xcom_push(key='health_status', value=data)
    return data


def scan_azure_cost_data(**context):
    logger.info("=" * 60)
    logger.info("COST SCAN - Real Azure Cost Management API")
    logger.info("[WARNING] This makes real Azure API calls")
    logger.info("=" * 60)
    request_body = {
        "regions": ["East US", "West US 2", "North Europe", "West Europe", "Southeast Asia"],
        "cpu_threshold": 5.0,
        "include_cost_data": True,
        "lookback_days": 30,
    }
    data = make_api_call('/api/v1/azure/analyze', method='POST', data=request_body)
    logger.info(f"Analysis ID: {data.get('analysis_id')}")
    logger.info(f"REAL potential savings: ${data.get('total_potential_savings', 0):.2f}")
    summary = data.get('summary', {})
    logger.info(f"Total VMs: {summary.get('total_vms', 0)}")
    logger.info(f"Running VMs: {summary.get('running_vms', 0)}")
    logger.info(f"Idle VMs: {summary.get('idle_vms', 0)}")
    logger.info(f"Unattached Disks: {summary.get('unattached_disks', 0)}")
    context['ti'].xcom_push(key='cost_summary', value=data)
    return data


def scan_azure_resources(**context):
    logger.info("=" * 60)
    logger.info("RESOURCE SCAN - Real Azure Compute API")
    logger.info("[WARNING] This makes real Azure API calls")
    logger.info("=" * 60)
    request_body = {
        "resource_types": ["vm", "disk"],
    }
    data = make_api_call('/api/v1/azure/resources/scan', method='POST', data=request_body)
    logger.info(f"Scan ID: {data.get('scan_id')}")
    resources = data.get('resources_found', {})
    logger.info(f"VMs found: {resources.get('virtual_machines', 0)}")
    logger.info(f"Disks found: {resources.get('managed_disks', 0)}")
    context['ti'].xcom_push(key='resource_summary', value=data)
    return data


def generate_azure_recommendations(**context):
    logger.info("=" * 60)
    logger.info("RECOMMENDATIONS - Real Azure Data Analysis")
    logger.info("=" * 60)
    data = make_api_call('/api/v1/azure/recommendations')
    total_savings = data.get('total_potential_savings', 0)
    logger.info(f"Total recommendations: {data.get('total_recommendations', 0)}")
    logger.info(f"REAL potential savings: ${total_savings:.2f}/month")

    recs = data.get('recommendations', [])
    for rec in recs[:3]:
        logger.info(f"  - {rec.get('resource_type')} | {rec.get('recommendation_type')} | ${rec.get('potential_savings', 0):.2f}")

    if total_savings > 100:
        logger.warning(f"[HIGH SAVINGS] HIGH SAVINGS DETECTED: ${total_savings:.2f}/month — review urgently!")

    context['ti'].xcom_push(key='recommendations', value=data)
    return data


def send_daily_summary(**context):
    logger.info("=" * 60)
    logger.info("SUMMARY - Real Azure Pipeline Complete")
    logger.info("=" * 60)
    ti = context['ti']
    cost_summary = ti.xcom_pull(key='cost_summary', task_ids='scan_azure_cost_data')
    recommendations = ti.xcom_pull(key='recommendations', task_ids='generate_azure_recommendations')

    total_savings = recommendations.get('total_potential_savings', 0) if recommendations else 0
    logger.info(f"Real Azure analysis complete")
    logger.info(f"REAL potential monthly savings: ${total_savings:.2f}")
    logger.info(f"Total recommendations: {recommendations.get('total_recommendations', 0) if recommendations else 0}")
    logger.info("=" * 60)
    logger.info("ACTION ITEMS:")
    logger.info("   1. Review recommendations at http://localhost:3000")
    logger.info("   2. Check Azure Portal for verification")
    logger.info("   3. Deallocate idle VMs and delete unattached disks")
    logger.info("=" * 60)

    return {'status': 'pipeline_complete', 'environment': 'azure_production', 'total_savings': total_savings}


dag = DAG(
    dag_id='azure_cost_optimization_production',
    default_args=default_args,
    description='Daily Azure cost optimization - PRODUCTION with real Azure API calls',
    schedule_interval='30 7 * * *',
    catchup=False,
    max_active_runs=1,
    tags=['azure', 'cost-optimization', 'production', 'real-azure', 'warning'],
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
