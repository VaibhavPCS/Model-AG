"""
Application Configuration - AI Comparison Service
Purpose: Centralized configuration using Pydantic Settings
Author: BMAD BMM Agents Dev
Date: 2025-11-26
"""

from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    
    # Project Info
    PROJECT_NAME: str = "Model for AG - AI Comparison Service"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Storage
    STORAGE_PATH: str = "./storage"
    
    # AI Models
    SAM3_MODEL_PATH: str = "models/sam3.pth"
    GROUNDING_DINO_MODEL_PATH: str = "models/groundingdino_1.6_pro.pth"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = "../../../.env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()
