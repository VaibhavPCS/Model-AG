from pathlib import Path
import requests

MODELS_DIR = Path("models")
CONFIG_DIR = MODELS_DIR / "config"
MODELS_DIR.mkdir(exist_ok=True)
CONFIG_DIR.mkdir(exist_ok=True)

def download(url: str, dest: Path):
    if dest.exists():
        print(f"✅ Exists: {dest}")
        return
    print(f"📥 Downloading {url} -> {dest}")
    r = requests.get(url, stream=True, timeout=120)
    r.raise_for_status()
    with open(dest, "wb") as f:
        for chunk in r.iter_content(1024 * 1024):
            f.write(chunk)
    print(f"✅ Saved {dest}")

if __name__ == "__main__":
    # RT-DETR-L
    download(
        "https://github.com/ultralytics/assets/releases/download/v0.0.0/rtdetr-l.pt",
        MODELS_DIR / "rtdetr-l.pt"
    )

    # Grounding DINO Swin-T
    download(
        "https://github.com/IDEA-Research/GroundingDINO/releases/download/v0.1.0-alpha/groundingdino_swint_ogc.pth",
        MODELS_DIR / "groundingdino_swint_ogc.pth"
    )
    download(
        "https://raw.githubusercontent.com/IDEA-Research/GroundingDINO/main/groundingdino/config/GroundingDINO_SwinT_OGC.py",
        CONFIG_DIR / "GroundingDINO_SwinT_OGC.py"
    )

    # SAM 1 ViT-H
    download(
        "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth",
        MODELS_DIR / "sam_vit_h_4b8939.pth"
    )
