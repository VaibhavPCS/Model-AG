"""
Site Model
Purpose: Represents a construction site
Author: BMAD BMM Agents Dev
Date: 2025-11-26
"""

from sqlalchemy import Column, Integer, String, DECIMAL, Date, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class Site(Base):
    """
    Construction site model.
    
    Attributes:
        id: Primary key
        site_code: Unique site identifier
        gps_lat: GPS latitude
        gps_lon: GPS longitude
        contractor: Contractor name
        expected_completion_date: Expected project completion
        created_at: Record creation timestamp
        updated_at: Record update timestamp
    """
    
    __tablename__ = "sites"
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Site Information
    site_code = Column(String(50), unique=True, nullable=False, index=True)
    gps_lat = Column(DECIMAL(10, 8), nullable=False)
    gps_lon = Column(DECIMAL(11, 8), nullable=False)
    contractor = Column(String(255), nullable=True)
    expected_completion_date = Column(Date, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime, 
        nullable=False, 
        server_default=func.now(), 
        onupdate=func.now()
    )
    
    # Relationships
    submissions = relationship(
        "Submission", 
        back_populates="site",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<Site(id={self.id}, code='{self.site_code}', contractor='{self.contractor}')>"
