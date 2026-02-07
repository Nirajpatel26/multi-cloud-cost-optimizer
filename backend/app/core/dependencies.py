# Database dependencies for FastAPI endpoints
import os
from typing import Generator
from app.services.aws_mock_service import AWSMockService
from app.services.aws_service import AWSService
from app.core.exceptions import DatabaseConnectionError
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


def get_database_url() -> str:
    """
    Construct database URL from environment variables
    """
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'cost_optimizer')
    db_user = os.getenv('DB_USER', 'admin')
    db_password = os.getenv('DB_PASSWORD', 'admin')
    
    return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


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
        database_url = get_database_url()
        
        logger.info(f"Initializing AWS Mock Service (env: {os.getenv('ENV', 'development')})")
        
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


def get_aws_service() -> Generator[AWSService, None, None]:
    """
    Returns REAL AWS Service (uses actual AWS API calls)
    
    Yields:
        AWSService instance configured with real AWS credentials
    
    Raises:
        DatabaseConnectionError: If connection fails
    """
    try:
        database_url = get_database_url()
        aws_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        aws_secret = os.getenv('AWS_SECRET_ACCESS_KEY')
        aws_region = os.getenv('AWS_REGION', 'us-east-1')
        
        logger.info(f"Initializing REAL AWS Service (region: {aws_region})")
        
        service = AWSService(
            aws_access_key_id=aws_key_id,
            aws_secret_access_key=aws_secret,
            region_name=aws_region,
            database_url=database_url
        )
        
        yield service
        
    except Exception as e:
        logger.error(f"Failed to initialize AWS service: {str(e)}")
        raise DatabaseConnectionError(
            detail=f"Unable to connect to AWS or database: {str(e)}"
        )
    finally:
        logger.debug("AWS service request completed")


def get_service():
    """
    Returns appropriate service based on environment configuration
    
    Determines which service to use based on:
    1. USE_REAL_AWS environment variable
    2. SERVICE_MODE environment variable
    
    Yields:
        AWSMockService or AWSService depending on configuration
    """
    use_real_aws = os.getenv('USE_REAL_AWS', 'false').lower() == 'true'
    service_mode = os.getenv('SERVICE_MODE', 'mock').lower()
    
    if use_real_aws or service_mode == 'aws':
        logger.info("Using REAL AWS Service (API calls will be made)")
        yield from get_aws_service()
    else:
        logger.info("Using MOCK AWS Service (zero cost)")
        yield from get_mock_service()


def get_db_session():
    """
    Alternative dependency for direct database session access
    Used when we need to query database directly without the mock service
    
    Also uses environment variables for secure configuration
    
    Yields:
        Database session
    """
    database_url = get_database_url()
    service = AWSMockService(database_url=database_url)
    session = service.get_db_session()
    try:
        yield session
    finally:
        session.close()
