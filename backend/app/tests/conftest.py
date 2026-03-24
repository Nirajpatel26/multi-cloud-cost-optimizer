"""
Test configuration — overrides the database dependency to use SQLite
so tests run in CI without a PostgreSQL instance.
"""
import os
import pytest
from app.main import app
from app.core.dependencies import get_service
from app.services.aws_mock_service import AWSMockService

TEST_DB_URL = "sqlite:///./test_ci.db"


def override_get_service():
    service = AWSMockService(database_url=TEST_DB_URL)
    yield service


app.dependency_overrides[get_service] = override_get_service


def pytest_sessionfinish(session, exitstatus):
    """Clean up the SQLite test database after the test run."""
    if os.path.exists("./test_ci.db"):
        os.remove("./test_ci.db")
