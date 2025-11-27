from typing import Tuple, Optional
from PIL import Image
import imagehash
from haversine import haversine, Unit
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.submission import Submission
from app.schemas.submission import FraudFlagModel


class FraudDetector:
    def __init__(self, gps_tolerance_meters=20, duplicate_hamming_threshold=5):
        self.gps_tolerance_meters = gps_tolerance_meters
        self.duplicate_hamming_threshold = duplicate_hamming_threshold

    def calculate_distance(self, coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
        """Calculate Haversine distance in meters."""
        return haversine(coord1, coord2, unit=Unit.METERS)

    def generate_phash(self, image_path: str) -> str:
        """Generate perceptual hash string of the image."""
        image = Image.open(image_path)
        phash = imagehash.phash(image)
        return str(phash)

    async def check_distance_to_last_photo(
        self,
        db: AsyncSession,
        site_id: int,
        surveyor_id: int,
        current_coords: Tuple[float, float]
    ) -> Tuple[bool, Optional[str]]:
        """Check GPS distance between current photo and last photo for same site and surveyor."""
        query = (
            select(Submission)
            .where(Submission.site_id == site_id, Submission.surveyor_id == surveyor_id)
            .order_by(Submission.created_at.desc())
            .limit(1)
        )
        result = await db.execute(query)
        last_submission = result.scalars().first()

        if not last_submission:
            return True, None  # No previous photo to compare, accept by default

        last_coords = (float(last_submission.gps_lat), float(last_submission.gps_lon))
        dist = self.calculate_distance(current_coords, last_coords)
        if dist > self.gps_tolerance_meters:
            msg = f"GPS discrepancy too large: {dist:.2f} meters; maximum allowed is {self.gps_tolerance_meters} meters."
            return False, msg
        return True, None

    async def check_duplicate_photo(
        self,
        db: AsyncSession,
        phash_new: str,
        site_id: int,
        surveyor_id: int
    ) -> Tuple[bool, Optional[str]]:
        """Check if photo is a duplicate comparing against previous photos."""
        site_query = (
            select(Submission.phash)
            .where(
                Submission.site_id == site_id,
                Submission.is_approved == True,
                Submission.phash != None
            )
            .order_by(Submission.created_at.desc())
            .limit(2)
        )
        site_res = await db.execute(site_query)
        site_hashes = [r[0] for r in site_res.all()]

        surv_query = (
            select(Submission.phash)
            .where(
                Submission.surveyor_id == surveyor_id,
                Submission.phash != None
            )
            .order_by(Submission.created_at.desc())
            .limit(3)
        )
        surv_res = await db.execute(surv_query)
        surv_hashes = [r[0] for r in surv_res.all()]

        all_hashes = set(site_hashes + surv_hashes)

        new_hash_obj = imagehash.hex_to_hash(phash_new)

        for old_hash_str in all_hashes:
            old_hash_obj = imagehash.hex_to_hash(old_hash_str)
            dist = new_hash_obj - old_hash_obj
            if dist <= self.duplicate_hamming_threshold:
                msg = f"Duplicate photo detected with hamming distance {dist} (threshold {self.duplicate_hamming_threshold})"
                return True, msg
        return False, None

    def create_fraud_flag(self, flag_type: str, description: Optional[str]) -> FraudFlagModel:
        return FraudFlagModel(flag_type=flag_type, description=description)
