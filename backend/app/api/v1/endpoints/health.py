# Health check endpoint
from fastapi import APIRouter, Depends
from datetime import datetime
from app.core.dependencies import get_mock_service
from app.services.aws_mock_service import AWSMockService
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/health")
async def health_check(service: AWSMockService = Depends(get_mock_service)):
    """
    Check API and database health status
    
    This endpoint:
    1. Tests database connectivity through the mock service dependency
    2. If dependency injection succeeds, database is connected
    3. Returns health status with timestamp
    
    Returns:
        Health status object with database connection status
    """
    try:
        # If we got here, the dependency injection worked
        # which means database connection is successful
        
        # Try a simple database query to double-check
        db_session = service.get_db_session()
        db_session.execute("SELECT 1")
        db_session.close()
        
        logger.info("Health check passed - database connected")
        
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    except Exception as e:
        # This shouldn't happen if dependency works correctly
        # but we catch it just in case
        logger.error(f"Health check failed: {str(e)}")
        
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
