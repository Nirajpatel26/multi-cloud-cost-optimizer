"""
Basic health check tests for the Multi-Cloud Cost Optimizer API
"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add parent directory to path to import main
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    """Test the health check endpoint returns 200 OK"""
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()
    assert response.json()["status"] == "healthy"


def test_root_endpoint():
    """Test the root endpoint is accessible"""
    response = client.get("/")
    assert response.status_code == 200


def test_api_docs_accessible():
    """Test that API documentation is accessible"""
    response = client.get("/docs")
    assert response.status_code == 200
