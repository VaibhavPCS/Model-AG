"""
Download SAM3 and Grounding DINO models for production
Run: python download_models.py
"""

import os
from pathlib import Path
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODELS_DIR = Path("models")
MODELS_DIR.mkdir(exist_ok=True)


def download_file(url: str, destination: str):
    """Download file from URL with progress."""
    logger.info(f"Downloading {url}...")
    
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    with open(destination, 'wb') as f:
        downloaded = 0
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
            downloaded += len(chunk)
            if total_size > 0:
                percent = (downloaded / total_size) * 100
                logger.info(f"  Progress: {percent:.1f}%")
    
    logger.info(f"✅ Downloaded to {destination}")


# Model URLs (will need to be updated with actual sources)
MODELS = {
    "SAM3": {
        "url": "https://dl.fbaipublicfiles.com/segment_anything_3/sam3.pth",
        "dest": MODELS_DIR / "sam3.pth"
    },
    "Grounding DINO": {
        "url": "https://github.com/IDEA-Research/GroundingDINO/releases/download/v0.1.0/groundingdino_swinT_ogc.pth",
        "dest": MODELS_DIR / "groundingdino_swinT_ogc.pth"
    }
}


if __name__ == "__main__":
    logger.info("🚀 Starting model downloads...")
    logger.info("⚠️  Note: URLs may need updating based on latest releases")
    
    for model_name, config in MODELS.items():
        dest = config["dest"]
        if dest.exists():
            logger.info(f"✅ {model_name} already exists, skipping")
            continue
        
        try:
            download_file(config["url"], str(dest))
        except Exception as e:
            logger.error(f"❌ Failed to download {model_name}: {e}")
    
    logger.info("\n✅ Model download complete!")
    logger.info(f"📦 Models are ready in: {MODELS_DIR}") 
