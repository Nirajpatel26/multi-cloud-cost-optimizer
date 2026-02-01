# Configuration management using environment variables
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    
    This class:
    1. Loads configuration from .env file
    2. Provides type-safe access to settings
    3. Validates required variables exist
    4. Builds database URL from components
    """
    
    # Database Configuration
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 5433
    DB_NAME: str = "cost_optimizer"
    DB_USER: str = "admin"
    DB_PASSWORD: str = "admin"
    
    # Application Settings
    ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    API_VERSION: str = "v1"
    
    class Config:
        # Tell pydantic to load from .env file
        env_file = ".env"
        case_sensitive = True
    
    @property
    def DATABASE_URL(self) -> str:
        """
        Construct database URL from components
        
        Returns:
            PostgreSQL connection string
        """
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.ENV.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.ENV.lower() == "development"


# Create a single instance to be imported throughout the app
settings = Settings()
