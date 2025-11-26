"""
Audit Log Model
Purpose: Immutable audit trail for all actions
Author: BMAD BMM Agents Dev
Date: 2025-11-26
"""

from sqlalchemy import Column, Integer, String, DateTime, JSON, Text
from sqlalchemy.sql import func
from app.db.base import Base


class AuditLog(Base):
    """
    Audit log model - immutable record of all system actions.
    
    Attributes:
        id: Primary key
        user_id: User who performed action
        action: Action type
        entity_type: Type of entity affected
        entity_id: ID of affected entity
        before_state: State before action (JSON)
        after_state: State after action (JSON)
        timestamp: When action occurred
        request_id: Request ID for tracing
    """
    
    __tablename__ = "audit_logs"
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Actor
    user_id = Column(Integer, nullable=True, index=True)  # Future: FK to users table
    
    # Action Details
    action = Column(String(100), nullable=False, index=True)
    entity_type = Column(String(50), nullable=False, index=True)
    entity_id = Column(Integer, nullable=False, index=True)
    
    # State Changes
    before_state = Column(JSON, nullable=True)
    after_state = Column(JSON, nullable=True)
    
    # Metadata
    timestamp = Column(DateTime, nullable=False, server_default=func.now(), index=True)
    request_id = Column(String(36), nullable=True)  # UUID for request tracing
    
    def __repr__(self):
        return (
            f"<AuditLog(id={self.id}, action='{self.action}', "
            f"entity='{self.entity_type}:{self.entity_id}')>"
        )
