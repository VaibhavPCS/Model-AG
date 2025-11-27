from fastapi import APIRouter
from datetime import datetime

from app.db.session import engine
from sqlalchemy import text

from app.api.v1.endpoints.submissions import rtdetr_service
from app.api.v1.endpoints.comparison import grounding_dino_service, sam3_service

router = APIRouter()


@router.get("/health")
async def health_root():
    return {"status": "ok"}


@router.get("/health/ready")
async def readiness_check():
    # Database check
    db_status = "disconnected"
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    # RT-DETR status
    rtdetr_status = "loaded" if getattr(rtdetr_service, "model", None) is not None else "not_loaded"

    # Grounding DINO status
    dino_status = "loaded" if getattr(grounding_dino_service, "model", None) is not None else "not_loaded"

    # SAM 2.1 status
    sam_status = "loaded" if getattr(sam3_service, "predictor", None) is not None else "not_loaded"

    return {
        "ready": db_status == "connected" and rtdetr_status == "loaded",
        "service": "API Gateway",
        "checks": {
            "database": db_status,
            "rtdetr_model": rtdetr_status,
            "grounding_dino": dino_status,
            "sam2_1": sam_status,
        },
        "database_url": "root@localhost:3306/construction_monitoring",
        "timestamp": datetime.utcnow().isoformat(),
    }
