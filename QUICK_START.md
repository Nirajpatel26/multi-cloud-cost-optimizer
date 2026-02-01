# Quick Start Guide - Multi-Cloud Cost Optimizer

## ✅ Repository Successfully Cloned!

**Location:** `~/Desktop/multi-cloud-cost-optimizer`

---

## 🚀 Next Steps

### Step 1: Set Up Environment Variables
```powershell
# Navigate to project directory
cd ~/Desktop/multi-cloud-cost-optimizer

# Copy the environment template
copy .env.example .env

# Edit .env file with your actual credentials
notepad .env
```

**Required Credentials:**
- Database password
- AWS Access Key & Secret
- Azure Subscription ID, Tenant ID, Client ID, Secret
- OCI User ID, Fingerprint, Tenancy ID
- Airflow Fernet Key (generate using Python)

---

### Step 2: Generate Airflow Fernet Key (Optional but Recommended)

```powershell
# Open Python
python

# In Python console:
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
# Copy the output and paste it in .env as AIRFLOW_FERNET_KEY
exit()
```

---

### Step 3: Start All Services with Docker Compose

```powershell
# Make sure Docker Desktop is running first!

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

---

### Step 4: Access the Services

Once all containers are running:

- **Backend API:** http://localhost:8000
- **Airflow UI:** http://localhost:8080
  - Default username: `admin`
  - Default password: `admin`
- **Jenkins:** http://localhost:8081
  - Follow setup wizard on first access
- **Frontend:** http://localhost:3000

---

### Step 5: Backend Development Setup (Optional)

If you want to develop the backend locally without Docker:

```powershell
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run backend locally
uvicorn app.main:app --reload
```

---

### Step 6: Frontend Development Setup (Optional)

If you want to develop the frontend locally:

```powershell
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

---

## 🔧 Common Commands

### Docker Management
```powershell
# Stop all services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v

# Rebuild and restart
docker-compose up -d --build

# View logs for specific service
docker-compose logs -f backend
docker-compose logs -f airflow-webserver
```

### Git Workflow
```powershell
# Check current branch
git branch

# Switch to develop branch
git checkout develop

# Create new feature branch
git checkout -b feature/your-feature-name

# Push changes
git add .
git commit -m "Your commit message"
git push origin feature/your-feature-name
```

---

## 📋 Available Branches

- **main** - Production-ready code
- **develop** - Development integration branch
- **staging** - Pre-production testing

---

## 🐛 Troubleshooting

### Docker Issues
- Ensure Docker Desktop is running
- Check if ports 8000, 8080, 8081, 3000, 5432 are available
- Try: `docker-compose down -v` then `docker-compose up -d`

### Permission Issues
- Run PowerShell as Administrator if needed
- Check file permissions in project directory

### Database Connection Issues
- Ensure PostgreSQL container is running: `docker-compose ps`
- Check logs: `docker-compose logs postgres`
- Verify DATABASE_URL in .env matches docker-compose.yml

---

## 📚 Documentation

- **Project Overview:** `docs/PROJECT_OVERVIEW.md`
- **Contributing Guide:** `CONTRIBUTING.md`
- **README:** `README.md`

---

## 🎯 Day 2 Tasks (Jenkins Configuration)

Now that the repo is cloned, you're ready to:

1. Set up Jenkins
2. Configure Jenkins credentials
3. Create pipeline jobs
4. Set up webhooks

Refer to Week 1 - Phase 1 documentation for detailed steps.

---

## 💡 Tips

- Always work on feature branches, not main/develop directly
- Run tests before committing: `pytest` (backend) or `npm test` (frontend)
- Use `docker-compose logs -f` to monitor service health
- Keep .env file secure and never commit it to Git

---

**Happy Coding! 🚀**
