from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.submission import SubmissionResponse, AIValidationResult  # ✅ ADD AIValidationResult
from app.db.session import get_db
from app.services.rtdetr_service import RTDETRService
from app.services.storage_service import StorageService
from app.services.fraud_detector import FraudDetector
from app.models import Submission, AIResult, FraudFlag, Site
from pathlib import Path
import tempfile

router = APIRouter()

rtdetr_service = RTDETRService(model_name="rtdetr-l")
storage_service = StorageService(base_path=Path("storage"))
fraud_detector = FraudDetector()

@router.post("/submissions", response_model=SubmissionResponse, status_code=status.HTTP_201_CREATED)
async def create_submission(
    site_id: int = Form(...),
    gps_lat: float = Form(...),
    gps_lon: float = Form(...),
    surveyor_id: int = Form(...),
    photo: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    site = await db.get(Site, site_id)
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")

    # Save photo temporarily to compute pHash
    with tempfile.NamedTemporaryFile(delete=True, suffix=Path(photo.filename).suffix) as tmp_file:
        tmp_file.write(await photo.read())
        tmp_file.flush()
        phash_str = fraud_detector.generate_phash(tmp_file.name)

        # GPS distance check vs last photo by same surveyor for this site
        gps_valid, gps_msg = await fraud_detector.check_distance_to_last_photo(
            db, site_id, surveyor_id, (gps_lat, gps_lon)
        )

        # Duplicate photo check
        is_duplicate, dup_msg = await fraud_detector.check_duplicate_photo(
            db, phash_str, site_id, surveyor_id
        )

        # Save photo permanently
        tmp_file.seek(0)
        photo_bytes = tmp_file.read()
        photo_path = storage_service.save_photo(site_id, photo_bytes, photo.filename)

    fraud_flags = []
    status_str = "COMPLETED"

    if not gps_valid:
        fraud_flags.append(fraud_detector.create_fraud_flag("GPS_MISMATCH", gps_msg))
        status_str = "FLAGGED"

    if is_duplicate:
        fraud_flags.append(fraud_detector.create_fraud_flag("DUPLICATE_PHOTO", dup_msg))
        status_str = "FLAGGED"

    submission = Submission(
        site_id=site_id,
        photo_url=str(photo_path),
        gps_lat=gps_lat,
        gps_lon=gps_lon,
        surveyor_id=surveyor_id,
        phash=phash_str,
        status=status_str,
        is_approved=not fraud_flags
    )
    db.add(submission)
    await db.flush()

    # Run RT-DETR inference
    infer_result = await rtdetr_service.infer(photo_path)
    bboxes = infer_result["bounding_boxes"]
    confidence = infer_result["confidence_score"]

    ai_result = AIResult(
        submission_id=submission.id,
        model_type="rtdetr",
        stage=None,
        confidence_score=confidence,
        model_output={"bboxes": bboxes},
        triggered_by="auto"
    )
    db.add(ai_result)

    # Save fraud flags if any
    for flag in fraud_flags:
        db.add(
            FraudFlag(
                submission_id=submission.id,
                flag_type=flag.flag_type,
                details={"description": flag.description},
                resolved=False
            )
        )

    await db.commit()

    # Return alerts to surveyor/admin to re-capture photo
    alerts = []
    if fraud_flags:
        alerts.append("Fraud detected: please recapture the photo.")

    response = SubmissionResponse(
        submission_id=submission.id,
        validation_result=AIValidationResult(
            bounding_boxes=bboxes,
            confidence_score=confidence,
            flags=fraud_flags
        ),
        alerts=alerts,
    )

    return response
