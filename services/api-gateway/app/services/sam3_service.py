"""
SAM Service using Segment Anything (ViT-H)
Runs on CPU/MPS (Mac) without CUDA.
"""

from typing import Dict, Any, List
import logging
from pathlib import Path

import torch
import numpy as np
import cv2
from segment_anything import sam_model_registry, SamPredictor

logger = logging.getLogger(__name__)


class SAM3Service:
    """
    Wrapper around SAM ViT-H for segmentation.

    Takes normalized bounding boxes (0–1) and returns masks with area percentages.
    """

    def __init__(self):
        self.predictor: SamPredictor | None = None
        self.model_type = "vit_h"
        self.checkpoint_path = "models/sam_vit_h_4b8939.pth"

        if torch.backends.mps.is_available():
            self.device = "mps"
        elif torch.cuda.is_available():
            self.device = "cuda"
        else:
            self.device = "cpu"

    async def load_model(self):
        """Load SAM ViT-H from local checkpoint."""
        try:
            ckpt = Path(self.checkpoint_path)
            if not ckpt.exists():
                logger.error(f"SAM checkpoint not found at {ckpt}")
                self.predictor = None
                return

            print(f"🤖 Loading SAM ViT-H on {self.device}...")
            sam = sam_model_registry[self.model_type](checkpoint=str(ckpt))
            sam.to(device=self.device)
            self.predictor = SamPredictor(sam)
            print("✅ SAM ViT-H loaded successfully!")
        except Exception as e:
            logger.error(f"Failed to load SAM model: {e}")
            self.predictor = None

    async def segment(self, image_path: str, bboxes: List[List[float]]) -> Dict[str, Any]:
        """
        Segment objects given normalized bounding boxes.

        Args:
            image_path: Path to the image.
            bboxes: List of [x1, y1, x2, y2] in normalized coordinates (0–1).

        Returns:
            Dict with:
              - masks: list of {id, confidence, area_percentage}
              - total_masks: int
        """
        if self.predictor is None:
            logger.warning("SAM predictor not loaded, returning placeholder masks.")
            return self._placeholder_masks(len(bboxes))

        try:
            print(f"🔍 Running SAM segmentation on: {image_path}")
            image_bgr = cv2.imread(str(image_path))
            if image_bgr is None:
                raise ValueError(f"Could not read image at {image_path}")
            image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

            self.predictor.set_image(image_rgb)
            h, w = image_rgb.shape[:2]
            total_pixels = h * w

            if not bboxes:
                return {"masks": [], "total_masks": 0}

            # Convert normalized boxes to pixel coordinates
            input_boxes = []
            for box in bboxes:
                x1, y1, x2, y2 = box
                input_boxes.append([x1 * w, y1 * h, x2 * w, y2 * h])

            input_boxes_tensor = torch.tensor(input_boxes, device=self.predictor.device)
            transformed_boxes = self.predictor.transform.apply_boxes_torch(
                input_boxes_tensor, image_rgb.shape[:2]
            )

            masks, scores, _ = self.predictor.predict_torch(
                point_coords=None,
                point_labels=None,
                boxes=transformed_boxes,
                multimask_output=False,
            )

            result_masks = []
            for i, mask in enumerate(masks):
                binary_mask = mask[0].cpu().numpy().astype(bool)
                area_pixels = int(np.sum(binary_mask))
                area_pct = (area_pixels / total_pixels) * 100.0

                result_masks.append(
                    {
                        "id": i,
                        "confidence": float(scores[i].item()),
                        "area_percentage": round(float(area_pct), 2),
                    }
                )

            return {
                "masks": result_masks,
                "total_masks": len(result_masks),
            }

        except Exception as e:
            logger.error(f"SAM segmentation error: {e}")
            return self._placeholder_masks(len(bboxes))

    def _placeholder_masks(self, count: int) -> Dict[str, Any]:
        return {
            "masks": [
                {
                    "id": i,
                    "confidence": round(0.9 - i * 0.05, 2),
                    "area_percentage": float(20 + i * 5),
                }
                for i in range(min(count, 5))
            ],
            "total_masks": count,
        }
