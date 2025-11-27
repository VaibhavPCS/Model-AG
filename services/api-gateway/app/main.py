from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.db.session import init_db_pool, close_db_pool
from app.api.v1.endpoints.comparison import grounding_dino_service, sam3_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle events."""
    print("🚀 Starting API Gateway Service...")
    print(f"📊 Database: {settings.MYSQL_DATABASE}")
    print(f"🔌 MySQL Host: {settings.MYSQL_HOST}:{settings.MYSQL_PORT}")
    print(f"👤 MySQL User: {settings.MYSQL_USER}")

    await init_db_pool()

    # RT-DETR
    from app.api.v1.endpoints.submissions import rtdetr_service
    print("🤖 Loading RT-DETR model...")
    await rtdetr_service.load_model()
    print("✅ RT-DETR model loaded!")

    # Grounding DINO
    print("🤖 Loading Grounding DINO model...")
    await grounding_dino_service.load_model()
    print("✅ Grounding DINO model loaded!")

    # SAM 2.1
    print("🤖 Loading SAM 2.1 model...")
    await sam3_service.load_model()
    print("✅ SAM 2.1 model loaded!")

    print("✅ API Gateway is ready!")

    yield

    print("🛑 Shutting down API Gateway Service...")
    await close_db_pool()


# ✅ CREATE APP HERE
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI-powered construction monitoring system for government housing schemes",
    version=settings.VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
from app.api.v1.endpoints import health, submissions, comparison

app.include_router(
    health.router, prefix=settings.API_V1_PREFIX, tags=["health"]
)
app.include_router(
    submissions.router, prefix=settings.API_V1_PREFIX, tags=["submissions"]
)
app.include_router(
    comparison.router, prefix=settings.API_V1_PREFIX, tags=["comparison"]
)


@app.get("/")
async def root():
    return {
        "service": "API Gateway",
        "version": settings.VERSION,
        "status": "running",
        "docs": "/api/docs",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
