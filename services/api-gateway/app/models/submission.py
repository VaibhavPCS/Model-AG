"""
Submission Model
Purpose: Represents a photo submission for a site
Author: BMAD BMM Agents Dev
Date: 2025-11-26
"""

from sqlalchemy import Column, Integer, String, DECIMAL, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.db.base import Base


class SubmissionStatus(enum.Enum):
    """Submission status enumeration."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    FLAGGED = "flagged"


class Submission(Base):
    """
    Photo submission model.
    
    Attributes:
        id: Primary key
        site_id: Foreign key to Site
        photo_url: Path to stored photo
        gps_lat: GPS latitude when photo was taken
        gps_lon: GPS longitude when photo was taken
        timestamp: When photo was submitted
        status: Processing status
        surveyor_id: ID of surveyor who submitted (future)
        created_at: Record creation timestamp
    """
    
    __tablename__ = "submissions"
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign Keys
    site_id = Column(Integer, ForeignKey("sites.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Submission Data
    photo_url = Column(Text, nullable=False)
    gps_lat = Column(DECIMAL(10, 8), nullable=False)
    gps_lon = Column(DECIMAL(11, 8), nullable=False)
    timestamp = Column(DateTime, nullable=False, server_default=func.now(), index=True)
    status = Column(
        Enum(SubmissionStatus),
        nullable=False,
        default=SubmissionStatus.PENDING,
        index=True
    )
    surveyor_id = Column(Integer, nullable=True)  # Future: FK to users table
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    
    # Relationships
    site = relationship("Site", back_populates="submissions")
    ai_results = relationship(
        "AIResult",
        back_populates="submission",
        cascade="all, delete-orphan"
    )
    fraud_flags = relationship(
        "FraudFlag",
        back_populates="submission",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<Submission(id={self.id}, site_id={self.site_id}, status='{self.status.value}')>"
