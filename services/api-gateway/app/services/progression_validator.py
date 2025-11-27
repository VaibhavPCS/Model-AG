"""
Progression Validator
Purpose: Detect impossible/fraudulent progress patterns
Author: BMAD BMM Agents Dev
Date: 2025-11-27
"""

from typing import Tuple, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Submission, AIResult
from app.services.construction_stage_classifier import ConstructionStage
import logging

logger = logging.getLogger(__name__)


class ProgressionValidator:
    """
    Validates construction progress for fraud indicators:
    - Impossible stage regressions
    - Unrealistic speed of progress
    - Timestamp anomalies
    """
    
    def __init__(
        self,
        days_per_stage: int = 7,  # Expected minimum days per stage
        max_stage_jumps: int = 2   # Max stages that can be skipped
    ):
        self.days_per_stage = days_per_stage
        self.max_stage_jumps = max_stage_jumps
    
    async def validate_progression(
        self,
        db: AsyncSession,
        site_id: int,
        current_stage: ConstructionStage,
        current_confidence: float
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate if the current stage progression is realistic.
        
        Args:
            db: Database session
            site_id: Site ID
            current_stage: Detected stage in current submission
            current_confidence: Confidence of stage detection
        
        Returns:
            (is_valid, error_message)
        """
        try:
            # Get previous approved submission with AI results
            query = (
                select(Submission)
                .where(
                    Submission.site_id == site_id,
                    Submission.is_approved == True
                )
                .order_by(Submission.created_at.desc())
                .limit(1)
            )
            result = await db.execute(query)
            previous_submission = result.scalars().first()
            
            if not previous_submission:
                # First submission, always valid
                return True, None
            
            # Get AI result for previous submission
            ai_query = (
                select(AIResult)
                .where(AIResult.submission_id == previous_submission.id)
                .order_by(AIResult.created_at.desc())
                .limit(1)
            )
            ai_result = await db.execute(ai_query)
            previous_ai = ai_result.scalars().first()
            
            if not previous_ai or not previous_ai.stage:
                return True, None
            
            previous_stage = ConstructionStage(previous_ai.stage)
            
            # Check 1: Stage regression (going backwards)
            is_regression, msg = self._check_regression(previous_stage, current_stage)
            if not is_regression:
                return False, msg
            
            # Check 2: Impossible speed (too many stages too fast)
            is_realistic_speed, msg = await self._check_realistic_speed(
                db, site_id, current_stage
            )
            if not is_realistic_speed:
                return False, msg
            
            # Check 3: Stage jump validation
            is_valid_jump, msg = self._check_stage_jump(previous_stage, current_stage)
            if not is_valid_jump:
                return False, msg
            
            return True, None
            
        except Exception as e:
            logger.error(f"Progression validation error: {e}")
            return True, None  # Default to allowing if error
    
    def _check_regression(
        self,
        previous_stage: ConstructionStage,
        current_stage: ConstructionStage
    ) -> Tuple[bool, Optional[str]]:
        """Check if stage regressed (went backwards)."""
        stage_order = [
            ConstructionStage.PLANNING,
            ConstructionStage.SITE_PREPARATION,
            ConstructionStage.FOUNDATION,
            ConstructionStage.WALLS,
            ConstructionStage.ROOFING,
            ConstructionStage.ELECTRICAL,
            ConstructionStage.PLUMBING,
            ConstructionStage.FINISHING,
            ConstructionStage.COMPLETED
        ]
        
        prev_idx = stage_order.index(previous_stage)
        curr_idx = stage_order.index(current_stage)
        
        if curr_idx < prev_idx:
            msg = f"Stage regression detected: {previous_stage.value} → {current_stage.value}"
            return False, msg
        
        return True, None
    
    async def _check_realistic_speed(
        self,
        db: AsyncSession,
        site_id: int,
        current_stage: ConstructionStage
    ) -> Tuple[bool, Optional[str]]:
        """Check if progress speed is realistic."""
        query = (
            select(Submission)
            .where(Submission.site_id == site_id)
            .order_by(Submission.created_at.desc())
            .limit(10)
        )
        result = await db.execute(query)
        recent = result.scalars().all()
        
        if len(recent) < 2:
            return True, None
        
        # If we've moved 3+ stages in less than min_days, flag it
        time_diff = (
            recent[0].created_at - recent[-1].created_at
        ).days
        
        if time_diff < self.days_per_stage and len(recent) > 2:
            msg = f"Unrealistic progress speed: {len(recent)} submissions in {time_diff} days"
            return False, msg
        
        return True, None
    
    def _check_stage_jump(
        self,
        previous_stage: ConstructionStage,
        current_stage: ConstructionStage
    ) -> Tuple[bool, Optional[str]]:
        """Check if jumping too many stages at once."""
        stage_order = [
            ConstructionStage.PLANNING,
            ConstructionStage.SITE_PREPARATION,
            ConstructionStage.FOUNDATION,
            ConstructionStage.WALLS,
            ConstructionStage.ROOFING,
            ConstructionStage.ELECTRICAL,
            ConstructionStage.PLUMBING,
            ConstructionStage.FINISHING,
            ConstructionStage.COMPLETED
        ]
        
        jump_size = abs(stage_order.index(current_stage) - stage_order.index(previous_stage))
        
        if jump_size > self.max_stage_jumps:
            msg = f"Impossible stage jump: skipped {jump_size} stages ({previous_stage.value} → {current_stage.value})"
            return False, msg
        
        return True, None
