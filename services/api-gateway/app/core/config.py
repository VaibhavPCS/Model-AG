"""
Application Configuration
Purpose: Centralized configuration using Pydantic Settings
Author: BMAD BMM Agents Dev
Date: 2025-11-26
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    
    # Project Info
    PROJECT_NAME: str = "Model for AG - API Gateway"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = True
    
    # MySQL Configuration
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = ""
    MYSQL_DATABASE: str = "construction_monitoring"
    
    # Storage
    STORAGE_PATH: str = "./storage"
    
    # Fraud Detection
    GPS_TOLERANCE_METERS: int = 100
    DUPLICATE_HASH_THRESHOLD: int = 5
    
    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    @property
    def DATABASE_URL(self) -> str:
        """
        Construct async MySQL database URL.
        
        Returns:
            str: SQLAlchemy async database URL
        """
        password = f":{self.MYSQL_PASSWORD}" if self.MYSQL_PASSWORD else ""
        return (
            f"mysql+aiomysql://{self.MYSQL_USER}{password}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
        )
    
    class Config:
        # Try to load .env from project root
        env_file = "../../../.env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()
