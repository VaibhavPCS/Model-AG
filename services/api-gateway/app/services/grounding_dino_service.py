"""
Grounding DINO Service
"""

import sys
from pathlib import Path
from typing import Dict, Any, List
import logging
import torch

logger = logging.getLogger(__name__)

# Add local GroundingDINO source to path
GROUNDINGDINO_ROOT = Path(__file__).resolve().parents[3] / "groundingdino_src"
if str(GROUNDINGDINO_ROOT) not in sys.path:
    sys.path.insert(0, str(GROUNDINGDINO_ROOT))

from groundingdino.util.inference import load_model, load_image, predict  # ✅ will raise if really missing


class GroundingDINOService:
    def __init__(self):
        self.model = None
        self.config_path = "models/config/GroundingDINO_SwinT_OGC.py"
        self.weights_path = "models/groundingdino_swint_ogc.pth"

        if torch.backends.mps.is_available():
            self.device = "mps"
        elif torch.cuda.is_available():
            self.device = "cuda"
        else:
            self.device = "cpu"

    async def load_model(self):
        """Load Grounding DINO model."""
        try:
            print(f"🤖 Loading Grounding DINO (Swin-T) on {self.device}...")
            self.model = load_model(self.config_path, self.weights_path)
            self.model = self.model.to(self.device)
            print("✅ Grounding DINO model loaded!")
        except Exception as e:
            logger.error(f"Failed to load Grounding DINO: {e}")
            self.model = None

    async def detect(self, image_path: str, prompts: List[str] = None) -> Dict[str, Any]:
        if prompts is None:
            prompts = [
                "foundation concrete",
                "brick walls",
                "steel reinforcement",
                "roofing materials",
                "scaffolding",
                "construction workers",
            ]
        if self.model is None:
            logger.warning("Grounding DINO model not loaded, returning empty detections.")
            return {"detections": [], "prompts_used": [], "image_path": str(image_path)}

        try:
            base_dir = Path(__file__).resolve().parents[2]  # services/api-gateway
            full_path = (base_dir / image_path).resolve()
            print(f"🔍 Running Grounding DINO on: {full_path}")
            image_source, image = load_image(str(full_path))
            text_prompt = " . ".join(prompts)
            boxes, logits, phrases = predict(
                model=self.model,
                image=image,
                caption=text_prompt,
                box_threshold=0.35,
                text_threshold=0.25,
                device=self.device,
            )

            detections = []
            for i in range(len(boxes)):
                cx, cy, w, h = boxes[i]
                x1 = float(cx - w / 2)
                y1 = float(cy - h / 2)
                x2 = float(cx + w / 2)
                y2 = float(cy + h / 2)
                detections.append(
                    {
                        "label": phrases[i],
                        "confidence": float(logits[i]),
                        "bbox": [x1, y1, x2, y2],
                    }
                )

            return {
                "detections": detections,
                "prompts_used": prompts,
                "image_path": str(image_path),
            }

        except Exception as e:
            logger.error(f"Grounding DINO detection error: {e}")
            return {"detections": [], "prompts_used": prompts, "image_path": str(image_path)}
