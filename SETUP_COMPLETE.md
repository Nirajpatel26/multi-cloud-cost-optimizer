# Dual Environment Setup Complete!

## What Was Created

### 1. Updated docker-compose.yml
- **Mock Environment**: Port 8000 with separate PostgreSQL (port 5433)
- **AWS Environment**: Port 8001 with separate PostgreSQL (port 5435)
- **Airflow**: Port 8080 with its own PostgreSQL (port 5434)
- **Frontend**: Port 3000 (can switch between backends)
- **Jenkins**: Port 8081

### 2. Two Separate Airflow DAGs
- **`aws_cost_optimization_mock.py`**: Runs daily at 6:00 AM, uses mock data (Zero cost)
- **`aws_cost_optimization_production.py`**: Runs daily at 7:00 AM, uses real AWS (Free tier)

### 3. Helper Scripts
- **`start-dual-environment.ps1`**: Quick start script with health checks
- **`compare-environments.ps1`**: Compare mock vs AWS data side-by-side
- **`DUAL_ENVIRONMENT_SETUP.md`**: Comprehensive documentation

---

## How to Start

### Option 1: Use Quick Start Script (Recommended)
```powershell
cd C:\Users\NIRAJ\Desktop\multi-cloud-cost-optimizer
.\start-dual-environment.ps1
```

### Option 2: Manual Start
```powershell
# Start everything
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

---

## Testing Your Setup

### Test Mock Backend (Should work immediately)
```powershell
# Health check
curl http://localhost:8000/api/v1/health

# API docs
Start-Process "http://localhost:8000/docs"
```

### Test AWS Backend (Requires real AWS credentials)
```powershell
# Health check
curl http://localhost:8001/api/v1/health

# API docs
Start-Process "http://localhost:8001/docs"
```

### Access Airflow
```powershell
Start-Process "http://localhost:8080"
# Username: admin
# Password: admin
```

---

## AWS Credentials Setup

### Step 1: Get Real AWS Credentials

1. Log in to [AWS Console](https://console.aws.amazon.com/)
2. Go to **IAM** -> **Users** -> **Create User**
3. Attach these policies (ReadOnly for safety):
   - `AmazonEC2ReadOnlyAccess`
   - `AWSCostExplorerReadOnlyAccess`
   - `AmazonS3ReadOnlyAccess`
4. Create **Access Key** -> Copy both **Access Key ID** and **Secret Access Key**

### Step 2: Update .env File

Edit your `.env` file:

```bash
# Replace these with your REAL AWS credentials
AWS_ACCESS_KEY_ID=your_actual_access_key_here
AWS_SECRET_ACCESS_KEY=your_actual_secret_key_here
AWS_REGION=us-east-1
```

### Step 3: Restart AWS Backend
```powershell
docker-compose restart backend-aws
```

---

## Airflow DAG Overview

### Mock DAG (aws_cost_optimization_mock)
- **Schedule**: Daily at 6:00 AM
- **Backend**: Mock (Port 8000)
- **Cost**: $0
- **Purpose**: Development and testing

### AWS DAG (aws_cost_optimization_production)
- **Schedule**: Daily at 7:00 AM
- **Backend**: AWS (Port 8001)
- **Cost**: Free Tier (Monitor usage!)
- **Purpose**: Real AWS data integration

### How to Trigger Manually:
1. Go to http://localhost:8080
2. Find the DAG you want
3. Click Trigger DAG
4. Watch tasks turn green!

---

## Cost Management

### Mock Environment (Always Safe)
```powershell
# Always running - Zero AWS costs
docker-compose up -d backend-mock postgres-mock
```

### AWS Environment (Use Carefully)
```powershell
# Start when needed
docker-compose up -d backend-aws postgres-aws

# Stop when not needed
docker-compose stop backend-aws postgres-aws
```

### Monitor AWS Costs
- **AWS Console**: Check Free Tier usage
- **Set Budget Alerts**: $5/month threshold
- **Monitor CloudTrail**: Track API calls

---

## Troubleshooting

### Backend Won't Start
```powershell
# Check logs
docker-compose logs backend-mock
docker-compose logs backend-aws

# Restart specific service
docker-compose restart backend-mock
```

### AWS Credentials Not Working
```powershell
# Test credentials
docker exec mcco-backend-aws env | grep AWS

# Check IAM permissions in AWS Console
```

### Database Connection Issues
```powershell
# Test database
docker exec mcco-postgres-mock pg_isready -U admin
docker exec mcco-postgres-aws pg_isready -U admin

# Recreate if needed
docker-compose down -v
docker-compose up -d
```

### Airflow DAG Not Appearing
```powershell
# Check scheduler logs
docker-compose logs airflow-scheduler

# Wait 30 seconds for DAG refresh
# Or restart scheduler
docker-compose restart airflow-scheduler
```

---

## Interview Talking Points

**Architecture Highlights:**

"I implemented a dual-environment architecture with separate backends and databases for mock and production AWS environments. This demonstrates:

- Multi-environment deployment patterns
- Cost optimization through selective service usage
- Dependency injection for environment switching
- Independent data storage preventing contamination
- Production-grade separation of concerns

The mock environment runs continuously at zero cost for development, while the AWS environment can be activated for demos with real cloud integration. Both share the same codebase but operate independently through Docker service orchestration."

---

## File Structure

```
multi-cloud-cost-optimizer/
  docker-compose.yml                           # Updated with dual environments
  .env                                         # Add your real AWS credentials here
  QUICKSTART.md                                # Quick start guide
  SETUP_COMPLETE.md                            # This file
  airflow/
    dags/
      aws_cost_optimization_mock.py            # Mock DAG (Port 8000)
      aws_cost_optimization_production.py      # AWS DAG (Port 8001)
      aws_cost_optimization_dag.py             # Original DAG
  backend/
    app/
      core/
        dependencies.py                        # Service selection logic
      api/v1/endpoints/
        health.py                              # Updated endpoints
        analytics.py
        costs.py
        resources.py
        recommendations.py
```

---

## Success Checklist

- [ ] Docker services started successfully
- [ ] Mock backend healthy (http://localhost:8000/api/v1/health)
- [ ] AWS backend configured with real credentials
- [ ] AWS backend healthy (http://localhost:8001/api/v1/health)
- [ ] Airflow UI accessible (http://localhost:8080)
- [ ] Mock DAG appears in Airflow
- [ ] AWS DAG appears in Airflow
- [ ] Mock DAG runs successfully
- [ ] Frontend accessible (http://localhost:3000)
