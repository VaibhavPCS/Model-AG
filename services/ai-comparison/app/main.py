"""
Main FastAPI Application - AI Comparison Service
Purpose: Initialize and configure the AI comparison service
Author: BMAD BMM Agents Dev
Date: 2025-11-26
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api.v1.endpoints import health
from app.core.config import settings


# Application lifespan manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle events.
    
    Startup:
        - Load SAM3 model (Story 2.2)
        - Load Grounding DINO model (Story 2.2)
        - Set up logging
        
    Shutdown:
        - Clean up model resources
    """
    # Startup
    print("🚀 Starting AI Comparison Service...")
    print(f"📁 Storage Path: {settings.STORAGE_PATH}")
    print(f"🤖 SAM3 Model Path: {settings.SAM3_MODEL_PATH}")
    print(f"🤖 Grounding DINO Path: {settings.GROUNDING_DINO_MODEL_PATH}")
    print("✅ AI Comparison Service is ready!")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down AI Comparison Service...")


# Initialize FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="SAM3 + Grounding DINO for construction stage classification",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
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
    tags=["health"]
)


@app.get("/")
async def root():
    """
    Root endpoint - Service information.
    
    Returns:
        dict: Service metadata and status
    """
    return {
        "service": "AI Comparison Service",
        "version": settings.VERSION,
        "status": "running",
        "models": {
            "sam3": "pending_story_2.2",
            "grounding_dino": "pending_story_2.2"
        },
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
