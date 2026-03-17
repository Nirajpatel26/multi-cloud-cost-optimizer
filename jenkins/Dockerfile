# Custom Jenkins image with Python and Docker pre-installed
FROM jenkins/jenkins:lts

# Switch to root user to install packages
USER root

# Install Python, Docker CLI, and other tools
RUN apt-get update && \
    apt-get install -y \
    python3 \
    python3-venv \
    python3-pip \
    docker.io \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Give jenkins user permission to use Docker
RUN usermod -aG docker jenkins

# Switch back to jenkins user
USER jenkins

# Pre-install commonly used Jenkins plugins (optional)
RUN jenkins-plugin-cli --plugins \
    git \
    workflow-aggregator \
    docker-workflow \
    pipeline-stage-view
