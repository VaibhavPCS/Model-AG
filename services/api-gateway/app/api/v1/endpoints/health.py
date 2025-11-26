"""
Health Check Endpoint
Purpose: System health and readiness checks
Author: BMAD BMM Agents Dev
Date: 2025-11-26
"""

from fastapi import APIRouter, status
from typing import Dict
from datetime import datetime
import sys
import os

from app.db.session import check_database_connection
from app.core.config import settings

router = APIRouter()


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    response_model=Dict,
    summary="Health Check",
    description="Check if the API Gateway service is running and healthy"
)
async def health_check() -> Dict:
    """
    Health check endpoint.
    
    Returns comprehensive health status including:
    - Service status
    - Python version
    - Timestamp
    - Environment info
    
    Returns:
        dict: Health status information
    """
    return {
        "status": "healthy",
        "service": "API Gateway",
        "timestamp": datetime.utcnow().isoformat(),
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "environment": "development" if settings.DEBUG else "production"
    }


@router.get(
    "/health/ready",
    status_code=status.HTTP_200_OK,
    response_model=Dict,
    summary="Readiness Check",
    description="Check if the service is ready to accept requests"
)
async def readiness_check() -> Dict:
    """
    Readiness check endpoint.
    
    Verifies that all required dependencies are available:
    - Database connection (MySQL)
    - AI model loaded (future)
    - Storage accessible (future)
    
    Returns:
        dict: Readiness status
    """
    # Check database connection
    db_connected = await check_database_connection()
    
    checks = {
        "database": "connected" if db_connected else "disconnected",
        "rtdetr_model": "not_loaded",  # Will be implemented in Story 2.1
        "storage": "available"
    }
    
    # Determine overall readiness
    all_ready = db_connected  # Database is critical for readiness
    
    return {
        "ready": all_ready,
        "service": "API Gateway",
        "checks": checks,
        "database_url": f"{settings.MYSQL_USER}@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}",
        "timestamp": datetime.utcnow().isoformat()
    }
