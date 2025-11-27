"""
Main FastAPI Application - API Gateway
Purpose: Initialize and configure the FastAPI application
Author: BMAD BMM Agents Dev
Date: 2025-11-26
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.db.session import init_db_pool, close_db_pool


# Application lifespan manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle events."""
    # Startup
    print("🚀 Starting API Gateway Service...")
    print(f"📊 Database: {settings.MYSQL_DATABASE}")
    print(f"🔌 MySQL Host: {settings.MYSQL_HOST}:{settings.MYSQL_PORT}")
    print(f"👤 MySQL User: {settings.MYSQL_USER}")
    
    # Initialize database pool
    await init_db_pool()
    
    # ✅ Load RT-DETR model (ADD THIS)
    from app.api.v1.endpoints.submissions import rtdetr_service
    print("🤖 Loading RT-DETR model...")
    await rtdetr_service.load_model()
    print("✅ RT-DETR model loaded!")
    
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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routers
from app.api.v1.endpoints import health, submissions

# Include routers
app.include_router(
    health.router,
    prefix=settings.API_V1_PREFIX,
    tags=["health"]
)

app.include_router(
    submissions.router,
    prefix=settings.API_V1_PREFIX,
    tags=["submissions"]
)


@app.get("/")
async def root():
    """Root endpoint - API information."""
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
