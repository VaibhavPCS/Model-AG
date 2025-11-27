from pydantic import BaseModel, Field, validator
from typing import Optional, List
from enum import Enum


class SubmissionStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    FLAGGED = "flagged"


class SubmissionCreate(BaseModel):
    site_id: int = Field(..., gt=0)
    gps_lat: float = Field(..., ge=-90, le=90)
    gps_lon: float = Field(..., ge=-180, le=180)
    surveyor_id: int = Field(..., gt=0)

    @validator("gps_lat", "gps_lon")
    def validate_coordinates(cls, v):
        # Additional validation can be added here
        return v


class FraudFlagModel(BaseModel):
    flag_type: str
    description: Optional[str] = None


class AIValidationResult(BaseModel):
    bounding_boxes: list
    confidence_score: float
    flags: List[FraudFlagModel]


class SubmissionResponse(BaseModel):
    submission_id: int
    validation_result: AIValidationResult
    alerts: Optional[List[str]] = []
