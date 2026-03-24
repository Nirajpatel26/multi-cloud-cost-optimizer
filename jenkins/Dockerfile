# Custom Jenkins image with Python, Docker, and all dependencies for requirements.txt
FROM jenkins/jenkins:lts

# Switch to root user to install packages
USER root

# Install system dependencies for all Python packages in requirements.txt
RUN apt-get update && \
    apt-get install -y \
    # Python essentials
    python3 \
    python3-venv \
    python3-pip \
    python3-dev \
    # Docker
    docker.io \
    # Version control
    git \
    curl \
    # PostgreSQL (for psycopg2-binary)
    libpq-dev \
    postgresql-client \
    # Cryptography & security (for python-jose, passlib)
    libffi-dev \
    libssl-dev \
    cargo \
    rustc \
    # Scientific computing (for pandas, numpy)
    gfortran \
    libblas-dev \
    liblapack-dev \
    # Build tools (for compiling any Python package)
    build-essential \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

# Install Docker Compose v2 as a standalone binary in PATH
RUN curl -SL "https://github.com/docker/compose/releases/download/v2.24.5/docker-compose-linux-x86_64" \
    -o /usr/local/bin/docker-compose && \
    chmod +x /usr/local/bin/docker-compose

# Give jenkins user permission to use Docker
RUN usermod -aG docker jenkins

# Switch back to jenkins user
USER jenkins

# Pre-install commonly used Jenkins plugins
RUN jenkins-plugin-cli --plugins \
    git \
    workflow-aggregator \
    docker-workflow \
    pipeline-stage-view

# Set environment variables for Python
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
