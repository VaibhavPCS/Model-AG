"""
Construction Stage Classifier
Purpose: Classify construction progress stage based on detections
Author: BMAD BMM Agents Dev
Date: 2025-11-27
"""

from typing import Dict, Any, List, Tuple
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ConstructionStage(str, Enum):
    """Construction project stages."""
    PLANNING = "planning"
    SITE_PREPARATION = "site_preparation"
    FOUNDATION = "foundation"
    WALLS = "walls"
    ROOFING = "roofing"
    ELECTRICAL = "electrical"
    PLUMBING = "plumbing"
    FINISHING = "finishing"
    COMPLETED = "completed"


class ConstructionStageClassifier:
    """
    Classify construction stage based on detected elements.
    Uses heuristics to determine project progress.
    """
    
    # Stage progression rules
    STAGE_INDICATORS = {
        ConstructionStage.FOUNDATION: {
            "keywords": ["foundation", "excavation", "concrete base", "concrete"],
            "confidence_threshold": 0.7
        },
        ConstructionStage.WALLS: {
            "keywords": ["brick", "walls", "steel reinforcement", "concrete blocks", "masonry"],
            "confidence_threshold": 0.7
        },
        ConstructionStage.ROOFING: {
            "keywords": ["roofing", "roof structure", "tiles", "metal sheets", "roof"],
            "confidence_threshold": 0.7
        },
        ConstructionStage.ELECTRICAL: {
            "keywords": ["wiring", "electrical", "conduits", "cables", "wires"],
            "confidence_threshold": 0.6
        },
        ConstructionStage.FINISHING: {
            "keywords": ["paint", "finishing", "windows", "doors", "tiles", "flooring"],
            "confidence_threshold": 0.6
        },
        ConstructionStage.COMPLETED: {
            "keywords": ["completed", "final", "handover"],
            "confidence_threshold": 0.8
        }
    }
    
    async def classify_stage(
        self,
        detections: Dict[str, Any]
    ) -> Tuple[ConstructionStage, float, Dict]:
        """
        Classify construction stage from detections.
        
        Args:
            detections: Output from Grounding DINO
        
        Returns:
            (stage, confidence, details)
        """
        try:
            if not detections.get("detections"):
                return ConstructionStage.SITE_PREPARATION, 0.5, {}
            
            detected_labels = [
                d["label"].lower() 
                for d in detections["detections"]
            ]
            
            stage_scores = {}
            
            # Score each stage
            for stage, indicators in self.STAGE_INDICATORS.items():
                score = 0
                matched_keywords = []
                
                for keyword in indicators["keywords"]:
                    if any(keyword.lower() in label for label in detected_labels):
                        score += 1
                        matched_keywords.append(keyword)
                
                if score > 0:
                    stage_scores[stage] = {
                        "score": score,
                        "matched": matched_keywords,
                        "confidence": min(score * 0.25, 1.0)
                    }
            
            if not stage_scores:
                return ConstructionStage.SITE_PREPARATION, 0.5, {}
            
            # Get highest scoring stage
            best_stage = max(
                stage_scores.items(),
                key=lambda x: x[1]["score"]
            )
            
            stage = best_stage[0]
            confidence = best_stage[1]["confidence"]
            details = {
                "matched_elements": best_stage[1]["matched"],
                "all_scores": {k.value: v for k, v in stage_scores.items()}
            }
            
            return stage, confidence, details
            
        except Exception as e:
            logger.error(f"Stage classification error: {e}")
            return ConstructionStage.SITE_PREPARATION, 0.0, {}
    
    async def estimate_completion_percentage(
        self,
        stage: ConstructionStage
    ) -> float:
        """Estimate project completion percentage based on stage."""
        stage_completion = {
            ConstructionStage.PLANNING: 5,
            ConstructionStage.SITE_PREPARATION: 10,
            ConstructionStage.FOUNDATION: 20,
            ConstructionStage.WALLS: 40,
            ConstructionStage.ROOFING: 60,
            ConstructionStage.ELECTRICAL: 75,
            ConstructionStage.PLUMBING: 80,
            ConstructionStage.FINISHING: 90,
            ConstructionStage.COMPLETED: 100
        }
        
        return float(stage_completion.get(stage, 0))
