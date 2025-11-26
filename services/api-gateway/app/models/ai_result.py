"""
AI Result Model
Purpose: Stores AI model inference results
Author: BMAD BMM Agents Dev
Date: 2025-11-26
"""

from sqlalchemy import Column, Integer, String, DECIMAL, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class AIResult(Base):
    """
    AI inference result model.
    
    Attributes:
        id: Primary key
        submission_id: Foreign key to Submission
        model_type: Type of AI model (rtdetr, sam3_grounding_dino)
        stage: Detected construction stage
        confidence_score: Model confidence (0-100)
        model_output: Raw model output (JSON)
        completion_percentages: Element completion percentages (JSON)
        processing_time_seconds: Time taken for inference
        triggered_by: How inference was triggered (auto, admin)
        created_at: Result timestamp
    """
    
    __tablename__ = "ai_results"
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign Keys
    submission_id = Column(
        Integer,
        ForeignKey("submissions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # AI Model Info
    model_type = Column(String(20), nullable=False, index=True)  # 'rtdetr' or 'sam3_grounding_dino'
    stage = Column(String(50), nullable=True, index=True)  # Foundation, Walls, Roofing, etc.
    confidence_score = Column(DECIMAL(5, 2), nullable=False)  # 0.00 to 100.00
    
    # Results
    model_output = Column(JSON, nullable=True)  # Raw model output
    completion_percentages = Column(JSON, nullable=True)  # {"foundation": 100, "walls": 65}
    
    # Metadata
    processing_time_seconds = Column(Integer, nullable=True)
    triggered_by = Column(String(20), nullable=False)  # 'auto' or 'admin'
    
    # Timestamp
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    
    # Relationships
    submission = relationship("Submission", back_populates="ai_results")
    
    def __repr__(self):
        return (
            f"<AIResult(id={self.id}, submission_id={self.submission_id}, "
            f"model='{self.model_type}', stage='{self.stage}')>"
        )
