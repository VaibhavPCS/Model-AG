"""
Comparison Endpoint
Purpose: Compare RT-DETR vs SAM3+Grounding DINO
Author: BMAD BMM Agents Dev
Date: 2025-11-27
"""

from fastapi import APIRouter, Depends, Form, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models import Submission, AIResult
from app.schemas.comparison import ComparisonResponse, ProgressionAlert
from app.services.grounding_dino_service import GroundingDINOService
from app.services.sam3_service import SAM3Service
from app.services.construction_stage_classifier import ConstructionStageClassifier
from app.services.progression_validator import ProgressionValidator
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize services
grounding_dino_service = GroundingDINOService()
sam3_service = SAM3Service()
stage_classifier = ConstructionStageClassifier()
progression_validator = ProgressionValidator()


@router.post(
    "/comparison",
    response_model=ComparisonResponse,
    status_code=status.HTTP_200_OK,
    summary="Compare Models",
    description="Compare RT-DETR vs Grounding DINO + SAM3 on a submission"
)
async def compare_models(
    submission_id: int = Form(..., description="Submission ID to analyze"),
    db: AsyncSession = Depends(get_db)
):
    """
    Compare RT-DETR vs Grounding DINO + SAM3 on a submission.
    Also performs construction stage classification and fraud detection.
    
    Args:
        submission_id: ID of submission to analyze
        db: Database session
    
    Returns:
        Comparison results with stage classification and progression validation
    """
    
    # Get submission
    submission = await db.get(Submission, submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    # Get RT-DETR results
    rtdetr_query = (
        select(AIResult)
        .where(
            AIResult.submission_id == submission_id,
            AIResult.model_type == "rtdetr"
        )
        .order_by(AIResult.created_at.desc())
        .limit(1)
    )
    rtdetr_result = await db.execute(rtdetr_query)
    rtdetr = rtdetr_result.scalars().first()
    
    if not rtdetr:
        raise HTTPException(status_code=404, detail="RT-DETR results not found")
    
    image_path = submission.photo_url
    
    # Step 1: Run Grounding DINO detection
    print(f"🎯 Running Grounding DINO on submission {submission_id}...")
    dino_results = await grounding_dino_service.detect(image_path)
    
    # Step 2: Run SAM3 segmentation
    print(f"🎯 Running SAM3 segmentation...")
    bboxes = [d["bbox"] for d in dino_results.get("detections", [])]
    sam3_results = await sam3_service.segment(image_path, bboxes)
    
    # Step 3: Classify construction stage
    print(f"🎯 Classifying construction stage...")
    stage, stage_confidence, stage_details = await stage_classifier.classify_stage(
        dino_results
    )
    completion_pct = await stage_classifier.estimate_completion_percentage(stage)
    
    # Step 4: Validate progression
    print(f"🎯 Validating progression...")
    is_valid, error_msg = await progression_validator.validate_progression(
        db, submission.site_id, stage, stage_confidence
    )
    
    progression_check = ProgressionAlert(
        is_valid=is_valid,
        alert_type=None if is_valid else "progression_violation",
        message=error_msg
    )
    
    # Step 5: Calculate model agreement
    rtdetr_boxes = len(rtdetr.model_output.get("bboxes", []))
    dino_detections = len(dino_results.get("detections", []))
    
    if rtdetr_boxes > 0 and dino_detections > 0:
        min_count = min(rtdetr_boxes, dino_detections)
        max_count = max(rtdetr_boxes, dino_detections)
        agreement = (min_count / max_count) * 100 if max_count > 0 else 0
    else:
        agreement = 0
    
    recommendation = (
        "Use Grounding DINO" if agreement < 50
        else "Models agree" if agreement > 70
        else "Manual review recommended"
    )
    
    # Build response
    response = ComparisonResponse(
        submission_id=submission_id,
        rtdetr_confidence=float(rtdetr.confidence_score),
        rtdetr_boxes_count=rtdetr_boxes,
        grounding_dino={
            "detections": [
                {
                    "label": d["label"],
                    "confidence": d["confidence"],
                    "bbox": d["bbox"]
                }
                for d in dino_results.get("detections", [])
            ],
            "prompts_used": dino_results.get("prompts_used", [])
        },
        sam3={
            "masks": sam3_results.get("masks", []),
            "total_masks": sam3_results.get("total_masks", 0)
        },
        stage_classification={
            "stage": stage.value,
            "confidence": float(stage_confidence),
            "matched_elements": stage_details.get("matched_elements", []),
            "completion_percentage": float(completion_pct)
        },
        progression_check=progression_check.dict(),
        comparison={
            "model_agreement": float(agreement),
            "recommendation": recommendation
        }
    )
    
    # Store comparison results in DB
    comparison_result = AIResult(
        submission_id=submission_id,
        model_type="comparison_dino_sam3",
        stage=stage.value,
        confidence_score=stage_confidence,
        model_output=dino_results,
        segmentation_masks=sam3_results,
        completion_percentages={"overall": completion_pct},
        triggered_by="manual"
    )
    db.add(comparison_result)
    await db.commit()
    
    print(f"✅ Comparison complete - Stage: {stage.value}, Completion: {completion_pct}%")
    
    return response
