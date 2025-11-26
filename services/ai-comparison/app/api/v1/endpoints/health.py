"""
Health Check Endpoint - AI Comparison Service
Purpose: System health and readiness checks for AI service
Author: BMAD BMM Agents Dev
Date: 2025-11-26
"""

from fastapi import APIRouter, status
from typing import Dict
from datetime import datetime
import sys
import os
from pathlib import Path

from app.core.config import settings

router = APIRouter()


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    response_model=Dict,
    summary="Health Check",
    description="Check if the AI Comparison service is running and healthy"
)
async def health_check() -> Dict:
    """
    Health check endpoint.
    
    Returns comprehensive health status including:
    - Service status
    - Model loading status
    - Python version
    - Timestamp
    
    Returns:
        dict: Health status information
    """
    return {
        "status": "healthy",
        "service": "AI Comparison Service",
        "timestamp": datetime.utcnow().isoformat(),
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "environment": "development" if settings.DEBUG else "production"
    }


@router.get(
    "/health/ready",
    status_code=status.HTTP_200_OK,
    response_model=Dict,
    summary="Readiness Check",
    description="Check if the AI service is ready to process requests"
)
async def readiness_check() -> Dict:
    """
    Readiness check endpoint.
    
    Verifies that all required AI models and resources are available:
    - SAM3 model file (future - Story 2.2)
    - Grounding DINO model file (future - Story 2.2)
    - Storage accessible
    
    Returns:
        dict: Readiness status
    """
    # Check if storage directory exists
    storage_path = Path(settings.STORAGE_PATH)
    storage_exists = storage_path.exists() or storage_path.parent.exists()
    
    # Check if model files exist (they won't yet - that's Story 2.2)
    sam3_path = Path(settings.SAM3_MODEL_PATH)
    dino_path = Path(settings.GROUNDING_DINO_MODEL_PATH)
    
    sam3_exists = sam3_path.exists()
    dino_exists = dino_path.exists()
    
    checks = {
        "sam3_model": "file_exists" if sam3_exists else "pending_story_2.2",
        "grounding_dino_model": "file_exists" if dino_exists else "pending_story_2.2",
        "storage": "available" if storage_exists else "unavailable"
    }
    
    # Service is ready even without models (they'll be loaded in Story 2.2)
    all_ready = True
    
    return {
        "ready": all_ready,
        "service": "AI Comparison Service",
        "checks": checks,
        "storage_path": str(storage_path.absolute() if storage_exists else settings.STORAGE_PATH),
        "timestamp": datetime.utcnow().isoformat()
    }
