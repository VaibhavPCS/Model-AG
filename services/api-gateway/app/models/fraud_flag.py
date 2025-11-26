"""
Fraud Flag Model
Purpose: Tracks fraud detection flags
Author: BMAD BMM Agents Dev
Date: 2025-11-26
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class FraudFlag(Base):
    """
    Fraud detection flag model.
    
    Attributes:
        id: Primary key
        submission_id: Foreign key to Submission
        flag_type: Type of fraud detected
        details: Additional fraud details (JSON)
        resolved: Whether flag has been resolved
        resolved_by: User who resolved the flag
        resolved_at: When flag was resolved
        created_at: Flag creation timestamp
    """
    
    __tablename__ = "fraud_flags"
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign Keys
    submission_id = Column(
        Integer,
        ForeignKey("submissions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Flag Information
    flag_type = Column(String(50), nullable=False, index=True)
    # Types: GPS_MISMATCH, DUPLICATE_PHOTO, IMPOSSIBLE_PROGRESS
    details = Column(JSON, nullable=False)
    
    # Resolution
    resolved = Column(Boolean, nullable=False, default=False, index=True)
    resolved_by = Column(Integer, nullable=True)  # Future: FK to users table
    resolved_at = Column(DateTime, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    
    # Relationships
    submission = relationship("Submission", back_populates="fraud_flags")
    
    def __repr__(self):
        return (
            f"<FraudFlag(id={self.id}, submission_id={self.submission_id}, "
            f"type='{self.flag_type}', resolved={self.resolved})>"
        )
