# Quick Start Guide - Dual Environment Setup

## All Changes Have Been Applied!

Your project now has a complete dual-environment setup with:

### Infrastructure
- docker-compose.yml configured with dual backends
- Separate PostgreSQL databases for mock and AWS
- Mock backend on port 8000
- AWS backend on port 8001
- Updated dependencies.py with service selection logic
- Two Airflow DAGs (mock and production)
- Updated .env file with dual environment configuration

---

## Start Your Dual Environment

```bash
# Navigate to project directory
cd C:\Users\NIRAJ\Desktop\multi-cloud-cost-optimizer

# Stop any existing containers
docker-compose down -v

# Start everything fresh
docker-compose up -d --build

# Watch the logs
docker-compose logs -f
```

---

## Verify Everything is Running

```bash
# Check all container status
docker-compose ps

# You should see 9 services running:
# - mcco-postgres-mock (5433)
# - mcco-postgres-aws (5435)
# - mcco-postgres-airflow (5434)
# - mcco-backend-mock (8000)
# - mcco-backend-aws (8001)
# - mcco-airflow-webserver (8080)
# - mcco-airflow-scheduler
# - mcco-frontend (3000)
# - mcco-jenkins (8081)
```

---

## Test Both Backends

### Test Mock Backend (Always Free)
```bash
curl http://localhost:8000/api/v1/health
# Should return: {"status":"healthy","database":"connected",...}
```

### Test AWS Backend (Requires Real Credentials)
```bash
curl http://localhost:8001/api/v1/health
# Should return: {"status":"healthy","database":"connected",...}
```

---

## Access Your Services

| Service | URL |
|---------|-----|
| Mock Backend API | http://localhost:8000 |
| AWS Backend API | http://localhost:8001 |
| Mock API Docs | http://localhost:8000/docs |
| AWS API Docs | http://localhost:8001/docs |
| Airflow UI | http://localhost:8080 |
| Frontend Dashboard | http://localhost:3000 |

### Airflow Login
- URL: http://localhost:8080
- Username: `admin`
- Password: `admin`

---

## Airflow DAGs

You'll see TWO DAGs in Airflow:

### 1. aws_cost_optimization_mock
- **Backend**: Port 8000 (Mock)
- **Schedule**: Daily at 6:00 AM
- **Cost**: $0 (Always Free)
- **Purpose**: Development and testing

### 2. aws_cost_optimization_production
- **Backend**: Port 8001 (Real AWS)
- **Schedule**: Daily at 7:00 AM
- **Cost**: AWS Free Tier
- **Purpose**: Production integration

---

## Cost Management

### To Use ONLY Mock Backend (Free)
Already configured! Just use port 8000

### To Enable Real AWS Backend
1. Get real AWS credentials from AWS Console
2. Update `.env` file:
   ```bash
   AWS_ACCESS_KEY_ID=YOUR_REAL_KEY
   AWS_SECRET_ACCESS_KEY=YOUR_REAL_SECRET
   ```
3. Restart AWS backend:
   ```bash
   docker-compose restart backend-aws
   ```

### To Stop AWS Backend (Save Money)
```bash
docker-compose stop backend-aws postgres-aws
```

### To Start AWS Backend Again
```bash
docker-compose start backend-aws postgres-aws
```

---

## Troubleshooting

### If Containers Keep Stopping
```bash
# Check logs for errors
docker-compose logs backend-mock
docker-compose logs backend-aws

# Restart specific service
docker-compose restart backend-mock
```

### If Health Endpoint Returns 404
The health endpoint is at: `/api/v1/health` (not just `/health`)

### If Database Connection Fails
```bash
# Check database status
docker-compose ps postgres-mock
docker-compose ps postgres-aws

# View database logs
docker-compose logs postgres-mock
```

### If Airflow DAGs Don't Appear
```bash
# Wait 30 seconds for Airflow to scan DAG files
# Then refresh the Airflow UI

# Check scheduler logs
docker-compose logs airflow-scheduler
```

---

## Next Steps

### 1. Test Mock Backend (Now!)
```bash
curl http://localhost:8000/api/v1/health
```

### 2. Trigger Mock DAG in Airflow
- Go to http://localhost:8080
- Find `aws_cost_optimization_mock`
- Click Trigger DAG
- Watch it run successfully

### 3. Get Real AWS Credentials (Later)
- Only when you want to test real AWS integration
- Follow AWS credential setup in DUAL_ENVIRONMENT_SETUP.md

### 4. Test Frontend Dashboard
- Go to http://localhost:3000
- Should connect to mock backend by default
- Can switch to AWS backend if configured

---

## Summary of What Was Changed

1. **docker-compose.yml** - Dual environment setup
2. **backend/app/core/dependencies.py** - Service selection logic
3. **airflow/dags/** - Two separate DAG files
4. **.env** - Updated with dual environment vars
5. **Documentation** - Created setup guides

---

## You're All Set!

Your dual-environment setup is complete. Start with the mock backend (port 8000) for free testing, and enable the AWS backend (port 8001) when you're ready for real AWS integration.

**Recommended First Steps:**
1. `docker-compose up -d --build`
2. Test mock backend: `curl http://localhost:8000/api/v1/health`
3. Open Airflow: http://localhost:8080
4. Trigger mock DAG and watch it succeed!
