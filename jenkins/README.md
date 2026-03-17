# Jenkins CI/CD Setup

This directory contains the Jenkins configuration for the Multi-Cloud Cost Optimizer project.

## Overview

Custom Jenkins image with pre-installed tools:
- Python 3 (for running tests)
- Docker CLI (for building images)
- Git (for source control)
- Jenkins Pipeline plugins

## Quick Start

### 1. Build and Start Jenkins

```bash
# Stop existing Jenkins container if running
docker stop mcco-jenkins
docker rm mcco-jenkins

# Build and start custom Jenkins
docker-compose -f docker-compose.jenkins.yml up -d --build
```

### 2. Get Initial Admin Password

```bash
docker exec mcco-jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

### 3. Access Jenkins

Open browser: http://localhost:8081

### 4. Create Pipeline Job

1. Click "New Item"
2. Name: `mcco-pipeline`
3. Type: Pipeline
4. Pipeline definition: "Pipeline script from SCM"
5. SCM: Git
6. Repository URL: `https://github.com/Nirajpatel26/multi-cloud-cost-optimizer`
7. Branch: `*/develop`
8. Script Path: `jenkins/pipelines/Jenkinsfile`
9. Save and click "Build Now"

## Architecture

```
Jenkins Container
├── Python 3 (pre-installed)
├── Docker CLI (pre-installed)
├── Git (pre-installed)
└── Jenkins Pipeline
    ├── Checkout code
    ├── Install Python dependencies (requirements.txt)
    ├── Run tests (pytest)
    ├── Build Docker images
    └── Deploy containers
```

## Files

- `Dockerfile` - Custom Jenkins image definition
- `docker-compose.jenkins.yml` - Jenkins service configuration
- `pipelines/Jenkinsfile` - CI/CD pipeline definition
- `scripts/` - Helper scripts for pipeline

## Why Custom Image?

**Infrastructure vs Application:**
- **Infrastructure** (Docker image): Python, Docker CLI, system tools
- **Application** (Pipeline): pip packages, virtual environments, your code

This separation ensures:
- ✅ Reproducible setup
- ✅ Version-controlled infrastructure
- ✅ Fast pipeline execution
- ✅ No manual installation steps

## Troubleshooting

### Docker socket permission denied
```bash
docker exec -u root mcco-jenkins chmod 666 /var/run/docker.sock
```

### Check Jenkins logs
```bash
docker logs -f mcco-jenkins
```

### Rebuild Jenkins image
```bash
docker-compose -f docker-compose.jenkins.yml up -d --build --force-recreate
```
