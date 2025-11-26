"""
Main FastAPI Application - API Gateway
Purpose: Initialize and configure the FastAPI application
Author: BMAD BMM Agents Dev
Date: 2025-11-26
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api.v1.endpoints import health
from app.core.config import settings
from app.db.session import init_db_pool, close_db_pool


# Application lifespan manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle events.
    
    Startup:
        - Initialize database connections
        - Load AI models into memory
        - Set up logging
        
    Shutdown:
        - Close database connections
        - Clean up resources
    """
    # Startup
    print("🚀 Starting API Gateway Service...")
    print(f"📊 Database: {settings.MYSQL_DATABASE}")
    print(f"🔌 MySQL Host: {settings.MYSQL_HOST}:{settings.MYSQL_PORT}")
    print(f"👤 MySQL User: {settings.MYSQL_USER}")
    
    # Initialize database pool
    await init_db_pool()
    
    print("✅ API Gateway is ready!")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down API Gateway Service...")
    await close_db_pool()


# Initialize FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI-powered construction monitoring system for government housing schemes",
    version=settings.VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    health.router,
    prefix=settings.API_V1_PREFIX,
    tags=["health"]
)


@app.get("/")
async def root():
    """
    Root endpoint - API information.
    
    Returns:
        dict: API metadata and status
    """
    return {
        "service": "API Gateway",
        "version": settings.VERSION,
        "status": "running",
        "docs": "/api/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
