# Database dependencies for FastAPI endpoints
from typing import Generator
from app.services.aws_mock_service import AWSMockService
from app.core.exceptions import DatabaseConnectionError
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


def get_mock_service() -> Generator[AWSMockService, None, None]:
    """
    Dependency function that provides AWSMockService instance
    
    This function:
    1. Loads database URL from environment variables (secure)
    2. Creates a connection to the mock service
    3. Yields the service to the endpoint
    4. Handles connection errors
    5. Cleans up after the request
    
    Database credentials are loaded from:
    - .env file in development
    - Environment variables in production
    
    Usage in endpoints:
        @router.get("/endpoint")
        async def endpoint(service: AWSMockService = Depends(get_mock_service)):
            # Use service here
    
    Yields:
        AWSMockService instance
    
    Raises:
        DatabaseConnectionError: If connection fails
    """
    try:
        # Get database URL from configuration (loaded from .env)
        database_url = settings.DATABASE_URL
        
        logger.info(f"Initializing AWS Mock Service (env: {settings.ENV})")
        logger.debug(f"Connecting to database at {settings.DB_HOST}:{settings.DB_PORT}")
        
        # Initialize the mock service with database connection
        service = AWSMockService(database_url=database_url)
        
        # Yield the service to the endpoint
        yield service
        
    except Exception as e:
        logger.error(f"Failed to initialize mock service: {str(e)}")
        raise DatabaseConnectionError(
            detail=f"Unable to connect to database: {str(e)}"
        )
    finally:
        # Cleanup happens here if needed
        logger.debug("Mock service request completed")


def get_db_session():
    """
    Alternative dependency for direct database session access
    Used when we need to query database directly without the mock service
    
    Also uses environment variables for secure configuration
    
    Yields:
        Database session
    """
    database_url = settings.DATABASE_URL
    service = AWSMockService(database_url=database_url)
    session = service.get_db_session()
    try:
        yield session
    finally:
        session.close()
