import os
from pathlib import Path
from datetime import datetime
import uuid


class StorageService:
    def __init__(self, base_path: Path):
        self.base_path = base_path

    def save_photo(self, site_id: int, photo_bytes: bytes, filename: str) -> Path:
        now = datetime.utcnow()
        folder = self.base_path / "photos" / str(site_id) / str(now.year) / str(now.month)
        folder.mkdir(parents=True, exist_ok=True)
        unique_name = f"{uuid.uuid4().hex}_{filename}"
        file_path = folder / unique_name

        with open(file_path, "wb") as f:
            f.write(photo_bytes)

        return file_path
