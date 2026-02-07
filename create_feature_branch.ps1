# Git Feature Branch Creation Script
# Creates feature/airflow-dual-environment-setup with 6 commits

cd C:\Users\NIRAJ\Desktop\multi-cloud-cost-optimizer

# Checkout develop
git checkout develop
git pull origin develop

# Create feature branch
git checkout -b feature/airflow-dual-environment-setup

# Commit 1
git add docker-compose.yml
git commit -m "Add dual-environment architecture to docker-compose

- Add separate PostgreSQL instances for mock and AWS environments
- Configure backend-mock service on port 8000 with mock database
- Configure backend-aws service on port 8001 with AWS database  
- Add postgres-airflow service for Airflow metadata storage
- Configure environment variables for service mode selection
- Add health checks for all PostgreSQL instances
- Update volume mappings for persistent data storage"

# Commit 2
git add backend/app/core/dependencies.py
git commit -m "Implement service selection logic for dual environments

- Add get_database_url for dynamic database URL construction
- Add get_aws_service for real AWS service initialization
- Add get_service for environment-based service selection
- Implement automatic selection based on USE_REAL_AWS
- Add comprehensive logging for service initialization"

# Commit 3
git add airflow/dags/aws_cost_optimization_mock.py
git commit -m "Add Airflow DAG for mock environment cost optimization

- Create daily scheduled DAG for mock backend
- Implement health check and cost analysis tasks
- Add resource scanning for EC2 and EBS
- Configure task dependencies and error handling
- Set schedule for daily execution at 6:00 AM"

# Commit 4
git add airflow/dags/aws_cost_optimization_production.py
git commit -m "Add Airflow DAG for production AWS environment

- Create DAG for real AWS backend on port 8001
- Implement real AWS API integration
- Add cost analysis using AWS Cost Explorer
- Configure warnings for AWS API costs
- Set schedule for 7:00 AM execution"

# Commit 5
git add .env
git commit -m "Update environment configuration for dual setup

- Add dual environment configuration
- Add frontend API URL configuration
- Organize environment variables by section
- Add AWS credentials placeholder
- Add Airflow encryption key"

# Commit 6
git add *.md *.ps1
git commit -m "Add comprehensive documentation for dual environment

- Add architecture overview and setup guides
- Add deployment instructions and troubleshooting
- Add diagnostic tools for Airflow issues
- Include cost management strategies
- Document all API endpoints and ports"

Write-Host "All commits complete! Push with:"
Write-Host "git push -u origin feature/airflow-dual-environment-setup"
