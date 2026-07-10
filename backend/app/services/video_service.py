import json
import logging
from pathlib import Path
import subprocess
from uuid import uuid4

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.video import Video

logger = logging.getLogger(__name__)


def _allowed_extensions() -> set[str]:
    settings = get_settings()
    return {
        item.strip().lower()
        for item in settings.allowed_video_extensions.split(",")
        if item.strip()
    }


def _extract_duration_seconds(path: Path) -> float | None:
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "json",
                str(path),
            ],
            capture_output=True,
            check=True,
            text=True,
            timeout=15,
        )
        data = json.loads(result.stdout)
        duration = data.get("format", {}).get("duration")
        return round(float(duration), 2) if duration else None
    except Exception:
        logger.info("Could not extract video duration with ffprobe for %s", path)
        return None


def save_upload(db: Session, user_id: str, file: UploadFile) -> Video:
    settings = get_settings()
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    suffix = Path(file.filename or "video.mp4").suffix or ".mp4"
    suffix = suffix.lower()
    if suffix not in _allowed_extensions():
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported video type. Allowed: {', '.join(sorted(_allowed_extensions()))}",
        )
    if file.content_type and not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be a video")

    stored_name = f"{uuid4()}{suffix}"
    destination = upload_dir / stored_name
    content = file.file.read()
    max_bytes = settings.max_upload_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"Video is too large. Max size is {settings.max_upload_mb} MB",
        )
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded video is empty")

    destination.write_bytes(content)
    duration_seconds = _extract_duration_seconds(destination)

    video = Video(
        user_id=user_id,
        title=Path(file.filename or stored_name).stem,
        filename=file.filename or stored_name,
        file_path=str(destination),
        file_size=len(content),
        duration_seconds=duration_seconds,
    )
    db.add(video)
    db.commit()
    db.refresh(video)
    return video
