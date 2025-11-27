"""
Comparison Response Schemas
Purpose: Schemas for Model 2 (DINO + SAM3) endpoint
Author: BMAD BMM Agents Dev
Date: 2025-11-27
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class Detection(BaseModel):
    """Single detection result."""
    label: str
    confidence: float = Field(ge=0, le=1)
    bbox: List[float]


class GroundingDINOResult(BaseModel):
    """Grounding DINO detection output."""
    detections: List[Detection]
    prompts_used: List[str]


class SegmentationMask(BaseModel):
    """Single segmentation mask."""
    id: int
    confidence: float
    area_percentage: float


class SAM3Result(BaseModel):
    """SAM3 segmentation output."""
    masks: List[SegmentationMask]
    total_masks: int


class StageClassification(BaseModel):
    """Construction stage classification."""
    stage: str
    confidence: float = Field(ge=0, le=1)
    matched_elements: List[str]
    completion_percentage: float = Field(ge=0, le=100)


class ProgressionAlert(BaseModel):
    """Progression validation alert."""
    is_valid: bool
    alert_type: Optional[str] = None
    message: Optional[str] = None


class ComparisonResponse(BaseModel):
    """Comparison endpoint response (RT-DETR vs DINO)."""
    submission_id: int
    rtdetr_confidence: float
    rtdetr_boxes_count: int
    grounding_dino: GroundingDINOResult
    sam3: SAM3Result
    stage_classification: StageClassification
    progression_check: ProgressionAlert
    comparison: Dict[str, Any]
